# Diagnostic Procedures

**Document:** 06 - Diagnostic Procedures  
**Version:** 1.2  
**Date:** December 23, 2025

---

## 1. Overview

The firmware includes a comprehensive interactive diagnostic menu system accessible:
- **At boot:** Press 'D' within 3 seconds
- **Via protocol:** Send `!DIAG_ENTER` command from RPi4
- **Via USB:** Connect serial monitor at 115200 baud

All diagnostic output is mirrored to both Serial (USB) and Serial1 (RPi4) as `#DIAG` messages.

---

## 2. Entering Diagnostic Mode

### 2.1 At Power-On

```
*** DIAGNOSTIC BOOT MENU ***
Press 'D' within 3 seconds to enter diagnostic mode...

[Press 'D']

========================================
DIAGNOSTIC MAIN MENU
========================================
1 - HOME All Axes (Sequential)
2 - MOVE Absolute Position
3 - JOG Incremental
4 - TEST Motors (Quick Test)
5 - SAFE LIMIT TEST (Step-by-step)
6 - Speed Settings
7 - Calibration Info
T - Top Menu
X - Exit Diagnostic Mode
S - Emergency STOP
? - Show Current Status
H - Help

Current Position: X=0.00 Y=0.00 Z=0.00 F=0.00
Homed: none
State: DIAGNOSTIC

Enter command:
```

### 2.2 Via Protocol

```
!DIAG_ENTER *2A
@ACK seq ENTERING_DIAGNOSTIC
#DIAG ========================================
#DIAG DIAGNOSTIC MAIN MENU
#DIAG ...
```

---

## 3. Main Menu Functions

### 3.1 HOME All Axes (Option 1)

**Purpose:** Execute full homing sequence

**Procedure:**
1. Select `1` from main menu
2. System homes Z → Y → X → Focus
3. Watch for limit switch triggers
4. Verify final positions all 0.00mm

**Expected Output:**
```
Starting sequential homing...
Homing Z axis...
  Phase: SEEK (3000 steps/sec)
  Z_MIN triggered
  Phase: BACKOFF (5mm)
  Phase: CREEP (400 steps/sec)
  Z_MIN triggered (precise)
  Phase: FINAL_BACKOFF (5mm)
  Z axis homed at 0.00mm

Homing Y axis...
[... similar ...]

HOMING COMPLETE
All axes homed successfully
```

### 3.2 MOVE Menu (Option 2)

**Purpose:** Coordinated multi-axis absolute positioning

**Submenu:**
```
MOVE MENU
1 X Y Z F - Set target position (e.g., "1 100 50 10 5")
2 - Execute move to target
3 - Reset target to current position
T - Top Menu
U - Up one level
```

**Usage:**
```
Enter command: 1 100 50 10 5
Target set to X=100.00 Y=50.00 Z=10.00 F=5.00

Enter command: 2
Moving: X=100.00mm Y=50.00mm Z=10.00mm F=5.00mm
Move complete!
```

**Via Protocol:**
```
!DIAG_CMD 1 100 50 10 5 *XX    # Set target
!DIAG_CMD 2 *XX                # Execute move
```

### 3.3 JOG Menu (Option 3)

**Purpose:** Incremental single-axis moves

**Submenu:**
```
JOG MENU
1 DIST - Jog X axis (e.g., "1 10.5" or "1 -5")
2 DIST - Jog Y axis
3 DIST - Jog Z axis
4 DIST - Jog Focus axis
```

**Usage:**
```
Enter command: 1 10.5
Jogging X by +10.5mm (100.00 -> 110.50)
Jog complete!

Enter command: 2 -5
Jogging Y by -5.00mm (50.00 -> 45.00)
Jog complete!
```

**Via Protocol:**
```
!DIAG_CMD 1 10.5 *XX    # Jog X +10.5mm
!DIAG_CMD 2 -5 *XX      # Jog Y -5mm
```

### 3.4 TEST Motors (Option 4)

**Purpose:** Quick motor and limit switch testing

**Submenu:**
```
MOTOR TEST MENU
1 - X axis toward MAX
2 - X axis toward MIN
3 - Y axis toward MAX
4 - Y axis toward MIN
5 - Z axis toward MAX
6 - Z axis toward MIN
7 - Focus toward MAX
8 - Focus toward MIN
9 - Safe Limit Test (step-by-step)
```

**Behavior:**
- Motor runs continuously toward selected limit
- Press any key to stop
- Auto-stops on limit switch trigger
- Good for verifying direction and limit detection

### 3.5 SAFE LIMIT TEST (Option 5)

**Purpose:** Step-by-step limit switch testing

**Submenu:**
```
SAFE LIMIT TEST
1 - Test X_MIN
2 - Test X_MAX
3 - Test Y_MIN
4 - Test Y_MAX
5 - Test Z_MIN
6 - Test Z_MAX
7 - Test F_MIN
8 - Test F_MAX
```

**Behavior:**
- Moves 2mm at a time toward limit
- Pauses 1 second between steps
- Prints pin state (HIGH/LOW) after each step
- Stops when limit triggered
- Safe for initial hardware validation

**Example Output:**
```
Testing X_MIN...
Step 1: Moving 2mm toward MIN
  Position: 98.00mm
  X_MIN pin: HIGH (not triggered)
  Press any key to abort

Step 2: Moving 2mm toward MIN
  Position: 96.00mm
  X_MIN pin: HIGH (not triggered)

...

Step 20: Moving 2mm toward MIN
  Position: 58.00mm
  X_MIN pin: LOW (TRIGGERED!)
  
X_MIN limit switch working correctly!
```

---

## 4. Global Commands

Available from any menu:

| Key | Function | Description |
|-----|----------|-------------|
| **T** | Top Menu | Return to main menu |
| **U** | Up | Go up one menu level |
| **X** | Exit | Exit diagnostic mode |
| **Q** | Quit | Same as Exit |
| **S** | Stop | Emergency stop all motors |
| **?** | Status | Show current position and state |
| **H** | Help | Show menu help |

---

## 5. Status Display (?)

```
Enter command: ?

========================================
CURRENT SYSTEM STATUS
========================================
Firmware: v1.2
State: DIAGNOSTIC
Homed: XYZF

Position (mm):
  X: 110.50
  Y: 45.00
  Z: 10.00
  F: 5.00

Target (mm):
  X: 110.50
  Y: 45.00
  Z: 10.00
  F: 5.00

Limit Switches:
  X_MIN: HIGH  X_MAX: HIGH
  Y_MIN: HIGH  Y_MAX: HIGH
  Z_MIN: HIGH  Z_MAX: HIGH
  F_MIN: HIGH  F_MAX: HIGH

Motor Drivers: ENABLED
Protocol Connection: NONE (diagnostic mode)
```

---

## 6. Testing Procedures

### 6.1 Initial Hardware Validation

**After first assembly:**

1. **Visual Inspection:**
   - Verify all wiring per [03 - Hardware Specification](03_HARDWARE_SPECIFICATION.md)
   - Check TB6600 DIP switches (1/16 microstepping)
   - Verify enable pin LOW enables motors

2. **Power-On Test:**
   ```
   - Connect Teensy USB
   - Open serial monitor (115200 baud)
   - Verify boot message appears
   - Press 'D' to enter diagnostic mode
   ```

3. **Limit Switch Test:**
   ```
   - Select option 5 (Safe Limit Test)
   - Test each limit switch (options 1-8)
   - Manually press switches to verify detection
   - Verify pin state changes in output
   ```

4. **Motor Direction Test:**
   ```
   - Select option 4 (Motor Test)
   - Test X toward MIN (option 2)
   - Verify motor moves toward MIN limit
   - If wrong direction: invert in firmware
   - Repeat for all axes
   ```

5. **Homing Test:**
   ```
   - Return to main menu (T)
   - Select option 1 (HOME)
   - Watch all axes home sequentially
   - Verify all end at 0.00mm position
   ```

6. **Movement Test:**
   ```
   - Select option 2 (MOVE)
   - Set target: 1 50 50 10 5
   - Execute: 2
   - Verify smooth coordinated motion
   ```

### 6.2 Limit Switch Reliability Test

**Purpose:** Verify 100% detection rate

**Procedure:**
1. Enter diagnostic mode
2. Select option 4 (Motor Test)
3. Test each limit 10 times:
   - Run motor toward limit
   - Verify auto-stop on trigger
   - Note any missed detections
4. Expected result: 0 misses (100% detection)

**If failures occur:**
- Check wiring
- Verify pull-ups enabled
- Review ISR code
- Check for electrical noise

### 6.3 Speed and Noise Test

**Purpose:** Find optimal speed settings

**Procedure:**
1. Note current `MAX_SPEED` in main.cpp
2. Perform test moves at current speed
3. Adjust speed (increase or decrease)
4. Recompile and test
5. Find balance between:
   - Speed (higher = faster)
   - Noise (lower = quieter)
   - Reliability (no skipped steps)

**Current Setting:** 6000 steps/sec (30 mm/sec)

### 6.4 Accuracy Test

**Purpose:** Verify positioning accuracy

**Procedure:**
1. Home all axes
2. Command move to known position (e.g., X100 Y100)
3. Measure actual position with ruler/caliper
4. Calculate error
5. If error > 1mm: recalibrate STEPS_PER_MM

**Current Calibration:** 400 steps/mm (verified accurate)

---

## 7. Protocol Testing

### 7.1 Manual Protocol Test

**Using serial terminal:**

```bash
# Connect via screen or minicom
screen /dev/serial0 115200

# Test connection
!CONNECT MASTER=test *3C
[Expect: @ACK 0 SLAVE=v1.2 *XX]

# Test status
!STATUS *1F
[Expect: @STATUS 1 X=0.00 Y=0.00 STATE=CONNECTED *XX]

# Test homing
!HOME *1A
[Expect: @ACK 2 HOMING=ZYXF *XX]
[Wait for completion]
[Expect: @COMPLETE 2 HOMED=XYZF *XX]

# Test move
!MOVE X10 Y10 *3A
[Expect: @ACK 3 MOVING ... *XX]
[Wait for completion]
[Expect: @COMPLETE 3 X=10.00 Y=10.00 *XX]
```

### 7.2 Error Condition Tests

**Test invalid command:**
```
!INVALID *XX
[Expect: @NACK seq ERR_UNKNOWN_CMD *XX]
```

**Test move without homing:**
```
!CONNECT MASTER=test *XX
!MOVE X10 *XX
[Expect: @NACK seq ERR_NOT_HOMED *XX]
```

**Test out of bounds:**
```
!MOVE X500 *XX
[Expect: @NACK seq ERR_OUT_OF_BOUNDS X=500 exceeds limit 270mm *XX]
```

**Test watchdog timeout:**
```
!CONNECT MASTER=test *XX
[Wait 6 seconds without sending anything]
[Expect: #COMM_LOST Watchdog timeout *XX]
```

### 7.3 Checksum Validation Test

**Send command with wrong checksum:**
```
!STATUS *FF
[Expect: @NACK seq ERR_CHECKSUM *XX]
```

**Verify correct checksum accepted:**
```
!STATUS *1F
[Expect: @STATUS seq ... *XX]
```

---

## 8. Performance Benchmarks

### 8.1 Timing Tests

**Command ACK Latency:**
```
for i in 1..100:
    t1 = time()
    send("!STATUS")
    wait_for_ack()
    t2 = time()
    latencies.append(t2 - t1)

Expected: < 10ms average
```

**Move Completion Time:**
```
send("!MOVE X100")
[Measure time to @COMPLETE]

Expected: ~3-4 seconds for 100mm move at 30mm/sec
```

### 8.2 Reliability Tests

**Long-Duration Test:**
```python
# Run for 8+ hours
for i in range(10000):
    home()
    move_to_random_position()
    check_position()
    
# Expected: 0 errors, 0 missed limits, no crashes
```

**Rapid Command Test:**
```python
# Stress test command processing
for i in range(1000):
    status = send("!STATUS")
    assert status.startswith("@STATUS")
    time.sleep(0.01)  # 100 commands/sec

# Expected: All commands acknowledged correctly
```

---

## 9. Troubleshooting Guide

### 9.1 Motor Issues

| Symptom | Check | Fix |
|---------|-------|-----|
| Motor doesn't move | Enable pin | Verify ENA_ALL LOW enables drivers |
| Motor moves wrong direction | Direction | Toggle setPinsInverted() for that axis |
| Motor stutters | Current setting | Increase TB6600 current DIP switches |
| Motor whines loudly | Speed/resonance | Reduce MAX_SPEED or change microstepping |
| Motor skips steps | Speed too high | Reduce MAX_SPEED and/or increase ACCEL time |

### 9.2 Limit Switch Issues

| Symptom | Check | Fix |
|---------|-------|-----|
| Limit not detected | Wiring | Verify one terminal to pin, other to GND |
| Limit reads inverted | Pull-up | Verify INPUT_PULLUP mode in setup() |
| False triggers | Cable noise | Check cable routing, verify triple-read logic |
| Intermittent detection | Connection | Check for loose wires or bad switches |

### 9.3 Communication Issues

| Symptom | Check | Fix |
|---------|-------|-----|
| No serial output | Baud rate | Verify 115200 on both sides |
| Garbled output | Cable | Check UART wiring (TX→RX, RX→TX) |
| Checksum errors | Implementation | Verify XOR algorithm correct |
| Commands ignored | State | Check if command valid for current state |

---

## 10. Diagnostic Mode Limitations

**Known Constraints:**

1. **Watchdog Disabled:**
   - Diagnostic mode disables watchdog timer
   - Safe for manual testing
   - Don't leave in diagnostic mode for autonomous operation

2. **Single Threaded:**
   - Commands execute sequentially
   - No parallel operations during menus

3. **No Command Queuing:**
   - One command at a time
   - Wait for completion before next command

4. **USB Serial Only (Local):**
   - Direct diagnostic mode via USB console
   - Remote diagnostic mode via !DIAG_CMD over Serial1

---

## 11. Advanced Diagnostic Techniques

### 11.1 Pin State Monitoring

**Add temporary debug output:**
```c++
// In main loop, add:
if (digitalRead(X_MIN_PIN) == LOW) {
    Serial.println("X_MIN pressed!");
}
```

### 11.2 Interrupt Counter

**Track ISR call frequency:**
```c++
volatile uint32_t xMinCount = 0;

void xMinISR() {
    xMinCount++;
    // ... existing ISR code ...
}

// In status display:
Serial.printf("X_MIN ISR count: %lu\n", xMinCount);
```

### 11.3 Step Counter Verification

**Compare commanded vs. actual:**
```c++
long commanded = 100 * STEPS_PER_MM;  // 40000 steps
xStepper.moveTo(commanded);
// ... wait for completion ...
long actual = xStepper.currentPosition();
float error = (float)(actual - commanded) / STEPS_PER_MM;
Serial.printf("Positioning error: %.3fmm\n", error);
```

---

**Next Section:** [07 - Issues and Resolutions](07_ISSUES_AND_RESOLUTIONS.md)
