# Software Specification

**Document:** 04 - Software Specification  
**Version:** 1.2  
**Date:** December 23, 2025

---

## 1. Development Environment

### 1.1 Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| **Visual Studio Code** | Latest | IDE |
| **PlatformIO Extension** | Latest | Build system and Arduino framework |
| **Teensy Loader** | Latest | Firmware upload (automatic via PlatformIO) |
| **Git** | Any | Version control (optional) |

### 1.2 Installation Steps

1. **Install VS Code:**
   ```
   https://code.visualstudio.com/
   ```

2. **Install PlatformIO Extension:**
   - Open VS Code
   - Click Extensions (Ctrl+Shift+X)
   - Search "PlatformIO IDE"
   - Click Install
   - Restart VS Code

3. **Install Teensy Udev Rules (Linux only):**
   ```bash
   wget https://www.pjrc.com/teensy/00-teensy.rules
   sudo cp 00-teensy.rules /etc/udev/rules.d/
   sudo udevadm control --reload-rules
   ```

4. **Open Project:**
   - File → Open Folder
   - Navigate to `teensy_firmware/`
   - PlatformIO will auto-detect `platformio.ini`

---

## 2. Project Structure

```
teensy_firmware/
├── .vscode/               # VS Code configuration
│   ├── extensions.json   # Recommended extensions
│   └── settings.json     # Workspace settings
├── .pio/                  # PlatformIO build cache (auto-generated)
├── docs/                  # Technical documentation (this folder)
│   ├── 00_INDEX.md
│   ├── 01_PRODUCT_OVERVIEW.md
│   ├── 02_SYSTEM_ARCHITECTURE.md
│   ├── 03_HARDWARE_SPECIFICATION.md
│   ├── 04_SOFTWARE_SPECIFICATION.md
│   ├── 05_PROTOCOL_SPECIFICATION.md
│   ├── 06_DIAGNOSTIC_PROCEDURES.md
│   ├── 07_ISSUES_AND_RESOLUTIONS.md
│   └── 08_RPI4_INTEGRATION.md
├── src/                   # Source code
│   └── main.cpp          # Main firmware (3114 lines)
├── platformio.ini        # Build configuration
├── project_context.md    # Development history/context
├── PROTOCOL.md           # Complete protocol specification
├── README.md             # Quick start guide
├── TEST_PROGRAM_GUIDE.md # Testing procedures
├── main_production.cpp   # Backup/archive
└── main_test.cpp         # Backup/archive
```

---

## 3. Build Configuration

### 3.1 platformio.ini

```ini
[env:teensy41]
platform = teensy
board = teensy41
framework = arduino
monitor_speed = 115200

; Upload settings
upload_protocol = teensy-gui

; Build flags for debugging
build_flags = 
    -DUSB_SERIAL
    -DCORE_TEENSY

; Library dependencies
lib_deps = 
    waspinator/AccelStepper@^1.64
```

### 3.2 Build Commands

**Via VS Code:**
- **Build:** Click checkmark (✓) in bottom toolbar OR `Ctrl+Alt+B`
- **Upload:** Click arrow (→) in bottom toolbar OR `Ctrl+Alt+U`
- **Monitor:** Click plug icon in bottom toolbar OR `Ctrl+Alt+S`
- **Clean:** PlatformIO → Clean

**Via Terminal:**
```bash
# Build
platformio run

# Upload
platformio run --target upload

# Monitor
platformio device monitor --baud 115200

# Clean build
platformio run --target clean
```

---

## 4. Firmware Architecture

### 4.1 Source Code Organization

**main.cpp** (3114 lines) is organized as follows:

| Line Range | Section | Description |
|------------|---------|-------------|
| 1-53 | Header Comment | Version, description, features |
| 54-93 | Pin Definitions | All GPIO assignments |
| 95-129 | Motion Configuration | Speed, acceleration, limits |
| 130-275 | State & Objects | State machine, stepper objects |
| 287-440 | ISRs | 8 interrupt handlers for limit switches |
| 441-614 | Helper Functions | Communication, utility functions |
| 615-784 | Setup | Pin initialization, motor config |
| 785-1024 | Main Loop | State processing, serial handling |
| 1025-1450 | Motion Control | Homing, movement, limit checking |
| 1451-1844 | Protocol Functions | ACK/NACK, sequence handling |
| 1845-2369 | Diagnostic Menu | Menu system printing |
| 2370-2630 | Diagnostic Commands | Interactive command processing |
| 2631-3114 | Protocol Commands | Protocol command execution |

### 4.2 Key Constants

Located at top of main.cpp, easily modifiable:

**Pin Assignments (lines 61-92):**
```c++
const int LED_PIN = 13;
const int ENA_ALL_PIN = 33;
const int X_STEP_PIN = 2;
const int X_DIR_PIN = 3;
const int X_MIN_PIN = 4;
const int X_MAX_PIN = 5;
// ... (similar for Y, Z, F)
```

**Motion Parameters (lines 95-129):**
```c++
const float MAX_SPEED = 6000.0;        // steps/sec
const float ACCEL = 2000.0;            // steps/sec²
const float HOMING_SPEED = 3000.0;     // steps/sec
const float HOMING_CREEP_SPEED = 400.0; // steps/sec

const float STEPS_PER_MM = 400.0;      // Calibrated value
const float BACKOFF_DISTANCE_MM = 5.0; // Homing backoff

const float X_MAX_TRAVEL_MM = 270.0;   // Soft limits
const float Y_MAX_TRAVEL_MM = 150.0;
const float Z_MAX_TRAVEL_MM = 30.0;
const float F_MAX_TRAVEL_MM = 30.0;

const unsigned long DEBOUNCE_MS = 50;  // Limit switch debounce
const unsigned int PULSE_WIDTH_US = 10; // Step pulse width
```

**Protocol Parameters (lines 218-228):**
```c++
const unsigned long WATCHDOG_TIMEOUT_MS = 5000;  // 5 seconds
const unsigned long HEARTBEAT_INTERVAL = 2000;   // 2 seconds
```

---

## 5. Calibration and Configuration

### 5.1 STEPS_PER_MM Calibration

**Current Value:** 400 steps/mm (verified accurate)

**How to Recalibrate:**
1. Home all axes
2. Mark current position on physical frame
3. Command 100mm move: `!MOVE X100`
4. Measure actual travel with ruler/caliper
5. Calculate new value:
   ```
   new_STEPS_PER_MM = old_STEPS_PER_MM × (commanded_mm / actual_mm)
   ```

**Example:**
- Commanded: 100mm
- Actual: 50mm
- Old value: 200
- New value: 200 × (100/50) = 400 ✓ (current setting)

### 5.2 Soft Limit Measurement

**Current Values:**
- X: 270mm
- Y: 150mm
- Z: 30mm
- F: 30mm (not enforced)

**How to Remeasure:**
1. Home axis
2. Slowly jog toward MAX limit
3. Note position just before MAX switch triggers
4. Update `X_MAX_TRAVEL_MM` etc. in main.cpp

### 5.3 Motor Direction Inversion

**Current Settings (lines 655-658):**
```c++
xStepper.setPinsInverted(true, false, false);  // Inverted
yStepper.setPinsInverted(false, false, false); // Normal
zStepper.setPinsInverted(true, false, false);  // Inverted
fStepper.setPinsInverted(true, false, false);  // Inverted
```

**To Change:**
- If motor moves opposite direction during homing
- Toggle first parameter: `true` ↔ `false`
- Recompile and test

### 5.4 Speed Tuning

**For Quieter Operation:**
- Reduce `MAX_SPEED` (e.g., from 6000 to 4000)
- Reduce `ACCEL` proportionally
- Trade-off: Slower moves vs. less motor whine

**For Faster Operation:**
- Increase `MAX_SPEED` (test up to 8000-10000)
- Increase `ACCEL` if moves are smooth
- Monitor for skipped steps or mechanical vibration

---

## 6. Programming Procedures

### 6.1 First-Time Upload

1. **Connect Teensy via USB**
2. **Build firmware:** `Ctrl+Alt+B`
3. **Upload:** `Ctrl+Alt+U`
4. **Teensy Loader opens automatically**
5. **Press button on Teensy** (if prompted)
6. **Firmware uploads**
7. **Teensy auto-reboots**

### 6.2 Subsequent Uploads

- PlatformIO remembers the Teensy
- Just press `Ctrl+Alt+U`
- Auto-uploads without manual button press

### 6.3 Troubleshooting Uploads

| Issue | Solution |
|-------|----------|
| "Device not found" | Check USB cable, try different port |
| Upload hangs | Press physical button on Teensy |
| Wrong board selected | Verify `board = teensy41` in platformio.ini |
| Compilation error | Check serial monitor for error details |

---

## 7. Debugging and Monitoring

### 7.1 Serial Monitor

**Open Monitor:** `Ctrl+Alt+S` or plug icon in toolbar

**What You'll See:**
- Boot messages
- State transitions
- Command processing
- Limit switch triggers
- Error messages
- Heartbeat telemetry (every 2 seconds)

**Example Output:**
```
Teensy 4.1 CNC/Microscope Motion Controller
Version: v1.2
Build Date: Dec 23 2025 14:32:15

Initializing...
  - 4 axes configured
  - 4x TB6600 drivers (8 microsteps)
  - Limit switches: 8 interrupts attached
  - Serial1: 115200 baud

*** DIAGNOSTIC BOOT MENU ***
Press 'D' within 3 seconds to enter diagnostic mode...

[3 seconds pass]

Entering PROTOCOL mode
RPI4 connection: Serial1 (pins 0/1, 115200 baud)
USB Serial: Debug console
Waiting for master connection...

#BOOT FW=v1.2 AXES=4 *1E

[HEARTBEAT] DISCONNECTED | X=0.00 Y=0.00 Z=0.00 F=0.00 | Homed=none
```

### 7.2 Debug Output Levels

The firmware outputs different verbosity levels:

**Normal:**
- State changes
- Command received/ACK
- Limit triggers
- Errors

**Verbose (in diagnostic mode):**
- Menu displays
- Every step of homing process
- Position updates
- Pin state changes

**To Reduce Output:**
- Remove `Serial.printf()` statements
- Comment out `diagPrintln()` in diagnostic functions

### 7.3 Using the Diagnostic Menu

**Enter at Boot:**
- Power on Teensy
- Press 'D' within 3 seconds

**OR Enter via Protocol:**
```
!DIAG_ENTER *XX
```

**Navigate:**
- Number keys: Select menu item
- 'T': Return to top menu
- 'U': Go up one level
- 'X' or 'Q': Exit diagnostic mode
- 'S': Emergency stop
- '?': Show current status

---

## 8. Code Modification Guidelines

### 8.1 Adding a New Axis

1. **Add pin definitions:**
   ```c++
   const int E_STEP_PIN = 23;
   const int E_DIR_PIN = 24;
   const int E_MIN_PIN = 25;
   const int E_MAX_PIN = 26;
   ```

2. **Create stepper object:**
   ```c++
   AccelStepper eStepper(AccelStepper::DRIVER, E_STEP_PIN, E_DIR_PIN);
   ```

3. **Create limit state:**
   ```c++
   LimitState eLimit = {false, false, 0, 0, HIGH, HIGH};
   ```

4. **Add ISRs:**
   ```c++
   void eMinISR() { /* similar to xMinISR */ }
   void eMaxISR() { /* similar to xMaxISR */ }
   ```

5. **Update setup():**
   ```c++
   pinMode(E_STEP_PIN, OUTPUT);
   pinMode(E_DIR_PIN, OUTPUT);
   pinMode(E_MIN_PIN, INPUT_PULLUP);
   pinMode(E_MAX_PIN, INPUT_PULLUP);
   attachInterrupt(digitalPinToInterrupt(E_MIN_PIN), eMinISR, FALLING);
   attachInterrupt(digitalPinToInterrupt(E_MAX_PIN), eMaxISR, FALLING);
   
   eStepper.setMaxSpeed(MAX_SPEED);
   eStepper.setAcceleration(ACCEL);
   eStepper.setMinPulseWidth(PULSE_WIDTH_US);
   
   multiStepper.addStepper(eStepper);
   ```

6. **Update homing, status, protocol commands**

### 8.2 Changing Protocol Messages

**Example:** Add velocity to status response

Find `processProtocolCommand()` and locate `!STATUS` handler:

```c++
else if (strcmp(cmd, "STATUS") == 0) {
  char buffer[256];
  
  // Add velocity calculation
  float xVel = xStepper.speed() / STEPS_PER_MM;
  float yVel = yStepper.speed() / STEPS_PER_MM;
  
  snprintf(buffer, sizeof(buffer),
           "X=%.2f Y=%.2f Z=%.2f F=%.2f STATE=%s HOMED=%s%s%s%s VEL_X=%.1f VEL_Y=%.1f",
           xStepper.currentPosition() / STEPS_PER_MM,
           yStepper.currentPosition() / STEPS_PER_MM,
           zStepper.currentPosition() / STEPS_PER_MM,
           fStepper.currentPosition() / STEPS_PER_MM,
           stateNames[currentState],
           xHomed ? "X" : "",
           yHomed ? "Y" : "",
           zHomed ? "Z" : "",
           fHomed ? "F" : "",
           xVel, yVel);
  
  sendAck(seq, buffer);
}
```

### 8.3 Adding a New Protocol Command

1. **Add to protocol parser:**
   ```c++
   else if (strcmp(cmd, "MYCOMMAND") == 0) {
     // Validate state
     if (currentState != STATE_IDLE) {
       sendNack(seq, "ERR_INVALID_STATE", "Must be in IDLE");
       return;
     }
     
     // Parse arguments
     float value;
     if (sscanf(message, "!MYCOMMAND %f", &value) != 1) {
       sendNack(seq, "ERR_INVALID_ARGS", "Expected: !MYCOMMAND <value>");
       return;
     }
     
     // Execute command
     // ...
     
     // Send response
     sendAck(seq, "COMMAND_EXECUTED");
   }
   ```

2. **Update PROTOCOL.md documentation**

3. **Add test case to TEST_PROGRAM_GUIDE.md**

---

## 9. Library Dependencies

### 9.1 AccelStepper Library

**Version:** 1.64  
**Purpose:** Stepper motor acceleration/deceleration  
**Documentation:** http://www.airspayce.com/mikem/arduino/AccelStepper/

**Key Classes Used:**
- `AccelStepper`: Single stepper control
- `MultiStepper`: Coordinated multi-axis moves

**Key Methods:**
```c++
setMaxSpeed(speed);          // Set maximum speed (steps/sec)
setAcceleration(accel);      // Set acceleration (steps/sec²)
setMinPulseWidth(width);     // Set pulse width (µs)
moveTo(position);            // Set target position (absolute)
move(distance);              // Set target position (relative)
run();                       // Must be called frequently
runSpeed();                  // Constant speed (no accel)
distanceToGo();              // Steps remaining
currentPosition();           // Current position (steps)
setCurrentPosition(pos);     // Reset position counter
```

**Why Not TeensyStep?**
- TeensyStep only works with Teensy 3.x (Kinetis processors)
- Teensy 4.x uses i.MX RT processor (different architecture)
- AccelStepper is cross-platform and proven
- Software timing adequate for CNC microscopy (not high-speed machining)

---

## 10. Memory and Performance

### 10.1 Resource Usage

**Flash Memory:**
- Firmware size: ~150 KB
- Available: 8 MB (plenty of headroom)

**RAM:**
- Global variables: ~10 KB
- Stack usage: ~2 KB
- Available: 1 MB (plenty of headroom)

**CPU Usage:**
- Typical: 5-10% (mostly idle)
- During motion: 20-30%
- Interrupt overhead: < 1%

### 10.2 Performance Benchmarks

**Command Processing:**
- ACK latency: < 5ms
- Status query: < 10ms
- Parse overhead: < 1ms per command

**Motion Control:**
- Step generation accuracy: < 1µs jitter
- AccelStepper loop time: ~50µs
- Main loop rate: > 1000 Hz

**Interrupt Response:**
- ISR execution time: < 10µs
- ISR to main loop: < 1ms (via flag)

---

## 11. Version Control

### 11.1 Current Version

**Firmware:** v1.2  
**Protocol:** v1.0  
**Date:** December 23, 2025

### 11.2 Version History

| Version | Date | Changes |
|---------|------|---------|
| **v1.2** | Dec 23, 2025 | Limit switch robustness redesign, complete documentation |
| **v1.1** | Dec 22, 2025 | Protocol implementation, diagnostic remote access |
| **v1.0** | Dec 20, 2025 | Initial working version with homing and protocol |
| **v0.5** | Dec 18, 2025 | Diagnostic menu system implemented |
| **v0.1** | Dec 15, 2025 | Basic motion control and limit switches |

### 11.3 Incrementing Version

Located at top of main.cpp (line 58):
```c++
const char* FIRMWARE_VERSION = "v1.2";
```

When making significant changes:
1. Update `FIRMWARE_VERSION`
2. Update `BUILD_DATE` (auto-generated from `__DATE__` and `__TIME__`)
3. Update documentation version numbers
4. Document changes in project_context.md

---

## 12. Testing After Code Changes

### 12.1 Checklist

After modifying firmware:

1. **Compile:** Verify no errors
2. **Upload:** Flash to Teensy
3. **Boot Test:** Check serial output for clean boot
4. **Diagnostic Mode:** Enter and test basic functions
5. **Protocol Test:** Send !CONNECT, !STATUS
6. **Motion Test:** Test homing, moves, jogs
7. **Limit Test:** Manually trigger each limit switch
8. **Watchdog Test:** Stop sending commands, verify timeout
9. **Error Test:** Send invalid commands, verify NACK

### 12.2 Regression Testing

**Critical Tests:**
- All 8 limit switches detect correctly
- Homing completes successfully (all 4 axes)
- Coordinated moves complete without error
- Emergency stop works immediately
- Watchdog triggers after 5 seconds
- State transitions work correctly

---

## 14. Python GUI Software Modules

The GUI system consists of 5 core Python modules and 2 configuration files.

### 14.1 Module Overview

| Module | Lines | Purpose | Key Classes/Functions |
|--------|-------|---------|----------------------|
| **scope_gui.py** | 789 | Main PyQt5 application | MicroscopeGUI, VideoWidget, SpecimenCard, JogButton |
| **motion_controller.py** | 360 | High-level motion control | MotionController with auto-cycle |
| **video_thread.py** | 80 | OpenCV video capture | VideoThread (QThread) |
| **teensy_protocol.py** | 320 | Serial protocol implementation | TeensyController |
| **specimen_grid.py** | 160 | Grid calculations | SpecimenGrid |
| **cli_menu.py** | 920 | CLI diagnostic interface | (optional, testing only) |
| **mindatnh_tray1.json** | 312 | Specimen configuration | 28 NH minerals with positions |
| **GUI_README.md** | - | Quick start guide | Documentation |

### 14.2 scope_gui.py - Main GUI Application

**Purpose:** PyQt5 kiosk interface with touch controls, video display, and specimen selection

**Key Components:**

```python
class MicroscopeGUI(QMainWindow):
    """Main application window (1920×1080 fullscreen)"""
    def __init__(self, json_file):
        # Initialize specimen grid
        # Create VideoWidget for camera display
        # Create specimen cards (7×4 grid)
        # Create jog buttons
        # Start auto-cycle
    
    def on_specimen_clicked(self, row, col):
        # Handle specimen selection
        # Move stage to specimen position
    
    def keyPressEvent(self, event):
        # ESC key exits application

class VideoWidget(QWidget):
    """Custom widget for video display with overlays (1670×1080)"""
    def paintEvent(self, event):
        # Draw OpenCV frame scaled to fill widget
        # Draw translucent title banner (alpha=200)
        # Draw specimen info overlay
    
    def set_title(self, text):
        # Thread-safe title update using QTimer.singleShot
    
    def set_status(self, text):
        # Thread-safe status update

class SpecimenCard(QPushButton):
    """Touch-friendly specimen selection button (230×80)"""
    def set_current(self, is_current):
        # Highlight selected card (update, not repaint!)

class JogButton(QPushButton):
    """Directional control button (60×60)"""
    # Handles touch events for manual stage movement
```

**Dependencies:**
```python
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter, QColor, QFont
```

**Critical Design Patterns:**
- **Thread Safety:** All GUI updates from other threads use `QTimer.singleShot(0, self.update)`
- **Never call repaint():** Always use `update()` to avoid segfaults
- **Deferred updates:** Card highlighting uses `QTimer.singleShot(10, update_cards)` to avoid paint conflicts

### 14.3 motion_controller.py - Motion Control Layer

**Purpose:** High-level motion control with auto-cycle and state management

**Key Components:**

```python
class MotionController:
    """High-level motion control with auto-cycle"""
    def __init__(self, serial_port, grid, callbacks):
        self.teensy = TeensyController(serial_port)
        self.grid = grid
        self._auto_cycle_thread = None
        self._manual_override_time = None
    
    def start_auto_cycle(self):
        """Start autonomous specimen cycling (10s interval)"""
    
    def _auto_cycle_loop(self):
        """Cycle through specimens, skip invalid ones, 30s timeout"""
        while self._auto_cycling:
            if self._is_manual_override():
                time.sleep(1)
                continue
            
            # Move to next specimen
            self.move_to_next_specimen()
            time.sleep(10)  # 10-second display time
    
    def move_to_specimen(self, specimen):
        """Move stage to specimen with focus/zoom"""
        x, y = self.grid.calculate_position(specimen)
        z = specimen.get("zoom_mm", 10.0)
        f = specimen.get("focus_mm", 5.0)
        
        self.teensy.move_to(x, y, z, f)
        self._manual_override_time = time.time()  # Reset timer
    
    def _is_manual_override(self):
        """Check if in manual mode (30s since last user input)"""
        if self._manual_override_time is None:
            return False
        return (time.time() - self._manual_override_time) < 30.0
```

**State Management:**
- AUTO mode: Cycles specimens every 10 seconds
- MANUAL mode: Triggered by user touch, lasts 30 seconds
- Automatically returns to AUTO after 30s of no input

### 14.4 video_thread.py - Video Capture

**Purpose:** Background thread for OpenCV camera capture

**Key Components:**

```python
class VideoThread(QThread):
    """OpenCV video capture in separate thread"""
    frame_ready = pyqtSignal(object)  # QImage signal
    
    def __init__(self, device_index=0):
        super().__init__()
        self.device_index = device_index
        self.running = False
        self.frame = None
        self.mutex = QMutex()
    
    def run(self):
        """Capture loop (30 FPS)"""
        cap = cv2.VideoCapture(self.device_index, cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        while self.running:
            ret, frame = cap.read()
            if ret:
                # Convert BGR → RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert to QImage
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                q_img = QImage(rgb_frame.data, w, h, 
                              bytes_per_line, QImage.Format_RGB888)
                
                # Thread-safe frame storage
                self.mutex.lock()
                self.frame = q_img.copy()
                self.mutex.unlock()
                
                # Emit signal to GUI thread
                self.frame_ready.emit(self.frame)
```

**Performance:**
- 30 FPS capture rate
- CAP_V4L2 backend for Linux
- QMutex for thread-safe frame access
- Signal/slot for GUI updates

### 14.5 teensy_protocol.py - Serial Communication

**Purpose:** Low-level serial protocol implementation with checksums

**Key Components:**

```python
class TeensyController:
    """Serial protocol implementation for Teensy communication"""
    def __init__(self, port='/dev/ttyACM0', baudrate=115200):
        self.serial = serial.Serial(port, baudrate, timeout=1.0)
        self.sequence = 0
        self.watchdog_thread = None
    
    def send_command(self, command, params=""):
        """Send command with XOR checksum"""
        self.sequence = (self.sequence + 1) % 100
        message = f"!{command} {self.sequence}"
        if params:
            message += f" {params}"
        
        # Calculate checksum
        checksum = 0
        for char in message:
            checksum ^= ord(char)
        
        full_message = f"{message} *{checksum:02X}\n"
        self.serial.write(full_message.encode())
        
        # Wait for @ACK or @NACK
        response = self.read_response()
        return response
    
    def home(self):
        """Execute homing sequence (30 seconds)"""
        return self.send_command("HOME")
    
    def move_to(self, x, y, z, f):
        """Coordinated 4-axis move"""
        params = f"{x:.2f} {y:.2f} {z:.2f} {f:.2f}"
        return self.send_command("MOVE", params)
    
    def watchdog_loop(self):
        """Send !PING every 3 seconds"""
        while self.running:
            self.send_command("PING")
            time.sleep(3.0)
```

**Protocol Features:**
- XOR checksum validation
- Sequence number tracking
- Watchdog timer (3-second ping)
- Command acknowledgment (@ACK/@NACK)

### 14.6 specimen_grid.py - Grid Calculations

**Purpose:** Specimen position calculations and JSON configuration parsing

**Key Components:**

```python
class SpecimenGrid:
    """7×4 grid of mineral specimens"""
    def __init__(self, json_file):
        self.specimens = []
        self.load_from_json(json_file)
    
    def load_from_json(self, json_file):
        """Parse mindatnh_tray1.json"""
        with open(json_file) as f:
            data = json.load(f)
            self.specimens = data["specimens"]
    
    def get_by_row_col(self, row, col):
        """Lookup specimen by grid position"""
        for specimen in self.specimens:
            if specimen["row"] == row and specimen["col"] == col:
                return specimen
        return None
    
    def calculate_position(self, specimen):
        """Calculate X,Y position from row/col"""
        row = specimen["row"]
        col = specimen["col"]
        
        # Grid spacing: 40mm in Y-direction
        base_x = col * 40.0  # Adjust based on actual spacing
        base_y = row * 40.0
        
        # Add specimen-specific offsets
        x = base_x + specimen.get("x_offset_mm", 0.0)
        y = base_y + specimen.get("y_offset_mm", 0.0)
        
        return (x, y)
```

**Grid Layout:**
```
7 columns × 4 rows = 28 specimens
Spacing: 40mm in Y-direction
Each specimen has calibrated offsets
```

### 14.7 Python Dependencies

**Required Packages:**
```bash
pip3 install pyserial    # Serial communication
pip3 install PyQt5       # GUI framework
pip3 install opencv-python  # Video capture
```

**System Requirements:**
- Python 3.7 or higher
- Raspberry Pi OS (64-bit) with Desktop
- UART enabled on GPIO 14/15
- V4L2 camera driver support

### 14.8 JSON Configuration Format

**mindatnh_tray1.json Structure:**
```json
{
  "specimens": [
    {
      "row": 0,
      "col": 0,
      "mineral_name": "Beryl",
      "location": "Palermo #1 Mine, North Groton, NH",
      "collector": "Tom Mortimer",
      "x_offset_mm": 0.5,
      "y_offset_mm": -0.2,
      "focus_mm": 10.0,
      "zoom_mm": 5.0
    },
    ...
  ]
}
```

**Fields:**
- `row`, `col`: Grid position (0-indexed)
- `mineral_name`: Display name
- `location`: Specimen locality
- `collector`: Collector name
- `x_offset_mm`, `y_offset_mm`: Fine positioning adjustments
- `focus_mm`: Z-axis position
- `zoom_mm`: Focus axis position

---

## 13. Common Programming Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "pinMode" not declared | Wrong framework | Check `framework = arduino` in platformio.ini |
| "AccelStepper" not found | Missing library | Check `lib_deps` in platformio.ini |
| Upload fails | Wrong board | Check `board = teensy41` |
| Serial output garbled | Wrong baud rate | Use 115200 on both sides |
| Motors don't respond | Enable logic wrong | Verify `digitalWrite(ENA_ALL_PIN, LOW)` |
| Limit switches inverted | Wrong interrupt edge | Use `FALLING` for NO switches |

---

**Next Section:** [05 - Protocol Specification](05_PROTOCOL_SPECIFICATION.md)
