# Technical Documentation - Robotic Microscope System

**System Name:** 4-Axis CNC Motion Controller with Touch Kiosk GUI  
**Firmware Version:** v1.2  
**GUI Version:** v1.0  
**Document Date:** December 23, 2025  
**Target Audience:** Developers, System Integrators, Museum Operators, Debug Engineers

---

## Document Structure

This technical documentation is organized into the following sections:

### **[01 - Product Overview](01_PRODUCT_OVERVIEW.md)**
High-level product description, use cases, system capabilities, and design philosophy.

### **[02 - System Architecture](02_SYSTEM_ARCHITECTURE.md)**
System block diagrams, component interactions, communication architecture, and state machines.

### **[03 - Hardware Specification](03_HARDWARE_SPECIFICATION.md)**
Complete hardware details: components, pinouts, wiring diagrams, signal levels, electrical specifications.

### **[04 - Software Specification](04_SOFTWARE_SPECIFICATION.md)**
Firmware architecture, source code organization, build system, programming procedures, calibration constants.

### **[05 - Protocol Specification](05_PROTOCOL_SPECIFICATION.md)**
Complete communication protocol reference: message formats, commands, responses, error codes, timing requirements.

### **[06 - Diagnostic Procedures](06_DIAGNOSTIC_PROCEDURES.md)**
Testing procedures, diagnostic menu system, troubleshooting guides, validation tests.

### **[07 - Issues and Resolutions](07_ISSUES_AND_RESOLUTIONS.md)**
Known issues, root cause analyses, implemented solutions, design evolution, lessons learned.

### **[08 - RPi4 Integration Guide](08_RPI4_INTEGRATION.md)**
Raspberry Pi 4 integration details, Python client implementation guide, complete working examples.

### **[09 - GUI Architecture](09_GUI_ARCHITECTURE.md)**
PyQt5 GUI architecture, threading model, video processing, touch interface, auto-cycle system.

### **[10 - User Guide](10_USER_GUIDE.md)**
Museum operator manual: starting the system, touch controls, troubleshooting, maintenance procedures.

### **[11 - Installation Guide](11_INSTALLATION.md)**
Complete system installation: OS setup, dependencies, configuration, autostart, deployment procedures.

### **[12 - Thermal Analysis](12_THERMAL_ANALYSIS.md)**
Comprehensive thermal performance analysis: heat load calculations, duty cycle analysis, ventilation system specification, temperature estimates, and cooling design validation.

### **[13 - Electrical Safety Analysis](13_ELECTRICAL_SAFETY.md)**
Complete electrical safety assessment: voltage classification, enclosure materials, circuit protection, hazard analysis, compliance standards, and safety recommendations.

### **[14 - System Schematics](14_SCHEMATICS.md)**
Electrical schematics and wiring diagrams: system overview, power distribution, signal details, component specifications, and wiring guidelines. PDF diagrams included.

---

## Quick Reference

### Essential Information
- **Firmware:** Teensy 4.1 running Arduino framework via PlatformIO
- **Language:** C++ (Arduino)
- **UART:** 115200 baud, 8N1, line-terminated (\n)
- **Protocol:** Text-based with XOR checksums
- **Power:** 5V USB + 12-24V motor power
- **Axes:** 4 (X, Y, Z, Focus)
- **Travel:** X=270mm, Y=150mm, Z=30mm, F=30mm

### Key Files

**Firmware:**
- `src/main.cpp` - Teensy firmware (3114 lines)
- `platformio.ini` - Build configuration
- `PROTOCOL.md` - Complete protocol specification

**Python GUI:**
- `scope_gui.py` - Main PyQt5 application (789 lines)
- `motion_controller.py` - High-level motion control with auto-cycle (360 lines)
- `video_thread.py` - OpenCV video capture thread (80 lines)
- `teensy_protocol.py` - Serial protocol implementation (320 lines)
- `specimen_grid.py` - Grid calculations and validation (160 lines)
- `cli_menu.py` - CLI diagnostic interface (optional, 920 lines)
- `mindatnh_tray1.json` - Specimen tray configuration

**Documentation:**
- `project_context.md` - Development history/context
- `GUI_README.md` - Quick start guide for GUI

### Development Tools
- **IDE:** Visual Studio Code with PlatformIO extension
- **Compiler:** Arduino framework (GCC ARM)
- **Upload:** Teensy Loader (teensy-gui protocol)
- **Monitor:** 115200 baud serial terminal

---

## Document Conventions

### Terminology
- **Master:** Raspberry Pi 4 (initiates all commands)
- **Slave:** Teensy 4.1 (executes commands, sends responses)
- **Protocol Mode:** Normal operation (RPi4 control)
- **Diagnostic Mode:** Human-interactive testing mode

### Signal Notation
- **HIGH:** 3.3V logic level
- **LOW:** 0V (GND)
- **Active LOW:** Signal is active when LOW (e.g., enable pins)
- **NO:** Normally Open (limit switches)

### Code References
- Line numbers refer to `src/main.cpp` unless otherwise specified
- Constants are `UPPERCASE_WITH_UNDERSCORES`
- Functions are `camelCase`

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.4 | Dec 30, 2025 | Added thermal analysis, electrical safety analysis, and system schematics (sections 12-14) |
| 1.3 | Dec 23, 2025 | Added GUI documentation (sections 09-11), updated for complete system |
| 1.2 | Dec 23, 2025 | Complete documentation set created |
| 1.1 | Dec 22, 2025 | Limit switch robustness redesign |
| 1.0 | Dec 20, 2025 | Initial protocol implementation |

---

## Contact & Support

For technical questions or issues:
- Review the appropriate section of this documentation
- Check [07 - Issues and Resolutions](07_ISSUES_AND_RESOLUTIONS.md) for known problems
- Examine `project_context.md` for development history
- Review code comments in `src/main.cpp`

---

**Next:** Start with [01 - Product Overview](01_PRODUCT_OVERVIEW.md)
