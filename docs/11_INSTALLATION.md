# Installation Guide

**Document:** 11 - Installation Guide  
**Version:** 1.0  
**Date:** December 23, 2025  
**Audience:** System Administrators, Technicians

---

## 1. Overview

This guide covers complete installation of The Mineral Microscope system from scratch, including:
- Raspberry Pi 4 OS setup
- Python environment and dependencies
- Hardware connections
- Teensy firmware upload
- GUI configuration and autostart
- System testing and validation

**Time Required:** 2-3 hours for complete setup

---

## 2. Hardware Requirements

### Components Checklist

**Electronics:**
- [ ] Raspberry Pi 4 (2GB RAM minimum, 4GB recommended)
- [ ] MicroSD card (16GB minimum, 32GB recommended, Class 10)
- [ ] Teensy 4.1 microcontroller
- [ ] 4× TB6600 stepper motor drivers
- [ ] 4× NEMA17 stepper motors
- [ ] 8× Normally-Open limit switches
- [ ] USB microscope camera (640×480 minimum)
- [ ] 1920×1080 touchscreen display with HDMI
- [ ] 12-24V DC power supply (5A minimum) for motors
- [ ] USB cables: Micro-USB (Teensy), USB-A (camera)
- [ ] 3-wire cable for UART (TX, RX, GND)

**Mechanical:**
- [ ] Modified 3018 CNC frame
- [ ] Specimen tray (7×4 grid)
- [ ] Microscope mount
- [ ] All mounting hardware

**Accessories:**
- [ ] Keyboard (for initial setup)
- [ ] Mouse (for initial setup)
- [ ] Ethernet cable or WiFi credentials

---

## 3. Raspberry Pi 4 Setup

### 3.1 Operating System Installation

**Recommended OS:** Raspberry Pi OS (64-bit) with Desktop

**Installation Steps:**

1. **Download Raspberry Pi Imager:**
   ```bash
   # On your PC:
   https://www.raspberrypi.com/software/
   ```

2. **Flash SD Card:**
   - Insert microSD card into PC
   - Open Raspberry Pi Imager
   - Choose OS: "Raspberry Pi OS (64-bit)" with Desktop
   - Choose Storage: Your microSD card
   - Click Settings (gear icon):
     - Set hostname: `microscope`
     - Enable SSH
     - Set username: `scope` password: [your choice]
     - Configure WiFi (if using)
     - Set locale/timezone
   - Click WRITE

3. **First Boot:**
   - Insert SD card into Raspberry Pi 4
   - Connect HDMI to monitor
   - Connect keyboard and mouse
   - Connect power (will boot automatically)
   - Wait 60-90 seconds for first boot
   - Complete any remaining setup wizards

4. **Update System:**
   ```bash
   sudo apt update
   sudo apt full-upgrade -y
   sudo reboot
   ```

### 3.2 Configure Hardware UART

The Raspberry Pi's GPIO 14/15 UART must be configured for Teensy communication:

1. **Edit boot configuration:**
   ```bash
   sudo nano /boot/firmware/config.txt
   ```

2. **Add these lines at the end:**
   ```
   # Enable hardware UART for Teensy communication
   enable_uart=1
   dtoverlay=disable-bt
   ```

3. **Save and exit** (Ctrl+X, Y, Enter)

4. **Disable serial console:**
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options → Serial Port
   # "Would you like a login shell accessible over serial?" → No
   # "Would you like the serial port hardware to be enabled?" → Yes
   # Finish and reboot
   ```

5. **Verify UART:**
   ```bash
   ls -l /dev/serial0
   # Should show: /dev/serial0 -> ttyAMA0
   ```

### 3.3 Install System Dependencies

```bash
# Python 3 and pip
sudo apt install -y python3-pip python3-venv

# PyQt5 and dependencies
sudo apt install -y python3-pyqt5 python3-pyqt5.qtmultimedia

# OpenCV dependencies
sudo apt install -y python3-opencv

# Serial communication
sudo apt install -y python3-serial

# Development tools
sudo apt install -y git vim

# Add user to dialout group for serial access
sudo usermod -a -G dialout scope

# Log out and back in for group change to take effect
```

### 3.4 Install Python Packages

```bash
# Create virtual environment (optional but recommended)
cd ~
python3 -m venv microscope_env
source microscope_env/bin/activate

# Install Python packages
pip3 install --upgrade pip
pip3 install pyserial
pip3 install PyQt5
pip3 install opencv-python

# Verify installations
python3 -c "import serial; print('pyserial OK')"
python3 -c "import PyQt5; print('PyQt5 OK')"
python3 -c "import cv2; print('OpenCV OK')"
```

---

## 4. Software Installation

### 4.1 Clone Repository

```bash
cd ~
git clone [your-repository-url] scope
cd scope
```

**Or if transferring via USB drive:**
```bash
# Mount USB drive
sudo mount /dev/sda1 /mnt
cp -r /mnt/scope ~
cd ~/scope
```

### 4.2 Verify File Structure

```bash
ls -l
# Should show:
# scope_gui.py
# motion_controller.py
# video_thread.py
# teensy_protocol.py
# specimen_grid.py
# cli_menu.py
# mindatnh_tray1.json
# docs/
```

### 4.3 Configure Serial Port

Edit `teensy_protocol.py` to verify serial port:

```bash
nano teensy_protocol.py
```

Look for this line (around line 45):
```python
self.serial = serial.Serial('/dev/ttyACM0', 115200, timeout=1.0)
```

**Note:** Port may be `/dev/ttyACM0` or `/dev/ttyUSB0` depending on Teensy connection.

To find correct port:
```bash
# Without Teensy connected:
ls /dev/tty*

# Connect Teensy
ls /dev/tty*

# New device is your Teensy (usually /dev/ttyACM0)
```

---

## 5. Teensy Firmware Upload

### 5.1 Install PlatformIO (on Development PC)

The Teensy firmware must be compiled and uploaded from a development PC (Windows/Mac/Linux).

**On your development PC:**

1. **Install Visual Studio Code:**
   ```
   https://code.visualstudio.com/
   ```

2. **Install PlatformIO Extension:**
   - Open VS Code
   - Extensions (Ctrl+Shift+X)
   - Search "PlatformIO IDE"
   - Install
   - Restart VS Code

3. **Install Teensy Udev Rules (Linux only):**
   ```bash
   wget https://www.pjrc.com/teensy/00-teensy.rules
   sudo cp 00-teensy.rules /etc/udev/rules.d/
   sudo udevadm control --reload-rules
   ```

### 5.2 Open and Build Firmware

1. **Open Project:**
   - File → Open Folder
   - Navigate to `teensy_firmware/`
   - PlatformIO will detect `platformio.ini`

2. **Build:**
   - Click checkmark (✓) in bottom toolbar
   - Or Terminal: `platformio run`
   - Verify "SUCCESS"

3. **Upload to Teensy:**
   - Connect Teensy 4.1 via USB
   - Click arrow (→) in bottom toolbar
   - Or Terminal: `platformio run --target upload`
   - Teensy Loader will open automatically
   - Press button on Teensy if prompted
   - Verify "Upload complete"

4. **Test Firmware:**
   - Open serial monitor (plug icon) at 115200 baud
   - Should see:
     ```
     *** SYSTEM BOOT ***
     Firmware: v1.2
     Initializing motors...
     Limit switches: configured
     Serial ready
     *** DIAGNOSTIC BOOT MENU ***
     ```

---

## 6. Hardware Connections

### 6.1 Teensy ↔ Raspberry Pi UART

**Connection:**
```
Teensy Pin 0 (RX) ───────> RPi GPIO 14 (TXD)
Teensy Pin 1 (TX) ───────> RPi GPIO 15 (RXD)
Teensy GND       ───────> RPi GND
```

**Wiring Notes:**
- Use 3-wire cable (TX, RX, GND)
- Keep cable < 30cm for reliability
- Both devices use 3.3V logic (compatible)
- Double-check TX→RX and RX→TX crossover

**Raspberry Pi GPIO Pinout:**
```
     3.3V  (1) (2)  5V
   GPIO 2  (3) (4)  5V
   GPIO 3  (5) (6)  GND
   GPIO 4  (7) (8)  GPIO 14 (TXD) ← Connect to Teensy RX
      GND  (9) (10) GPIO 15 (RXD) ← Connect to Teensy TX
```

### 6.2 Teensy ↔ TB6600 Motor Drivers

See [03_HARDWARE_SPECIFICATION.md](03_HARDWARE_SPECIFICATION.md) for complete wiring diagrams.

**Quick Summary:**
- Each axis has dedicated TB6600 driver
- Teensy provides: STEP, DIR, ENA signals
- TB6600 provides: Motor coil drive
- All motors share common ENA pin (Teensy pin 33)

### 6.3 USB Camera

**Connection:**
- Plug USB camera into any Raspberry Pi USB port
- Verify detection:
  ```bash
  ls /dev/video*
  # Should show: /dev/video0
  ```

**Test Camera:**
```bash
ffplay /dev/video0
# Should show live video
# Press Q to quit
```

### 6.4 Touchscreen

**Connection:**
- Connect HDMI cable from RPi to touchscreen
- Connect USB touch controller to RPi USB port
- Power on display

**Test Touch:**
```bash
# Open any GUI application
# Touch screen should move mouse cursor
```

---

## 7. Testing

### 7.1 Test Teensy Communication

```bash
cd ~/scope
python3 cli_menu.py
```

**Expected Output:**
```
Connecting to /dev/ttyACM0...
Connected successfully!
Firmware: v1.2
```

**If connection fails:**
- Check UART wiring (TX/RX crossed?)
- Verify serial port: `ls /dev/ttyACM*`
- Check Teensy power LED
- Try different port in teensy_protocol.py

### 7.2 Test Homing

In CLI menu:
1. Press `1` for HOME
2. Watch motors home sequentially (Z→Y→X→F)
3. Verify completion without hitting limits hard
4. Check final positions all show 0.00mm

### 7.3 Test Movement

In CLI menu:
1. Press `2` for MOVE menu
2. Enter: `1 100 50 10 5` (set target)
3. Press `2` to execute
4. Verify smooth coordinated movement
5. Check arrival at target position

### 7.4 Test GUI

```bash
cd ~/scope
python3 scope_gui.py mindatnh_tray1.json
```

**Expected Behavior:**
- GUI opens fullscreen
- "DISCONNECTED" briefly, then "CONNECTED"
- Homing starts automatically (30 seconds)
- First specimen displays
- Video shows live camera feed
- Touching specimens works
- Jog buttons respond

**Test Checklist:**
- [ ] Video feed is live (not frozen)
- [ ] Touch specimen → stage moves
- [ ] Jog buttons move stage
- [ ] Auto-cycle works (moves every 10 seconds)
- [ ] Manual override works (touching pauses auto)
- [ ] Returns to AUTO after 30 seconds
- [ ] ESC key exits cleanly

---

## 8. Autostart Configuration

### 8.1 Create Systemd Service

Create service file:
```bash
sudo nano /etc/systemd/system/microscope-gui.service
```

Add this content:
```ini
[Unit]
Description=Mineral Microscope Touch Kiosk
After=graphical.target

[Service]
Type=simple
User=scope
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/scope/.Xauthority
WorkingDirectory=/home/scope/scope
ExecStart=/usr/bin/python3 /home/scope/scope/scope_gui.py /home/scope/scope/mindatnh_tray1.json
Restart=always
RestartSec=5

[Install]
WantedBy=graphical.target
```

**Enable service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable microscope-gui.service
```

**Test service:**
```bash
# Start service
sudo systemctl start microscope-gui.service

# Check status
sudo systemctl status microscope-gui.service

# View logs
sudo journalctl -u microscope-gui.service -f
```

### 8.2 Auto-Login Configuration

Configure Raspberry Pi to auto-login:
```bash
sudo raspi-config
# Navigate to: System Options → Boot / Auto Login
# Choose: Desktop Autologin
# Finish and reboot
```

### 8.3 Hide Mouse Cursor (Optional)

For kiosk mode, hide cursor after inactivity:
```bash
sudo apt install -y unclutter
```

Edit autostart:
```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/unclutter.desktop
```

Add:
```ini
[Desktop Entry]
Type=Application
Name=Unclutter
Exec=unclutter -idle 3
```

### 8.4 Disable Screen Blanking

Prevent screen from turning off:
```bash
sudo nano /etc/lightdm/lightdm.conf
```

Find `[Seat:*]` section and add:
```ini
xserver-command=X -s 0 -dpms
```

Also edit:
```bash
nano ~/.config/lxsession/LXDE-pi/autostart
```

Add these lines:
```bash
@xset s off
@xset -dpms
@xset s noblank
```

---

## 9. Production Deployment

### 9.1 Pre-Deployment Checklist

**Hardware:**
- [ ] All motors move smoothly
- [ ] All limit switches trigger correctly
- [ ] Camera produces clear image
- [ ] Touchscreen responds accurately
- [ ] All cables secured and labeled
- [ ] Power supply adequate (no brownouts)

**Software:**
- [ ] GUI starts automatically on boot
- [ ] Auto-cycle works reliably
- [ ] Manual override with 30s timeout verified
- [ ] No segfaults after extended runtime
- [ ] Homing completes successfully every time

**Configuration:**
- [ ] mindatnh_tray1.json has correct specimen data
- [ ] Focus/zoom values set for each specimen
- [ ] Position offsets calibrated
- [ ] Screen resolution matches display (1920×1080)

### 9.2 24-Hour Burn-In Test

**Before deploying to museum:**
1. Run system for 24 hours continuously
2. Monitor for:
   - Memory leaks (check `htop`)
   - Segfaults (check system logs)
   - Motor overheating
   - Consistent auto-cycle timing
3. Verify recovery from power cycle
4. Test several manual interventions per hour

### 9.3 Final Configuration

**Create quick-access shortcuts:**
```bash
# Desktop shortcut to restart GUI
nano ~/Desktop/restart-microscope.sh
```

Add:
```bash
#!/bin/bash
sudo systemctl restart microscope-gui.service
```

Make executable:
```bash
chmod +x ~/Desktop/restart-microscope.sh
```

---

## 10. Maintenance and Updates

### 10.1 Updating Specimen Configuration

To change specimens or adjust positions:

1. **Edit JSON file:**
   ```bash
   nano ~/scope/mindatnh_tray1.json
   ```

2. **Restart GUI:**
   ```bash
   sudo systemctl restart microscope-gui.service
   ```

**JSON Format:**
```json
{
  "specimens": [
    {
      "row": 0,
      "col": 0,
      "mineral_name": "New Mineral Name",
      "location": "New Location",
      "collector": "Collector Name",
      "x_offset_mm": 0.0,
      "y_offset_mm": 0.0,
      "focus_mm": 10.0,
      "zoom_mm": 5.0
    }
  ]
}
```

### 10.2 Updating Software

**Pull latest changes:**
```bash
cd ~/scope
git pull origin main
sudo systemctl restart microscope-gui.service
```

### 10.3 Viewing Logs

**System logs:**
```bash
# GUI logs
sudo journalctl -u microscope-gui.service -f

# System errors
dmesg | tail -50

# Python errors
cat ~/scope/error.txt
```

### 10.4 Backup Configuration

**Create backup:**
```bash
cd ~
tar -czf microscope-backup-$(date +%Y%m%d).tar.gz scope/
```

**Restore from backup:**
```bash
cd ~
tar -xzf microscope-backup-YYYYMMDD.tar.gz
```

---

## 11. Troubleshooting Installation Issues

### Problem: "Cannot connect to /dev/ttyACM0"

**Solutions:**
- Verify Teensy USB connection
- Check user in dialout group: `groups scope`
- Try different port: `ls /dev/tty*`
- Update teensy_protocol.py with correct port

### Problem: "No video device found"

**Solutions:**
- Check camera connection: `ls /dev/video*`
- Test with ffplay: `ffplay /dev/video0`
- Try different USB port
- Check `dmesg` for USB errors

### Problem: GUI won't start automatically

**Solutions:**
- Check service status: `sudo systemctl status microscope-gui.service`
- View logs: `sudo journalctl -u microscope-gui.service`
- Verify DISPLAY variable in service file
- Check file permissions: `ls -l ~/scope/scope_gui.py`

### Problem: Touchscreen not responding

**Solutions:**
- Check USB touch controller connection
- Test with: `xinput list`
- Calibrate touch: `xinput_calibrator`
- Check for conflicting input devices

---

## 12. Performance Optimization

### 12.1 Reduce Boot Time

```bash
# Disable unnecessary services
sudo systemctl disable bluetooth.service
sudo systemctl disable hciuart.service
sudo systemctl disable avahi-daemon.service

# Reduce boot delay
sudo nano /boot/firmware/cmdline.txt
# Add: quiet splash
```

### 12.2 Increase Video Performance

```bash
# Increase GPU memory
sudo nano /boot/firmware/config.txt
```

Add:
```ini
gpu_mem=256
```

### 12.3 Reduce Motor Noise

If TB6600 motor whine is too loud, consider upgrading drivers:

**Option 1: Reduce current (may affect torque):**
- Adjust TB6600 DIP switches to lower current setting
- Test thoroughly to ensure adequate holding torque

**Option 2: Upgrade to TMC2209 drivers:**
- Near-silent operation
- Requires different wiring (see hardware docs)
- ~$8 each (4× = $32 total)

---

## 13. Security Considerations

### 13.1 Kiosk Lockdown

For public deployment:

```bash
# Disable VT switching (Ctrl+Alt+F1-F7)
sudo nano /etc/X11/xorg.conf.d/50-novt.conf
```

Add:
```ini
Section "ServerFlags"
    Option "DontVTSwitch" "true"
EndSection
```

**Disable keyboard shortcuts:**
```bash
nano ~/.config/openbox/lxde-pi-rc.xml
```

Comment out all keyboard shortcuts.

### 13.2 SSH Access

**Enable SSH for remote maintenance:**
```bash
sudo systemctl enable ssh
```

**But disable password login (use keys only):**
```bash
sudo nano /etc/ssh/sshd_config
```

Set:
```ini
PasswordAuthentication no
PermitRootLogin no
```

Generate SSH key pair and copy public key to `~/.ssh/authorized_keys`.

---

## 14. Documentation and Support

### 14.1 Complete Documentation Set

- [00_INDEX.md](00_INDEX.md) - Documentation index
- [01_PRODUCT_OVERVIEW.md](01_PRODUCT_OVERVIEW.md) - System overview
- [02_SYSTEM_ARCHITECTURE.md](02_SYSTEM_ARCHITECTURE.md) - Architecture diagrams
- [03_HARDWARE_SPECIFICATION.md](03_HARDWARE_SPECIFICATION.md) - Hardware details
- [04_SOFTWARE_SPECIFICATION.md](04_SOFTWARE_SPECIFICATION.md) - Firmware code
- [05_PROTOCOL_SPECIFICATION.md](05_PROTOCOL_SPECIFICATION.md) - Communication protocol
- [06_DIAGNOSTIC_PROCEDURES.md](06_DIAGNOSTIC_PROCEDURES.md) - Testing procedures
- [07_ISSUES_AND_RESOLUTIONS.md](07_ISSUES_AND_RESOLUTIONS.md) - Known issues
- [08_RPI4_INTEGRATION.md](08_RPI4_INTEGRATION.md) - Python client examples
- [09_GUI_ARCHITECTURE.md](09_GUI_ARCHITECTURE.md) - GUI code documentation
- [10_USER_GUIDE.md](10_USER_GUIDE.md) - Museum operator manual
- [11_INSTALLATION.md](11_INSTALLATION.md) - This document

### 14.2 Additional Resources

- **GUI_README.md:** Quick start guide for GUI
- **protocol.md:** Detailed protocol specification
- **project_context.md:** Development history

---

## 15. Appendix: Quick Command Reference

```bash
# Start GUI manually
cd ~/scope
python3 scope_gui.py mindatnh_tray1.json

# Start CLI diagnostic tool
python3 cli_menu.py

# Restart GUI service
sudo systemctl restart microscope-gui.service

# View GUI logs
sudo journalctl -u microscope-gui.service -f

# Check serial port
ls -l /dev/serial0

# Test camera
ffplay /dev/video0

# Check Teensy connection
ls /dev/ttyACM*

# Monitor system resources
htop

# Check for errors
dmesg | tail -50
```

---

**Previous Section:** [10 - User Guide](10_USER_GUIDE.md)  
**Back to Index:** [00 - Index](00_INDEX.md)
