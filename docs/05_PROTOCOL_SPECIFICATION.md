# Protocol Specification

**Document:** 05 - Protocol Specification  
**Version:** 1.1  
**Date:** January 6, 2026

---

## Note

This document is a **summary and quick reference** for the complete protocol specification.

**For full protocol details, see:** `PROTOCOL.md` in the root directory

That document includes:
- Complete command reference
- All error codes
- Timing requirements
- Example communication sessions
- Python implementation examples
- Q&A section addressing common concerns

---

## 1. Protocol Overview

**Type:** Text-based, line-oriented, master/slave  
**Master:** Raspberry Pi 4 (initiates all commands)  
**Slave:** Teensy 4.1 (executes and responds)

**Key Features:**
- XOR checksums on all messages
- Sequence numbers for duplicate detection
- ACK/NACK responses
- Async event reporting
- Watchdog timer (5-second timeout)
- Human-readable for debugging

---

## 2. Message Format

### 2.1 Commands (Master → Slave)

```
!<CMD> [args] *<checksum>\n
```

**Example:**
```
!MOVE X100 Y50 *3A\n
```

### 2.2 Responses (Slave → Master)

```
@<TYPE> <seq> [data] *<checksum>\n
```

**Examples:**
```
@ACK 42 *1F\n
@NACK 43 ERR_LIMIT X exceeds 270mm *5C\n
@STATUS 44 X=100.00 Y=50.00 STATE=IDLE *7A\n
@COMPLETE 45 X=100.00 Y=50.00 *8B\n
```

### 2.3 Events (Slave → Master, unsolicited)

```
#<EVENT> [data] *<checksum>\n
```

**Examples:**
```
#BOOT FW=v1.2 AXES=4 *1E\n
#LIMIT X_MIN *2B\n
#COMM_LOST Watchdog timeout *4D\n
#DIAG Menu output line *3F\n
```

---

## 3. Checksum Calculation

**Algorithm:** XOR all bytes before the asterisk

**C Implementation:**
```c
uint8_t calculateChecksum(const char* msg) {
    uint8_t checksum = 0;
    while (*msg && *msg != '*') {
        checksum ^= *msg++;
    }
    return checksum;
}
```

**Python Implementation:**
```python
def calculate_checksum(message):
    """Calculate XOR checksum of message up to asterisk"""
    checksum = 0
    for char in message:
        if char == '*':
            break
        checksum ^= ord(char)
    return checksum

def add_checksum(message):
    """Add checksum to message"""
    cs = calculate_checksum(message)
    return f"{message}*{cs:02X}\n"

# Example
msg = add_checksum("!MOVE X100 Y50")
# Result: "!MOVE X100 Y50 *3A\n"
```

---

## 4. Essential Commands

### 4.1 Connection Management

| Command | Description | Response |
|---------|-------------|----------|
| `!CONNECT MASTER=<ver>` | Establish connection | @ACK seq SLAVE=v1.2 |
| `!DISCONNECT` | Close connection | @ACK seq |
| `!PING` | Watchdog keepalive | @ACK seq |

### 4.2 Motion Commands

| Command | Description | State Required |
|---------|-------------|----------------|
| `!HOME [axes]` | Sequential homing (Z→Y→X→F) | CONNECTED or IDLE |
| `!HOME_FAST` | Parallel homing (all at once) | CONNECTED or IDLE |
| `!MOVE X# Y# Z# F#` | Coordinated absolute move | IDLE (homed) |
| `!JOG <axis> <dist>` | Incremental single-axis jog | IDLE (homed) |
| `!STOP` | Emergency stop all axes | Any |

### 4.3 Status and Query

| Command | Description | Response |
|---------|-------------|----------|
| `!STATUS` | Get position and state | @STATUS seq X=... Y=... STATE=... |
| `!VERSION` | Get firmware version | @ACK seq FW=v1.2 AXES=4 |
| `!LIMITS` | Get limit switch states | @ACK seq X_MIN=0 X_MAX=0 ... |

### 4.4 Diagnostic Mode

| Command | Description | State Change |
|---------|-------------|--------------|
| `!DIAG_ENTER` | Enter diagnostic mode | → DIAGNOSTIC |
| `!DIAG_EXIT` | Exit diagnostic mode | → IDLE |
| `!DIAG_CMD <char>` | Send menu command | (in DIAGNOSTIC) |
| `!DIAG_MENU` | Get current menu | (in DIAGNOSTIC) |

---

## 5. Error Codes

### 5.1 Protocol Errors

| Code | Description | Recovery |
|------|-------------|----------|
| `ERR_CHECKSUM` | Checksum mismatch | Retry with correct checksum |
| `ERR_UNKNOWN_CMD` | Command not recognized | Check spelling |
| `ERR_INVALID_ARGS` | Missing or malformed args | Check syntax |

### 5.2 State Errors

| Code | Description | Recovery |
|------|-------------|----------|
| `ERR_NOT_CONNECTED` | Must CONNECT first | Send !CONNECT |
| `ERR_NOT_HOMED` | Must home before move | Send !HOME |
| `ERR_ALREADY_MOVING` | Previous motion not done | Wait or !STOP |
| `ERR_INVALID_STATE` | Operation not allowed now | Check !STATUS |

### 5.3 Motion Errors

| Code | Description | Recovery |
|------|-------------|----------|
| `ERR_LIMIT_HIT` | Limit switch triggered | !CLEAR_ERROR, re-home |
| `ERR_OUT_OF_BOUNDS` | Position exceeds soft limits | Reduce target position |
| `ERR_HOMING_FAILED` | Homing did not complete | Check wiring, retry |

---

## 6. Communication Parameters

### 6.1 UART Settings

| Parameter | Value |
|-----------|-------|
| Baud Rate | 115200 |
| Data Bits | 8 |
| Parity | None |
| Stop Bits | 1 |
| Flow Control | None |
| Line Ending | \n (LF, 0x0A) |

### 6.2 Timing Requirements

| Parameter | Value | Notes |
|-----------|-------|-------|
| **ACK Latency** | < 10ms | Typical response time |
| **Status Query** | < 20ms | Includes position calculation |
| **Move Start** | < 50ms | After ACK sent |
| **Watchdog Timeout** | 5 seconds | Motor shutdown on timeout |
| **Master Heartbeat** | Every 3 seconds | !PING or any command |

---

## 7. Sequence Numbers

**Purpose:** Duplicate detection and retry logic

**Master Behavior:**
- Assign increasing sequence number to each command (0-255, wraps)
- Track last 10 sequence numbers for duplicate detection
- Retry with same sequence number on timeout/NACK

**Slave Behavior:**
- Echo sequence number in responses
- Detect duplicate sequences (resend last ACK)
- 10-command window sufficient

**Example:**
```
RPi:    !CONNECT MASTER=v1.0 *3C    [seq 0]
Teensy: @ACK 0 SLAVE=v1.2 *2F

RPi:    !HOME *1A                   [seq 1]
Teensy: @ACK 1 HOMING=ZYXF *4B
[... homing happens ...]
Teensy: @COMPLETE 1 HOMED=XYZF *5C

RPi:    !STATUS *1F                 [seq 2]
Teensy: @STATUS 2 X=0.00 Y=0.00 STATE=IDLE *7A
```

---

## 8. Watchdog Timer

### 8.1 Behavior

**Timeout:** 5 seconds of no messages from master

**Actions on Timeout:**
1. Immediately stop all motors (emergency stop)
2. Disable motor drivers
3. Transition to STATE_COMM_LOST
4. Send `#COMM_LOST Watchdog timeout *XX`
5. Attempt auto-recovery (send #BOOT every 10 seconds)

### 8.2 Master Responsibilities

- Send !PING or any command at least every 3 seconds
- Recommended: Send !STATUS every 1 second during idle
- During moves: @COMPLETE resets watchdog

**Python Example:**
```python
import threading
import time

def watchdog_thread(ser, stop_event):
    """Background thread to send periodic PING"""
    while not stop_event.is_set():
        send_command(ser, "!PING")
        time.sleep(3)  # Ping every 3 seconds
```

### 8.3 Diagnostic Mode Exception

**Watchdog is DISABLED in diagnostic mode**
- Human interaction has unpredictable timing
- No PING required during !DIAG_ENTER
- Watchdog re-enabled on !DIAG_EXIT

---

## 9. State Machine

### 9.1 Valid State Transitions

```
BOOT → DISCONNECTED → CONNECTED → IDLE
         ↑                 ↓
         └─ COMM_LOST ←───┘
         
IDLE → HOMING → IDLE
     → MOVING → IDLE
     → JOGGING → IDLE
     → DIAGNOSTIC → IDLE
     → ERROR → DISCONNECTED
```

### 9.2 Commands by State

| Command | DISCONNECTED | CONNECTED | IDLE | HOMING | MOVING | ERROR | DIAGNOSTIC |
|---------|--------------|-----------|------|--------|--------|-------|------------|
| !CONNECT | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| !HOME | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| !MOVE | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| !JOG | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| !STOP | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| !STATUS | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| !PING | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| !DIAG_ENTER | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| !DIAG_EXIT | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |

---

## 10. Example Communication Sessions

### 10.1 Startup and Homing

```
[Teensy boots]
Teensy: #BOOT FW=v1.2 AXES=4 *1E

[RPi connects]
RPi:    !CONNECT MASTER=v1.0 *3C
Teensy: @ACK 0 SLAVE=v1.2 *2F

[Home all axes]
RPi:    !HOME *1A
Teensy: @ACK 1 HOMING=ZYXF *4B
[... 30 seconds of homing ...]
Teensy: @COMPLETE 1 HOMED=XYZF *5C

[Check status]
RPi:    !STATUS *1F
Teensy: @STATUS 2 X=0.00 Y=0.00 Z=0.00 F=0.00 STATE=IDLE HOMED=XYZF *7A
```

### 10.2 Coordinated Move

```
RPi:    !MOVE X100 Y50 Z10 *3A
Teensy: @ACK 3 MOVING X=100.0mm Y=50.0mm Z=10.0mm *5F
[... 3 seconds of motion ...]
Teensy: @COMPLETE 3 X=100.00 Y=50.00 Z=10.00 *6C
```

### 10.3 Error Handling

```
[Try to move out of bounds]
RPi:    !MOVE X500 *2B
Teensy: @NACK 4 ERR_OUT_OF_BOUNDS X=500.00 exceeds limit 270.00mm *7D

[Check status after error]
RPi:    !STATUS *1F
Teensy: @STATUS 5 X=100.00 Y=50.00 STATE=IDLE HOMED=XYZF *8E
```

### 10.4 Jog Command (v1.1)

```
[Jog X axis by +2mm]
RPi:    !JOG X 2.00 *3E
Teensy: @ACK 6 JOGGING X +2.00mm *4A
[... motion completes ...]
Teensy: @COMPLETE 6 X=102.00 Y=50.00 Z=10.00 F=5.00 *7B
```

**Note (Protocol v1.1):** The `@COMPLETE` response for `!JOG` now includes full position (X, Y, Z, F), matching the behavior of `!MOVE`. This allows the master to synchronize its position with the authoritative Teensy position after each jog.

### 10.5 Watchdog Timeout

```
[Master stops sending commands]
[... 5 seconds pass ...]
Teensy: #COMM_LOST Watchdog timeout *4D
[Teensy enters STATE_COMM_LOST, motors disabled]

[Every 10 seconds until master reconnects]
Teensy: #BOOT FW=v1.2 AXES=4 *1E
```

---

## 11. Implementation Tips

### 11.1 Python Client Structure

**Recommended Architecture:**
```python
import serial
import threading
from queue import Queue

class TeensyClient:
    def __init__(self, port='/dev/serial0', baud=115200):
        self.ser = serial.Serial(port, baud, timeout=0.1)
        self.seq = 0
        self.response_queue = Queue()
        self.event_queue = Queue()
        
        # Start background threads
        self.rx_thread = threading.Thread(target=self._rx_loop)
        self.watchdog_thread = threading.Thread(target=self._watchdog_loop)
        self.rx_thread.start()
        self.watchdog_thread.start()
    
    def send_command(self, cmd):
        """Send command with checksum and sequence number"""
        msg = f"{cmd}"
        checksum = self.calculate_checksum(msg)
        self.ser.write(f"{msg} *{checksum:02X}\n".encode())
        self.seq = (self.seq + 1) % 256
    
    def _rx_loop(self):
        """Background thread to receive and parse messages"""
        while True:
            line = self.ser.readline().decode().strip()
            if line.startswith('@'):
                self.response_queue.put(line)
            elif line.startswith('#'):
                self.event_queue.put(line)
    
    def _watchdog_loop(self):
        """Background thread to send periodic PING"""
        while True:
            time.sleep(3)
            self.send_command("!PING")
```

### 11.2 Error Handling

**Always check responses:**
```python
response = self.response_queue.get(timeout=5.0)
if response.startswith('@NACK'):
    # Parse error code and message
    parts = response.split(' ', 3)
    seq = int(parts[1])
    error_code = parts[2]
    message = parts[3].split('*')[0]
    raise TeensyError(f"{error_code}: {message}")
```

### 11.3 Async Events

**Monitor event queue:**
```python
def event_monitor_thread():
    while True:
        event = client.event_queue.get()
        if event.startswith('#LIMIT'):
            print(f"WARNING: Limit switch triggered: {event}")
        elif event.startswith('#COMM_LOST'):
            print("ERROR: Communication lost!")
            # Attempt reconnection
```

---

## 12. Testing and Validation

### 12.1 Manual Testing

Use terminal emulator (screen, minicom, or VS Code serial monitor):

```bash
# Connect to Teensy
screen /dev/serial0 115200

# Send commands manually
!CONNECT MASTER=test *XX
!HOME *XX
!STATUS *XX
!MOVE X10 Y10 *XX
```

**Note:** Calculate checksums manually or use test script

### 12.2 Checksum Test Script

```python
def test_checksum():
    # Test cases from PROTOCOL.md Appendix A
    assert calculate_checksum("!CONNECT MASTER=v1.0 ") == 0x3C
    assert calculate_checksum("!PING ") == 0x1F
    assert calculate_checksum("@ACK 0 SLAVE=v1.2 ") == 0x2F
    print("Checksum tests passed!")
```

### 12.3 Automated Test Suite

See `TEST_PROGRAM_GUIDE.md` for comprehensive test procedures

---

## 13. Diagnostic Mode Special Features

### 13.1 Remote Diagnostic Access

Via protocol commands, RPi can control diagnostic menu:

```
RPi:    !DIAG_ENTER *2A
Teensy: @ACK 20 ENTERING_DIAGNOSTIC *4F
Teensy: #DIAG ======================================== *3A
Teensy: #DIAG DIAGNOSTIC MAIN MENU *1F
Teensy: #DIAG 1 - HOME All Axes *2B
Teensy: #DIAG 2 - MOVE Absolute Position *3C
...

RPi:    !DIAG_CMD 1 *3C
Teensy: @ACK 21 CMD_SENT *2D
Teensy: #DIAG Starting sequential homing... *4E
...

RPi:    !DIAG_EXIT *4D
Teensy: @ACK 22 EXITING_DIAGNOSTIC *5E
```

### 13.2 Non-Interactive Menu Commands

**MOVE Menu:**
```
!DIAG_CMD 1 100 50 10 0 *XX    # Set target: X=100, Y=50, Z=10, F=0
```

**JOG Menu:**
```
!DIAG_CMD 1 10.5 *XX           # Jog X axis by +10.5mm
!DIAG_CMD 2 -5 *XX             # Jog Y axis by -5mm
```

---

## 14. Advanced Topics

### 14.1 Future: Command Queuing

Not implemented in v1.0, but protocol supports future extension:

```
!QUEUE_MOVE X100 Y50 *XX
@ACK 10 QUEUED pos=1 *XX

!QUEUE_MOVE X150 Y75 *XX
@ACK 11 QUEUED pos=2 *XX

!EXECUTE_QUEUE *XX
@ACK 12 EXECUTING count=2 *XX
@COMPLETE 12 queue_finished *XX
```

### 14.2 Future: Trajectory Smoothing

Could add spline interpolation or S-curve acceleration

### 14.3 Future: Position Feedback

Could add encoder support for closed-loop positioning

---

## 15. Quick Reference Card

**Connect and Home:**
```
!CONNECT MASTER=v1.0
!HOME
```

**Move:**
```
!MOVE X100 Y50 Z10
```

**Status:**
```
!STATUS
```

**Emergency Stop:**
```
!STOP
```

**Keep Alive:**
```
!PING
```

**Enter Diagnostic:**
```
!DIAG_ENTER
!DIAG_CMD 1    # Execute menu option 1
!DIAG_EXIT
```

---

**For complete protocol details, see:** `PROTOCOL.md`

**Next Section:** [06 - Diagnostic Procedures](06_DIAGNOSTIC_PROCEDURES.md)
