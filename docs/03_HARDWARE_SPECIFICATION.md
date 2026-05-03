# Hardware Specification

**Document:** 03 - Hardware Specification  
**Version:** 1.2  
**Date:** December 23, 2025

---

## 1. Component List

### 1.1 Electronics

| Component | Part Number / Spec | Quantity | Notes |
|-----------|-------------------|----------|-------|
| **Microcontroller** | Teensy 4.1 | 1 | i.MX RT1062 (600MHz ARM Cortex-M7) |
| **Master Computer** | Raspberry Pi 4 | 1 | 2GB+ RAM recommended |
| **Motor Drivers** | TB6600 | 4 | 1/16 microstepping, 4A peak |
| **Stepper Motors** | NEMA17 (200 steps/rev) | 4 | Bipolar, 1.5-2A rated |
| **Limit Switches** | Mechanical NO switches | 8 | 3-pin: COM, NO, NC |
| **Power Supply** | 12-24V DC, 5A+ | 1 | For motor drivers |
| **USB Cable** | Micro-USB | 1 | For Teensy programming/debug |
| **UART Cable** | 3-wire (TX, RX, GND) | 1 | Teensy ↔ RPi4 connection |

### 1.2 Mechanical

| Component | Specification | Quantity | Notes |
|-----------|--------------|----------|-------|
| **CNC Frame** | 3018 CNC | 1 | Modified for microscopy |
| **Lead Screws** | T8 (8mm pitch) | 3 | X, Y, Z axes |
| **Linear Rails** | As per 3018 | - | Stock configuration |
| **Microscope Mount** | Custom | 1 | Focus mechanism |

---

## 2. Teensy 4.1 Pinout

### 2.1 Pin Assignments

#### UART Communication
| Function | Pin | Direction | Signal | Description |
|----------|-----|-----------|--------|-------------|
| RX | 0 | Input | Serial1 RX | Receives commands from RPi4 |
| TX | 1 | Output | Serial1 TX | Sends responses to RPi4 |

#### Common Motor Enable
| Function | Pin | Direction | Signal | Description |
|----------|-----|-----------|--------|-------------|
| ENA_ALL | 33 | Output | Active LOW | Enables all 4 TB6600 drivers |

#### X Axis (Gantry Left-Right)
| Function | Pin | Direction | Signal | Description |
|----------|-----|-----------|--------|-------------|
| X_STEP | 2 | Output | Rising edge | Step pulse to driver |
| X_DIR | 3 | Output | HIGH/LOW | Direction control |
| X_MIN | 4 | Input | Active LOW | Min limit switch (left) |
| X_MAX | 5 | Input | Active LOW | Max limit switch (right) |

#### Y Axis (Table Forward-Back)
| Function | Pin | Direction | Signal | Description |
|----------|-----|-----------|--------|-------------|
| Y_STEP | 6 | Output | Rising edge | Step pulse to driver |
| Y_DIR | 7 | Output | HIGH/LOW | Direction control |
| Y_MIN | 8 | Input | Active LOW | Min limit switch (back) |
| Y_MAX | 9 | Input | Active LOW | Max limit switch (front) |

#### Z Axis (Vertical Up-Down)
| Function | Pin | Direction | Signal | Description |
|----------|-----|-----------|--------|-------------|
| Z_STEP | 10 | Output | Rising edge | Step pulse to driver |
| Z_DIR | 11 | Output | HIGH/LOW | Direction control |
| Z_MIN | 12 | Input | Active LOW | Min limit switch (down) |
| Z_MAX | 14 | Input | Active LOW | Max limit switch (up) |

**Note:** Pin 13 skipped (onboard LED)

#### Focus Axis (Microscope Focus)
| Function | Pin | Direction | Signal | Description |
|----------|-----|-----------|--------|-------------|
| F_STEP | 15 | Output | Rising edge | Step pulse to driver |
| F_DIR | 16 | Output | HIGH/LOW | Direction control |
| F_MIN | 22 | Input | Active LOW | Min limit switch |
| F_MAX | 18 | Input | Active LOW | Max limit switch |

### 2.2 Pin Summary Table

```
┌────────────┬──────────────┬───────────┬──────────┐
│  Function  │     Pin      │   Type    │  Signal  │
├────────────┼──────────────┼───────────┼──────────┤
│ Serial1 RX │      0       │   Input   │  UART    │
│ Serial1 TX │      1       │   Output  │  UART    │
│ X_STEP     │      2       │   Output  │  Pulse   │
│ X_DIR      │      3       │   Output  │  Logic   │
│ X_MIN      │      4       │   Input   │  Switch  │
│ X_MAX      │      5       │   Input   │  Switch  │
│ Y_STEP     │      6       │   Output  │  Pulse   │
│ Y_DIR      │      7       │   Output  │  Logic   │
│ Y_MIN      │      8       │   Input   │  Switch  │
│ Y_MAX      │      9       │   Input   │  Switch  │
│ Z_STEP     │     10       │   Output  │  Pulse   │
│ Z_DIR      │     11       │   Output  │  Logic   │
│ Z_MIN      │     12       │   Input   │  Switch  │
│ [LED]      │     13       │  (unused) │  Onboard │
│ Z_MAX      │     14       │   Input   │  Switch  │
│ F_STEP     │     15       │   Output  │  Pulse   │
│ F_DIR      │     16       │   Output  │  Logic   │
│ F_MAX      │     18       │   Input   │  Switch  │
│ F_MIN      │     22       │   Input   │  Switch  │
│ ENA_ALL    │     33       │   Output  │  Active L│
└────────────┴──────────────┴───────────┴──────────┘
```

---

## 3. TB6600 Stepper Driver Wiring

### 3.1 Driver Configuration

Each TB6600 driver has the following connections:

#### Power Connections
| Terminal | Connection | Voltage | Notes |
|----------|------------|---------|-------|
| **VCC** | +12-24V DC | 12-24V | Motor power supply |
| **GND** | Power supply GND | 0V | Common ground |

#### Motor Connections (to NEMA17)
| Terminal | Connection | Notes |
|----------|------------|-------|
| **A+** | Motor coil A, wire 1 | Red or Black |
| **A-** | Motor coil A, wire 2 | Green or Red |
| **B+** | Motor coil B, wire 1 | Blue or Yellow |
| **B-** | Motor coil B, wire 2 | White or Green |

**Note:** Motor wire colors vary by manufacturer. Use multimeter to identify coil pairs (A-A and B-B).

#### Control Connections (from Teensy)

Each driver connects to Teensy as follows:

| TB6600 Terminal | Teensy Pin | Signal Type | Notes |
|-----------------|------------|-------------|-------|
| **PUL+** | STEP pin (2, 6, 10, or 15) | 3.3V output | Step pulse input |
| **PUL-** | GND | Ground | Pulse reference |
| **DIR+** | DIR pin (3, 7, 11, or 16) | 3.3V output | Direction input |
| **DIR-** | GND | Ground | Direction reference |
| **ENA+** | Pin 33 (shared) | 3.3V output | Enable input (active LOW) |
| **ENA-** | GND | Ground | Enable reference |

### 3.2 Critical Enable Logic (Active LOW)

**IMPORTANT:** TB6600 enable logic is **INVERTED**:
- **ENA LOW (0V) = Driver ENABLED** (motor holding torque)
- **ENA HIGH (3.3V) = Driver DISABLED** (motor freewheeling)

This is opposite of what some datasheets show. Verified empirically.

Firmware implementation:
```c++
void enableMotors() {
  digitalWrite(ENA_ALL_PIN, LOW);  // Active LOW enables drivers
}

void disableMotors() {
  digitalWrite(ENA_ALL_PIN, HIGH); // HIGH disables drivers
}
```

### 3.3 TB6600 DIP Switch Settings

Each driver has DIP switches for current and microstepping:

**Current Setting:**
- Set to **1.0A** for NEMA17 motors (DIP switches SW1-3 per TB6600 datasheet)
- Provides adequate torque while reducing power consumption
- Total system power: ~112W (well within 120W supply capacity)

**Microstepping:** Set to **1/16** (SW5-8)
| SW5 | SW6 | SW7 | SW8 | Microsteps |
|-----|-----|-----|-----|------------|
| ON  | ON  | ON  | ON  | 1/16       |

**Verified Configuration:**
- STEPS_PER_MM = 400 is calibrated for 1/16 microstepping
- Changing microstepping requires recalibrating STEPS_PER_MM

### 3.4 Signal Timing

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Pulse Width** | 10µs | Teensy generates 10µs HIGH pulse |
| **TB6600 Minimum** | 2.5µs | Driver datasheet requirement |
| **Step on:** | Rising edge | Transition from LOW→HIGH |
| **Max Step Rate** | 6000 Hz | Current firmware limit (can go higher) |

---

## 4. Limit Switch Wiring

### 4.1 Switch Type

**Specification:** Mechanical Normally-Open (NO) switches

Each switch has 3 terminals:
- **COM** (Common)
- **NO** (Normally Open)
- **NC** (Normally Closed) - **Not used**

### 4.2 Wiring Diagram

```
Teensy Pin (INPUT_PULLUP)
    │
    ├── 3.3V (internal pull-up resistor)
    │
    │   [Switch not pressed]
    │   Pin reads HIGH (3.3V)
    │
    ○  ← Switch NO terminal
    │
    ○  ← Switch COM terminal
    │
   GND

When switch pressed:
    NO terminal connects to COM → Pin pulled to GND → Pin reads LOW
```

### 4.3 Connection Table

| Axis | Limit | Teensy Pin | Switch Terminal 1 | Switch Terminal 2 |
|------|-------|------------|-------------------|-------------------|
| X | MIN | 4 | Pin 4 | GND |
| X | MAX | 5 | Pin 5 | GND |
| Y | MIN | 8 | Pin 8 | GND |
| Y | MAX | 9 | Pin 9 | GND |
| Z | MIN | 12 | Pin 12 | GND |
| Z | MAX | 14 | Pin 14 | GND |
| F | MIN | 22 | Pin 22 | GND |
| F | MAX | 18 | Pin 18 | GND |

**Wiring Instructions:**
1. Connect one switch terminal to the Teensy pin
2. Connect the other switch terminal to any GND pin on Teensy
3. Polarity doesn't matter (switch just shorts pin to GND)
4. No external resistors needed (internal pull-ups enabled)

### 4.4 Interrupt Configuration

All 8 limit switches use interrupts:

```c++
pinMode(X_MIN_PIN, INPUT_PULLUP);
attachInterrupt(digitalPinToInterrupt(X_MIN_PIN), xMinISR, FALLING);
```

- **Mode:** FALLING edge (triggered when pin goes HIGH→LOW)
- **Debounce:** 50ms timestamp-based (in ISR)
- **Noise Rejection:** Triple-read with 200µs delays
- **Hysteresis:** Tracks last pin state, only triggers on HIGH→LOW

---

## 5. Raspberry Pi 4 UART Connection

### 5.1 Physical Connection

**Teensy Side:**
- Pin 0 (RX) - Receives data FROM RPi4
- Pin 1 (TX) - Sends data TO RPi4
- GND - Common ground

**RPi4 Side:**
- GPIO 14 (TX) - Sends data TO Teensy (connects to Teensy RX/pin 0)
- GPIO 15 (RX) - Receives data FROM Teensy (connects to Teensy TX/pin 1)
- GND - Common ground

**Wiring:**
```
Teensy Pin 0 (RX) ←──→ RPi4 GPIO 14 (TX)
Teensy Pin 1 (TX) ←──→ RPi4 GPIO 15 (RX)
Teensy GND       ←──→ RPi4 GND
```

### 5.2 RPi4 UART Configuration

**Device:** `/dev/serial0` (or `/dev/ttyAMA0` on some models)

**Parameters:**
- Baud Rate: 115200
- Data Bits: 8
- Parity: None
- Stop Bits: 1
- Flow Control: None

**Enable UART on RPi4:**
```bash
# Edit /boot/config.txt
enable_uart=1
dtoverlay=disable-bt  # Disables Bluetooth to free up UART

# Reboot
sudo reboot
```

**Test Connection:**
```bash
# Install screen
sudo apt install screen

# Connect to UART
screen /dev/serial0 115200

# Should see Teensy boot message and can send commands
```

---

## 6. Signal Levels and Logic

### 6.1 Voltage Levels

| Signal | Logic HIGH | Logic LOW | Notes |
|--------|------------|-----------|-------|
| **Teensy Outputs** | 3.3V | 0V | All GPIO pins |
| **TB6600 Inputs** | 3.3V - 5V | 0V | 3.3V compatible (verified) |
| **Limit Switches** | 3.3V (pulled up) | 0V (when closed) | Internal pull-up |

**CRITICAL:** Teensy 4.1 is **NOT 5V tolerant**
- Do NOT connect 5V signals to Teensy pins
- Limit switches pull to GND (safe)
- TB6600 outputs not used (safe)
- RPi4 GPIO is 3.3V (safe)

### 6.2 Current Consumption

| Component | Typical | Peak | Notes |
|-----------|---------|------|-------|
| **Teensy 4.1** | 100mA | 150mA | USB powered |
| **TB6600 Logic** | 10mA each | - | Powered from motor supply |
| **Motors (each)** | 1.5A | 2.0A | From motor power supply |
| **Total Motor Current** | 6A | 8A | 4 motors @ 2A peak |

**Power Supply Sizing:**
- Motor Supply: 12-24V DC, minimum 8A (10A recommended)
- Teensy: USB 5V, 500mA available
- RPi4: Separate 5V 3A supply

---

## 7. Cable Specifications

### 7.1 Motor Cables
- **Type:** 4-conductor shielded cable (if available)
- **Length:** Keep < 2 meters to minimize noise
- **Gauge:** 22-18 AWG
- **Shielding:** Connect to GND at one end only

### 7.2 Limit Switch Cables
- **Type:** 2-conductor cable
- **Length:** Several feet (3-6ft typical)
- **Gauge:** 24-22 AWG
- **Note:** Long cables caused noise issues, resolved via:
  - Software triple-read verification
  - Pin state hysteresis
  - 50ms debouncing

### 7.3 UART Cable (Teensy ↔ RPi4)
- **Type:** 3-conductor (TX, RX, GND)
- **Length:** < 1 meter recommended
- **Gauge:** 26-24 AWG
- **Shielding:** Not required (3.3V logic, short run)

---

## 8. Physical Layout Recommendations

### 8.1 Component Placement
1. **Teensy:** Mount near stepper drivers
2. **TB6600 Drivers:** Mount on DIN rail or insulated surface
3. **Power Supply:** Separate from logic components
4. **RPi4:** Can be remote (UART cable up to ~1m)

### 8.2 Grounding
- **Single-point ground:** All GND connections meet at power supply
- **Motor power GND** and **Teensy GND** must be connected
- **Avoid ground loops:** Don't create multiple ground paths

### 8.3 Noise Mitigation
- Keep motor power cables away from signal cables
- Twist motor cable pairs (A+/A- and B+/B-)
- Use shielded cables if noise is an issue
- Add ferrite beads on motor cables if EMI is problematic

---

## 9. Mechanical Specifications

### 9.1 Travel Ranges (Measured on 3018 CNC)

| Axis | Min | Max | Travel | Mechanical Limit |
|------|-----|-----|--------|------------------|
| **X** | 0mm | 270mm | 270mm | MIN at 0, MAX at 270 |
| **Y** | 0mm | 150mm | 150mm | MIN at 0, MAX at 150 |
| **Z** | 0mm | 30mm | 30mm | MIN at 0, MAX at 30 |
| **Focus** | 0mm | 30mm | 30mm | Soft limits disabled |

### 9.2 Resolution

**Calculation:**
- Motor: 200 steps/rev (1.8° per step)
- Microstepping: 1/16
- Lead Screw: 8mm pitch (T8)

**Steps per revolution:** 200 × 16 = 3200 steps/rev  
**Linear motion per rev:** 8mm  
**Steps per mm:** 3200 / 8 = 400 steps/mm  
**Resolution:** 1 / 400 = 0.0025mm = 2.5µm

### 9.3 Speed Limits

**Current Settings:**
- **Max Speed:** 6000 steps/sec = 15 mm/sec = 900 mm/min
- **Homing Speed:** 3000 steps/sec = 7.5 mm/sec
- **Creep Speed:** 400 steps/sec = 1 mm/sec

**Mechanical Limits:**
- TB6600 supports up to ~20 kHz (20,000 steps/sec)
- Lead screws and mechanics limit practical speed
- Current settings are conservative and proven

---

## 10. Safety Considerations

### 10.1 Electrical Safety
- **Motor power:** 12-24V DC is low voltage, but high current
- **Short circuit protection:** Use fused power supply
- **Polarity:** Double-check motor power polarity before applying
- **Teensy protection:** Never apply > 3.3V to GPIO pins

### 10.2 Mechanical Safety
- **Homing direction:** Ensure MIN limits are in safe direction
- **Soft limits:** Software enforces travel boundaries
- **Emergency stop:** Accessible via !STOP command or diagnostic 'S' key
- **Limit switches:** Hardware protection against over-travel

### 10.3 Operational Safety
- **Always home before moving:** Firmware enforces this
- **Watch first homing:** Ensure axes move toward MIN limits
- **Test at low speed:** Use diagnostic mode before full-speed operation
- **Monitor for unusual sounds:** Grinding indicates mechanical issue

---

## 12. GUI Hardware Components

### 12.1 Raspberry Pi 4 Specifications

| Component | Specification | Notes |
|-----------|--------------|-------|
| **Model** | Raspberry Pi 4 Model B | 2GB RAM minimum, 4GB recommended |
| **CPU** | Broadcom BCM2711 (quad-core Cortex-A72 @ 1.5GHz) | Runs PyQt5 GUI |
| **RAM** | 2GB / 4GB / 8GB | 2GB sufficient for GUI + video |
| **Storage** | MicroSD card, 16GB minimum | 32GB Class 10 recommended |
| **Power** | 5V 3A USB-C | Official RPi power supply |
| **GPIO** | 40-pin header | UART on pins 14/15 |
| **Video Output** | Micro-HDMI × 2 | Connect display to HDMI0 |
| **USB** | 2× USB 3.0, 2× USB 2.0 | Camera on USB 3.0 |
| **Network** | Gigabit Ethernet, WiFi 5 | For remote access |

### 12.2 USB Microscope Camera

| Specification | Requirement | Recommended |
|--------------|-------------|-------------|
| **Resolution** | 640×480 minimum | 1280×720 or higher |
| **Frame Rate** | 30 FPS | 30 FPS (video_thread.py uses 30) |
| **Interface** | USB 2.0 or 3.0 | USB 3.0 for higher resolution |
| **Sensor** | CMOS | Low-light performance important |
| **Focus** | Manual or motorized | Manual focus acceptable |
| **Light** | Built-in LED ring | Adjustable brightness preferred |
| **Driver** | V4L2 compatible | Most USB cameras work with OpenCV |

**Testing Camera Compatibility:**
```bash
# Check device detection
ls /dev/video*
# Should show: /dev/video0

# Test capture
ffplay /dev/video0
# Should display live video

# Check capabilities
v4l2-ctl --device=/dev/video0 --list-formats-ext
# Verify resolution and frame rate support
```

**Recommended Models:**
- AmScope MU300 (3.0MP, USB 2.0, ~$100)
- Jiusion 40-1000x (2MP, USB 2.0, ~$40)
- Generic USB microscopes with V4L2 support

### 12.3 Touchscreen Display

| Specification | Requirement | Notes |
|--------------|-------------|-------|
| **Resolution** | 1920×1080 | GUI designed for 1920×1080 |
| **Size** | 15-24 inches | Museum kiosk visibility |
| **Touch Technology** | Capacitive | Multi-touch not required |
| **Interface** | HDMI video + USB touch | Standard connections |
| **Brightness** | 250 nits minimum | Museum lighting conditions |
| **Viewing Angle** | 170° horizontal | Public viewing |
| **Power** | 12V DC or built-in PSU | Depends on model |
| **Mounting** | VESA 75 or 100 | Optional for kiosk integration |

**Recommended Models:**
- Waveshare 15.6" 1920×1080 capacitive touch (~$200)
- Elecrow 15.6" IPS HDMI display (~$150)
- Generic 1920×1080 USB touch monitors

**Connection to RPi4:**
```
Display → HDMI → RPi4 micro-HDMI port 0
Touch controller → USB → RPi4 USB port (any)
```

**Testing Touch Functionality:**
```bash
# List input devices
xinput list
# Should show touchscreen device

# Test touch events
xinput test-xi2 --root
# Touch screen, should show events
```

### 12.4 RPi4 GPIO UART Connection

**Raspberry Pi GPIO Pinout (relevant section):**
```
     3.3V  (1) (2)  5V
   GPIO 2  (3) (4)  5V
   GPIO 3  (5) (6)  GND ──────────┐
   GPIO 4  (7) (8)  GPIO 14 (TXD) ├─┐
      GND  (9) (10) GPIO 15 (RXD) ├─┤
                                  │ │
                                  │ │
  To Teensy 4.1:                 │ │
    GPIO 14 (TXD) ────────────────┼─┤─> Teensy Pin 0 (RX1)
    GPIO 15 (RXD) ────────────────┘ ├─> Teensy Pin 1 (TX1)
    GND  ────────────────────────────> Teensy GND
```

**UART Configuration:**
- RPi4 transmits on GPIO 14 (TXD) → Teensy receives on Pin 0 (RX1)
- Teensy transmits on Pin 1 (TX1) → RPi4 receives on GPIO 15 (RXD)
- Both devices use 3.3V logic (compatible, no level shifter needed)
- Baud rate: 115200, 8 data bits, no parity, 1 stop bit (8N1)

**Cable Requirements:**
- 3-wire cable: TX, RX, GND
- Length: < 30cm for reliability
- Twisted pair preferred for noise immunity
- Secure connections (no loose wiring)

### 12.5 Complete Bill of Materials (BOM) - GUI System

| Component | Quantity | Unit Cost | Total | Notes |
|-----------|----------|-----------|-------|-------|
| **Raspberry Pi 4 (4GB)** | 1 | $55 | $55 | With power supply |
| **MicroSD Card (32GB)** | 1 | $10 | $10 | Class 10 |
| **USB Microscope Camera** | 1 | $40-100 | $70 | Mid-range model |
| **15.6" Touch Display** | 1 | $150-200 | $175 | 1920×1080 capacitive |
| **HDMI Cable (micro-HDMI)** | 1 | $10 | $10 | 1-2m length |
| **USB Cables** | 2 | $5 | $10 | Camera + touch |
| **3-Wire UART Cable** | 1 | $5 | $5 | TX, RX, GND |
| **Teensy 4.1** | 1 | $27 | $27 | Already in firmware BOM |
| **Motor System** | 1 | $200 | $200 | See section 1.1 |
| **Mechanical Frame** | 1 | $150 | $150 | Modified 3018 CNC |
| **Miscellaneous** | - | - | $50 | Cables, mounting, etc. |
| **TOTAL** | - | - | **$762** | Complete system |

---

## 11. Troubleshooting Hardware Issues

| Symptom | Likely Cause | Check |
|---------|--------------|-------|
| Motor doesn't move | Enable logic inverted | Verify ENA_ALL LOW enables motors |
| Motor moves wrong direction | DIR inverted in firmware | Check setPinsInverted() settings |
| Limit switch not detected | Wiring or pull-up issue | Measure voltage: HIGH when not pressed |
| False limit triggers | Cable noise | Verify triple-read logic, check cable routing |
| Communication errors | Baud rate mismatch | Verify 115200 on both sides |
| Motor stalls or skips steps | Current too low | Adjust TB6600 current DIP switches |
| Motors whine loudly | Resonance frequency | Try different speed or microstepping |
| Teensy not responding | USB power issue | Check USB cable, try different port |

---

**Next Section:** [04 - Software Specification](04_SOFTWARE_SPECIFICATION.md)
