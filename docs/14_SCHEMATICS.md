# System Schematics

**Document ID:** 14_SCHEMATICS  
**Revision:** 1.0  
**Date:** December 30, 2025  

---

## Overview

This document contains the complete electrical schematics for the 4-axis CNC robotic microscope system. Three diagrams are provided:

1. **System Overview** - High-level block diagram
2. **Power Distribution** - Detailed power routing and budget
3. **Signal Details** - Pin-level wiring specifications

All diagrams are generated using Graphviz DOT format for maintainability and version control.

---

## Generating PDF Schematics

The schematic source files are located in `/home/scope/scope/schematics/` directory.

### Prerequisites
```bash
sudo apt install graphviz
```

### Build Commands
```bash
cd /home/scope/scope/schematics

# Generate all PDFs
dot -Tpdf 01_system_overview.dot -o 01_system_overview.pdf
dot -Tpdf 02_power_distribution.dot -o 02_power_distribution.pdf
dot -Tpdf 03_signal_details.dot -o 03_signal_details.pdf

# Or build all at once
for file in *.dot; do dot -Tpdf "$file" -o "${file%.dot}.pdf"; done
```

---

## Schematic 1: System Overview

**File:** `01_system_overview.dot`  
**Purpose:** High-level system architecture showing major components and connections

**Key Features:**
- Power supply and distribution paths
- Control signal flow (RPi → Teensy → Drivers → Motors)
- Limit switch feedback paths
- LED ring control
- Camera integration

**Components Shown:**
- Liteon 24V 5A power supply
- Raspberry Pi 4 (control computer)
- Teensy 4.1 (motion controller)
- 4× TB6600 stepper drivers
- 4× NEMA 17 stepper motors
- 8× limit switches
- 24× WS2812B LED ring
- USB camera
- 60mm cooling fan

**Diagram Preview:**
```
AC Mains → 24V PSU ──┬──→ TB6600 Drivers → Motors
                     ├──→ Buck Conv. (5V) → RPi4, Teensy, Camera
                     ├──→ WS2812B LEDs
                     └──→ Cooling Fan

RPi4 ──[USB]──→ Teensy ──[GPIO]──→ TB6600 Drivers
         │
         └─[GPIO10]──→ LED Ring
         └─[USB]──→ Camera

Limit Switches ──→ Teensy ──→ RPi4 (status)
```

---

## Schematic 2: Power Distribution

**File:** `02_power_distribution.dot`  
**Purpose:** Detailed power routing with voltage levels, current ratings, and power budget

**Key Information:**

### Power Budget Table

| Component | Voltage | Current | Power | % Supply |
|-----------|---------|---------|-------|----------|
| 4× TB6600 (1A config) | 24V | 4.0A | 96W | 80% |
| Cooling Fan | 24V | 0.1A | 2.4W | 2% |
| Buck Converter Input | 24V | 0.66A | 15.8W | 13% |
| Raspberry Pi 4 | 5V | 1.3A | 6.5W | 5% |
| Teensy 4.1 | 5V | 0.16A | 0.8W | <1% |
| USB Camera | 5V | 0.2A | 1.0W | <1% |
| 24× WS2812B LEDs | 5V | 0.12A | 0.6W | <1% |
| **Total System** | — | — | **114.2W** | **95%** |
| **Supply Capacity** | 24V | 5A | **120W** | **100%** |
| **Safety Margin** | — | — | **5.8W** | **5%** |

### TB6600 Current Configuration

**DIP Switch Settings (1.0A running current):**
```
SW1 SW2 SW3 | Peak Current | Running Current
ON  OFF OFF | 1.0A        | 0.707A (1.0A / √2)

SW5 ON, SW6 OFF | Microstep: 1/8 step
```

**Justification for 1.0A Setting:**
- Motors rated for 1.7A but run cooler at 1.0A
- Sufficient torque for microscope positioning
- Reduces power dissipation: 48W vs 83W (at 1.7A)
- Better thermal management

### Power Distribution Topology

```
AC Input (120/240V)
    │
[Liteon PSU] 24V 5A
    │
    ├─[24V Rail]────┬─→ TB6600 #1 (X-axis) → Motor 1
    │               ├─→ TB6600 #2 (Y-axis) → Motor 2
    │               ├─→ TB6600 #3 (Z-axis) → Motor 3
    │               ├─→ TB6600 #4 (Cam)    → Motor 4
    │               ├─→ 60mm Fan (2.4W)
    │               └─→ Buck Converter (5V @ 3.16A)
    │
    └─[5V Rail]─────┬─→ Raspberry Pi 4 (USB-C)
                    ├─→ Teensy 4.1 (USB)
                    ├─→ USB Camera
                    └─→ WS2812B LED Ring (via GPIO10)
```

---

## Schematic 3: Signal Details

**File:** `03_signal_details.dot`  
**Purpose:** Pin-level wiring specifications for all control signals

### Raspberry Pi 4 Pinout

| GPIO | Pin | Function | Connection |
|------|-----|----------|------------|
| — | USB | Serial to Teensy | Teensy USB (native) |
| — | USB | Camera | USB Camera |
| GPIO10 | 19 | SPI0_MOSI | WS2812B LED DIN (via level shifter) |
| GND | 6 | Ground | Common ground |
| 5V | 2 | Power | Buck converter output |

### Teensy 4.1 Pinout

**Motor Control (to TB6600 drivers):**

| Pin | Function | Connection | Signal |
|-----|----------|------------|--------|
| 0 | X_PUL | TB6600 #1 PUL+ | Step pulses (X-axis) |
| 1 | X_DIR | TB6600 #1 DIR+ | Direction (X-axis) |
| 2 | Y_PUL | TB6600 #2 PUL+ | Step pulses (Y-axis) |
| 3 | Y_DIR | TB6600 #2 DIR+ | Direction (Y-axis) |
| 4 | Z_PUL | TB6600 #3 PUL+ | Step pulses (Z-axis) |
| 5 | Z_DIR | TB6600 #3 DIR+ | Direction (Z-axis) |
| 6 | C_PUL | TB6600 #4 PUL+ | Step pulses (Camera axis) |
| 7 | C_DIR | TB6600 #4 DIR+ | Direction (Camera axis) |
| 8 | ENABLE | All TB6600 ENA+ | Global motor enable (active low) |

**Limit Switches:**

| Pin | Function | Switch | Location |
|-----|----------|--------|----------|
| 9 | X_LIM+ | NC switch | X-axis positive limit |
| 10 | X_LIM- | NC switch | X-axis negative limit |
| 11 | Y_LIM+ | NC switch | Y-axis positive limit |
| 12 | Y_LIM- | NC switch | Y-axis negative limit |
| 13 | Z_LIM+ | NC switch | Z-axis positive limit |
| 14 | Z_LIM- | NC switch | Z-axis negative limit |
| 15 | C_LIM+ | NC switch | Camera axis positive limit |
| 16 | C_LIM- | NC switch | Camera axis negative limit |

**Special Notes:**
- Pin 22: Previously used for test LED, available for future expansion
- All limit switches are NC (Normally Closed) for fail-safe operation
- Internal pull-up resistors enabled on all limit switch inputs

### TB6600 Driver Connections

**Per Driver (4 total):**

| Terminal | Connection | Notes |
|----------|------------|-------|
| PUL+ | Teensy GPIO (step pulses) | 5V logic compatible |
| PUL- | Common ground | Ground reference |
| DIR+ | Teensy GPIO (direction) | 5V logic compatible |
| DIR- | Common ground | Ground reference |
| ENA+ | Teensy Pin 8 (all drivers) | Active low, shared |
| ENA- | Common ground | Ground reference |
| A+, A- | Motor coil A | Phase A winding |
| B+, B- | Motor coil B | Phase B winding |
| VCC | 24V positive rail | From PSU |
| GND | Common ground | System ground |

**Important:** PUL-, DIR-, ENA- terminals all connect to common ground plane, not isolated returns.

### WS2812B LED Ring

**Connection via SN74AHCT125N Level Shifter:**

```
RPi GPIO10 (3.3V) ──→ [SN74AHCT125N] ──→ WS2812B DIN (5V)
                          │
                       5V supply
```

**LED Ring Specifications:**
- 24× WS2812B NeoPixels
- 5V supply from buck converter
- Data: GPIO10 (RPi) via level shifter
- Protocol: WS2812B serial (800 kHz)
- Current @ 40% brightness: ~120mA (0.6W)

---

## Component Specifications

### Stepper Motors
- **Type:** NEMA 17 bipolar stepper
- **Rated Current:** 1.7A per phase
- **Operating Current:** 1.0A (derated for thermal management)
- **Step Angle:** 1.8° (200 steps/rev)
- **Microstepping:** 1/8 step (1600 steps/rev)
- **Holding Torque:** ~40 N·cm @ 1.0A

### TB6600 Drivers
- **Type:** Bipolar stepper driver, PWM chopping
- **Input Voltage:** 10-42V DC
- **Output Current:** 0.5-4.0A (configurable)
- **Current Setting:** 1.0A peak (SW1=ON, SW2=OFF, SW3=OFF)
- **Microstep Setting:** 1/8 step (SW5=ON, SW6=OFF)
- **Logic Input:** 5V compatible (opto-isolated)
- **Thermal Shutdown:** 150°C

### Power Supply
- **Manufacturer:** Liteon
- **Model:** Industry-standard ATX/industrial unit
- **Output:** 24V DC, 5A (120W)
- **Input:** 120/240V AC, 50/60 Hz
- **Protection:** Overcurrent, overvoltage, short circuit
- **Certifications:** UL/CE (assumed)

### Buck Converter (24V → 5V)
- **Input:** 24V DC
- **Output:** 5V DC, 3.5A max
- **Efficiency:** ~85% typical
- **Regulation:** ±2% line/load
- **Topology:** Synchronous buck (switching regulator)

---

## Wiring Guidelines

### Wire Gauge Recommendations

| Circuit | Voltage | Current | Wire Gauge | Length Limit |
|---------|---------|---------|------------|--------------|
| 24V Main Bus | 24V | 5A | 16 AWG | 3m |
| TB6600 to Motors | 24V | 1A | 18-20 AWG | 1m |
| 5V Logic Rail | 5V | 3.16A | 18 AWG | 0.5m |
| Teensy to TB6600 | 5V | <10mA | 22-24 AWG | 1m |
| Limit Switches | 5V | <1mA | 24-26 AWG | 2m |
| LED Ring | 5V | 0.12A | 22 AWG | 0.3m |

### Grounding Architecture

```
[Earth Ground] ──→ PSU Chassis ──→ Metal enclosure (if present)

[24V Ground] ──┬──→ TB6600 drivers (GND, PUL-, DIR-, ENA-)
               ├──→ Buck converter (GND)
               └──→ Motor return paths

[5V Ground] ───┬──→ Raspberry Pi (pin 6, 9, 14, 20, 25, 30, 34, 39)
               ├──→ Teensy 4.1 (GND pins)
               ├──→ USB Camera
               └──→ LED ring

Note: 5V ground and 24V ground are connected through buck converter.
```

### Signal Integrity Notes

1. **Keep signal wires away from motor cables** (minimize EMI)
2. **Twist pairs for limit switches** (noise immunity)
3. **Shield motor cables if >1m length** (optional, reduces emissions)
4. **Star grounding for sensitive analog signals** (not applicable, all digital)
5. **Bypass capacitors on power rails:**
   - 100µF electrolytic + 100nF ceramic at each TB6600
   - 470µF + 100nF at buck converter output
   - 100nF at each IC power pin (Teensy, level shifter)

---

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-12-30 | 1.0 | Initial release with 1A TB6600 configuration | System Documentation |

---

## Related Documents

- [03_HARDWARE_SPECIFICATION.md](03_HARDWARE_SPECIFICATION.md) - Detailed component specifications
- [12_THERMAL_ANALYSIS.md](12_THERMAL_ANALYSIS.md) - Thermal design and validation
- [13_ELECTRICAL_SAFETY.md](13_ELECTRICAL_SAFETY.md) - Safety assessment and compliance

---

**Note:** The actual PDF schematics are generated from DOT files and contain detailed graphical representations of the above information. Always refer to the PDF files for the most accurate and detailed wiring diagrams.

**Schematic Files Location:** `/home/scope/scope/schematics/`

---

**End of Schematics Documentation**
