# System Architecture

**Document:** 02 - System Architecture  
**Version:** 1.2  
**Date:** December 23, 2025

---

## 1. System Block Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         RPi4 Master                              │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │   Python     │  │   Camera     │  │   GUI / User       │   │
│  │   Client     │  │   Interface  │  │   Interface        │   │
│  └──────┬───────┘  └──────────────┘  └────────────────────┘   │
│         │                                                        │
│         │ UART (Serial1, 115200 baud, 8N1)                     │
└─────────┼────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Teensy 4.1 Slave                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Main Firmware (main.cpp)                     │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │  │
│  │  │  Protocol   │  │  State       │  │  Motion        │  │  │
│  │  │  Parser     │  │  Machine     │  │  Control       │  │  │
│  │  └─────────────┘  └──────────────┘  └────────────────┘  │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │  │
│  │  │  Diagnostic │  │  Limit       │  │  Homing        │  │  │
│  │  │  Menu       │  │  Detection   │  │  Logic         │  │  │
│  │  └─────────────┘  └──────────────┘  └────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  GPIO Pins:                                                     │
│  ├─ Serial1 (pins 0/1) → RPi4 UART                            │
│  ├─ Serial (USB) → Debug Console                               │
│  ├─ Digital Outputs → TB6600 Drivers (STEP/DIR/EN)            │
│  └─ Digital Inputs → Limit Switches (8 interrupts)             │
└──────────────┬───────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TB6600 Motor Drivers (×4)                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │  X Driver  │  │  Y Driver  │  │  Z Driver  │  │ F Driver │ │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └────┬─────┘ │
└────────┼───────────────┼───────────────┼──────────────┼─────────┘
         │               │               │              │
         ▼               ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    NEMA17 Stepper Motors (×4)                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │  X Motor   │  │  Y Motor   │  │  Z Motor   │  │ F Motor  │ │
│  │  (Gantry)  │  │  (Table)   │  │  (Height)  │  │ (Focus)  │ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Communication Architecture

### 2.1 Master/Slave Model

**Master (RPi4):**
- Initiates all commands
- Maintains watchdog timer (sends !PING every 3 seconds)
- Processes responses and events
- Makes high-level decisions
- Handles user interaction and imaging

**Slave (Teensy):**
- Executes motion commands
- Enforces safety constraints
- Reports status and events
- Maintains real-time control
- No autonomous decision-making

### 2.2 Dual Serial Configuration

The Teensy uses TWO serial ports simultaneously:

| Port | Purpose | Connection | Baud | Usage |
|------|---------|------------|------|-------|
| **Serial1** | Protocol | Pins 0/1 (UART) → RPi4 GPIO 14/15 | 115200 | Commands, responses, events |
| **Serial** | Diagnostics | USB → PC | 115200 | Debug output, local testing |

**Key Benefits:**
- RPi4 communication independent of USB connection
- Debug console always available during development
- `#DIAG` messages mirrored to both ports for remote diagnostics

### 2.3 Message Flow

```
Normal Operation:
RPi4 → !COMMAND → Teensy
Teensy → @ACK → RPi4
[Teensy executes]
Teensy → @COMPLETE → RPi4

Error Condition:
RPi4 → !COMMAND → Teensy
Teensy → @NACK ERR_CODE message → RPi4

Asynchronous Event:
Teensy → #EVENT data → RPi4
```

---

## 3. State Machine

### 3.1 System States

```c++
enum SystemState {
  STATE_BOOT,          // Power-on initialization
  STATE_DISCONNECTED,  // No master connection
  STATE_CONNECTED,     // Master connected, not homed
  STATE_IDLE,          // Ready for commands (homed)
  STATE_HOMING_Z,      // Homing Z axis
  STATE_HOMING_Y,      // Homing Y axis
  STATE_HOMING_X,      // Homing X axis
  STATE_HOMING_F,      // Homing Focus axis
  STATE_HOMING,        // Generic homing (for protocol)
  STATE_MOVING,        // Executing coordinated move
  STATE_JOGGING,       // Executing single-axis jog
  STATE_ERROR,         // Fault condition
  STATE_DIAGNOSTIC,    // Human-interactive mode
  STATE_COMM_LOST      // Watchdog timeout
};
```

### 3.2 State Transition Diagram

```
BOOT
 │
 ├─────────────────────────────────────────────────┐
 │                                                  │
 ▼                                                  │
DISCONNECTED ──!CONNECT──> CONNECTED               │
 ▲                             │                    │
 │                             │ !HOME              │
 │                             ▼                    │
 │                         HOMING_Z                 │
 │                             │                    │
 │                             ▼                    │
 │                         HOMING_Y                 │
 │                             │                    │
 │                             ▼                    │
 │                         HOMING_X                 │
 │                             │                    │
 │                             ▼                    │
 │                         HOMING_F                 │
 │                             │                    │
 │                             ▼                    │
 │                           IDLE ◄─────────┐       │
 │                             │            │       │
 │                 ┌───────────┼──────────┐ │       │
 │                 │           │          │ │       │
 │           !MOVE │      !JOG │          │ │       │
 │                 ▼           ▼          │ │       │
 │              MOVING      JOGGING       │ │       │
 │                 │           │          │ │       │
 │                 └───────────┴──────────┘ │       │
 │                     (complete)           │       │
 │                                          │       │
 ├─ !DIAG_ENTER ──> DIAGNOSTIC ─ !DIAG_EXIT┘       │
 │                      │                            │
 │                      │ (watchdog disabled)        │
 │                      │                            │
 │                                                   │
 └──────────────────── ERROR ◄─────────────────────┘
          ▲               │ !CLEAR_ERROR
          │               │
          │               ▼
      (limit hit,    DISCONNECTED
       timeout,
       etc.)
      
 COMM_LOST ──(watchdog timeout from any state)──> #BOOT every 10s
```

### 3.3 State Behaviors

| State | Motors | Watchdog | Commands Accepted | Description |
|-------|--------|----------|-------------------|-------------|
| **BOOT** | Disabled | Off | None | Initialization, 3-second boot menu |
| **DISCONNECTED** | Disabled | Off | !CONNECT, !DIAG_ENTER | Waiting for master |
| **CONNECTED** | Disabled | On | !HOME, !STATUS, etc. | Connected but not homed |
| **IDLE** | Enabled | On | !MOVE, !JOG, !HOME, !STATUS | Ready for motion |
| **HOMING_Z/Y/X/F** | Enabled | On | !STOP | Executing homing sequence |
| **MOVING** | Enabled | On | !STOP, !STATUS | Executing coordinated move |
| **JOGGING** | Enabled | On | !STOP, !STATUS | Executing jog move |
| **ERROR** | Disabled | Off | !CLEAR_ERROR, !STATUS | Fault condition |
| **DIAGNOSTIC** | Enabled | Off | Menu commands, !DIAG_EXIT | Human testing mode |
| **COMM_LOST** | Disabled | Off | None (auto-recovery) | Watchdog timeout |

---

## 4. Firmware Architecture

### 4.1 Module Organization

```
main.cpp (3114 lines)
├─ CONFIGURATION (lines 54-129)
│  ├─ Pin definitions
│  ├─ Speed settings
│  ├─ Calibration constants
│  └─ Soft limits
│
├─ STATE & OBJECTS (lines 130-275)
│  ├─ State machine enums
│  ├─ AccelStepper objects
│  ├─ LimitState structures
│  └─ Protocol variables
│
├─ INTERRUPT SERVICE ROUTINES (lines 287-440)
│  ├─ xMinISR(), xMaxISR()
│  ├─ yMinISR(), yMaxISR()
│  ├─ zMinISR(), zMaxISR()
│  └─ fMinISR(), fMaxISR()
│
├─ HELPER FUNCTIONS (lines 441-1450)
│  ├─ Communication (sendAck, sendNack, etc.)
│  ├─ Motor control (enableMotors, emergencyStop)
│  ├─ Limit detection (checkLimitTriggered)
│  └─ Homing logic (homeAxis, handleHomingState)
│
├─ SETUP & MAIN LOOP (lines 615-1024)
│  ├─ setup(): Pin init, motor config, interrupts
│  └─ loop(): State processing, watchdog, serial
│
├─ DIAGNOSTIC MENU SYSTEM (lines 1845-2630)
│  ├─ Menu printing functions
│  ├─ Command processing
│  └─ Interactive motion testing
│
└─ PROTOCOL COMMAND PROCESSING (lines 2370-3114)
   ├─ Command parser
   ├─ State validation
   ├─ Motion execution
   └─ Response generation
```

### 4.2 Key Data Structures

**LimitState Structure:**
```c++
struct LimitState {
  volatile bool triggered;              // ISR sets, main loop clears
  volatile bool isMin;                  // true=MIN, false=MAX
  volatile unsigned long lastTriggerTime;
  volatile unsigned long debounceUntil; // Timestamp-based debouncing
  volatile int lastMinPinState;         // Pin state hysteresis (MIN)
  volatile int lastMaxPinState;         // Pin state hysteresis (MAX)
};
```

**Stepper Objects:**
```c++
AccelStepper xStepper(DRIVER, X_STEP_PIN, X_DIR_PIN);
AccelStepper yStepper(DRIVER, Y_STEP_PIN, Y_DIR_PIN);
AccelStepper zStepper(DRIVER, Z_STEP_PIN, Z_DIR_PIN);
AccelStepper fStepper(DRIVER, F_STEP_PIN, F_DIR_PIN);
MultiStepper multiStepper;  // For coordinated moves
```

---

## 5. Homing System Architecture

### 5.1 Sequential Homing

**Order:** Z → Y → X → Focus

**Rationale:**
- Z-axis homing first prevents collisions (lifts tool away from work)
- Y before X avoids gantry interference
- Focus last (least critical for positioning)

**Process Flow:**
```
!HOME command received
→ STATE_IDLE → STATE_HOMING_Z
   ↓
   homeAxis(Z) [4 phases]
   ↓
   STATE_HOMING_Z → STATE_HOMING_Y
   ↓
   homeAxis(Y) [4 phases]
   ↓
   STATE_HOMING_Y → STATE_HOMING_X
   ↓
   homeAxis(X) [4 phases]
   ↓
   STATE_HOMING_X → STATE_HOMING_F
   ↓
   homeAxis(F) [4 phases]
   ↓
   STATE_HOMING_F → STATE_IDLE
   ↓
   @COMPLETE sent to master
```

### 5.2 Parallel Homing (!HOME_FAST)

All axes home simultaneously:
```
!HOME_FAST command received
→ STATE_IDLE → STATE_HOMING
   ↓
   Start all axes: xHomingPhase = HOMING_SEEK
                   yHomingPhase = HOMING_SEEK
                   zHomingPhase = HOMING_SEEK
                   fHomingPhase = HOMING_SEEK
   ↓
   Loop: Update each axis independently
         Check if all complete
   ↓
   All axes HOMING_COMPLETE
   ↓
   STATE_HOMING → STATE_IDLE (or STATE_DIAGNOSTIC)
   ↓
   @COMPLETE sent
```

### 5.3 Four-Phase Homing Process

Each axis goes through:

1. **HOMING_SEEK** - Fast approach (3000 steps/sec)
   - Move toward MIN limit
   - If MAX limit hit → ERROR (wrong direction)
   - Timeout: 120 seconds

2. **HOMING_BACKOFF** - Release switch (normal speed)
   - Move 5mm away from MIN limit
   - Ensures clean switch release

3. **HOMING_CREEP** - Precision approach (400 steps/sec)
   - Slow approach to MIN limit
   - Establishes precise home position

4. **HOMING_COMPLETE** - Final backoff
   - Move 5mm away from physical MIN
   - Set position to 0.00mm (5mm from limit)
   - Zero position is safe for operations

---

## 6. Limit Switch Architecture

### 6.1 Robust Detection System (v1.2)

**Problem Solved:** Original detach/reattach interrupt approach had 25% failure rate

**Solution:** Three-layer hybrid architecture

#### Layer 1: Interrupt Detection (Primary)
```c++
void xMinISR() {
  unsigned long now = millis();
  int pinState = digitalRead(X_MIN_PIN);
  
  // Timestamp-based debouncing (no detach)
  if (now >= xLimit.debounceUntil &&
      pinState == LOW &&                    // Switch pressed
      xLimit.lastMinPinState == HIGH) {     // Was released (hysteresis)
    
    xLimit.triggered = true;
    xLimit.isMin = true;
    xLimit.lastTriggerTime = now;
    xLimit.debounceUntil = now + DEBOUNCE_MS;  // 50ms
    xLimit.lastMinPinState = LOW;              // Track state
  }
}
```

#### Layer 2: Polling Fallback
```c++
bool checkLimitTriggered(LimitState& limit, int minPin, int maxPin) {
  // 1. Check ISR flag (primary detection)
  if (limit.triggered) {
    return true;
  }
  
  // 2. Poll pins directly (fallback if ISR missed)
  if (digitalRead(minPin) == LOW) {
    // Triple-read verification (200µs stable)
    delayMicroseconds(200);
    if (digitalRead(minPin) == LOW) {
      delayMicroseconds(200);
      if (digitalRead(minPin) == LOW) {
        limit.triggered = true;
        limit.isMin = true;
        return true;
      }
    }
  }
  
  // [similar for maxPin]
}
```

#### Layer 3: State Tracking
```c++
// In main loop and all tight loops:
if (digitalRead(X_MIN_PIN) == HIGH) xLimit.lastMinPinState = HIGH;
if (digitalRead(X_MAX_PIN) == HIGH) xLimit.lastMaxPinState = HIGH;
// [repeat for all 8 pins]
```

**Result:** Zero missed detections, zero false triggers

---

## 7. Protocol Integration

### 7.1 Command Processing Flow

```
Serial1 byte arrives
   ↓
Accumulate in buffer until '\n'
   ↓
Extract checksum, validate
   ↓
Parse command and sequence number
   ↓
Check for duplicate sequence
   ↓
Validate state (can this command run now?)
   ↓
Execute command
   ↓
Send @ACK or @NACK
   ↓
[Command continues asynchronously]
   ↓
Send @COMPLETE when done
```

### 7.2 Watchdog Timer

```c++
// In loop():
if (watchdogEnabled && (millis() - lastMasterMessage > WATCHDOG_TIMEOUT_MS)) {
  emergencyStop();
  disableMotors();
  currentState = STATE_COMM_LOST;
  sendEvent("COMM_LOST", "Watchdog timeout");
  watchdogEnabled = false;
  
  // Auto-recovery: Send #BOOT every 10 seconds
}
```

---

## 8. Diagnostic Mode Architecture

### 8.1 Menu System

Hierarchical numbered menus:
```
MAIN MENU
├─ 1: HOME (all axes)
├─ 2: MOVE (submenu)
├─ 3: JOG (submenu)
├─ 4: TEST MOTORS (submenu)
├─ 5: SAFE LIMIT TEST (submenu)
├─ 6: SPEED SETTINGS
└─ 7: CALIBRATION
```

### 8.2 Remote Diagnostic Access

Via protocol commands:
- `!DIAG_ENTER` - Switch to diagnostic mode
- `!DIAG_CMD <char>` - Send menu command
- `!DIAG_MENU` - Get current menu display
- `!DIAG_EXIT` - Return to protocol mode

All diagnostic output prefixed with `#DIAG` and sent to RPi4

---

## 9. Performance Considerations

### 9.1 Real-Time Constraints
- AccelStepper.run() must be called frequently (< 1ms gaps)
- No blocking delays in main loop
- Interrupt handlers kept minimal (< 10µs)
- Serial buffer checked every loop iteration

### 9.2 Non-Blocking Architecture
- No `delay()` calls (except in ISRs for debounce)
- All operations use state machines
- Homing, moving, jogging all non-blocking
- Watchdog uses `millis()` timestamps

---

## 10. GUI Software Architecture (PyQt5)

### 10.1 GUI System Block Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    MicroscopeGUI (Main Window)                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  VideoWidget (1670×1080)                    │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  OpenCV Frame (640×480) scaled to fill             │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  Translucent Overlays (alpha=200):                   │  │ │
│  │  │  - Title Banner (70px top)                           │  │ │
│  │  │  - Specimen Info (bottom)                            │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         Left Panel (230px wide)                             │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  Specimen Grid (7×4 = 28 cards)                      │  │ │
│  │  │  - Touch to select specimen                          │  │ │
│  │  │  - Current specimen highlighted                      │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  Jog Controls (9 buttons)                            │  │ │
│  │  │  - XY movement (8-way)                               │  │ │
│  │  │  - Z/Focus (2 buttons)                               │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Threading Architecture                       │
├─────────────────────────────────────────────────────────────────┤
│  Main Thread (PyQt5 GUI)                                         │
│  ├─ Event loop                                                   │
│  ├─ Painting (VideoWidget.paintEvent)                           │
│  ├─ Touch event handling                                         │
│  └─ UI updates (QTimer.singleShot for thread safety)            │
├─────────────────────────────────────────────────────────────────┤
│  VideoThread (QThread)                                           │
│  ├─ OpenCV camera capture                                        │
│  ├─ BGR → RGB conversion                                         │
│  └─ emit frame_ready signal → Main thread                       │
├─────────────────────────────────────────────────────────────────┤
│  MotionController (separate thread)                              │
│  ├─ Serial communication (teensy_protocol.py)                   │
│  ├─ Homing sequence                                              │
│  ├─ Movement commands                                            │
│  ├─ Watchdog (!PING every 3s)                                   │
│  └─ Callbacks to GUI (connected_callback, etc.)                 │
├─────────────────────────────────────────────────────────────────┤
│  Auto-Cycle Thread (MotionController)                            │
│  ├─ Specimen rotation (10s timer)                               │
│  ├─ Skip invalid specimens                                       │
│  └─ Pause on manual intervention (30s timeout)                  │
└─────────────────────────────────────────────────────────────────┘
```

### 10.2 Component Hierarchy

```
scope_gui.py (789 lines)
├─ MicroscopeGUI (QMainWindow)
│  ├─ VideoWidget (custom QWidget for video + overlays)
│  │  ├─ paintEvent() - Render video and overlays
│  │  ├─ set_title() - Update title text
│  │  ├─ set_status() - Update status text
│  │  └─ set_position() - Update position text
│  │
│  ├─ SpecimenCard (QPushButton, 230×80)
│  │  ├─ set_current() - Highlight selected card
│  │  └─ paintEvent() - Custom border rendering
│  │
│  ├─ JogButton (QPushButton, 60×60)
│  │  └─ Touch-friendly directional controls
│  │
│  └─ Layout
│     ├─ Central Widget: VideoWidget (1670×1080)
│     └─ Left Panel: Specimen grid + jog controls (230×1080)
│
video_thread.py (80 lines)
└─ VideoThread (QThread)
   ├─ __init__(device_index=0)
   ├─ run() - Capture loop
   └─ frame_ready signal
   
motion_controller.py (360 lines)
└─ MotionController
   ├─ teensy_protocol.TeensyController (serial communication)
   ├─ _auto_cycle_loop() - Autonomous specimen rotation
   ├─ move_to_specimen() - High-level specimen positioning
   └─ Callbacks: connected_callback, position_callback, etc.

specimen_grid.py (160 lines)
├─ SpecimenGrid
│  ├─ load_from_json() - Parse mindatnh_tray1.json
│  ├─ get_by_row_col() - Lookup specimen
│  └─ calculate_position() - Grid math (40mm Y-spacing)
│
teensy_protocol.py (320 lines)
└─ TeensyController
   ├─ connect() - Open serial port
   ├─ send_command() - Protocol with checksum
   ├─ home() - Homing sequence
   ├─ move_to() - Coordinated 4-axis move
   └─ watchdog_loop() - !PING every 3 seconds
```

### 10.3 Data Flow: Specimen Selection

```
User touches SpecimenCard
   ↓
SpecimenCard.clicked signal
   ↓
MicroscopeGUI.on_specimen_clicked(row, col)
   ↓
MotionController.move_to_specimen(specimen)
   ↓
Calculate position: SpecimenGrid.calculate_position()
   ↓
Send commands via TeensyController:
   1. !MOVE X Y Z F
   2. !WAIT (until complete)
   3. !WAIT (until complete)
   ↓
Teensy executes move
   ↓
@COMPLETE received
   ↓
MotionController.move_complete_callback()
   ↓
GUI updates: VideoWidget.set_title(mineral_name)
   ↓
Reset manual override timer (30s)
```

### 10.4 Thread Safety

**Critical Pattern:** Never call `repaint()` from non-GUI threads

**Correct Approach:**
```python
# In VideoWidget methods called from other threads:
def set_title(self, text):
    self.current_title = text
    QTimer.singleShot(0, self.update)  # Schedule update on main thread

# In SpecimenCard:
def set_current(self, is_current):
    self.is_current = is_current
    self.update()  # NOT repaint()
```

**Wrong Approach (causes segfaults):**
```python
def set_title(self, text):
    self.current_title = text
    self.repaint()  # WRONG: Synchronous paint from wrong thread
```

### 10.5 Auto-Cycle State Machine

```
AUTO Mode (default)
   ↓
   Timer: 10 seconds
   ↓
   Move to next specimen
   ↓
   [User touches specimen card]
   ↓
MANUAL Mode
   ↓
   Timer: 30 seconds (no user input)
   ↓
   Return to AUTO Mode
   ↓
   Resume cycling
```

### 10.6 Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **Video FPS** | 30 | OpenCV capture rate |
| **GUI FPS** | 30 | paintEvent refresh rate |
| **Memory** | ~120 MB | Typical RAM usage |
| **CPU** | 20% | RPi4 single core |
| **Startup** | 90s | From power-on to first specimen |
| **Homing** | 30s | Sequential Z→Y→X→F |
| **Move Time** | 3-8s | Depends on distance |
| **Cycle Time** | 10s | Auto-cycle interval |

---

**Next Section:** [03 - Hardware Specification](03_HARDWARE_SPECIFICATION.md)
