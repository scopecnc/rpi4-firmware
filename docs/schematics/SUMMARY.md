# Robotic Microscope - Schematics Summary

**Created:** December 30, 2025  
**Format:** Graphviz DOT → PDF  
**Location:** `/home/scope/scope/schematics/`

---

## Files Created

### Source Files (Editable)
1. **01_system_overview.dot** (7.1 KB) - System architecture
2. **02_power_distribution.dot** (9.0 KB) - Power routing
3. **03_signal_details.dot** (15 KB) - Pin-level connections

### Generated PDFs (Ready to Print)
1. **01_system_overview.pdf** (36 KB)
2. **02_power_distribution.pdf** (59 KB)
3. **03_signal_details.pdf** (66 KB)

### Documentation
- **README.md** (3.3 KB) - Instructions for regenerating and editing

---

## Schematic Contents

### 01 - System Overview
**High-level architecture showing:**
- Power distribution (24V AC/DC adapter → fuse → bus bars → 24V/5V rails)
- Control systems (RPi4, Teensy 4.1, Camera, LED Ring)
- Motor drivers (4× TB6600)
- Motors (4× NEMA17: X, Y, Z, F axes)
- Limit switches (8× NO switches: MIN/MAX for each axis)
- All major interconnections
- Color-coded signal types (power, ground, control, data)

**Key Features:**
- Component grouping by function
- Power flow visualization
- Signal routing
- eSTOP provision (future)

### 02 - Power Distribution
**Detailed power system including:**
- AC input → 24V 5A adapter
- 5A fuse protection
- 24V and GND bus bars (12 positions each)
- 24V → 5V buck converter (5A, 25W capacity)
- Complete power budget table with calculations
- Current consumption breakdown per component
- Total system power: 160-208W (depending on motor load)

**Load Analysis:**
- **5V Rail:** 3.16A (Teensy, RPi4, LED Ring, Level Shifter)
- **24V Rail:** 6-8A (4× motors at 1.5-2A each)
- **Safety margins:** Includes notes on fusing, grounding, SELV compliance

**Critical Notes:**
- Single-point ground at bus bar
- Ground loop prevention
- JST-SM connectors for all external connections
- Insulation requirements

### 03 - Signal Details
**Complete pin-level schematics:**

**Teensy 4.1 Pinout Table:**
- UART: Pins 0 (RX), 1 (TX) → RPi4
- X-Axis: Pins 2 (STEP), 3 (DIR), 4 (MIN), 5 (MAX)
- Y-Axis: Pins 6 (STEP), 7 (DIR), 8 (MIN), 9 (MAX)
- Z-Axis: Pins 10 (STEP), 11 (DIR), 12 (MIN), 14 (MAX)
- F-Axis: Pins 15 (STEP), 16 (DIR), 22 (MIN), 18 (MAX)
- Enable: Pin 33 (ENA_ALL, shared across all TB6600s, active LOW)
- **Pin 22 note:** F_MIN moved from pin 17 due to I2C interference

**RPi4 GPIO:**
- GPIO 10: SPI MOSI → LED Ring (via level shifter)
- GPIO 14: UART TX → Teensy Pin 0
- GPIO 15: UART RX → Teensy Pin 1
- Camera: CSI ribbon cable → HDMI adapter

**UART Detail:**
- 3-wire connection (TX, RX, GND)
- 115200 baud, 8N1, no flow control
- Both 3.3V logic (no level shifting needed)

**LED Ring with Level Shifter:**
- **SN74AHCT125N** (14-pin quad buffer)
  - Pin 14: VCC → 5V
  - Pin 7: GND
  - Pin 1 (1A): RPi GPIO10 input (3.3V)
  - Pin 2 (1Y): Output to LED DIN (5V)
  - Pin 1 (1OE): GND (enable active LOW)
  - Unused inputs: Tie to GND
- **WS2812B Ring:** 24 LEDs
  - DIN: From level shifter
  - 5V, GND: From power rail
  - Current: 500mA @ 40%, 900mA @ 70% max

**TB6600 Wiring (all 4 identical):**
- PUL+/- : Teensy STEP pin / GND
- DIR+/- : Teensy DIR pin / GND
- ENA+/- : Pin 33 (shared) / GND
- Motor: A+/A-, B+/B- to NEMA17 coils
- Power: 24V, GND
- Configuration: 1/16 microstepping (400 steps/mm)
- **Enable logic:** Active LOW (LOW = enabled)

**Limit Switch Wiring:**
- Type: Normally Open (NO)
- Pull-up: Internal (INPUT_PULLUP)
- Connection: Teensy pin → Switch → GND
- Debounce: 50ms in firmware
- Interrupt: FALLING edge

**Connector Summary:**
- Motors: 4-pin JST-SM (4×)
- Limits: 2-pin JST-SM (8×)
- LED: 3-pin JST-SM (1×)
- eStop: 2-pin JST-SM (provision)

---

## Viewing the Schematics

### On Linux/Mac:
```bash
# View PDFs
xdg-open 01_system_overview.pdf  # Linux
open 01_system_overview.pdf      # Mac

# Or use any PDF viewer
evince *.pdf    # Linux with Evince
okular *.pdf    # Linux with Okular
```

### Regenerating After Edits:
```bash
cd /home/scope/scope/schematics

# Single file
dot -Tpdf 01_system_overview.dot -o 01_system_overview.pdf

# All files
for file in *.dot; do
    dot -Tpdf "$file" -o "${file%.dot}.pdf"
done
```

### Generating Other Formats:
```bash
# PNG (for documents/presentations)
dot -Tpng 01_system_overview.dot -o 01_system_overview.png -Gdpi=300

# SVG (scalable, web-friendly)
dot -Tsvg 01_system_overview.dot -o 01_system_overview.svg
```

---

## Technical Specifications Referenced

### Voltage Levels
- **Teensy 4.1:** 3.3V logic (NOT 5V tolerant)
- **RPi4 GPIO:** 3.3V logic
- **TB6600 inputs:** 3.3V-5V compatible
- **WS2812B LEDs:** Require 5V logic (hence level shifter)

### Communication
- **UART:** 115200 baud, 3.3V, 8N1, no flow control
- **SPI (LED):** 800kHz, unidirectional (MOSI only)

### Power Requirements
- **Input:** 24V DC, 5A (120W)
- **5V Rail:** 3.16A max (15.8W)
- **24V Rail:** 6-8A (144-192W motors)
- **Total:** ~160-208W typical/peak

### Microstepping
- **All TB6600:** 1/16 microstepping
- **Calibration:** 400 steps/mm
- **DIP switches:** SW5-8 all ON

### Protection
- **Fuse:** 5A automotive blade type at 24V input
- **Ground:** Single-point at bus bar
- **Connectors:** JST-SM for all external cables

---

## Integration with Project Documentation

These schematics complement existing documentation:

| Document | Location | Purpose |
|----------|----------|---------|
| Hardware Spec | `docs/03_HARDWARE_SPECIFICATION.md` | Detailed component specs |
| RPi Integration | `docs/08_RPI4_INTEGRATION.md` | Software setup, Python code |
| System Architecture | `docs/02_SYSTEM_ARCHITECTURE.md` | Software design |
| Protocol Spec | `docs/05_PROTOCOL_SPECIFICATION.md` | UART protocol details |

**Recommended Reading Order:**
1. Start with **01_system_overview.pdf** for big picture
2. Review **02_power_distribution.pdf** for power system
3. Reference **03_signal_details.pdf** when wiring/debugging
4. Cross-reference with `docs/03_HARDWARE_SPECIFICATION.md` for pin details

---

## Notes and Warnings

### Critical Hardware Notes
⚠️ **Pin 22 for F_MIN** - Do not use pin 17 (I2C interference, hardware-verified issue)

⚠️ **Enable Logic** - TB6600 ENA is active LOW:
- Pin 33 LOW = Motors ENABLED
- Pin 33 HIGH = Motors DISABLED

⚠️ **3.3V Sensitivity** - Teensy 4.1 is NOT 5V tolerant on GPIO pins

⚠️ **Level Shifter Required** - WS2812B needs 5V logic, RPi outputs 3.3V

### Best Practices
✓ Use JST-SM connectors for all external cables  
✓ Maintain single-point ground at bus bar  
✓ Keep motor cables < 2m and away from signal cables  
✓ Verify coil pairs with multimeter before connecting motors  
✓ Set TB6600 to 1/16 microstepping before powering  
✓ Insulate all connections - 24V is SELV but still requires care

---

**End of Summary**  
For questions or updates, see `README.md` in this directory.
