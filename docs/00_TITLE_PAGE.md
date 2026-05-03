# The Mineral Microscope
## Robotic 4-Axis CNC Motion Controller
## with Touch Kiosk Interface

---

<div align="center">

**Technical Documentation**

**Complete System Specification**

---

### System Information

**Firmware Version:** 1.2  
**GUI Version:** 1.0  
**Documentation Version:** 1.3

**Date:** December 23, 2025

---

### System Overview

4-axis automated microscope positioning system  
with touch-screen kiosk interface  
for museum mineral specimen display

- **Control System:** Teensy 4.1 microcontroller
- **Host Computer:** Raspberry Pi 4
- **Interface:** 1920×1080 touch-screen kiosk
- **Motion:** 4-axis CNC (X, Y, Z, Focus)
- **Specimens:** 28-position automated grid
- **Operation:** Fully autonomous with manual override

---

### Developed For

**The Palermo Mine & Mineral Museum**  
**mindatnh.org**  
North Groton, New Hampshire

---

### Documentation Contents

This complete technical documentation set includes:

- **Product Overview** - System capabilities and use cases
- **System Architecture** - Block diagrams and data flow
- **Hardware Specification** - Complete electrical design
- **Software Specification** - Firmware and Python code
- **Protocol Specification** - Communication protocol
- **Diagnostic Procedures** - Testing and troubleshooting
- **Issues and Resolutions** - Design evolution
- **RPi4 Integration** - Python client examples
- **GUI Architecture** - PyQt5 implementation details
- **User Guide** - Museum operator manual
- **Installation Guide** - Complete deployment procedures

---

### Target Audience

- **Museum Operators** - Daily operation and maintenance
- **System Administrators** - Installation and deployment
- **Software Developers** - Code modification and enhancement
- **Hardware Engineers** - Circuit design and troubleshooting
- **Debug Engineers** - Diagnostic procedures and testing

---

### Document Conventions

**Signal Levels:**
- HIGH: 3.3V logic
- LOW: 0V (GND)

**Code Style:**
- `Constants`: UPPERCASE_WITH_UNDERSCORES
- `Functions`: camelCase
- `Classes`: PascalCase

**Communication:**
- **Master:** Raspberry Pi 4 (initiates commands)
- **Slave:** Teensy 4.1 (executes commands)

---

### Quick Specifications

| Parameter | Value |
|-----------|-------|
| **Axes** | 4 (X, Y, Z, Focus) |
| **Travel** | X: 270mm, Y: 150mm, Z: 30mm, F: 30mm |
| **Resolution** | 0.025mm (40 steps/mm) |
| **Speed** | Max 100 mm/s |
| **Communication** | 115200 baud UART |
| **Power** | 5V USB + 12-24V motors |
| **Display** | 1920×1080 touchscreen |
| **Camera** | USB microscope, 640×480 minimum |
| **Specimens** | 7×4 grid = 28 positions |

---

### Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.3 | Dec 23, 2025 | Complete GUI documentation added |
| 1.2 | Dec 23, 2025 | Full system documentation |
| 1.1 | Dec 22, 2025 | Limit switch robustness |
| 1.0 | Dec 20, 2025 | Initial release |

---

**START HERE:** [00 - Documentation Index](00_INDEX.md)

---

</div>
