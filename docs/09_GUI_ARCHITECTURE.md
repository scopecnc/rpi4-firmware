# GUI Architecture

**Document:** 09 - GUI Architecture  
**Version:** 1.1  
**Date:** January 6, 2026

---

## 1. Overview

The GUI is a PyQt5-based touch kiosk interface designed for museum visitors to interact with the robotic microscope. It features live video display, automatic cycling through specimens, and manual jog controls, all with thread-safe operation.

### Key Design Goals
- **Museum-quality presentation:** Professional UI with branding
- **Touch-friendly:** Large buttons, clear labeling, intuitive layout
- **Autonomous operation:** Automatic cycling with minimal supervision
- **Manual override:** Visitors can explore without breaking auto-cycle
- **Thread-safe:** Video capture and motion control run in separate threads
- **Robust:** Handles segfaults from Qt painting race conditions

---

## 2. Application Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      scope_gui.py (789 lines)                    │
│                     Main PyQt5 Application                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               MicroscopeGUI (QMainWindow)                 │  │
│  │  - Main window management                                 │  │
│  │  - Event loop coordination                                │  │
│  │  - Callback registration                                  │  │
│  └───┬──────────────────────────────────────────────────────┘  │
│      │                                                           │
│      ├─> VideoWidget (1670×1080)                                │
│      │    - Live camera display                                 │
│      │    - Semi-transparent overlays                           │
│      │    - Title banner, specimen info, scale ruler           │
│      │                                                           │
│      ├─> SpecimenCard ×28 (230×80 each)                         │
│      │    - Touch-sensitive buttons                             │
│      │    - Visual highlighting when selected                   │
│      │    - Mineral name + location display                     │
│      │                                                           │
│      └─> JogButton ×8 (60×60 for XY, 75×38 for ZF)             │
│           - Press/hold detection                                │
│           - Continuous jog when held                            │
│           - Manual override trigger                             │
│                                                                  │
└──────┬───────────────────────────────────┬──────────────────────┘
       │                                    │
       ▼                                    ▼
┌──────────────────┐              ┌─────────────────────┐
│  video_thread.py │              │motion_controller.py │
│   (80 lines)     │              │    (360 lines)      │
│                  │              │                     │
│  VideoThread     │              │ MotionController    │
│  - QThread       │              │  - Protocol wrapper │
│  - OpenCV cap    │              │  - Auto-cycle logic │
│  - cv2.CAP_V4L2  │              │  - Watchdog thread  │
│  - QMutex lock   │              │  - Skip invalid pos │
│  - 30 FPS target │              │  - Callbacks        │
└────────┬─────────┘              └──────────┬──────────┘
         │                                   │
         │ QImage frames                     │ Serial
         │ (30 Hz)                           │ Commands
         │                                   │
         ▼                                   ▼
    GUI Paint Event              ┌──────────────────────┐
    (Main Thread)                │ teensy_protocol.py   │
                                 │    (320 lines)       │
                                 │                      │
                                 │ TeensyProtocol       │
                                 │  - Serial comm       │
                                 │  - Checksum calc     │
                                 │  - Message parsing   │
                                 │  - Error handling    │
                                 └───────────┬──────────┘
                                            │
                                            ▼
                                    Teensy 4.1 UART
                                    (115200 baud)
```

---

## 3. Threading Model

### Thread-Safe Design

The application uses multiple threads that must be carefully coordinated to avoid Qt painting conflicts:

**Main GUI Thread (Qt Event Loop):**
- Handles all UI updates
- Processes QPainter operations
- Responds to touch events
- Updates specimen card highlighting

**Video Thread (QThread):**
- Captures frames from USB camera via OpenCV
- Converts BGR → RGB → QImage
- Emits `frame_ready` signal with new frames
- Protected by QMutex during frame handoff

**Motion Controller Threads:**
- **Watchdog thread:** Sends !PING every 3 seconds
- **Auto-cycle thread:** Moves between specimens every 10 seconds
- **Serial read thread:** Processes Teensy responses (in teensy_protocol.py)

### Critical Threading Issues Resolved

**Problem:** Segmentation faults when updating GUI from multiple threads

**Root Cause:**
1. Video thread calls `set_video_frame()` → triggers `update()`
2. Motion controller calls `set_specimen_info()` → triggers `update()`
3. Specimen card highlighting calls `repaint()` → forces immediate paint
4. Multiple paint events overlap → QPainter collision → segfault

**Solution:**
```python
# WRONG - causes segfaults:
def set_specimen_info(self, specimen):
    self.specimen_info = specimen
    self.update()  # Direct call from callback thread

# WRONG - even worse:
def set_current(self, is_current):
    self.is_current = is_current
    self.repaint()  # Forces immediate paint, crashes if another paint active

# CORRECT - deferred to main thread:
def set_specimen_info(self, specimen):
    self.specimen_info = specimen
    QTimer.singleShot(0, self.update)  # Queue to main thread event loop

def set_current(self, is_current):
    self.is_current = is_current
    self.update()  # Schedule paint, don't force
```

**Key Rules:**
1. **Never call `repaint()` directly** - use `update()` to schedule paint
2. **Use `QTimer.singleShot(0, func)`** to defer from callbacks to main thread
3. **Lock shared data with QMutex** (video frames)
4. **Don't update 28 cards synchronously** during paint - defer with QTimer

---

## 4. Key Classes

### 4.1 MicroscopeGUI (QMainWindow)

**Purpose:** Main application window and event coordinator

**Responsibilities:**
- Create and layout all widgets
- Initialize motion controller and video thread
- Register callbacks for motion events
- Handle keyboard shortcuts (ESC to exit)
- Manage auto-mode timer (updates every 500ms)

**Key Methods:**
```python
def __init__(self, tray_file: str):
    # Initialize motion controller
    self.motion = MotionController(tray_file)
    self.motion.set_callbacks(
        position_callback=self.on_position_update,
        state_callback=self.on_state_change,
        specimen_callback=self.on_specimen_change
    )
    
    # Initialize video
    self.video = VideoThread(camera_index=0)
    self.video.frame_ready.connect(self.video_widget.set_video_frame)
    
def on_specimen_change(self, index: int, specimen: SpecimenPosition):
    """Handle specimen changes from motion controller"""
    # Update video overlay
    self.video_widget.set_specimen_info(specimen)
    
    # Update list highlighting (deferred to avoid paint conflicts)
    def update_cards():
        for i, card in enumerate(self.specimen_cards):
            card.set_current(i == index)
    QTimer.singleShot(10, update_cards)  # 10ms delay
```

**Event Flow:**
1. User touches specimen card → `on_specimen_selected(index)`
2. Calls `motion.move_to_specimen(index)` → marks user interaction
3. Motion controller sends serial command → Teensy moves
4. Teensy reports completion → callback fires
5. `on_specimen_change()` updates GUI

---

### 4.2 VideoWidget (QWidget)

**Purpose:** Display live video with semi-transparent overlays

**Layout:**
```
┌────────────────────────────────────────────────────┐
│  Title Banner (translucent, 70px height)           │
│  ┌──────────┬─────────────────────┬──────────┐    │
│  │ Status   │   "The Mineral      │ Position │    │
│  │ (Green ● │    Microscope"      │  X: 58mm │    │
│  │  IDLE)   │  Tom Mortimer URL   │  Y: 21mm │    │
│  │ AUTO     │                     │  Z:  9mm │    │
│  └──────────┴─────────────────────┴──────────┘    │
├────────────────────────────────────────────────────┤
│                                                    │
│            Live Video (1920x1080)                 │
│            (scaled to fill widget)                │
│                                                    │
│                              ┌──────────────────┐ │
│                              │ Golden Beryl     │ │
│                              │ Palermo Mine,    │ │
│                              │ North Groton     │ │
│                              │ Collected by:    │ │
│                              │ Sarah Johnson    │ │
│                              └──────────────────┘ │
│                                                    │
│                    ┌─────────────┐                │
│                    │ Scale Ruler  │                │
│                    │ 0────5mm────10│                │
│                    └─────────────┘                │
└────────────────────────────────────────────────────┘
```

**Key Methods:**
```python
def paintEvent(self, event):
    """Draw video frame and overlays"""
    painter = QPainter(self)
    
    # Draw video (fill entire widget to avoid black bars)
    self.frame_mutex.lock()
    current_frame = self.video_frame
    self.frame_mutex.unlock()
    
    if current_frame:
        scaled_pixmap = current_frame.scaled(
            self.size(), 
            Qt.KeepAspectRatioByExpanding,  # Fill widget
            Qt.SmoothTransformation
        )
        painter.drawPixmap(0, 0, scaled_pixmap)
    
    # Draw overlays (all thread-safe, read-only)
    self._draw_title_banner(painter)
    self._draw_specimen_info(painter)
    self._draw_scale_ruler(painter)
```

**Overlay Details:**

**Title Banner (70px height, alpha=200):**
- Left: Status indicator (green/red/yellow circle) + state name + AUTO/MANUAL
- Center: "The Mineral Microscope" title + "Tom Mortimer (mindatnh.org)" subtitle
- Right: Position display (X, Y, Z, F stacked vertically)

**Specimen Info Card (300×150px, bottom-right):**
- Mineral name (14pt bold, word-wrapped)
- Location (11pt, word-wrapped)
- Collector (10pt gray, single line)
- Semi-transparent background (alpha=200)

**Scale Ruler (bottom-center):**
- Dynamic: adjusts based on zoom (F position)
- FOV ranges from 20mm (F=0) to 5mm (F=30)
- Shows ruler with multiple tick marks and labels

---

### 4.3 MotionController

**Purpose:** High-level motion control with auto-cycle logic

**Key Features:**
- Wraps `TeensyProtocol` for serial communication
- Implements auto-cycle thread (10s per specimen)
- Tracks user interaction with 30s timeout
- Skips invalid specimens automatically
- Provides callbacks for GUI updates

**Auto-Cycle State Machine:**
```
┌─────────────────┐
│   Initialize    │
│   (Connect +    │
│    Home)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AUTO-CYCLE     │◄────────────────┐
│  (Moving to     │                 │
│   next spec)    │                 │
└────────┬────────┘                 │
         │                          │
         │ Specimen reached         │
         ▼                          │
┌─────────────────┐                 │
│  VIEWING        │                 │
│  (10 seconds)   │                 │
└────────┬────────┘                 │
         │                          │
         │ Time elapsed             │
         ├─────────────────────────►│
         │                          │
         │ User touches button      │
         ▼                          │
┌─────────────────┐                 │
│  MANUAL MODE    │                 │
│  (30s timeout)  │                 │
└────────┬────────┘                 │
         │                          │
         │ 30s no interaction       │
         └──────────────────────────┘
```

**Code Example:**
```python
def _auto_cycle_loop(self):
    """Auto-cycle thread main loop"""
    while self.running:
        # Check if manual override active
        if time.time() - self.last_interaction_time < self.manual_timeout:
            time.sleep(0.5)
            continue
        
        # Move to next valid specimen
        attempts = 0
        while attempts < len(self.specimens):
            next_idx = (self.current_specimen_index + 1) % len(self.specimens)
            
            # Skip invalid specimens
            if not self.is_specimen_valid(next_idx):
                self.current_specimen_index = next_idx
                attempts += 1
                continue
            
            # Move to specimen
            if self.move_to_specimen(next_idx):
                break
            attempts += 1
        
        # Wait before next move
        time.sleep(self.cycle_interval)  # 10 seconds
```

---

### 4.4 VideoThread (QThread)

**Purpose:** Capture video frames from USB camera in background thread

**Implementation:**
```python
class VideoThread(QThread):
    frame_ready = pyqtSignal(QImage)  # Signal to main thread
    
    def run(self):
        """Thread main loop - runs until stop() called"""
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  # V4L2 backend required
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        while self.running:
            ret, frame = cap.read()
            if ret:
                # Convert BGR → RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                
                # Convert to QImage
                q_image = QImage(
                    rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888
                )
                
                # Emit to main thread
                self.frame_ready.emit(q_image.copy())
            
            time.sleep(0.033)  # ~30 FPS
        
        cap.release()
```

**Critical Details:**
- **Must use `cv2.CAP_V4L2`** - GStreamer backend fails on RPi4
- **Emit `q_image.copy()`** - Qt requires ownership transfer
- **No direct GUI updates** - only emit signals
- **Clean shutdown** with 2-second timeout

---

## 5. Data Flow

### Specimen Selection Flow

```
User touches specimen card
    │
    ▼
SpecimenCard.clicked signal
    │
    ▼
MicroscopeGUI.on_specimen_selected(index)
    │
    ├─> motion.mark_user_interaction()  # Reset 30s timer
    │
    └─> motion.move_to_specimen(index)
            │
            ▼
        TeensyProtocol.move_absolute(x, y, z, f)
            │
            ▼
        Serial: "!MOVE X58.00 Y21.50 Z9.00 F3.00 *2C\n"
            │
            ▼
        Teensy executes move
            │
            ▼
        Serial: "@COMPLETE 9 X=58.00 Y=21.50 Z=9.00 F=3.00 *4C\n"
            │
            ▼
        motion_controller._handle_complete_response()
            │
            ▼
        Callbacks fire:
            ├─> on_position_update(x, y, z, f)
            │       └─> VideoWidget.set_position()
            │
            ├─> on_state_change("IDLE")
            │       └─> VideoWidget.set_state()
            │
            └─> on_specimen_change(index, specimen)
                    ├─> VideoWidget.set_specimen_info()
                    └─> SpecimenCard highlighting (deferred)
```

---

## 6. Configuration

### Specimen Tray JSON Format

```json
{
  "specimens": [
    {
      "row": 0,
      "col": 0,
      "mineral_name": "Smoky Quartz",
      "location": "Ruggles Mine, Grafton",
      "collector": "Tom Mortimer",
      "x_offset_mm": -1.0,
      "y_offset_mm": -1.0,
      "focus_mm": 8.0,
      "zoom_mm": 2.0
    },
    ...
  ]
}
```

**Fields:**
- `row`, `col`: Grid position (0-indexed)
- `mineral_name`: Display name
- `location`: Locality (e.g., "Palermo Mine, North Groton")
- `collector`: Collector name
- `x_offset_mm`, `y_offset_mm`: Fine-tuning offsets
- `focus_mm`: Z-axis height for this specimen
- `zoom_mm`: F-axis zoom level

**Grid Calculation:**
```python
# From specimen_grid.py
GRID_START_X = 20.0      # mm
GRID_START_Y = 22.5      # mm
BOX_WIDTH_MM = 36.0      # mm spacing
BOX_HEIGHT_MM = 40.0     # mm spacing (reduced to fit Y limit)

def calculate_position(row, col):
    x = GRID_START_X + (col * BOX_WIDTH_MM)
    y = GRID_START_Y + (row * BOX_HEIGHT_MM)
    return x, y
```

---

## 7. Known Issues and Solutions

### Issue: Segmentation Faults

**Cause:** Qt doesn't allow nested `QPainter` usage. Calling `repaint()` during a `paintEvent()` causes crash.

**Solution:**
- Use `update()` instead of `repaint()` (schedules paint, doesn't force)
- Defer specimen card updates with `QTimer.singleShot(10, update_func)`
- Never call GUI methods directly from callbacks - use QTimer

### Issue: Black Bars on Video

**Cause:** `Qt.KeepAspectRatio` adds black bars if aspect ratio doesn't match

**Solution:**
- Use `Qt.KeepAspectRatioByExpanding` to fill entire widget
- Video will be cropped at edges, but no black bars
- Ensures translucent title banner overlays actual video

### Issue: Specimen Cards Not Highlighting

**Cause:** GUI updates from callbacks on different thread, Qt event loop not processing immediately

**Solution:**
- Added `force_initial_highlight()` called 500ms after startup
- Deferred card updates to avoid conflicts with paint events
- Removed `QApplication.processEvents()` which was causing interference

### Issue: Video Capture Fails

**Cause:** Default OpenCV backend (GStreamer) doesn't work reliably on RPi4

**Solution:**
```python
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  # Explicit V4L2 backend
```

---

## 8. Performance Considerations

### Frame Rate
- **Target:** 30 FPS
- **Actual:** 25-30 FPS (depends on RPi4 CPU load)
- **Acceptable:** Anything >20 FPS appears smooth

### Memory
- **Video frames:** ~1.2 MB each (640×480×3 bytes)
- **Total GUI:** ~50 MB typical
- **PyQt5 overhead:** ~30 MB
- **Total process:** ~120 MB on RPi4

### CPU Usage
- **Video thread:** ~15% of one core
- **GUI thread:** ~5% (mostly paint events)
- **Motion thread:** <1% (mostly sleeping)
- **Total:** ~20% of RPi4 (plenty of headroom)

---

## 9. Testing and Debugging

### Debug Prints

All major operations have debug prints:
```
[GUI] Specimen change: 1 - Golden Beryl
[VideoWidget] Setting specimen info: Golden Beryl (thread 546995827040)
[VideoWidget] Queuing update() call
[VideoWidget] Update queued
[GUI] Deferred: Updating card highlighting for index 1
[paintEvent] START
[paintEvent] Frame locked/unlocked
[paintEvent] Drawing title banner
[paintEvent] Drawing status bar
[paintEvent] Drawing specimen info
[_draw_specimen_info] Drawing card for Golden Beryl
[paintEvent] Drawing scale ruler
[paintEvent] END
```

### Common Issues

**"QBackingStore::endPaint() called with active painter":**
- **Cause:** Nested painting (repaint() during paintEvent)
- **Fix:** Use update() instead of repaint()

**Video black screen:**
- **Cause:** Wrong OpenCV backend
- **Fix:** Add `cv2.CAP_V4L2` parameter

**Segfault after specimen change:**
- **Cause:** Card highlighting during paint event
- **Fix:** Defer with QTimer.singleShot()

---

## 10. January 2026 Updates

### 10.1 Step Size Selector

Added to production GUI jog controls:
- Toggle buttons: [0.1] [0.5] [2.0] [5.0] mm
- Default: 0.5mm
- Visual highlight shows selected step size
- All axes use the same step size

### 10.2 Jog Re-entrancy Protection

Fixed double-move bug on button tap:
- Added `_jog_in_progress` per-axis flag
- Timer interval increased from 200ms to 500ms
- Jog command blocks until COMPLETE received

### 10.3 Scale Ruler Calibration

Calibrated using micrometer measurement:
```python
self.f_max = 11.5    # Actual max F value
self.fov_min = 4.7   # mm FOV at F=0 (zoomed out)
self.fov_max = 0.83  # mm FOV at F=11.5 (zoomed in)
```

### 10.4 Video Initialization Reliability

Added retry logic to video_thread.py:
- 3-attempt retry for DV timing query
- 3-attempt retry for DV timing lock
- 3-attempt retry for camera open
- Increased delays for HDMI signal stabilization

---

## 11. Future Enhancements

### Potential Improvements
- **Image capture:** Save snapshots to disk
- **Multi-camera:** Support multiple views simultaneously
- **Zoom presets:** Quick zoom buttons
- **Annotation mode:** Let visitors add comments
- **Statistics:** Track most-viewed specimens
- **Remote monitoring:** Web interface for staff
- **Voice narration:** Audio descriptions of minerals
- **Non-blocking homing:** Background thread for responsive video during startup

---

**Next Section:** [10 - User Guide](10_USER_GUIDE.md)
