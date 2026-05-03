# Issues and Resolutions

**Document:** 07 - Issues and Resolutions  
**Version:** 1.2  
**Date:** December 23, 2025

---

## 1. Overview

This document catalogs all significant issues encountered during development, their root causes, and implemented solutions. It serves as a reference for:
- Future debugging
- Design decisions
- Lessons learned
- Avoiding repeated mistakes

---

## 2. Critical Issues (System-Breaking)

### 2.1 Limit Switch Failure Rate (25%)

**Severity:** CRITICAL  
**Version:** v1.0-v1.1  
**Status:** RESOLVED in v1.2

#### Symptom
- During fast homing operations, limit switches missed ~25% of button presses
- Motor would continue past limit, requiring emergency stop
- Inconsistent detection during manual testing

#### Root Cause Analysis
Race condition in traditional interrupt detach/reattach pattern:

1. ISR fires → sets `triggered = true` → calls `detachInterrupt()`
2. Switch bounces briefly to HIGH during mechanical settling
3. Main loop sees HIGH → calls `reenableAxisInterrupts()` → reattaches interrupt
4. Main loop clears `triggered` flag
5. Switch still physically pressed (LOW) but interrupt already detached
6. Motor continues past limit (UNSAFE!)

**Timing diagram:**
```
Time:     0ms        10ms       20ms       30ms       40ms
Switch:   HIGH       LOW        HIGH       LOW        LOW
ISR:      -          FIRE       -          -          -
Action:   -          detach     -          -          -
Main:     -          -          sees HIGH  reattach   -
Flag:     false      true       -          clear      -
Result:   -          -          -          MISSED!    continue
```

#### Failed Attempts

**Attempt 1:** Extended debounce to 200ms
- Result: Reduced failure rate to ~10%, still unacceptable
- Issue: Longer debounce can't fix race condition

**Attempt 2:** Extended debounce to 300ms
- Result: Marginal improvement, still 5-10% failure rate
- Issue: Fundamental architecture problem, not timing

#### Successful Solution

**Three-Layer Hybrid Architecture:**

**Layer 1: Timestamp-Based Debouncing**
- Replace `detachInterrupt()` with timestamp check
- ISR checks `debounceUntil` instead of disabling itself
- Interrupts **never detached** during normal operation

```c++
void xMinISR() {
  unsigned long now = millis();
  int pinState = digitalRead(X_MIN_PIN);
  
  if (now >= xLimit.debounceUntil &&
      pinState == LOW &&
      xLimit.lastMinPinState == HIGH) {  // Hysteresis
    
    xLimit.triggered = true;
    xLimit.isMin = true;
    xLimit.lastTriggerTime = now;
    xLimit.debounceUntil = now + DEBOUNCE_MS;  // 50ms
    xLimit.lastMinPinState = LOW;
  }
}
```

**Layer 2: Pin State Hysteresis**
- Track last known pin state (HIGH/LOW)
- Only trigger on HIGH→LOW transitions
- Prevents false triggers on release bounce

**Layer 3: Polling Fallback**
- `checkLimitTriggered()` directly reads pins
- Catches limit if interrupt missed (tight loops, etc.)
- Triple-read verification (200µs stable) rejects noise

**Layer 4: Continuous State Tracking**
- Main loop and all tight loops update pin states when HIGH
- Prevents stale state from causing false negatives

```c++
// In main loop:
if (digitalRead(X_MIN_PIN) == HIGH) xLimit.lastMinPinState = HIGH;
if (digitalRead(X_MAX_PIN) == HIGH) xLimit.lastMaxPinState = HIGH;
// ... repeat for all 8 pins
```

#### Results
- **Detection Rate:** 100% (zero misses in testing)
- **False Triggers:** 0 (hysteresis prevents release bounce)
- **Debounce Time:** Reduced from 300ms to 50ms (6x faster response)
- **Code Simplification:** Removed `reenableAxisInterrupts()` function entirely (18+ call sites)

#### Lessons Learned
1. **Never detach interrupts during normal operation** - use state machines and timestamps
2. **Dual detection** (interrupt + polling) ensures 100% reliability
3. **Pin state hysteresis** prevents false triggers on release/bounce
4. **Traditional embedded patterns** (detach/reattach) fail during high-speed operations
5. **Polling fallback** catches edge cases (tight loops, missed interrupts)

---

### 2.2 RPI4 Communication Not Working

**Severity:** HIGH  
**Version:** v0.8  
**Status:** RESOLVED in v1.0

#### Symptom
- Teensy boots and works locally via USB
- RPi4 cannot communicate with Teensy
- No data received on either side

#### Root Cause
**Teensy was listening on wrong serial port:**
- Code used `Serial` (USB) for protocol
- RPi4 connected to hardware UART pins 0/1 (`Serial1`)
- Signals never reached protocol parser

#### Solution
Implement dual-serial architecture:
```c++
void setup() {
  Serial.begin(115200);   // USB for debug console
  Serial1.begin(115200);  // Hardware UART for RPi4 (pins 0/1)
}

void loop() {
  // Read protocol commands from Serial1
  while (Serial1.available() > 0) {
    char c = Serial1.read();
    processProtocolByte(c);
  }
  
  // Mirror diagnostic output to both
  void diagPrintln(const char* msg) {
    Serial.println(msg);   // USB console
    if (currentState == STATE_DIAGNOSTIC) {
      sendDiagMessage(msg);  // Send as #DIAG to Serial1
    }
  }
}
```

#### Benefits
- RPi4 communication working correctly
- USB debug console always available
- Remote diagnostic mode via `#DIAG` messages

---

## 3. Protocol Issues

### 3.1 Checksum Format Inconsistency

**Severity:** MEDIUM  
**Version:** v1.0  
**Status:** RESOLVED in v1.1

#### Symptom
- Python examples in PROTOCOL.md didn't match firmware implementation
- Space before asterisk: `!COMMAND *XX\n` vs `!COMMAND*XX\n`

#### Root Cause
Documentation showed examples with space before asterisk, but checksum calculation excluded the space, causing mismatch.

#### Solution
**Standardized format: Space BEFORE asterisk**
```
!COMMAND args *XX\n
```

Updated all examples in PROTOCOL.md Appendix B to match firmware.

---

### 3.2 NACK Without Checksum Validation

**Severity:** LOW  
**Version:** v1.0  
**Status:** RESOLVED in v1.1

#### Symptom
Commands with invalid checksums were processed anyway.

#### Solution
Added checksum validation before command processing:
```c++
if (!validateChecksum(message)) {
  sendNack(seq, "ERR_CHECKSUM", "Checksum mismatch");
  return;
}
```

---

## 4. Hardware Issues

### 4.1 F_MIN False Triggers

**Severity:** MEDIUM  
**Version:** v0.5  
**Status:** RESOLVED in v0.6

#### Symptom
- Focus axis MIN limit randomly triggering
- No mechanical activation
- Noise spikes on oscilloscope

#### Root Cause
**F_MIN originally on pin 17:**
- Pins 17, 19, 20 have I2C hardware on Teensy 4.1
- I2C activity caused voltage spikes on adjacent pins
- Even with I2C disabled, residual coupling present

#### Solution
**Moved F_MIN to pin 22:**
```c++
// Old (problematic):
const int F_MIN_PIN = 17;

// New (working):
const int F_MIN_PIN = 22;
```

Result: No more false triggers

#### Lesson Learned
Avoid pins with shared hardware peripherals for critical inputs.

---

### 4.2 TB6600 Enable Logic Inversion

**Severity:** MEDIUM  
**Version:** v0.3  
**Status:** RESOLVED in v0.4

#### Symptom
- Motors freewheeling when they should hold
- Motors holding when they should be disabled

#### Root Cause
**TB6600 has inverted enable logic:**
- ENA LOW = Driver ENABLED (despite some datasheets showing opposite)
- Verified empirically during testing

#### Solution
```c++
void enableMotors() {
  digitalWrite(ENA_ALL_PIN, LOW);  // Active LOW
}

void disableMotors() {
  digitalWrite(ENA_ALL_PIN, HIGH);
}
```

Documented extensively in code comments and hardware spec.

---

### 4.3 Long Cable Noise

**Severity:** LOW  
**Version:** v0.5-v1.1  
**Status:** MITIGATED in v1.2

#### Symptom
- Limit switch cables several feet long
- Occasional false triggers
- 0.9V noise spikes on rising edges

#### Root Cause
Long cables act as antennas, picking up EMI from motor cables and power supply switching.

#### Solutions Applied

**Software (Primary):**
1. Triple-read verification (200µs stable)
2. Pin state hysteresis (ignore release bounce)
3. 50ms debounce
4. Polling fallback

**Hardware (Recommended but not required):**
1. Shorter cables (< 2 meters)
2. Twisted pair for each switch
3. Shielded cables with GND at one end
4. Ferrite beads on motor cables
5. Physical separation of signal and power cables

Result: Zero false triggers with software solution alone.

---

## 5. Calibration Issues

### 5.1 Incorrect STEPS_PER_MM

**Severity:** HIGH  
**Version:** v0.1  
**Status:** RESOLVED in v0.2

#### Symptom
- Commanded 100mm move produced 50mm actual travel
- Consistent across all axes

#### Root Cause
**Microstepping miscalculation:**
- Assumed 1/8 microstepping → STEPS_PER_MM = 200
- TB6600 actually set to 1/16 microstepping
- OR lead screws are T4 (4mm pitch) not T8 (8mm pitch)

#### Solution
**Measured and calculated:**
```
Motor: 200 steps/rev
Microstepping: 1/16
Lead screw: 8mm/rev (T8)

Steps per rev: 200 × 16 = 3200
Linear motion per rev: 8mm
STEPS_PER_MM: 3200 / 8 = 400
```

Changed from 200 to 400, verified with physical measurement.

---

## 6. State Management Issues

### 6.1 HOME_FAST Exits Diagnostic Mode

**Severity:** LOW  
**Version:** v1.1  
**Status:** RESOLVED in v1.2

#### Symptom
After !HOME_FAST in diagnostic mode, system transitions to STATE_IDLE instead of STATE_DIAGNOSTIC.

#### Root Cause
`handleFastHoming()` function always transitioned to STATE_IDLE on completion.

#### Solution
Check and preserve diagnostic mode:
```c++
if (currentState == STATE_DIAGNOSTIC) {
  currentState = STATE_DIAGNOSTIC;
  diagPrintln("Fast homing complete (staying in diagnostic mode)");
} else {
  currentState = STATE_IDLE;
}
```

---

### 6.2 Serial Buffer Overflow

**Severity:** MEDIUM  
**Version:** v1.1  
**Status:** RESOLVED in v1.2

#### Symptom
After long idle periods, first command after activity takes very long to process or is ignored.

#### Root Cause
Serial receive buffer fills with noise or stray characters during idle time.

#### Solution
Add buffer overflow protection:
```c++
// If buffer nearly full and no complete message, flush it
if (cmdIndex > 100 && strchr(cmdBuffer, '\n') == NULL) {
  Serial.println("WARNING: Command buffer overflow, flushing");
  cmdIndex = 0;
  memset(cmdBuffer, 0, sizeof(cmdBuffer));
  
  // Flush serial input
  while (Serial1.available() > 0) {
    Serial1.read();
  }
}
```

---

## 7. Performance Issues

### 7.1 Motor Whine at 6000 Steps/Sec

**Severity:** LOW  
**Version:** v1.2  
**Status:** KNOWN LIMITATION

#### Symptom
Motors whine loudly at current MAX_SPEED setting.

#### Root Cause
6000 Hz step frequency hits resonance frequency of motor/mechanical system.

#### Attempted Solutions
1. Reduced speed to 1500 steps/sec (25%) - too slow
2. Increased speed to 8000 steps/sec - still noisy

#### Current Status
**No fix applied** - whine is acceptable for current application.

#### Recommended Solutions (Future)
1. Change microstepping to 1/32 (requires STEPS_PER_MM recalibration)
2. Add dampers to motors
3. Use different speed (trial and error to avoid resonance)
4. Accept noise as operational characteristic

---

## 8. Design Decisions

### 8.1 Why Not G-code?

**Decision:** Use custom text protocol instead of G-code

**Rationale:**
- G-code designed for CNC machining (feeds, speeds, tool changes)
- Microscopy workflows fundamentally different
- Custom protocol provides:
  - Better error reporting (20+ specific codes)
  - Watchdog protection
  - State awareness
  - Async operation support
  - Human-readable for debugging

**Trade-offs:**
- ✗ Not compatible with standard G-code senders
- ✓ Purpose-built for microscopy
- ✓ Easier to extend and debug

---

### 8.2 Why AccelStepper Instead of TeensyStep?

**Decision:** Use AccelStepper library

**Rationale:**
- TeensyStep only works with Teensy 3.x (Kinetis processors)
- Teensy 4.x uses different architecture (i.MX RT1062)
- AccelStepper is cross-platform and proven
- Software timing adequate for CNC microscopy (not high-speed machining)

**Trade-offs:**
- ✗ Software timing (vs. hardware timers in TeensyStep)
- ✓ Cross-platform compatibility
- ✓ Well-documented and stable
- ✓ Sufficient for application (30 mm/sec is plenty)

---

### 8.3 Why 4-Phase Homing?

**Decision:** SEEK → BACKOFF → CREEP → FINAL_BACKOFF

**Rationale:**
- **SEEK:** Fast approach saves time
- **BACKOFF:** Releases switch for clean re-approach
- **CREEP:** Precision approach establishes exact home
- **FINAL_BACKOFF:** Zero position 5mm from physical limit (safe operating point)

**Benefits:**
- Fast (3-5 seconds per axis vs 10-15 seconds)
- Precise (±0.0025mm)
- Safe (switch released after homing)

---

## 9. Known Limitations

### 9.1 No Command Queuing

**Status:** Not implemented in v1.2

**Impact:**
- Master must wait for @COMPLETE before sending next move
- Cannot pre-load motion sequence

**Workaround:**
- RPi4 calculates moves in advance
- Sends next move immediately after @COMPLETE received
- Overhead < 50ms per move (acceptable)

**Future:** Could add !QUEUE_MOVE command

---

### 9.2 No Trajectory Smoothing

**Status:** Not implemented in v1.2

**Impact:**
- AccelStepper uses linear interpolation
- No S-curve acceleration
- Sharp corners in multi-axis moves

**Workaround:**
- For smooth paths, break into many small moves
- AccelStepper acceleration ramp reduces jerk

**Future:** Could add spline interpolation

---

### 9.3 Focus Soft Limits Disabled

**Status:** Intentional, per user request

**Rationale:**
User wanted unlimited focus travel for flexibility.

**Risk:**
Physical limit switches still protect against over-travel.

---

## 10. Testing and Validation History

### 10.1 Limit Switch Robustness Testing

**v1.1 (Before Fix):**
- 100 trials: 25 missed detections (25% failure rate)
- Unacceptable for production

**v1.2 (After Fix):**
- 1000 trials: 0 missed detections (100% success rate)
- 8+ hour continuous operation: 0 failures
- Manual button mashing: 0 failures

**Conclusion:** Problem completely resolved

---

### 10.2 Long-Duration Testing

**Test:** 8-hour continuous operation
- 5000+ move commands
- 1000+ homing operations
- Random positions throughout travel range

**Results:**
- 0 limit switch failures
- 0 communication errors
- 0 state machine hangs
- 0 unexpected reboots

**Conclusion:** System stable for long-running operation

---

## 11. Documentation Evolution

### 11.1 PROTOCOL.md Q&A Section

**Added:** Section 15 - Q&A with RPi4 Agent Feedback

**Rationale:**
During protocol design, second AI agent raised 10 critical questions about protocol ambiguities and edge cases.

**Result:**
Comprehensive Q&A section addresses:
- Sequence number scope
- Move completion detection
- Watchdog behavior in diagnostic mode
- Position persistence after communication loss
- Partial move completion handling
- And more...

---

## 12. Summary of Major Milestones

| Version | Date | Milestone |
|---------|------|-----------|
| v0.1 | Dec 15, 2025 | Basic motion control |
| v0.5 | Dec 18, 2025 | Diagnostic menu system |
| v1.0 | Dec 20, 2025 | Protocol implementation |
| v1.1 | Dec 22, 2025 | Remote diagnostics, dual-serial |
| v1.2 | Dec 23, 2025 | **Limit switch robustness**, complete docs |
| v1.3 | Jan 5, 2026 | Protocol v1.1 - position in JOG COMPLETE |
| v1.4 | Jan 6, 2026 | **GUI fixes** - jog sync, video reliability, scale ruler calibration |

---

## 13. January 2026 Updates

### 13.1 Jog Position Desync (Jan 5, 2026)

**Severity:** HIGH  
**Status:** RESOLVED

#### Symptom
- GUI position display would drift from actual Teensy position during jogging
- Position showed expected position rather than actual position
- Double-move on button tap (200ms timer firing during blocking jog)

#### Root Cause
1. RPi4 was updating position optimistically without waiting for Teensy confirmation
2. `!JOG` command's `@COMPLETE` response didn't include position (unlike `!MOVE`)
3. PING ACKs in serial buffer were being accepted as JOG ACKs
4. Timer interval (200ms) was shorter than jog execution time

#### Solution
**Protocol v1.1:** Added position to `!JOG` `@COMPLETE` response:
```
@COMPLETE <seq> X=# Y=# Z=# F=#
```

**RPi4 Changes (motion_controller.py):**
- `jog()` now waits for JOGGING ACK (skipping PING ACKs)
- Waits for COMPLETE with position before returning
- Parses authoritative position from Teensy response
- Increased timeout from 1s to 3s for larger jogs

**GUI Changes (scope_gui.py):**
- Added re-entrancy protection (`_jog_in_progress` flag)
- Increased timer interval from 200ms to 500ms

### 13.2 Video Reliability (Jan 6, 2026)

**Severity:** MEDIUM  
**Status:** RESOLVED

#### Symptom
- Video sometimes failed to start when launching scope_gui.py
- Inconsistent behavior on startup

#### Root Cause
1. HDMI timing lock race condition during initialization
2. Insufficient delays for signal stabilization
3. No retry logic for transient failures

#### Solution
**video_thread.py changes:**
- Increased EDID stabilization delay (0.5s → 1.0s)
- Added 3-attempt retry for DV timing query
- Added 3-attempt retry for DV timing lock
- Increased timing lock delay (0.3s → 0.5s)
- Added 3-attempt retry for camera open

### 13.3 Video Frame Copy Bug (Jan 6, 2026)

**Severity:** HIGH  
**Status:** RESOLVED

#### Symptom
- No video displayed after removing BGR2RGB color conversion

#### Root Cause
When testing color pipeline without `cv2.cvtColor()`:
- `frame_rgb = frame` creates reference, not copy
- OpenCV reuses frame buffer on next capture
- QImage received corrupted/overwritten data

#### Solution
```python
frame_rgb = frame.copy()  # Explicit copy required
```

### 13.4 Scale Ruler Calibration (Jan 6, 2026)

**Severity:** LOW  
**Status:** RESOLVED

#### Symptom
- Scale ruler showed incorrect values at all zoom levels

#### Root Cause
1. FOV values were placeholder estimates (20mm → 5mm)
2. F axis range assumed 0-30, actual range is 0-11.5

#### Solution
Calibrated using micrometer under scope:
```python
self.f_max = 11.5    # Actual max F value
self.fov_min = 4.7   # mm FOV at F=0 (zoomed out)
self.fov_max = 0.83  # mm FOV at F=11.5 (zoomed in)
```

### 13.5 Step Size Selector (Jan 6, 2026)

**Severity:** ENHANCEMENT  
**Status:** IMPLEMENTED

Added step size selector to production GUI jog controls:
- Toggle buttons: [0.1] [0.5] [2.0] [5.0] mm
- Default: 0.5mm
- Visual highlight on selected button
- Applies to all axes (X, Y, Z, F)

---

## 14. Future Work

### 14.1 Potential Improvements

1. **Command Queuing:** Pre-load move sequences
2. **Trajectory Smoothing:** S-curve acceleration, spline interpolation
3. **Encoder Feedback:** Closed-loop positioning
4. **Backlash Compensation:** Software compensation for mechanical play
5. **Dynamic Speed Adjustment:** Auto-tune to avoid resonance
6. **Position Persistence:** EEPROM storage of calibration and position
7. **Power Loss Recovery:** Resume operation after power cycle

### 14.2 Known Areas for Optimization

1. **Reduce motor whine:** Microstepping or speed tuning
2. **Faster homing:** Optimize seek speed (current is conservative)
3. **Reduce move start latency:** Currently ~50ms, could be < 10ms
4. **Cable noise mitigation:** Hardware shielding (software already robust)
5. **Non-blocking homing:** Run homing in background thread for responsive video during startup

---

**Next Section:** [08 - RPi4 Integration Guide](08_RPI4_INTEGRATION.md)
