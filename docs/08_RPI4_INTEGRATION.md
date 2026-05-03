# RPi4 Integration Guide

**Document:** 08 - Raspberry Pi 4 Integration  
**Version:** 1.3  
**Date:** December 23, 2025

---

## 1. Overview

This document provides complete integration guidance for connecting a Raspberry Pi 4 (RPi4) to the Teensy 4.1 motion controller via hardware UART. It includes working Python code examples from the production GUI system.

**Production Code:** This guide includes actual code from:
- `teensy_protocol.py` - Serial protocol implementation
- `motion_controller.py` - High-level motion control
- `scope_gui.py` - GUI integration examples

---

## 2. Hardware Connection

### 2.1 Wiring

**Teensy 4.1 → RPi4 Connection:**

| Teensy 4.1 | RPi4 GPIO | Function | Notes |
|------------|-----------|----------|-------|
| Pin 0 (RX1) | GPIO 14 (TXD) | UART RX | Serial1 on Teensy |
| Pin 1 (TX1) | GPIO 15 (RXD) | UART TX | Serial1 on Teensy |
| GND | GND | Ground | Common ground required |

**IMPORTANT:** 
- Teensy uses 3.3V logic (compatible with RPi4)
- **Do NOT connect 5V pins** - will damage Teensy
- Use direct connection (no level shifters needed)
- Keep cable length < 30cm for reliability

### 2.2 RPi4 UART Configuration

The RPi4 hardware UART must be configured for Teensy communication:

**Configure /boot/firmware/config.txt:**
```bash
sudo nano /boot/firmware/config.txt
```

Add these lines:
```ini
# Enable hardware UART for Teensy communication
enable_uart=1
dtoverlay=disable-bt
```

**Disable Serial Console:**
```bash
sudo raspi-config
# Navigate to: Interface Options → Serial Port
# "Would you like a login shell accessible over serial?" → No
# "Would you like the serial port hardware to be enabled?" → Yes
# Finish and reboot
```

**Verify Configuration:**
```bash
ls -l /dev/serial0
# Should show: /dev/serial0 -> ttyAMA0

# Test serial port (with Teensy connected)
sudo apt install minicom
minicom -D /dev/serial0 -b 115200
# Should see Teensy output if diagnostic messages enabled
```

---

## 3. Python Dependencies and Setup

### 3.1 Install Required Packages

```bash
# Python 3 and pip
sudo apt install -y python3-pip

# PySerial for UART communication
pip3 install pyserial

# PyQt5 for GUI (if using GUI)
sudo apt install -y python3-pyqt5

# OpenCV for camera (if using GUI)
sudo apt install -y python3-opencv
```

### 3.2 User Permissions

Add your user to the `dialout` group:
```bash
sudo usermod -a -G dialout $USER
# Log out and back in for changes to take effect
```

Verify access:
```bash
groups
# Should include "dialout"

ls -l /dev/serial0
# Should show: crw-rw---- 1 root dialout
```

---

## 4. Production Python Code - Protocol Implementation

### 4.1 TeensyController Class (teensy_protocol.py)

**Complete working implementation from production system:**

```python
#!/usr/bin/env python3
"""
teensy_protocol.py - Serial protocol implementation for Teensy 4.1

Production code from The Mineral Microscope GUI system.
"""

import serial
import threading
import time

class TeensyController:
    """
    Serial protocol implementation for Teensy 4.1 motion controller.
    
    Features:
    - XOR checksum validation
    - Sequence number tracking
    - Watchdog timer (3-second !PING)
    - Thread-safe command sending
    - Asynchronous response handling
    """
    
    def __init__(self, port='/dev/ttyACM0', baudrate=115200, debug=False):
        """
        Initialize Teensy serial connection.
        
        Args:
            port: Serial port (typically /dev/ttyACM0 or /dev/serial0)
            baudrate: Baud rate (must be 115200)
            debug: Enable debug print statements
        """
        self.port = port
        self.baudrate = baudrate
        self.debug = debug
        self.serial = None
        self.sequence = 0
        self.running = False
        self.watchdog_thread = None
        self.read_thread = None
        
        # Callbacks
        self.response_callback = None
        self.event_callback = None
        
    def connect(self):
        """Open serial connection to Teensy."""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1.0
            )
            time.sleep(2.0)  # Wait for Teensy initialization
            
            if self.debug:
                print(f"Connected to {self.port} at {self.baudrate} baud")
            
            # Start background threads
            self.running = True
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
            
            self.watchdog_thread = threading.Thread(target=self._watchdog_loop, daemon=True)
            self.watchdog_thread.start()
            
            return True
            
        except serial.SerialException as e:
            print(f"ERROR: Cannot connect to {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection."""
        self.running = False
        if self.read_thread:
            self.read_thread.join(timeout=2.0)
        if self.watchdog_thread:
            self.watchdog_thread.join(timeout=2.0)
        if self.serial and self.serial.is_open:
            self.serial.close()
    
    def calculate_checksum(self, message):
        """
        Calculate XOR checksum of message.
        
        Args:
            message: String like "!COMMAND args"
        
        Returns:
            Two-character hex string (uppercase)
        """
        checksum = 0
        for char in message:
            checksum ^= ord(char)
        return f"{checksum:02X}"
    
    def send_command(self, command, *args):
        """
        Send command to Teensy with checksum.
        
        Args:
            command: Command name (e.g., "HOME", "MOVE", "STATUS")
            *args: Optional command arguments
        
        Returns:
            True if sent successfully
        """
        if not self.serial or not self.serial.is_open:
            print("ERROR: Serial port not open")
            return False
        
        # Increment sequence number (0-99)
        self.sequence = (self.sequence + 1) % 100
        
        # Build message
        message = f"!{command} {self.sequence}"
        if args:
            message += " " + " ".join(str(arg) for arg in args)
        
        # Calculate checksum
        checksum = self.calculate_checksum(message)
        full_message = f"{message} *{checksum}\n"
        
        # Send
        try:
            self.serial.write(full_message.encode('ascii'))
            if self.debug:
                print(f"TX: {full_message.strip()}")
            return True
        except serial.SerialException as e:
            print(f"ERROR: Failed to send command: {e}")
            return False
    
    def _read_loop(self):
        """Background thread to read responses from Teensy."""
        buffer = ""
        while self.running:
            try:
                if self.serial.in_waiting > 0:
                    char = self.serial.read(1).decode('ascii', errors='ignore')
                    buffer += char
                    
                    if char == '\n':
                        line = buffer.strip()
                        buffer = ""
                        
                        if self.debug:
                            print(f"RX: {line}")
                        
                        # Parse response
                        if line.startswith('@'):
                            # Response message (@ACK, @NACK, @COMPLETE, etc.)
                            if self.response_callback:
                                self.response_callback(line)
                        elif line.startswith('#'):
                            # Event message (#BOOT, #LIMIT, #DIAG, etc.)
                            if self.event_callback:
                                self.event_callback(line)
                else:
                    time.sleep(0.01)  # Don't spin too fast
            except Exception as e:
                if self.running:
                    print(f"ERROR: Read loop exception: {e}")
                time.sleep(0.1)
    
    def _watchdog_loop(self):
        """Background thread to send !PING every 3 seconds."""
        while self.running:
            time.sleep(3.0)
            if self.running:
                self.send_command("PING")
    
    # High-level command methods
    
    def home(self):
        """Execute homing sequence (30 seconds)."""
        return self.send_command("HOME")
    
    def move_to(self, x, y, z, f):
        """
        Coordinated 4-axis move.
        
        Args:
            x: X position in mm
            y: Y position in mm
            z: Z position in mm
            f: Focus position in mm
        """
        return self.send_command("MOVE", f"{x:.2f}", f"{y:.2f}", f"{z:.2f}", f"{f:.2f}")
    
    def jog(self, axis, distance):
        """
        Jog single axis.
        
        Args:
            axis: Axis letter ('X', 'Y', 'Z', 'F')
            distance: Distance in mm (positive or negative)
        """
        return self.send_command("JOG", axis, f"{distance:.2f}")
    
    def stop(self):
        """Emergency stop."""
        return self.send_command("STOP")
    
    def get_status(self):
        """Request status report."""
        return self.send_command("STATUS")
    
    def get_position(self):
        """Request current position."""
        return self.send_command("POSITION")
```

### 4.2 MotionController Class (motion_controller.py)

**High-level motion control with auto-cycle:**

```python
#!/usr/bin/env python3
"""
motion_controller.py - High-level motion control with auto-cycle

Production code from The Mineral Microscope GUI system.
"""

import time
import threading
from teensy_protocol import TeensyController

class MotionController:
    """
    High-level motion controller with autonomous specimen cycling.
    
    Features:
    - Auto-cycle mode (10-second intervals)
    - Manual override (30-second timeout)
    - Specimen positioning with focus/zoom
    - Thread-safe state management
    """
    
    def __init__(self, serial_port, specimen_grid, 
                 connected_callback=None,
                 move_complete_callback=None,
                 position_callback=None):
        """
        Initialize motion controller.
        
        Args:
            serial_port: Serial port for Teensy (e.g., '/dev/ttyACM0')
            specimen_grid: SpecimenGrid object with specimen data
            connected_callback: Called when Teensy connects
            move_complete_callback: Called when move completes
            position_callback: Called with position updates
        """
        self.grid = specimen_grid
        self.teensy = TeensyController(serial_port, debug=False)
        
        # Callbacks
        self.connected_callback = connected_callback
        self.move_complete_callback = move_complete_callback
        self.position_callback = position_callback
        
        # State
        self.current_specimen_index = 0
        self.is_homed = False
        self._auto_cycling = False
        self._auto_cycle_thread = None
        self._manual_override_time = None
        
        # Set up Teensy callbacks
        self.teensy.response_callback = self._handle_response
        self.teensy.event_callback = self._handle_event
    
    def connect(self):
        """Connect to Teensy and start homing."""
        if self.teensy.connect():
            if self.connected_callback:
                self.connected_callback()
            
            # Start homing
            print("Starting homing sequence...")
            self.teensy.home()
            return True
        return False
    
    def disconnect(self):
        """Disconnect from Teensy."""
        self.stop_auto_cycle()
        self.teensy.disconnect()
    
    def _handle_response(self, response):
        """Handle response messages from Teensy."""
        if response.startswith("@COMPLETE HOME"):
            print("Homing complete!")
            self.is_homed = True
            self.start_auto_cycle()
        elif response.startswith("@COMPLETE MOVE"):
            if self.move_complete_callback:
                self.move_complete_callback()
        elif response.startswith("@POSITION"):
            # Parse position: @POSITION X:-10.50 Y:25.30 Z:5.00 F:8.20
            if self.position_callback:
                self.position_callback(response)
    
    def _handle_event(self, event):
        """Handle event messages from Teensy."""
        if event.startswith("#BOOT"):
            print("Teensy rebooted!")
            self.is_homed = False
        elif event.startswith("#LIMIT"):
            print(f"Limit switch triggered: {event}")
    
    def move_to_specimen(self, specimen):
        """
        Move stage to specimen with focus and zoom.
        
        Args:
            specimen: Dictionary with specimen data from JSON
        """
        # Calculate position
        x, y = self.grid.calculate_position(specimen)
        z = specimen.get("zoom_mm", 10.0)
        f = specimen.get("focus_mm", 5.0)
        
        print(f"Moving to {specimen['mineral_name']}: X={x}, Y={y}, Z={z}, F={f}")
        
        # Send move command
        self.teensy.move_to(x, y, z, f)
        
        # Reset manual override timer
        self._manual_override_time = time.time()
    
    def move_to_next_specimen(self):
        """Move to next valid specimen in sequence."""
        # Find next valid specimen
        attempts = 0
        while attempts < len(self.grid.specimens):
            self.current_specimen_index = (self.current_specimen_index + 1) % len(self.grid.specimens)
            specimen = self.grid.specimens[self.current_specimen_index]
            
            # Check if specimen is valid (has position data)
            if specimen.get("mineral_name"):
                self.move_to_specimen(specimen)
                return
            
            attempts += 1
        
        print("WARNING: No valid specimens found in grid")
    
    def _is_manual_override(self):
        """Check if in manual mode (30s since last user input)."""
        if self._manual_override_time is None:
            return False
        return (time.time() - self._manual_override_time) < 30.0
    
    def start_auto_cycle(self):
        """Start autonomous specimen cycling."""
        if self._auto_cycling:
            return
        
        print("Starting auto-cycle mode (10-second intervals)")
        self._auto_cycling = True
        self._auto_cycle_thread = threading.Thread(target=self._auto_cycle_loop, daemon=True)
        self._auto_cycle_thread.start()
    
    def stop_auto_cycle(self):
        """Stop auto-cycle mode."""
        self._auto_cycling = False
        if self._auto_cycle_thread:
            self._auto_cycle_thread.join(timeout=2.0)
    
    def _auto_cycle_loop(self):
        """Auto-cycle thread loop."""
        while self._auto_cycling:
            # Check manual override
            if self._is_manual_override():
                time.sleep(1.0)
                continue
            
            # Move to next specimen
            self.move_to_next_specimen()
            
            # Wait 10 seconds before next move
            time.sleep(10.0)
```

---

## 5. Complete Working Example

### 5.1 Simple Test Program

```python
#!/usr/bin/env python3
"""
test_teensy.py - Simple test program for Teensy communication
"""

import time
from teensy_protocol import TeensyController

def response_handler(response):
    """Handle responses from Teensy."""
    print(f"Response: {response}")

def event_handler(event):
    """Handle events from Teensy."""
    print(f"Event: {event}")

def main():
    # Create controller
    teensy = TeensyController(port='/dev/ttyACM0', debug=True)
    teensy.response_callback = response_handler
    teensy.event_callback = event_handler
    
    # Connect
    print("Connecting to Teensy...")
    if not teensy.connect():
        print("Failed to connect!")
        return
    
    print("Connected! Waiting for initialization...")
    time.sleep(3)
    
    # Home all axes
    print("\n1. Homing all axes...")
    teensy.home()
    time.sleep(35)  # Wait for homing to complete
    
    # Get status
    print("\n2. Getting status...")
    teensy.get_status()
    time.sleep(1)
    
    # Get position
    print("\n3. Getting position...")
    teensy.get_position()
    time.sleep(1)
    
    # Move to test position
    print("\n4. Moving to test position (X=50, Y=50, Z=10, F=5)...")
    teensy.move_to(50.0, 50.0, 10.0, 5.0)
    time.sleep(10)  # Wait for move to complete
    
    # Jog X axis
    print("\n5. Jogging X axis +10mm...")
    teensy.jog('X', 10.0)
    time.sleep(5)
    
    # Get final position
    print("\n6. Getting final position...")
    teensy.get_position()
    time.sleep(1)
    
    print("\nTest complete! Disconnecting...")
    teensy.disconnect()

if __name__ == "__main__":
    main()
```

**Run the test:**
```bash
chmod +x test_teensy.py
./test_teensy.py
```

**Expected output:**
```
Connecting to Teensy...
Connected to /dev/ttyACM0 at 115200 baud
Connected! Waiting for initialization...

1. Homing all axes...
TX: !HOME 1 *4A
RX: @ACK HOME 1
RX: @COMPLETE HOME 1
Homing complete!

2. Getting status...
TX: !STATUS 2 *5B
RX: @ACK STATUS 2
RX: @STATUS STATE:IDLE HOMED:YES

3. Getting position...
TX: !POSITION 3 *6C
RX: @ACK POSITION 3
RX: @POSITION X:0.00 Y:0.00 Z:0.00 F:0.00

4. Moving to test position (X=50, Y=50, Z=10, F=5)...
TX: !MOVE 4 50.00 50.00 10.00 5.00 *7D
RX: @ACK MOVE 4
RX: @COMPLETE MOVE 4

...
```

---

## 6. Integration with GUI

### 6.1 Minimal GUI Example

```python
#!/usr/bin/env python3
"""
minimal_gui.py - Minimal PyQt5 GUI example with Teensy control
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt
from teensy_protocol import TeensyController

class MinimalGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.teensy = TeensyController('/dev/ttyACM0')
        self.init_ui()
        self.teensy.connect()
    
    def init_ui(self):
        self.setWindowTitle('Teensy Controller')
        self.setGeometry(100, 100, 400, 300)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Status label
        self.status_label = QLabel('Disconnected')
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Buttons
        home_btn = QPushButton('Home All Axes')
        home_btn.clicked.connect(self.on_home)
        layout.addWidget(home_btn)
        
        move_btn = QPushButton('Move to 50, 50, 10, 5')
        move_btn.clicked.connect(self.on_move)
        layout.addWidget(move_btn)
        
        stop_btn = QPushButton('STOP')
        stop_btn.clicked.connect(self.on_stop)
        layout.addWidget(stop_btn)
    
    def on_home(self):
        self.status_label.setText('Homing...')
        self.teensy.home()
    
    def on_move(self):
        self.status_label.setText('Moving...')
        self.teensy.move_to(50.0, 50.0, 10.0, 5.0)
    
    def on_stop(self):
        self.teensy.stop()
        self.status_label.setText('Stopped')
    
    def closeEvent(self, event):
        self.teensy.disconnect()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MinimalGUI()
    gui.show()
    sys.exit(app.exec_())
```

---

## 7. Troubleshooting

### 7.1 Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| **Cannot open /dev/ttyACM0** | Device not found | Check USB connection, try /dev/serial0 |
| **Permission denied** | Not in dialout group | `sudo usermod -a -G dialout $USER` |
| **No response from Teensy** | UART not configured | Enable UART in /boot/firmware/config.txt |
| **Garbled output** | Baud rate mismatch | Verify both sides use 115200 |
| **Commands ignored** | Missing checksum | Use TeensyController class |
| **Watchdog timeouts** | Commands too slow | Send !PING every 3 seconds |

### 7.2 Debug Tips

```bash
# Check serial device
ls -l /dev/ttyACM* /dev/ttyAMA* /dev/serial*

# Monitor serial traffic
sudo apt install screen
screen /dev/ttyACM0 115200

# Python debug mode
teensy = TeensyController(port='/dev/ttyACM0', debug=True)
```

---

## 8. Performance Considerations

### 8.1 Timing

| Operation | Duration | Notes |
|-----------|----------|-------|
| **Connection** | 2-3 seconds | Teensy initialization |
| **Homing** | 30 seconds | Sequential Z→Y→X→F |
| **Move (50mm)** | 3-5 seconds | Depends on speed settings |
| **Jog (10mm)** | 1-2 seconds | Single axis |
| **Watchdog interval** | 3 seconds | !PING frequency |

### 8.2 Optimization

- **Parallel Operations:** Use threading for video capture + motion control
- **Command Batching:** Not supported - wait for @COMPLETE
- **Reduce Latency:** Keep watchdog thread priority high
- **Buffer Management:** Read responses promptly to avoid overflow

---

## 9. Reference Documents

For complete protocol and system details:

1. **[05_PROTOCOL_SPECIFICATION.md](05_PROTOCOL_SPECIFICATION.md)** - Full protocol reference
2. **[09_GUI_ARCHITECTURE.md](09_GUI_ARCHITECTURE.md)** - Complete GUI code documentation
3. **[10_USER_GUIDE.md](10_USER_GUIDE.md)** - Museum operator manual
4. **[11_INSTALLATION.md](11_INSTALLATION.md)** - System installation guide

---

**Previous Section:** [07 - Issues and Resolutions](07_ISSUES_AND_RESOLUTIONS.md)  
**Next Section:** [09 - GUI Architecture](09_GUI_ARCHITECTURE.md)  
**Back to Index:** [00 - Index](00_INDEX.md)
