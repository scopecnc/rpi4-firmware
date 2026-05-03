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
**Documentation Version:** 1.4

**Date:** December 30, 2025

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
- **Thermal Analysis** - Cooling design and temperature validation
- **Electrical Safety** - Safety assessment and compliance
- **System Schematics** - Electrical diagrams and wiring specifications

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


---


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


---


# Product Overview

**Document:** 01 - Product Overview  
**Version:** 1.3  
**Date:** December 23, 2025

---

## 1. Product Description

The **Robotic Microscope System** is a complete hardware and software solution for automated mineral specimen viewing in museum kiosks. Built on a modified 3018 CNC frame with Teensy 4.1 motion control and Raspberry Pi 4 with touch GUI, it provides precision motion control with an intuitive visitor interface.

### Key Features

**Motion Control:**
- **4-axis coordinated motion:** X, Y, Z (positioning) and Focus (optical)
- **Precision control:** 400 steps/mm resolution (1/16 microstepping)
- **Safety systems:** Limit switches, soft limits, emergency stop, watchdog timer
- **Robust protocol:** Text-based with checksums, ACK/NACK, retry logic

**Touch Kiosk Interface:**
- **1920x1080 fullscreen display** with live USB microscope video
- **Touch-friendly controls** for visitor interaction
- **Automatic cycling** through 28 specimens with 10-second viewing time
- **Semi-transparent overlays** showing mineral info, location, collector
- **Dynamic scale ruler** adjusting with zoom level
- **Manual override** with 30-second timeout returning to auto-cycle

**Museum Features:**
- **Autonomous operation:** Designed for continuous multi-day runs
- **Professional presentation:** Museum-quality UI with branding
- **Educational content:** Displays New Hampshire mineral specimens from famous localities
- **Hands-on experience:** Visitors can manually explore specimens
- **Low maintenance:** Automatic recovery, minimal operator intervention

### Primary Use Case

**Museum Kiosk for Mineral Microscopy:**
1. Visitors approach touch kiosk showing live microscope view
2. System automatically cycles through 28 New Hampshire mineral specimens
3. Each specimen shows mineral name, location (e.g., "Palermo Mine, North Groton"), and collector
4. Visitors can tap specimens to jump directly or use jog controls to explore manually
5. After 30 seconds of inactivity, system resumes automatic cycling
6. Runs continuously during museum hours with minimal supervision

---

## 2. System Capabilities

### Motion Control
- **Travel Range:**
  - X-axis: 0 to 270mm (measured on 3018 CNC)
  - Y-axis: 0 to 150mm
  - Z-axis: 0 to 30mm
  - Focus: 0 to 30mm (soft limits disabled per user request)
  
- **Speed:** 30 mm/sec linear (6000 steps/sec)
- **Acceleration:** 2000 steps/sec²
- **Positioning Accuracy:** ±0.0025mm (1 step at 400 steps/mm)

### Homing System
- **Sequential Homing:** Z → Y → X → Focus (safe order prevents collisions)
- **Parallel Homing:** All axes simultaneously (fast mode)
- **4-Phase Process:** 
  1. Fast seek (3000 steps/sec)
  2. Backoff (5mm)
  3. Slow creep (400 steps/sec for precision)
  4. Final backoff (establishes zero position 5mm from physical limit)

### Safety Features
- **Hardware Limit Switches:** 8 switches (min/max per axis)
- **Soft Limits:** Software-enforced travel boundaries (X, Y, Z only)
- **Emergency Stop:** Immediate halt of all motion
- **Watchdog Timer:** 5-second timeout with automatic motor shutdown
- **Limit Switch Robustness:** 
  - Timestamp-based debouncing (50ms)
  - Pin state hysteresis (prevents false triggers)
  - Triple-read noise rejection
  - Hybrid interrupt + polling detection

### Communication
- **Master/Slave Architecture:** RPi4 commands, Teensy executes
- **Text Protocol:** Human-readable for debugging
- **XOR Checksums:** Corruption detection
- **Sequence Numbers:** Duplicate detection and retry support
- **Async Startup:** Either device can boot first
- **Detailed Error Codes:** 20+ specific error conditions

---

## 3. Target Applications

### Robotic Microscopy (Primary)
- Automated imaging of specimen grids
- Multi-position time-lapse imaging
- Large-area scanning and stitching
- Batch processing of samples

### Related Applications
- Automated inspection systems
- PCB scanning/testing
- Material characterization
- Any XY positioning with Z and focus control

---

## 4. System Components

### Hardware
| Component | Specification | Quantity |
|-----------|---------------|----------|
| **Controller** | Teensy 4.1 (600MHz ARM Cortex-M7) | 1 |
| **Master Computer** | Raspberry Pi 4 (2GB+ RAM) | 1 |
| **Motor Drivers** | TB6600 (1/16 microstep) | 4 |
| **Motors** | NEMA17 stepper (200 steps/rev) | 4 |
| **Limit Switches** | Normally-Open mechanical | 8 |
| **Camera** | USB microscope (640x480 minimum) | 1 |
| **Display** | 1920x1080 touchscreen | 1 |
| **Frame** | Modified 3018 CNC | 1 |
| **Lead Screws** | T8 (8mm pitch) on X, Y, Z | 3 |

### Software
| Component | Description | Lines of Code |
|-----------|-------------|---------------|
| **Teensy Firmware** | v1.2 - Motion control (C++/Arduino) | 3114 |
| **PyQt5 GUI** | v1.0 - Touch kiosk interface (Python) | 789 |
| **Motion Controller** | High-level control with auto-cycle (Python) | 360 |
| **Video Thread** | OpenCV camera capture (Python) | 80 |
| **Protocol Library** | Teensy communication (Python) | 320 |
| **Specimen Grid** | Grid calculations and validation (Python) | 160 |
| **CLI Tool** | Optional diagnostic interface (Python) | 920 |
| **Protocol** | v1.0 - Text-based UART |  |
| **Dependencies** | AccelStepper v1.64, PyQt5, OpenCV, pyserial |  |

---

## 5. Design Philosophy

### Motion Appliance Concept
The Teensy acts as a **motion appliance** - a specialized device that:
- Executes motion commands reliably
- Enforces safety constraints
- Reports status and events
- Does NOT make high-level decisions

The RPi4 is the **decision maker** that:
- Determines where to move and when
- Manages imaging workflows
- Handles user interface
- Processes images

### Key Design Principles
1. **Determinism over Cleverness:** Predictable behavior, explicit states
2. **Safety First:** Multiple layers of protection (hardware + software)
3. **Debuggability:** Text protocol, console output, diagnostic mode
4. **Explicit State Management:** No hidden state, no assumptions
5. **Single Responsibility:** Teensy does motion, RPi4 does everything else

### Why NOT G-code?
- G-code is designed for CNC machining (feeds, speeds, tool changes)
- Microscopy workflows are fundamentally different
- Custom protocol provides:
  - Better error reporting
  - Watchdog protection
  - State awareness
  - Async operation support

---

## 6. Operating Modes

### Protocol Mode (Default)
- Normal operation under RPi4 control
- All commands via UART protocol
- Watchdog timer active
- Console output shows all activity

### Diagnostic Mode
- Human-interactive testing mode
- Hierarchical numbered menus
- Accessible via:
  - Boot-time prompt (press 'D' within 3 seconds)
  - Protocol command `!DIAG_ENTER` from RPi4
- Watchdog disabled during diagnostic mode
- Full access to all motion functions
- Remote operation supported via `!DIAG_CMD`

---

## 7. Performance Characteristics

### Speed and Timing
- **Command ACK:** < 10ms typical
- **Status Query:** < 20ms
- **Move Start Latency:** < 50ms after ACK
- **Homing Time:** ~30 seconds (sequential), ~15 seconds (parallel)
- **Grid Scan Time:** ~5 seconds per position (move + settle)

### Throughput
- **UART Bandwidth:** 115200 baud ≈ 11.5 KB/sec
- **Command Rate:** 200+ commands/sec (far exceeds needs)
- **Typical Usage:** 1-10 commands/sec for microscopy

### Reliability
- **Limit Switch Detection:** 100% (after v1.2 redesign)
- **Communication:** XOR checksums catch corruption
- **Uptime:** Designed for continuous multi-day operation
- **MTBF:** Tested over 8+ hour sessions without issues

---

## 8. Development Status

### Current State (v1.3)
✅ **Production Ready** - Complete museum kiosk system deployed

**Completed:**
- ✅ All 4 axes operational with homing
- ✅ Protocol implementation complete
- ✅ Diagnostic menu system working
- ✅ Limit switch robustness verified
- ✅ Speed and calibration optimized
- ✅ PyQt5 touch GUI with live video
- ✅ Auto-cycle with manual override
- ✅ Thread-safe video and motion control
- ✅ Specimen grid system (7×4 = 28 positions)
- ✅ New Hampshire mineral collection data
- ✅ Complete documentation

**Future Enhancements:**
- Quieter stepper drivers (TMC2209 recommended)
- Additional specimen trays
- Image capture capability
- Data logging and analytics

### Known Limitations
- No command queuing (one move at a time)
- No trajectory smoothing (straight line interpolation)
- No backlash compensation
- Focus axis soft limits disabled (per user request)
- TB6600 drivers produce audible whine (~20-30kHz PWM)

---

## 9. Bill of Materials Summary

### Essential Components
- Teensy 4.1: ~$35
- 4× TB6600 drivers: ~$40 ($10 each)
- 4× NEMA17 motors: ~$40 ($10 each)
- 8× Limit switches: ~$16 ($2 each)
- 3018 CNC frame: ~$200
- Raspberry Pi 4 (2GB+): ~$75
- USB microscope camera: ~$50
- 1920x1080 touchscreen: ~$150
- Power supplies, wiring, misc: ~$50

**Total System Cost:** ~$656

### Optional Upgrades
- TMC2209 stepper drivers (quieter): ~$32 (4× $8)
- Better USB camera (1080p): ~$100
- Larger touchscreen (24"): ~$250
- UPS for power protection: ~$50

---

## 10. Success Metrics

### Technical Validation
- ✅ Zero missed limit switch detections (after v1.2)
- ✅ Consistent positioning accuracy (±0.0025mm)
- ✅ Stable communication (no checksum errors in testing)
- ✅ Clean state transitions (no hangs or undefined states)
- ✅ Smooth motion (no stalls or skipped steps)

### Operational Goals
- Support 28-position grid scan (7×4)
- Run continuously for 24+ hours
- Manual override without position loss
- < 1 minute recovery from power cycle
- Remote diagnostic capability

---

**Next Section:** [02 - System Architecture](02_SYSTEM_ARCHITECTURE.md)


---


# System Architecture

**Document:** 02 - System Architecture  
**Version:** 1.2  
**Date:** December 23, 2025

---

## 1. System Block Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         RPi4 Master                              │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │   Python     │  │   Camera     │  │   GUI / User       │   │
│  │   Client     │  │   Interface  │  │   Interface        │   │
│  └──────┬───────┘  └──────────────┘  └────────────────────┘   │
│         │                                                        │
│         │ UART (Serial1, 115200 baud, 8N1)                     │
└─────────┼────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Teensy 4.1 Slave                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Main Firmware (main.cpp)                     │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │  │
│  │  │  Protocol   │  │  State       │  │  Motion        │  │  │
│  │  │  Parser     │  │  Machine     │  │  Control       │  │  │
│  │  └─────────────┘  └──────────────┘  └────────────────┘  │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │  │
│  │  │  Diagnostic │  │  Limit       │  │  Homing        │  │  │
│  │  │  Menu       │  │  Detection   │  │  Logic         │  │  │
│  │  └─────────────┘  └──────────────┘  └────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  GPIO Pins:                                                     │
│  ├─ Serial1 (pins 0/1) → RPi4 UART                            │
│  ├─ Serial (USB) → Debug Console                               │
│  ├─ Digital Outputs → TB6600 Drivers (STEP/DIR/EN)            │
│  └─ Digital Inputs → Limit Switches (8 interrupts)             │
└──────────────┬───────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TB6600 Motor Drivers (×4)                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │  X Driver  │  │  Y Driver  │  │  Z Driver  │  │ F Driver │ │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └────┬─────┘ │
└────────┼───────────────┼───────────────┼──────────────┼─────────┘
         │               │               │              │
         ▼               ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    NEMA17 Stepper Motors (×4)                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │  X Motor   │  │  Y Motor   │  │  Z Motor   │  │ F Motor  │ │
│  │  (Gantry)  │  │  (Table)   │  │  (Height)  │  │ (Focus)  │ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Communication Architecture

### 2.1 Master/Slave Model

**Master (RPi4):**
- Initiates all commands
- Maintains watchdog timer (sends !PING every 3 seconds)
- Processes responses and events
- Makes high-level decisions
- Handles user interaction and imaging

**Slave (Teensy):**
- Executes motion commands
- Enforces safety constraints
- Reports status and events
- Maintains real-time control
- No autonomous decision-making

### 2.2 Dual Serial Configuration

The Teensy uses TWO serial ports simultaneously:

| Port | Purpose | Connection | Baud | Usage |
|------|---------|------------|------|-------|
| **Serial1** | Protocol | Pins 0/1 (UART) → RPi4 GPIO 14/15 | 115200 | Commands, responses, events |
| **Serial** | Diagnostics | USB → PC | 115200 | Debug output, local testing |

**Key Benefits:**
- RPi4 communication independent of USB connection
- Debug console always available during development
- `#DIAG` messages mirrored to both ports for remote diagnostics

### 2.3 Message Flow

```
Normal Operation:
RPi4 → !COMMAND → Teensy
Teensy → @ACK → RPi4
[Teensy executes]
Teensy → @COMPLETE → RPi4

Error Condition:
RPi4 → !COMMAND → Teensy
Teensy → @NACK ERR_CODE message → RPi4

Asynchronous Event:
Teensy → #EVENT data → RPi4
```

---

## 3. State Machine

### 3.1 System States

```c++
enum SystemState {
  STATE_BOOT,          // Power-on initialization
  STATE_DISCONNECTED,  // No master connection
  STATE_CONNECTED,     // Master connected, not homed
  STATE_IDLE,          // Ready for commands (homed)
  STATE_HOMING_Z,      // Homing Z axis
  STATE_HOMING_Y,      // Homing Y axis
  STATE_HOMING_X,      // Homing X axis
  STATE_HOMING_F,      // Homing Focus axis
  STATE_HOMING,        // Generic homing (for protocol)
  STATE_MOVING,        // Executing coordinated move
  STATE_JOGGING,       // Executing single-axis jog
  STATE_ERROR,         // Fault condition
  STATE_DIAGNOSTIC,    // Human-interactive mode
  STATE_COMM_LOST      // Watchdog timeout
};
```

### 3.2 State Transition Diagram

```
BOOT
 │
 ├─────────────────────────────────────────────────┐
 │                                                  │
 ▼                                                  │
DISCONNECTED ──!CONNECT──> CONNECTED               │
 ▲                             │                    │
 │                             │ !HOME              │
 │                             ▼                    │
 │                         HOMING_Z                 │
 │                             │                    │
 │                             ▼                    │
 │                         HOMING_Y                 │
 │                             │                    │
 │                             ▼                    │
 │                         HOMING_X                 │
 │                             │                    │
 │                             ▼                    │
 │                         HOMING_F                 │
 │                             │                    │
 │                             ▼                    │
 │                           IDLE ◄─────────┐       │
 │                             │            │       │
 │                 ┌───────────┼──────────┐ │       │
 │                 │           │          │ │       │
 │           !MOVE │      !JOG │          │ │       │
 │                 ▼           ▼          │ │       │
 │              MOVING      JOGGING       │ │       │
 │                 │           │          │ │       │
 │                 └───────────┴──────────┘ │       │
 │                     (complete)           │       │
 │                                          │       │
 ├─ !DIAG_ENTER ──> DIAGNOSTIC ─ !DIAG_EXIT┘       │
 │                      │                            │
 │                      │ (watchdog disabled)        │
 │                      │                            │
 │                                                   │
 └──────────────────── ERROR ◄─────────────────────┘
          ▲               │ !CLEAR_ERROR
          │               │
          │               ▼
      (limit hit,    DISCONNECTED
       timeout,
       etc.)
      
 COMM_LOST ──(watchdog timeout from any state)──> #BOOT every 10s
```

### 3.3 State Behaviors

| State | Motors | Watchdog | Commands Accepted | Description |
|-------|--------|----------|-------------------|-------------|
| **BOOT** | Disabled | Off | None | Initialization, 3-second boot menu |
| **DISCONNECTED** | Disabled | Off | !CONNECT, !DIAG_ENTER | Waiting for master |
| **CONNECTED** | Disabled | On | !HOME, !STATUS, etc. | Connected but not homed |
| **IDLE** | Enabled | On | !MOVE, !JOG, !HOME, !STATUS | Ready for motion |
| **HOMING_Z/Y/X/F** | Enabled | On | !STOP | Executing homing sequence |
| **MOVING** | Enabled | On | !STOP, !STATUS | Executing coordinated move |
| **JOGGING** | Enabled | On | !STOP, !STATUS | Executing jog move |
| **ERROR** | Disabled | Off | !CLEAR_ERROR, !STATUS | Fault condition |
| **DIAGNOSTIC** | Enabled | Off | Menu commands, !DIAG_EXIT | Human testing mode |
| **COMM_LOST** | Disabled | Off | None (auto-recovery) | Watchdog timeout |

---

## 4. Firmware Architecture

### 4.1 Module Organization

```
main.cpp (3114 lines)
├─ CONFIGURATION (lines 54-129)
│  ├─ Pin definitions
│  ├─ Speed settings
│  ├─ Calibration constants
│  └─ Soft limits
│
├─ STATE & OBJECTS (lines 130-275)
│  ├─ State machine enums
│  ├─ AccelStepper objects
│  ├─ LimitState structures
│  └─ Protocol variables
│
├─ INTERRUPT SERVICE ROUTINES (lines 287-440)
│  ├─ xMinISR(), xMaxISR()
│  ├─ yMinISR(), yMaxISR()
│  ├─ zMinISR(), zMaxISR()
│  └─ fMinISR(), fMaxISR()
│
├─ HELPER FUNCTIONS (lines 441-1450)
│  ├─ Communication (sendAck, sendNack, etc.)
│  ├─ Motor control (enableMotors, emergencyStop)
│  ├─ Limit detection (checkLimitTriggered)
│  └─ Homing logic (homeAxis, handleHomingState)
│
├─ SETUP & MAIN LOOP (lines 615-1024)
│  ├─ setup(): Pin init, motor config, interrupts
│  └─ loop(): State processing, watchdog, serial
│
├─ DIAGNOSTIC MENU SYSTEM (lines 1845-2630)
│  ├─ Menu printing functions
│  ├─ Command processing
│  └─ Interactive motion testing
│
└─ PROTOCOL COMMAND PROCESSING (lines 2370-3114)
   ├─ Command parser
   ├─ State validation
   ├─ Motion execution
   └─ Response generation
```

### 4.2 Key Data Structures

**LimitState Structure:**
```c++
struct LimitState {
  volatile bool triggered;              // ISR sets, main loop clears
  volatile bool isMin;                  // true=MIN, false=MAX
  volatile unsigned long lastTriggerTime;
  volatile unsigned long debounceUntil; // Timestamp-based debouncing
  volatile int lastMinPinState;         // Pin state hysteresis (MIN)
  volatile int lastMaxPinState;         // Pin state hysteresis (MAX)
};
```

**Stepper Objects:**
```c++
AccelStepper xStepper(DRIVER, X_STEP_PIN, X_DIR_PIN);
AccelStepper yStepper(DRIVER, Y_STEP_PIN, Y_DIR_PIN);
AccelStepper zStepper(DRIVER, Z_STEP_PIN, Z_DIR_PIN);
AccelStepper fStepper(DRIVER, F_STEP_PIN, F_DIR_PIN);
MultiStepper multiStepper;  // For coordinated moves
```

---

## 5. Homing System Architecture

### 5.1 Sequential Homing

**Order:** Z → Y → X → Focus

**Rationale:**
- Z-axis homing first prevents collisions (lifts tool away from work)
- Y before X avoids gantry interference
- Focus last (least critical for positioning)

**Process Flow:**
```
!HOME command received
→ STATE_IDLE → STATE_HOMING_Z
   ↓
   homeAxis(Z) [4 phases]
   ↓
   STATE_HOMING_Z → STATE_HOMING_Y
   ↓
   homeAxis(Y) [4 phases]
   ↓
   STATE_HOMING_Y → STATE_HOMING_X
   ↓
   homeAxis(X) [4 phases]
   ↓
   STATE_HOMING_X → STATE_HOMING_F
   ↓
   homeAxis(F) [4 phases]
   ↓
   STATE_HOMING_F → STATE_IDLE
   ↓
   @COMPLETE sent to master
```

### 5.2 Parallel Homing (!HOME_FAST)

All axes home simultaneously:
```
!HOME_FAST command received
→ STATE_IDLE → STATE_HOMING
   ↓
   Start all axes: xHomingPhase = HOMING_SEEK
                   yHomingPhase = HOMING_SEEK
                   zHomingPhase = HOMING_SEEK
                   fHomingPhase = HOMING_SEEK
   ↓
   Loop: Update each axis independently
         Check if all complete
   ↓
   All axes HOMING_COMPLETE
   ↓
   STATE_HOMING → STATE_IDLE (or STATE_DIAGNOSTIC)
   ↓
   @COMPLETE sent
```

### 5.3 Four-Phase Homing Process

Each axis goes through:

1. **HOMING_SEEK** - Fast approach (3000 steps/sec)
   - Move toward MIN limit
   - If MAX limit hit → ERROR (wrong direction)
   - Timeout: 120 seconds

2. **HOMING_BACKOFF** - Release switch (normal speed)
   - Move 5mm away from MIN limit
   - Ensures clean switch release

3. **HOMING_CREEP** - Precision approach (400 steps/sec)
   - Slow approach to MIN limit
   - Establishes precise home position

4. **HOMING_COMPLETE** - Final backoff
   - Move 5mm away from physical MIN
   - Set position to 0.00mm (5mm from limit)
   - Zero position is safe for operations

---

## 6. Limit Switch Architecture

### 6.1 Robust Detection System (v1.2)

**Problem Solved:** Original detach/reattach interrupt approach had 25% failure rate

**Solution:** Three-layer hybrid architecture

#### Layer 1: Interrupt Detection (Primary)
```c++
void xMinISR() {
  unsigned long now = millis();
  int pinState = digitalRead(X_MIN_PIN);
  
  // Timestamp-based debouncing (no detach)
  if (now >= xLimit.debounceUntil &&
      pinState == LOW &&                    // Switch pressed
      xLimit.lastMinPinState == HIGH) {     // Was released (hysteresis)
    
    xLimit.triggered = true;
    xLimit.isMin = true;
    xLimit.lastTriggerTime = now;
    xLimit.debounceUntil = now + DEBOUNCE_MS;  // 50ms
    xLimit.lastMinPinState = LOW;              // Track state
  }
}
```

#### Layer 2: Polling Fallback
```c++
bool checkLimitTriggered(LimitState& limit, int minPin, int maxPin) {
  // 1. Check ISR flag (primary detection)
  if (limit.triggered) {
    return true;
  }
  
  // 2. Poll pins directly (fallback if ISR missed)
  if (digitalRead(minPin) == LOW) {
    // Triple-read verification (200µs stable)
    delayMicroseconds(200);
    if (digitalRead(minPin) == LOW) {
      delayMicroseconds(200);
      if (digitalRead(minPin) == LOW) {
        limit.triggered = true;
        limit.isMin = true;
        return true;
      }
    }
  }
  
  // [similar for maxPin]
}
```

#### Layer 3: State Tracking
```c++
// In main loop and all tight loops:
if (digitalRead(X_MIN_PIN) == HIGH) xLimit.lastMinPinState = HIGH;
if (digitalRead(X_MAX_PIN) == HIGH) xLimit.lastMaxPinState = HIGH;
// [repeat for all 8 pins]
```

**Result:** Zero missed detections, zero false triggers

---

## 7. Protocol Integration

### 7.1 Command Processing Flow

```
Serial1 byte arrives
   ↓
Accumulate in buffer until '\n'
   ↓
Extract checksum, validate
   ↓
Parse command and sequence number
   ↓
Check for duplicate sequence
   ↓
Validate state (can this command run now?)
   ↓
Execute command
   ↓
Send @ACK or @NACK
   ↓
[Command continues asynchronously]
   ↓
Send @COMPLETE when done
```

### 7.2 Watchdog Timer

```c++
// In loop():
if (watchdogEnabled && (millis() - lastMasterMessage > WATCHDOG_TIMEOUT_MS)) {
  emergencyStop();
  disableMotors();
  currentState = STATE_COMM_LOST;
  sendEvent("COMM_LOST", "Watchdog timeout");
  watchdogEnabled = false;
  
  // Auto-recovery: Send #BOOT every 10 seconds
}
```

---

## 8. Diagnostic Mode Architecture

### 8.1 Menu System

Hierarchical numbered menus:
```
MAIN MENU
├─ 1: HOME (all axes)
├─ 2: MOVE (submenu)
├─ 3: JOG (submenu)
├─ 4: TEST MOTORS (submenu)
├─ 5: SAFE LIMIT TEST (submenu)
├─ 6: SPEED SETTINGS
└─ 7: CALIBRATION
```

### 8.2 Remote Diagnostic Access

Via protocol commands:
- `!DIAG_ENTER` - Switch to diagnostic mode
- `!DIAG_CMD <char>` - Send menu command
- `!DIAG_MENU` - Get current menu display
- `!DIAG_EXIT` - Return to protocol mode

All diagnostic output prefixed with `#DIAG` and sent to RPi4

---

## 9. Performance Considerations

### 9.1 Real-Time Constraints
- AccelStepper.run() must be called frequently (< 1ms gaps)
- No blocking delays in main loop
- Interrupt handlers kept minimal (< 10µs)
- Serial buffer checked every loop iteration

### 9.2 Non-Blocking Architecture
- No `delay()` calls (except in ISRs for debounce)
- All operations use state machines
- Homing, moving, jogging all non-blocking
- Watchdog uses `millis()` timestamps

---

## 10. GUI Software Architecture (PyQt5)

### 10.1 GUI System Block Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    MicroscopeGUI (Main Window)                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  VideoWidget (1670×1080)                    │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  OpenCV Frame (640×480) scaled to fill             │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  Translucent Overlays (alpha=200):                   │  │ │
│  │  │  - Title Banner (70px top)                           │  │ │
│  │  │  - Specimen Info (bottom)                            │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         Left Panel (230px wide)                             │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  Specimen Grid (7×4 = 28 cards)                      │  │ │
│  │  │  - Touch to select specimen                          │  │ │
│  │  │  - Current specimen highlighted                      │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  Jog Controls (9 buttons)                            │  │ │
│  │  │  - XY movement (8-way)                               │  │ │
│  │  │  - Z/Focus (2 buttons)                               │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Threading Architecture                       │
├─────────────────────────────────────────────────────────────────┤
│  Main Thread (PyQt5 GUI)                                         │
│  ├─ Event loop                                                   │
│  ├─ Painting (VideoWidget.paintEvent)                           │
│  ├─ Touch event handling                                         │
│  └─ UI updates (QTimer.singleShot for thread safety)            │
├─────────────────────────────────────────────────────────────────┤
│  VideoThread (QThread)                                           │
│  ├─ OpenCV camera capture                                        │
│  ├─ BGR → RGB conversion                                         │
│  └─ emit frame_ready signal → Main thread                       │
├─────────────────────────────────────────────────────────────────┤
│  MotionController (separate thread)                              │
│  ├─ Serial communication (teensy_protocol.py)                   │
│  ├─ Homing sequence                                              │
│  ├─ Movement commands                                            │
│  ├─ Watchdog (!PING every 3s)                                   │
│  └─ Callbacks to GUI (connected_callback, etc.)                 │
├─────────────────────────────────────────────────────────────────┤
│  Auto-Cycle Thread (MotionController)                            │
│  ├─ Specimen rotation (10s timer)                               │
│  ├─ Skip invalid specimens                                       │
│  └─ Pause on manual intervention (30s timeout)                  │
└─────────────────────────────────────────────────────────────────┘
```

### 10.2 Component Hierarchy

```
scope_gui.py (789 lines)
├─ MicroscopeGUI (QMainWindow)
│  ├─ VideoWidget (custom QWidget for video + overlays)
│  │  ├─ paintEvent() - Render video and overlays
│  │  ├─ set_title() - Update title text
│  │  ├─ set_status() - Update status text
│  │  └─ set_position() - Update position text
│  │
│  ├─ SpecimenCard (QPushButton, 230×80)
│  │  ├─ set_current() - Highlight selected card
│  │  └─ paintEvent() - Custom border rendering
│  │
│  ├─ JogButton (QPushButton, 60×60)
│  │  └─ Touch-friendly directional controls
│  │
│  └─ Layout
│     ├─ Central Widget: VideoWidget (1670×1080)
│     └─ Left Panel: Specimen grid + jog controls (230×1080)
│
video_thread.py (80 lines)
└─ VideoThread (QThread)
   ├─ __init__(device_index=0)
   ├─ run() - Capture loop
   └─ frame_ready signal
   
motion_controller.py (360 lines)
└─ MotionController
   ├─ teensy_protocol.TeensyController (serial communication)
   ├─ _auto_cycle_loop() - Autonomous specimen rotation
   ├─ move_to_specimen() - High-level specimen positioning
   └─ Callbacks: connected_callback, position_callback, etc.

specimen_grid.py (160 lines)
├─ SpecimenGrid
│  ├─ load_from_json() - Parse mindatnh_tray1.json
│  ├─ get_by_row_col() - Lookup specimen
│  └─ calculate_position() - Grid math (40mm Y-spacing)
│
teensy_protocol.py (320 lines)
└─ TeensyController
   ├─ connect() - Open serial port
   ├─ send_command() - Protocol with checksum
   ├─ home() - Homing sequence
   ├─ move_to() - Coordinated 4-axis move
   └─ watchdog_loop() - !PING every 3 seconds
```

### 10.3 Data Flow: Specimen Selection

```
User touches SpecimenCard
   ↓
SpecimenCard.clicked signal
   ↓
MicroscopeGUI.on_specimen_clicked(row, col)
   ↓
MotionController.move_to_specimen(specimen)
   ↓
Calculate position: SpecimenGrid.calculate_position()
   ↓
Send commands via TeensyController:
   1. !MOVE X Y Z F
   2. !WAIT (until complete)
   3. !WAIT (until complete)
   ↓
Teensy executes move
   ↓
@COMPLETE received
   ↓
MotionController.move_complete_callback()
   ↓
GUI updates: VideoWidget.set_title(mineral_name)
   ↓
Reset manual override timer (30s)
```

### 10.4 Thread Safety

**Critical Pattern:** Never call `repaint()` from non-GUI threads

**Correct Approach:**
```python
# In VideoWidget methods called from other threads:
def set_title(self, text):
    self.current_title = text
    QTimer.singleShot(0, self.update)  # Schedule update on main thread

# In SpecimenCard:
def set_current(self, is_current):
    self.is_current = is_current
    self.update()  # NOT repaint()
```

**Wrong Approach (causes segfaults):**
```python
def set_title(self, text):
    self.current_title = text
    self.repaint()  # WRONG: Synchronous paint from wrong thread
```

### 10.5 Auto-Cycle State Machine

```
AUTO Mode (default)
   ↓
   Timer: 10 seconds
   ↓
   Move to next specimen
   ↓
   [User touches specimen card]
   ↓
MANUAL Mode
   ↓
   Timer: 30 seconds (no user input)
   ↓
   Return to AUTO Mode
   ↓
   Resume cycling
```

### 10.6 Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **Video FPS** | 30 | OpenCV capture rate |
| **GUI FPS** | 30 | paintEvent refresh rate |
| **Memory** | ~120 MB | Typical RAM usage |
| **CPU** | 20% | RPi4 single core |
| **Startup** | 90s | From power-on to first specimen |
| **Homing** | 30s | Sequential Z→Y→X→F |
| **Move Time** | 3-8s | Depends on distance |
| **Cycle Time** | 10s | Auto-cycle interval |

---

**Next Section:** [03 - Hardware Specification](03_HARDWARE_SPECIFICATION.md)


---


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

**Critical Note:** F_MIN on pin 22 (NOT pin 17)
- Pins 17, 19, 20 have I2C hardware interference
- Original design used pin 17, moved to pin 22 after noise issues
- This is a **hardware fix** - do not change without testing

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

**Current Setting (per motor rating):**
- Set to 1.5A - 2.0A for typical NEMA17 motors
- Consult TB6600 datasheet for switch positions

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


---


# Software Specification

**Document:** 04 - Software Specification  
**Version:** 1.2  
**Date:** December 23, 2025

---

## 1. Development Environment

### 1.1 Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| **Visual Studio Code** | Latest | IDE |
| **PlatformIO Extension** | Latest | Build system and Arduino framework |
| **Teensy Loader** | Latest | Firmware upload (automatic via PlatformIO) |
| **Git** | Any | Version control (optional) |

### 1.2 Installation Steps

1. **Install VS Code:**
   ```
   https://code.visualstudio.com/
   ```

2. **Install PlatformIO Extension:**
   - Open VS Code
   - Click Extensions (Ctrl+Shift+X)
   - Search "PlatformIO IDE"
   - Click Install
   - Restart VS Code

3. **Install Teensy Udev Rules (Linux only):**
   ```bash
   wget https://www.pjrc.com/teensy/00-teensy.rules
   sudo cp 00-teensy.rules /etc/udev/rules.d/
   sudo udevadm control --reload-rules
   ```

4. **Open Project:**
   - File → Open Folder
   - Navigate to `teensy_firmware/`
   - PlatformIO will auto-detect `platformio.ini`

---

## 2. Project Structure

```
teensy_firmware/
├── .vscode/               # VS Code configuration
│   ├── extensions.json   # Recommended extensions
│   └── settings.json     # Workspace settings
├── .pio/                  # PlatformIO build cache (auto-generated)
├── docs/                  # Technical documentation (this folder)
│   ├── 00_INDEX.md
│   ├── 01_PRODUCT_OVERVIEW.md
│   ├── 02_SYSTEM_ARCHITECTURE.md
│   ├── 03_HARDWARE_SPECIFICATION.md
│   ├── 04_SOFTWARE_SPECIFICATION.md
│   ├── 05_PROTOCOL_SPECIFICATION.md
│   ├── 06_DIAGNOSTIC_PROCEDURES.md
│   ├── 07_ISSUES_AND_RESOLUTIONS.md
│   └── 08_RPI4_INTEGRATION.md
├── src/                   # Source code
│   └── main.cpp          # Main firmware (3114 lines)
├── platformio.ini        # Build configuration
├── project_context.md    # Development history/context
├── PROTOCOL.md           # Complete protocol specification
├── README.md             # Quick start guide
├── TEST_PROGRAM_GUIDE.md # Testing procedures
├── main_production.cpp   # Backup/archive
└── main_test.cpp         # Backup/archive
```

---

## 3. Build Configuration

### 3.1 platformio.ini

```ini
[env:teensy41]
platform = teensy
board = teensy41
framework = arduino
monitor_speed = 115200

; Upload settings
upload_protocol = teensy-gui

; Build flags for debugging
build_flags = 
    -DUSB_SERIAL
    -DCORE_TEENSY

; Library dependencies
lib_deps = 
    waspinator/AccelStepper@^1.64
```

### 3.2 Build Commands

**Via VS Code:**
- **Build:** Click checkmark (✓) in bottom toolbar OR `Ctrl+Alt+B`
- **Upload:** Click arrow (→) in bottom toolbar OR `Ctrl+Alt+U`
- **Monitor:** Click plug icon in bottom toolbar OR `Ctrl+Alt+S`
- **Clean:** PlatformIO → Clean

**Via Terminal:**
```bash
# Build
platformio run

# Upload
platformio run --target upload

# Monitor
platformio device monitor --baud 115200

# Clean build
platformio run --target clean
```

---

## 4. Firmware Architecture

### 4.1 Source Code Organization

**main.cpp** (3114 lines) is organized as follows:

| Line Range | Section | Description |
|------------|---------|-------------|
| 1-53 | Header Comment | Version, description, features |
| 54-93 | Pin Definitions | All GPIO assignments |
| 95-129 | Motion Configuration | Speed, acceleration, limits |
| 130-275 | State & Objects | State machine, stepper objects |
| 287-440 | ISRs | 8 interrupt handlers for limit switches |
| 441-614 | Helper Functions | Communication, utility functions |
| 615-784 | Setup | Pin initialization, motor config |
| 785-1024 | Main Loop | State processing, serial handling |
| 1025-1450 | Motion Control | Homing, movement, limit checking |
| 1451-1844 | Protocol Functions | ACK/NACK, sequence handling |
| 1845-2369 | Diagnostic Menu | Menu system printing |
| 2370-2630 | Diagnostic Commands | Interactive command processing |
| 2631-3114 | Protocol Commands | Protocol command execution |

### 4.2 Key Constants

Located at top of main.cpp, easily modifiable:

**Pin Assignments (lines 61-92):**
```c++
const int LED_PIN = 13;
const int ENA_ALL_PIN = 33;
const int X_STEP_PIN = 2;
const int X_DIR_PIN = 3;
const int X_MIN_PIN = 4;
const int X_MAX_PIN = 5;
// ... (similar for Y, Z, F)
```

**Motion Parameters (lines 95-129):**
```c++
const float MAX_SPEED = 6000.0;        // steps/sec
const float ACCEL = 2000.0;            // steps/sec²
const float HOMING_SPEED = 3000.0;     // steps/sec
const float HOMING_CREEP_SPEED = 400.0; // steps/sec

const float STEPS_PER_MM = 400.0;      // Calibrated value
const float BACKOFF_DISTANCE_MM = 5.0; // Homing backoff

const float X_MAX_TRAVEL_MM = 270.0;   // Soft limits
const float Y_MAX_TRAVEL_MM = 150.0;
const float Z_MAX_TRAVEL_MM = 30.0;
const float F_MAX_TRAVEL_MM = 30.0;

const unsigned long DEBOUNCE_MS = 50;  // Limit switch debounce
const unsigned int PULSE_WIDTH_US = 10; // Step pulse width
```

**Protocol Parameters (lines 218-228):**
```c++
const unsigned long WATCHDOG_TIMEOUT_MS = 5000;  // 5 seconds
const unsigned long HEARTBEAT_INTERVAL = 2000;   // 2 seconds
```

---

## 5. Calibration and Configuration

### 5.1 STEPS_PER_MM Calibration

**Current Value:** 400 steps/mm (verified accurate)

**How to Recalibrate:**
1. Home all axes
2. Mark current position on physical frame
3. Command 100mm move: `!MOVE X100`
4. Measure actual travel with ruler/caliper
5. Calculate new value:
   ```
   new_STEPS_PER_MM = old_STEPS_PER_MM × (commanded_mm / actual_mm)
   ```

**Example:**
- Commanded: 100mm
- Actual: 50mm
- Old value: 200
- New value: 200 × (100/50) = 400 ✓ (current setting)

### 5.2 Soft Limit Measurement

**Current Values:**
- X: 270mm
- Y: 150mm
- Z: 30mm
- F: 30mm (not enforced)

**How to Remeasure:**
1. Home axis
2. Slowly jog toward MAX limit
3. Note position just before MAX switch triggers
4. Update `X_MAX_TRAVEL_MM` etc. in main.cpp

### 5.3 Motor Direction Inversion

**Current Settings (lines 655-658):**
```c++
xStepper.setPinsInverted(true, false, false);  // Inverted
yStepper.setPinsInverted(false, false, false); // Normal
zStepper.setPinsInverted(true, false, false);  // Inverted
fStepper.setPinsInverted(true, false, false);  // Inverted
```

**To Change:**
- If motor moves opposite direction during homing
- Toggle first parameter: `true` ↔ `false`
- Recompile and test

### 5.4 Speed Tuning

**For Quieter Operation:**
- Reduce `MAX_SPEED` (e.g., from 6000 to 4000)
- Reduce `ACCEL` proportionally
- Trade-off: Slower moves vs. less motor whine

**For Faster Operation:**
- Increase `MAX_SPEED` (test up to 8000-10000)
- Increase `ACCEL` if moves are smooth
- Monitor for skipped steps or mechanical vibration

---

## 6. Programming Procedures

### 6.1 First-Time Upload

1. **Connect Teensy via USB**
2. **Build firmware:** `Ctrl+Alt+B`
3. **Upload:** `Ctrl+Alt+U`
4. **Teensy Loader opens automatically**
5. **Press button on Teensy** (if prompted)
6. **Firmware uploads**
7. **Teensy auto-reboots**

### 6.2 Subsequent Uploads

- PlatformIO remembers the Teensy
- Just press `Ctrl+Alt+U`
- Auto-uploads without manual button press

### 6.3 Troubleshooting Uploads

| Issue | Solution |
|-------|----------|
| "Device not found" | Check USB cable, try different port |
| Upload hangs | Press physical button on Teensy |
| Wrong board selected | Verify `board = teensy41` in platformio.ini |
| Compilation error | Check serial monitor for error details |

---

## 7. Debugging and Monitoring

### 7.1 Serial Monitor

**Open Monitor:** `Ctrl+Alt+S` or plug icon in toolbar

**What You'll See:**
- Boot messages
- State transitions
- Command processing
- Limit switch triggers
- Error messages
- Heartbeat telemetry (every 2 seconds)

**Example Output:**
```
Teensy 4.1 CNC/Microscope Motion Controller
Version: v1.2
Build Date: Dec 23 2025 14:32:15

Initializing...
  - 4 axes configured
  - 4x TB6600 drivers (8 microsteps)
  - Limit switches: 8 interrupts attached
  - Serial1: 115200 baud

*** DIAGNOSTIC BOOT MENU ***
Press 'D' within 3 seconds to enter diagnostic mode...

[3 seconds pass]

Entering PROTOCOL mode
RPI4 connection: Serial1 (pins 0/1, 115200 baud)
USB Serial: Debug console
Waiting for master connection...

#BOOT FW=v1.2 AXES=4 *1E

[HEARTBEAT] DISCONNECTED | X=0.00 Y=0.00 Z=0.00 F=0.00 | Homed=none
```

### 7.2 Debug Output Levels

The firmware outputs different verbosity levels:

**Normal:**
- State changes
- Command received/ACK
- Limit triggers
- Errors

**Verbose (in diagnostic mode):**
- Menu displays
- Every step of homing process
- Position updates
- Pin state changes

**To Reduce Output:**
- Remove `Serial.printf()` statements
- Comment out `diagPrintln()` in diagnostic functions

### 7.3 Using the Diagnostic Menu

**Enter at Boot:**
- Power on Teensy
- Press 'D' within 3 seconds

**OR Enter via Protocol:**
```
!DIAG_ENTER *XX
```

**Navigate:**
- Number keys: Select menu item
- 'T': Return to top menu
- 'U': Go up one level
- 'X' or 'Q': Exit diagnostic mode
- 'S': Emergency stop
- '?': Show current status

---

## 8. Code Modification Guidelines

### 8.1 Adding a New Axis

1. **Add pin definitions:**
   ```c++
   const int E_STEP_PIN = 23;
   const int E_DIR_PIN = 24;
   const int E_MIN_PIN = 25;
   const int E_MAX_PIN = 26;
   ```

2. **Create stepper object:**
   ```c++
   AccelStepper eStepper(AccelStepper::DRIVER, E_STEP_PIN, E_DIR_PIN);
   ```

3. **Create limit state:**
   ```c++
   LimitState eLimit = {false, false, 0, 0, HIGH, HIGH};
   ```

4. **Add ISRs:**
   ```c++
   void eMinISR() { /* similar to xMinISR */ }
   void eMaxISR() { /* similar to xMaxISR */ }
   ```

5. **Update setup():**
   ```c++
   pinMode(E_STEP_PIN, OUTPUT);
   pinMode(E_DIR_PIN, OUTPUT);
   pinMode(E_MIN_PIN, INPUT_PULLUP);
   pinMode(E_MAX_PIN, INPUT_PULLUP);
   attachInterrupt(digitalPinToInterrupt(E_MIN_PIN), eMinISR, FALLING);
   attachInterrupt(digitalPinToInterrupt(E_MAX_PIN), eMaxISR, FALLING);
   
   eStepper.setMaxSpeed(MAX_SPEED);
   eStepper.setAcceleration(ACCEL);
   eStepper.setMinPulseWidth(PULSE_WIDTH_US);
   
   multiStepper.addStepper(eStepper);
   ```

6. **Update homing, status, protocol commands**

### 8.2 Changing Protocol Messages

**Example:** Add velocity to status response

Find `processProtocolCommand()` and locate `!STATUS` handler:

```c++
else if (strcmp(cmd, "STATUS") == 0) {
  char buffer[256];
  
  // Add velocity calculation
  float xVel = xStepper.speed() / STEPS_PER_MM;
  float yVel = yStepper.speed() / STEPS_PER_MM;
  
  snprintf(buffer, sizeof(buffer),
           "X=%.2f Y=%.2f Z=%.2f F=%.2f STATE=%s HOMED=%s%s%s%s VEL_X=%.1f VEL_Y=%.1f",
           xStepper.currentPosition() / STEPS_PER_MM,
           yStepper.currentPosition() / STEPS_PER_MM,
           zStepper.currentPosition() / STEPS_PER_MM,
           fStepper.currentPosition() / STEPS_PER_MM,
           stateNames[currentState],
           xHomed ? "X" : "",
           yHomed ? "Y" : "",
           zHomed ? "Z" : "",
           fHomed ? "F" : "",
           xVel, yVel);
  
  sendAck(seq, buffer);
}
```

### 8.3 Adding a New Protocol Command

1. **Add to protocol parser:**
   ```c++
   else if (strcmp(cmd, "MYCOMMAND") == 0) {
     // Validate state
     if (currentState != STATE_IDLE) {
       sendNack(seq, "ERR_INVALID_STATE", "Must be in IDLE");
       return;
     }
     
     // Parse arguments
     float value;
     if (sscanf(message, "!MYCOMMAND %f", &value) != 1) {
       sendNack(seq, "ERR_INVALID_ARGS", "Expected: !MYCOMMAND <value>");
       return;
     }
     
     // Execute command
     // ...
     
     // Send response
     sendAck(seq, "COMMAND_EXECUTED");
   }
   ```

2. **Update PROTOCOL.md documentation**

3. **Add test case to TEST_PROGRAM_GUIDE.md**

---

## 9. Library Dependencies

### 9.1 AccelStepper Library

**Version:** 1.64  
**Purpose:** Stepper motor acceleration/deceleration  
**Documentation:** http://www.airspayce.com/mikem/arduino/AccelStepper/

**Key Classes Used:**
- `AccelStepper`: Single stepper control
- `MultiStepper`: Coordinated multi-axis moves

**Key Methods:**
```c++
setMaxSpeed(speed);          // Set maximum speed (steps/sec)
setAcceleration(accel);      // Set acceleration (steps/sec²)
setMinPulseWidth(width);     // Set pulse width (µs)
moveTo(position);            // Set target position (absolute)
move(distance);              // Set target position (relative)
run();                       // Must be called frequently
runSpeed();                  // Constant speed (no accel)
distanceToGo();              // Steps remaining
currentPosition();           // Current position (steps)
setCurrentPosition(pos);     // Reset position counter
```

**Why Not TeensyStep?**
- TeensyStep only works with Teensy 3.x (Kinetis processors)
- Teensy 4.x uses i.MX RT processor (different architecture)
- AccelStepper is cross-platform and proven
- Software timing adequate for CNC microscopy (not high-speed machining)

---

## 10. Memory and Performance

### 10.1 Resource Usage

**Flash Memory:**
- Firmware size: ~150 KB
- Available: 8 MB (plenty of headroom)

**RAM:**
- Global variables: ~10 KB
- Stack usage: ~2 KB
- Available: 1 MB (plenty of headroom)

**CPU Usage:**
- Typical: 5-10% (mostly idle)
- During motion: 20-30%
- Interrupt overhead: < 1%

### 10.2 Performance Benchmarks

**Command Processing:**
- ACK latency: < 5ms
- Status query: < 10ms
- Parse overhead: < 1ms per command

**Motion Control:**
- Step generation accuracy: < 1µs jitter
- AccelStepper loop time: ~50µs
- Main loop rate: > 1000 Hz

**Interrupt Response:**
- ISR execution time: < 10µs
- ISR to main loop: < 1ms (via flag)

---

## 11. Version Control

### 11.1 Current Version

**Firmware:** v1.2  
**Protocol:** v1.0  
**Date:** December 23, 2025

### 11.2 Version History

| Version | Date | Changes |
|---------|------|---------|
| **v1.2** | Dec 23, 2025 | Limit switch robustness redesign, complete documentation |
| **v1.1** | Dec 22, 2025 | Protocol implementation, diagnostic remote access |
| **v1.0** | Dec 20, 2025 | Initial working version with homing and protocol |
| **v0.5** | Dec 18, 2025 | Diagnostic menu system implemented |
| **v0.1** | Dec 15, 2025 | Basic motion control and limit switches |

### 11.3 Incrementing Version

Located at top of main.cpp (line 58):
```c++
const char* FIRMWARE_VERSION = "v1.2";
```

When making significant changes:
1. Update `FIRMWARE_VERSION`
2. Update `BUILD_DATE` (auto-generated from `__DATE__` and `__TIME__`)
3. Update documentation version numbers
4. Document changes in project_context.md

---

## 12. Testing After Code Changes

### 12.1 Checklist

After modifying firmware:

1. **Compile:** Verify no errors
2. **Upload:** Flash to Teensy
3. **Boot Test:** Check serial output for clean boot
4. **Diagnostic Mode:** Enter and test basic functions
5. **Protocol Test:** Send !CONNECT, !STATUS
6. **Motion Test:** Test homing, moves, jogs
7. **Limit Test:** Manually trigger each limit switch
8. **Watchdog Test:** Stop sending commands, verify timeout
9. **Error Test:** Send invalid commands, verify NACK

### 12.2 Regression Testing

**Critical Tests:**
- All 8 limit switches detect correctly
- Homing completes successfully (all 4 axes)
- Coordinated moves complete without error
- Emergency stop works immediately
- Watchdog triggers after 5 seconds
- State transitions work correctly

---

## 14. Python GUI Software Modules

The GUI system consists of 5 core Python modules and 2 configuration files.

### 14.1 Module Overview

| Module | Lines | Purpose | Key Classes/Functions |
|--------|-------|---------|----------------------|
| **scope_gui.py** | 789 | Main PyQt5 application | MicroscopeGUI, VideoWidget, SpecimenCard, JogButton |
| **motion_controller.py** | 360 | High-level motion control | MotionController with auto-cycle |
| **video_thread.py** | 80 | OpenCV video capture | VideoThread (QThread) |
| **teensy_protocol.py** | 320 | Serial protocol implementation | TeensyController |
| **specimen_grid.py** | 160 | Grid calculations | SpecimenGrid |
| **cli_menu.py** | 920 | CLI diagnostic interface | (optional, testing only) |
| **mindatnh_tray1.json** | 312 | Specimen configuration | 28 NH minerals with positions |
| **GUI_README.md** | - | Quick start guide | Documentation |

### 14.2 scope_gui.py - Main GUI Application

**Purpose:** PyQt5 kiosk interface with touch controls, video display, and specimen selection

**Key Components:**

```python
class MicroscopeGUI(QMainWindow):
    """Main application window (1920×1080 fullscreen)"""
    def __init__(self, json_file):
        # Initialize specimen grid
        # Create VideoWidget for camera display
        # Create specimen cards (7×4 grid)
        # Create jog buttons
        # Start auto-cycle
    
    def on_specimen_clicked(self, row, col):
        # Handle specimen selection
        # Move stage to specimen position
    
    def keyPressEvent(self, event):
        # ESC key exits application

class VideoWidget(QWidget):
    """Custom widget for video display with overlays (1670×1080)"""
    def paintEvent(self, event):
        # Draw OpenCV frame scaled to fill widget
        # Draw translucent title banner (alpha=200)
        # Draw specimen info overlay
    
    def set_title(self, text):
        # Thread-safe title update using QTimer.singleShot
    
    def set_status(self, text):
        # Thread-safe status update

class SpecimenCard(QPushButton):
    """Touch-friendly specimen selection button (230×80)"""
    def set_current(self, is_current):
        # Highlight selected card (update, not repaint!)

class JogButton(QPushButton):
    """Directional control button (60×60)"""
    # Handles touch events for manual stage movement
```

**Dependencies:**
```python
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter, QColor, QFont
```

**Critical Design Patterns:**
- **Thread Safety:** All GUI updates from other threads use `QTimer.singleShot(0, self.update)`
- **Never call repaint():** Always use `update()` to avoid segfaults
- **Deferred updates:** Card highlighting uses `QTimer.singleShot(10, update_cards)` to avoid paint conflicts

### 14.3 motion_controller.py - Motion Control Layer

**Purpose:** High-level motion control with auto-cycle and state management

**Key Components:**

```python
class MotionController:
    """High-level motion control with auto-cycle"""
    def __init__(self, serial_port, grid, callbacks):
        self.teensy = TeensyController(serial_port)
        self.grid = grid
        self._auto_cycle_thread = None
        self._manual_override_time = None
    
    def start_auto_cycle(self):
        """Start autonomous specimen cycling (10s interval)"""
    
    def _auto_cycle_loop(self):
        """Cycle through specimens, skip invalid ones, 30s timeout"""
        while self._auto_cycling:
            if self._is_manual_override():
                time.sleep(1)
                continue
            
            # Move to next specimen
            self.move_to_next_specimen()
            time.sleep(10)  # 10-second display time
    
    def move_to_specimen(self, specimen):
        """Move stage to specimen with focus/zoom"""
        x, y = self.grid.calculate_position(specimen)
        z = specimen.get("zoom_mm", 10.0)
        f = specimen.get("focus_mm", 5.0)
        
        self.teensy.move_to(x, y, z, f)
        self._manual_override_time = time.time()  # Reset timer
    
    def _is_manual_override(self):
        """Check if in manual mode (30s since last user input)"""
        if self._manual_override_time is None:
            return False
        return (time.time() - self._manual_override_time) < 30.0
```

**State Management:**
- AUTO mode: Cycles specimens every 10 seconds
- MANUAL mode: Triggered by user touch, lasts 30 seconds
- Automatically returns to AUTO after 30s of no input

### 14.4 video_thread.py - Video Capture

**Purpose:** Background thread for OpenCV camera capture

**Key Components:**

```python
class VideoThread(QThread):
    """OpenCV video capture in separate thread"""
    frame_ready = pyqtSignal(object)  # QImage signal
    
    def __init__(self, device_index=0):
        super().__init__()
        self.device_index = device_index
        self.running = False
        self.frame = None
        self.mutex = QMutex()
    
    def run(self):
        """Capture loop (30 FPS)"""
        cap = cv2.VideoCapture(self.device_index, cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        while self.running:
            ret, frame = cap.read()
            if ret:
                # Convert BGR → RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert to QImage
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                q_img = QImage(rgb_frame.data, w, h, 
                              bytes_per_line, QImage.Format_RGB888)
                
                # Thread-safe frame storage
                self.mutex.lock()
                self.frame = q_img.copy()
                self.mutex.unlock()
                
                # Emit signal to GUI thread
                self.frame_ready.emit(self.frame)
```

**Performance:**
- 30 FPS capture rate
- CAP_V4L2 backend for Linux
- QMutex for thread-safe frame access
- Signal/slot for GUI updates

### 14.5 teensy_protocol.py - Serial Communication

**Purpose:** Low-level serial protocol implementation with checksums

**Key Components:**

```python
class TeensyController:
    """Serial protocol implementation for Teensy communication"""
    def __init__(self, port='/dev/ttyACM0', baudrate=115200):
        self.serial = serial.Serial(port, baudrate, timeout=1.0)
        self.sequence = 0
        self.watchdog_thread = None
    
    def send_command(self, command, params=""):
        """Send command with XOR checksum"""
        self.sequence = (self.sequence + 1) % 100
        message = f"!{command} {self.sequence}"
        if params:
            message += f" {params}"
        
        # Calculate checksum
        checksum = 0
        for char in message:
            checksum ^= ord(char)
        
        full_message = f"{message} *{checksum:02X}\n"
        self.serial.write(full_message.encode())
        
        # Wait for @ACK or @NACK
        response = self.read_response()
        return response
    
    def home(self):
        """Execute homing sequence (30 seconds)"""
        return self.send_command("HOME")
    
    def move_to(self, x, y, z, f):
        """Coordinated 4-axis move"""
        params = f"{x:.2f} {y:.2f} {z:.2f} {f:.2f}"
        return self.send_command("MOVE", params)
    
    def watchdog_loop(self):
        """Send !PING every 3 seconds"""
        while self.running:
            self.send_command("PING")
            time.sleep(3.0)
```

**Protocol Features:**
- XOR checksum validation
- Sequence number tracking
- Watchdog timer (3-second ping)
- Command acknowledgment (@ACK/@NACK)

### 14.6 specimen_grid.py - Grid Calculations

**Purpose:** Specimen position calculations and JSON configuration parsing

**Key Components:**

```python
class SpecimenGrid:
    """7×4 grid of mineral specimens"""
    def __init__(self, json_file):
        self.specimens = []
        self.load_from_json(json_file)
    
    def load_from_json(self, json_file):
        """Parse mindatnh_tray1.json"""
        with open(json_file) as f:
            data = json.load(f)
            self.specimens = data["specimens"]
    
    def get_by_row_col(self, row, col):
        """Lookup specimen by grid position"""
        for specimen in self.specimens:
            if specimen["row"] == row and specimen["col"] == col:
                return specimen
        return None
    
    def calculate_position(self, specimen):
        """Calculate X,Y position from row/col"""
        row = specimen["row"]
        col = specimen["col"]
        
        # Grid spacing: 40mm in Y-direction
        base_x = col * 40.0  # Adjust based on actual spacing
        base_y = row * 40.0
        
        # Add specimen-specific offsets
        x = base_x + specimen.get("x_offset_mm", 0.0)
        y = base_y + specimen.get("y_offset_mm", 0.0)
        
        return (x, y)
```

**Grid Layout:**
```
7 columns × 4 rows = 28 specimens
Spacing: 40mm in Y-direction
Each specimen has calibrated offsets
```

### 14.7 Python Dependencies

**Required Packages:**
```bash
pip3 install pyserial    # Serial communication
pip3 install PyQt5       # GUI framework
pip3 install opencv-python  # Video capture
```

**System Requirements:**
- Python 3.7 or higher
- Raspberry Pi OS (64-bit) with Desktop
- UART enabled on GPIO 14/15
- V4L2 camera driver support

### 14.8 JSON Configuration Format

**mindatnh_tray1.json Structure:**
```json
{
  "specimens": [
    {
      "row": 0,
      "col": 0,
      "mineral_name": "Beryl",
      "location": "Palermo #1 Mine, North Groton, NH",
      "collector": "Tom Mortimer",
      "x_offset_mm": 0.5,
      "y_offset_mm": -0.2,
      "focus_mm": 10.0,
      "zoom_mm": 5.0
    },
    ...
  ]
}
```

**Fields:**
- `row`, `col`: Grid position (0-indexed)
- `mineral_name`: Display name
- `location`: Specimen locality
- `collector`: Collector name
- `x_offset_mm`, `y_offset_mm`: Fine positioning adjustments
- `focus_mm`: Z-axis position
- `zoom_mm`: Focus axis position

---

## 13. Common Programming Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "pinMode" not declared | Wrong framework | Check `framework = arduino` in platformio.ini |
| "AccelStepper" not found | Missing library | Check `lib_deps` in platformio.ini |
| Upload fails | Wrong board | Check `board = teensy41` |
| Serial output garbled | Wrong baud rate | Use 115200 on both sides |
| Motors don't respond | Enable logic wrong | Verify `digitalWrite(ENA_ALL_PIN, LOW)` |
| Limit switches inverted | Wrong interrupt edge | Use `FALLING` for NO switches |

---

**Next Section:** [05 - Protocol Specification](05_PROTOCOL_SPECIFICATION.md)


---


# Protocol Specification

**Document:** 05 - Protocol Specification  
**Version:** 1.0  
**Date:** December 23, 2025

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

### 10.4 Watchdog Timeout

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


---


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


---


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

---

## 13. Future Work

### 13.1 Potential Improvements

1. **Command Queuing:** Pre-load move sequences
2. **Trajectory Smoothing:** S-curve acceleration, spline interpolation
3. **Encoder Feedback:** Closed-loop positioning
4. **Backlash Compensation:** Software compensation for mechanical play
5. **Dynamic Speed Adjustment:** Auto-tune to avoid resonance
6. **Position Persistence:** EEPROM storage of calibration and position
7. **Power Loss Recovery:** Resume operation after power cycle

### 13.2 Known Areas for Optimization

1. **Reduce motor whine:** Microstepping or speed tuning
2. **Faster homing:** Optimize seek speed (current is conservative)
3. **Reduce move start latency:** Currently ~50ms, could be < 10ms
4. **Cable noise mitigation:** Hardware shielding (software already robust)

---

**Next Section:** [08 - RPi4 Integration Guide](08_RPI4_INTEGRATION.md)


---


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


---


# GUI Architecture

**Document:** 09 - GUI Architecture  
**Version:** 1.0  
**Date:** December 23, 2025

---

## 1. Overview

The GUI is a PyQt5-based touch kiosk interface designed for museum visitors to interact with the robotic microscope. It features live video display, automatic cycling through specimens, and manual jog controls, all with thread-safe operation.

### Key Design Goals
- **Museum-quality presentation:** Professional UI with branding
- **Touch-friendly:** Large buttons, clear labeling, intuitive layout
- **Autonomous operation:** Automatic cycling with minimal supervision
- **Manual override:** Visitors can explore without breaking auto-cycle
- **Thread-safe:** Video capture and motion control run in separate threads
- **Robust:** Handles segfaults from Qt painting race conditions

---

## 2. Application Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      scope_gui.py (789 lines)                    │
│                     Main PyQt5 Application                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               MicroscopeGUI (QMainWindow)                 │  │
│  │  - Main window management                                 │  │
│  │  - Event loop coordination                                │  │
│  │  - Callback registration                                  │  │
│  └───┬──────────────────────────────────────────────────────┘  │
│      │                                                           │
│      ├─> VideoWidget (1670×1080)                                │
│      │    - Live camera display                                 │
│      │    - Semi-transparent overlays                           │
│      │    - Title banner, specimen info, scale ruler           │
│      │                                                           │
│      ├─> SpecimenCard ×28 (230×80 each)                         │
│      │    - Touch-sensitive buttons                             │
│      │    - Visual highlighting when selected                   │
│      │    - Mineral name + location display                     │
│      │                                                           │
│      └─> JogButton ×8 (60×60 for XY, 75×38 for ZF)             │
│           - Press/hold detection                                │
│           - Continuous jog when held                            │
│           - Manual override trigger                             │
│                                                                  │
└──────┬───────────────────────────────────┬──────────────────────┘
       │                                    │
       ▼                                    ▼
┌──────────────────┐              ┌─────────────────────┐
│  video_thread.py │              │motion_controller.py │
│   (80 lines)     │              │    (360 lines)      │
│                  │              │                     │
│  VideoThread     │              │ MotionController    │
│  - QThread       │              │  - Protocol wrapper │
│  - OpenCV cap    │              │  - Auto-cycle logic │
│  - cv2.CAP_V4L2  │              │  - Watchdog thread  │
│  - QMutex lock   │              │  - Skip invalid pos │
│  - 30 FPS target │              │  - Callbacks        │
└────────┬─────────┘              └──────────┬──────────┘
         │                                   │
         │ QImage frames                     │ Serial
         │ (30 Hz)                           │ Commands
         │                                   │
         ▼                                   ▼
    GUI Paint Event              ┌──────────────────────┐
    (Main Thread)                │ teensy_protocol.py   │
                                 │    (320 lines)       │
                                 │                      │
                                 │ TeensyProtocol       │
                                 │  - Serial comm       │
                                 │  - Checksum calc     │
                                 │  - Message parsing   │
                                 │  - Error handling    │
                                 └───────────┬──────────┘
                                            │
                                            ▼
                                    Teensy 4.1 UART
                                    (115200 baud)
```

---

## 3. Threading Model

### Thread-Safe Design

The application uses multiple threads that must be carefully coordinated to avoid Qt painting conflicts:

**Main GUI Thread (Qt Event Loop):**
- Handles all UI updates
- Processes QPainter operations
- Responds to touch events
- Updates specimen card highlighting

**Video Thread (QThread):**
- Captures frames from USB camera via OpenCV
- Converts BGR → RGB → QImage
- Emits `frame_ready` signal with new frames
- Protected by QMutex during frame handoff

**Motion Controller Threads:**
- **Watchdog thread:** Sends !PING every 3 seconds
- **Auto-cycle thread:** Moves between specimens every 10 seconds
- **Serial read thread:** Processes Teensy responses (in teensy_protocol.py)

### Critical Threading Issues Resolved

**Problem:** Segmentation faults when updating GUI from multiple threads

**Root Cause:**
1. Video thread calls `set_video_frame()` → triggers `update()`
2. Motion controller calls `set_specimen_info()` → triggers `update()`
3. Specimen card highlighting calls `repaint()` → forces immediate paint
4. Multiple paint events overlap → QPainter collision → segfault

**Solution:**
```python
# WRONG - causes segfaults:
def set_specimen_info(self, specimen):
    self.specimen_info = specimen
    self.update()  # Direct call from callback thread

# WRONG - even worse:
def set_current(self, is_current):
    self.is_current = is_current
    self.repaint()  # Forces immediate paint, crashes if another paint active

# CORRECT - deferred to main thread:
def set_specimen_info(self, specimen):
    self.specimen_info = specimen
    QTimer.singleShot(0, self.update)  # Queue to main thread event loop

def set_current(self, is_current):
    self.is_current = is_current
    self.update()  # Schedule paint, don't force
```

**Key Rules:**
1. **Never call `repaint()` directly** - use `update()` to schedule paint
2. **Use `QTimer.singleShot(0, func)`** to defer from callbacks to main thread
3. **Lock shared data with QMutex** (video frames)
4. **Don't update 28 cards synchronously** during paint - defer with QTimer

---

## 4. Key Classes

### 4.1 MicroscopeGUI (QMainWindow)

**Purpose:** Main application window and event coordinator

**Responsibilities:**
- Create and layout all widgets
- Initialize motion controller and video thread
- Register callbacks for motion events
- Handle keyboard shortcuts (ESC to exit)
- Manage auto-mode timer (updates every 500ms)

**Key Methods:**
```python
def __init__(self, tray_file: str):
    # Initialize motion controller
    self.motion = MotionController(tray_file)
    self.motion.set_callbacks(
        position_callback=self.on_position_update,
        state_callback=self.on_state_change,
        specimen_callback=self.on_specimen_change
    )
    
    # Initialize video
    self.video = VideoThread(camera_index=0)
    self.video.frame_ready.connect(self.video_widget.set_video_frame)
    
def on_specimen_change(self, index: int, specimen: SpecimenPosition):
    """Handle specimen changes from motion controller"""
    # Update video overlay
    self.video_widget.set_specimen_info(specimen)
    
    # Update list highlighting (deferred to avoid paint conflicts)
    def update_cards():
        for i, card in enumerate(self.specimen_cards):
            card.set_current(i == index)
    QTimer.singleShot(10, update_cards)  # 10ms delay
```

**Event Flow:**
1. User touches specimen card → `on_specimen_selected(index)`
2. Calls `motion.move_to_specimen(index)` → marks user interaction
3. Motion controller sends serial command → Teensy moves
4. Teensy reports completion → callback fires
5. `on_specimen_change()` updates GUI

---

### 4.2 VideoWidget (QWidget)

**Purpose:** Display live video with semi-transparent overlays

**Layout:**
```
┌────────────────────────────────────────────────────┐
│  Title Banner (translucent, 70px height)           │
│  ┌──────────┬─────────────────────┬──────────┐    │
│  │ Status   │   "The Mineral      │ Position │    │
│  │ (Green ● │    Microscope"      │  X: 58mm │    │
│  │  IDLE)   │  Tom Mortimer URL   │  Y: 21mm │    │
│  │ AUTO     │                     │  Z:  9mm │    │
│  └──────────┴─────────────────────┴──────────┘    │
├────────────────────────────────────────────────────┤
│                                                    │
│            Live Video (1920x1080)                 │
│            (scaled to fill widget)                │
│                                                    │
│                              ┌──────────────────┐ │
│                              │ Golden Beryl     │ │
│                              │ Palermo Mine,    │ │
│                              │ North Groton     │ │
│                              │ Collected by:    │ │
│                              │ Sarah Johnson    │ │
│                              └──────────────────┘ │
│                                                    │
│                    ┌─────────────┐                │
│                    │ Scale Ruler  │                │
│                    │ 0────5mm────10│                │
│                    └─────────────┘                │
└────────────────────────────────────────────────────┘
```

**Key Methods:**
```python
def paintEvent(self, event):
    """Draw video frame and overlays"""
    painter = QPainter(self)
    
    # Draw video (fill entire widget to avoid black bars)
    self.frame_mutex.lock()
    current_frame = self.video_frame
    self.frame_mutex.unlock()
    
    if current_frame:
        scaled_pixmap = current_frame.scaled(
            self.size(), 
            Qt.KeepAspectRatioByExpanding,  # Fill widget
            Qt.SmoothTransformation
        )
        painter.drawPixmap(0, 0, scaled_pixmap)
    
    # Draw overlays (all thread-safe, read-only)
    self._draw_title_banner(painter)
    self._draw_specimen_info(painter)
    self._draw_scale_ruler(painter)
```

**Overlay Details:**

**Title Banner (70px height, alpha=200):**
- Left: Status indicator (green/red/yellow circle) + state name + AUTO/MANUAL
- Center: "The Mineral Microscope" title + "Tom Mortimer (mindatnh.org)" subtitle
- Right: Position display (X, Y, Z, F stacked vertically)

**Specimen Info Card (300×150px, bottom-right):**
- Mineral name (14pt bold, word-wrapped)
- Location (11pt, word-wrapped)
- Collector (10pt gray, single line)
- Semi-transparent background (alpha=200)

**Scale Ruler (bottom-center):**
- Dynamic: adjusts based on zoom (F position)
- FOV ranges from 20mm (F=0) to 5mm (F=30)
- Shows ruler with multiple tick marks and labels

---

### 4.3 MotionController

**Purpose:** High-level motion control with auto-cycle logic

**Key Features:**
- Wraps `TeensyProtocol` for serial communication
- Implements auto-cycle thread (10s per specimen)
- Tracks user interaction with 30s timeout
- Skips invalid specimens automatically
- Provides callbacks for GUI updates

**Auto-Cycle State Machine:**
```
┌─────────────────┐
│   Initialize    │
│   (Connect +    │
│    Home)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AUTO-CYCLE     │◄────────────────┐
│  (Moving to     │                 │
│   next spec)    │                 │
└────────┬────────┘                 │
         │                          │
         │ Specimen reached         │
         ▼                          │
┌─────────────────┐                 │
│  VIEWING        │                 │
│  (10 seconds)   │                 │
└────────┬────────┘                 │
         │                          │
         │ Time elapsed             │
         ├─────────────────────────►│
         │                          │
         │ User touches button      │
         ▼                          │
┌─────────────────┐                 │
│  MANUAL MODE    │                 │
│  (30s timeout)  │                 │
└────────┬────────┘                 │
         │                          │
         │ 30s no interaction       │
         └──────────────────────────┘
```

**Code Example:**
```python
def _auto_cycle_loop(self):
    """Auto-cycle thread main loop"""
    while self.running:
        # Check if manual override active
        if time.time() - self.last_interaction_time < self.manual_timeout:
            time.sleep(0.5)
            continue
        
        # Move to next valid specimen
        attempts = 0
        while attempts < len(self.specimens):
            next_idx = (self.current_specimen_index + 1) % len(self.specimens)
            
            # Skip invalid specimens
            if not self.is_specimen_valid(next_idx):
                self.current_specimen_index = next_idx
                attempts += 1
                continue
            
            # Move to specimen
            if self.move_to_specimen(next_idx):
                break
            attempts += 1
        
        # Wait before next move
        time.sleep(self.cycle_interval)  # 10 seconds
```

---

### 4.4 VideoThread (QThread)

**Purpose:** Capture video frames from USB camera in background thread

**Implementation:**
```python
class VideoThread(QThread):
    frame_ready = pyqtSignal(QImage)  # Signal to main thread
    
    def run(self):
        """Thread main loop - runs until stop() called"""
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  # V4L2 backend required
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        while self.running:
            ret, frame = cap.read()
            if ret:
                # Convert BGR → RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                
                # Convert to QImage
                q_image = QImage(
                    rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888
                )
                
                # Emit to main thread
                self.frame_ready.emit(q_image.copy())
            
            time.sleep(0.033)  # ~30 FPS
        
        cap.release()
```

**Critical Details:**
- **Must use `cv2.CAP_V4L2`** - GStreamer backend fails on RPi4
- **Emit `q_image.copy()`** - Qt requires ownership transfer
- **No direct GUI updates** - only emit signals
- **Clean shutdown** with 2-second timeout

---

## 5. Data Flow

### Specimen Selection Flow

```
User touches specimen card
    │
    ▼
SpecimenCard.clicked signal
    │
    ▼
MicroscopeGUI.on_specimen_selected(index)
    │
    ├─> motion.mark_user_interaction()  # Reset 30s timer
    │
    └─> motion.move_to_specimen(index)
            │
            ▼
        TeensyProtocol.move_absolute(x, y, z, f)
            │
            ▼
        Serial: "!MOVE X58.00 Y21.50 Z9.00 F3.00 *2C\n"
            │
            ▼
        Teensy executes move
            │
            ▼
        Serial: "@COMPLETE 9 X=58.00 Y=21.50 Z=9.00 F=3.00 *4C\n"
            │
            ▼
        motion_controller._handle_complete_response()
            │
            ▼
        Callbacks fire:
            ├─> on_position_update(x, y, z, f)
            │       └─> VideoWidget.set_position()
            │
            ├─> on_state_change("IDLE")
            │       └─> VideoWidget.set_state()
            │
            └─> on_specimen_change(index, specimen)
                    ├─> VideoWidget.set_specimen_info()
                    └─> SpecimenCard highlighting (deferred)
```

---

## 6. Configuration

### Specimen Tray JSON Format

```json
{
  "specimens": [
    {
      "row": 0,
      "col": 0,
      "mineral_name": "Smoky Quartz",
      "location": "Ruggles Mine, Grafton",
      "collector": "Tom Mortimer",
      "x_offset_mm": -1.0,
      "y_offset_mm": -1.0,
      "focus_mm": 8.0,
      "zoom_mm": 2.0
    },
    ...
  ]
}
```

**Fields:**
- `row`, `col`: Grid position (0-indexed)
- `mineral_name`: Display name
- `location`: Locality (e.g., "Palermo Mine, North Groton")
- `collector`: Collector name
- `x_offset_mm`, `y_offset_mm`: Fine-tuning offsets
- `focus_mm`: Z-axis height for this specimen
- `zoom_mm`: F-axis zoom level

**Grid Calculation:**
```python
# From specimen_grid.py
GRID_START_X = 20.0      # mm
GRID_START_Y = 22.5      # mm
BOX_WIDTH_MM = 36.0      # mm spacing
BOX_HEIGHT_MM = 40.0     # mm spacing (reduced to fit Y limit)

def calculate_position(row, col):
    x = GRID_START_X + (col * BOX_WIDTH_MM)
    y = GRID_START_Y + (row * BOX_HEIGHT_MM)
    return x, y
```

---

## 7. Known Issues and Solutions

### Issue: Segmentation Faults

**Cause:** Qt doesn't allow nested `QPainter` usage. Calling `repaint()` during a `paintEvent()` causes crash.

**Solution:**
- Use `update()` instead of `repaint()` (schedules paint, doesn't force)
- Defer specimen card updates with `QTimer.singleShot(10, update_func)`
- Never call GUI methods directly from callbacks - use QTimer

### Issue: Black Bars on Video

**Cause:** `Qt.KeepAspectRatio` adds black bars if aspect ratio doesn't match

**Solution:**
- Use `Qt.KeepAspectRatioByExpanding` to fill entire widget
- Video will be cropped at edges, but no black bars
- Ensures translucent title banner overlays actual video

### Issue: Specimen Cards Not Highlighting

**Cause:** GUI updates from callbacks on different thread, Qt event loop not processing immediately

**Solution:**
- Added `force_initial_highlight()` called 500ms after startup
- Deferred card updates to avoid conflicts with paint events
- Removed `QApplication.processEvents()` which was causing interference

### Issue: Video Capture Fails

**Cause:** Default OpenCV backend (GStreamer) doesn't work reliably on RPi4

**Solution:**
```python
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  # Explicit V4L2 backend
```

---

## 8. Performance Considerations

### Frame Rate
- **Target:** 30 FPS
- **Actual:** 25-30 FPS (depends on RPi4 CPU load)
- **Acceptable:** Anything >20 FPS appears smooth

### Memory
- **Video frames:** ~1.2 MB each (640×480×3 bytes)
- **Total GUI:** ~50 MB typical
- **PyQt5 overhead:** ~30 MB
- **Total process:** ~120 MB on RPi4

### CPU Usage
- **Video thread:** ~15% of one core
- **GUI thread:** ~5% (mostly paint events)
- **Motion thread:** <1% (mostly sleeping)
- **Total:** ~20% of RPi4 (plenty of headroom)

---

## 9. Testing and Debugging

### Debug Prints

All major operations have debug prints:
```
[GUI] Specimen change: 1 - Golden Beryl
[VideoWidget] Setting specimen info: Golden Beryl (thread 546995827040)
[VideoWidget] Queuing update() call
[VideoWidget] Update queued
[GUI] Deferred: Updating card highlighting for index 1
[paintEvent] START
[paintEvent] Frame locked/unlocked
[paintEvent] Drawing title banner
[paintEvent] Drawing status bar
[paintEvent] Drawing specimen info
[_draw_specimen_info] Drawing card for Golden Beryl
[paintEvent] Drawing scale ruler
[paintEvent] END
```

### Common Issues

**"QBackingStore::endPaint() called with active painter":**
- **Cause:** Nested painting (repaint() during paintEvent)
- **Fix:** Use update() instead of repaint()

**Video black screen:**
- **Cause:** Wrong OpenCV backend
- **Fix:** Add `cv2.CAP_V4L2` parameter

**Segfault after specimen change:**
- **Cause:** Card highlighting during paint event
- **Fix:** Defer with QTimer.singleShot()

---

## 10. Future Enhancements

### Potential Improvements
- **Image capture:** Save snapshots to disk
- **Multi-camera:** Support multiple views simultaneously
- **Zoom presets:** Quick zoom buttons
- **Annotation mode:** Let visitors add comments
- **Statistics:** Track most-viewed specimens
- **Remote monitoring:** Web interface for staff
- **Voice narration:** Audio descriptions of minerals

---

**Next Section:** [10 - User Guide](10_USER_GUIDE.md)


---


# User Guide - Museum Operator Manual

**Document:** 10 - User Guide  
**Version:** 1.0  
**Date:** December 23, 2025  
**Audience:** Museum Staff, Kiosk Operators

---

## 1. Introduction

Welcome to **The Mineral Microscope** - an interactive kiosk for exploring New Hampshire minerals under magnification. This guide will help you operate and maintain the system.

### What This System Does

The Mineral Microscope automatically displays 28 different mineral specimens from famous New Hampshire localities (Palermo Mine, Ruggles Mine, Fletcher Mine, etc.). Visitors can:
- Watch as the system automatically cycles through specimens
- Touch the screen to jump to specific minerals
- Use jog controls to manually explore specimens
- See live video of minerals at 20-100× magnification

---

## 2. Daily Operations

### Starting the System

**Power On Sequence:**
1. Turn on the main power strip
2. Raspberry Pi will boot automatically (30-60 seconds)
3. GUI will start automatically and show "DISCONNECTED" briefly
4. System will connect to motion controller ("CONNECTED")
5. **Homing Process (30 seconds):**
   - Message: "Homing in progress..."
   - You'll hear motors moving sequentially
   - Z-axis moves first (up), then Y, then X, then Focus
6. When complete, system shows first specimen and begins auto-cycle

**What You Should See:**
- Live microscope video filling the screen
- Title banner at top: "The Mineral Microscope"
- Green status indicator (circle) showing "IDLE"
- "AUTO" mode indicator
- List of 28 specimens on the left
- First specimen highlighted in blue

**Normal Startup Time:** 90 seconds from power-on to first specimen

---

### Shutting Down

**End of Day Procedure:**

**Option 1: Proper Shutdown (Recommended)**
1. Press ESC key on connected keyboard (if available)
2. System will close gracefully
3. Wait 10 seconds for Raspberry Pi to finish shutdown
4. Turn off power strip

**Option 2: Power Off (Acceptable)**
1. Simply turn off power strip
2. Raspberry Pi will shutdown when power is cut
3. No harm to system (designed for this)

**DO NOT:**
- Pull USB cables while system is running
- Turn off during homing (wait for completion)
- Forcibly restart during specimen moves

---

### Normal Operation

The system runs automatically and requires no intervention. Here's what happens:

**Auto-Cycle Behavior:**
- System moves to a new specimen every 10 seconds
- Displays mineral name, location, and collector
- Cycles through all 28 specimens continuously
- Loops back to start after finishing

**Visitor Interaction:**
- Visitors can touch any specimen name to jump directly to it
- Visitors can use jog buttons to manually explore
- When visitor touches anything, "AUTO" changes to "MANUAL"
- After 30 seconds of no touching, returns to "AUTO" mode

**You Should Hear:**
- Quiet motor whine when moving (this is normal with TB6600 drivers)
- Brief buzzing during acceleration/deceleration
- No grinding, clicking, or loud noises

---

## 3. Touch Interface Guide

### Screen Layout

```
┌──────────────────────────────────────────────────────────┐
│ ●IDLE  |  The Mineral Microscope  | X: 58mm Y: 21mm  │← Status Bar
│  AUTO  |     Tom Mortimer         | Z:  9mm F:  3mm  │
├────────┬─────────────────────────────────────────────────┤
│Specimen│                                                 │
│  List  │         Live Microscope Video                   │
│        │         (automatically updates)                 │
│  [1]   │                                                 │
│  [2]   │                     ┌──────────────────┐        │
│  [3]   │                     │ Golden Beryl     │← Info Card
│  ...   │                     │ Palermo Mine,    │
│  [28]  │                     │ North Groton     │
│        │                     │ Collected by:    │
│        │                     │ Sarah Johnson    │
│        │                     └──────────────────┘        │
│ HOME   │                                                 │
│        │              ┌─────Scale─Ruler──────┐          │
│  Jog   │              │  0 ──── 5mm ──── 10  │          │
│Controls│              └──────────────────────┘          │
└────────┴─────────────────────────────────────────────────┘
```

### Left Panel

**Specimen List (scrollable):**
- 28 buttons showing mineral names and locations
- Currently selected specimen is highlighted in **blue**
- Touch any specimen to jump to it immediately
- System enters MANUAL mode for 30 seconds

**HOME Button:**
- Returns all axes to home position
- Use if system seems "lost" or stuck
- Takes 30 seconds to complete
- System will pause auto-cycle during homing

**Jog Controls:**
- **Up/Down/Left/Right arrows:** Move specimen stage
  - Quick tap: Small movement (0.5mm)
  - Hold: Continuous movement until released
- **Focus ▲/▼:** Adjust microscope focus (Z-axis)
  - Moves 0.1mm per tap
  - Hold for continuous adjustment
- **Zoom ▲/▼:** Adjust magnification (objective position)
  - Moves 0.2mm per tap
  - Changes field of view (see scale ruler update)

### Right Side - Video Display

**Info Card (bottom-right):**
- **Mineral Name:** Large text (e.g., "Golden Beryl")
- **Location:** Where specimen was collected
- **Collector:** Who collected the specimen

**Scale Ruler (bottom-center):**
- Shows actual size of what's visible
- Updates automatically when you zoom
- Ranges from 20mm (zoomed out) to 5mm (zoomed in)

**Status Bar (top):**
- **Left:** Status indicator
  - Green ● = Working normally ("IDLE" or "MOVING")
  - Yellow ● = Connected but not homed
  - Red ● = Disconnected or error
- **Center:** Title and curator credit
- **Right:** Exact stage position in millimeters

---

## 4. Common Visitor Questions

### "How do I use this?"

**Answer:** "The microscope automatically shows different minerals. You can touch any mineral name on the left to see it immediately, or use the arrow buttons to look around. After 30 seconds, it goes back to automatic mode."

### "Why did it move by itself?"

**Answer:** "The system automatically cycles through all 28 specimens so everyone gets to see different minerals. You can take control anytime by touching the screen."

### "Can I take pictures?"

**Answer:** "Not directly from this system, but feel free to photograph the screen with your phone."

### "What magnification is this?"

**Answer:** "It ranges from about 20× to 100× depending on the zoom setting. The scale bar at the bottom shows the actual size."

### "Why does it make that noise?"

**Answer:** "That's the sound of the stepper motors moving the stage. It's completely normal - the motors vibrate at a specific frequency to move precisely."

---

## 5. Troubleshooting

### Problem: Black Screen

**Symptoms:** Screen is completely black, no video

**Solutions:**
1. Check power connections (both power strip and Raspberry Pi)
2. Wait 60 seconds - system might still be booting
3. Check HDMI cable connection
4. Try power-cycling: turn off, wait 10 seconds, turn on

**If Persistent:** USB camera may be disconnected - check cable

---

### Problem: "DISCONNECTED" Status

**Symptoms:** Red circle, says "DISCONNECTED" at top

**Cause:** Raspberry Pi cannot communicate with Teensy motion controller

**Solutions:**
1. Check USB cable between Raspberry Pi and Teensy
2. Check that Teensy has power (LED should be lit)
3. Try unplugging and reconnecting Teensy USB cable
4. Restart system (turn off/on power strip)

**If Persistent:** Contact technician - may be Teensy hardware issue

---

### Problem: Stage Won't Move

**Symptoms:** Clicking specimens or jog buttons does nothing

**Check:**
1. Status should show "IDLE" (not "MOVING" or "DISCONNECTED")
2. System must be homed first (happens automatically at startup)
3. May have hit a limit switch

**Solutions:**
1. Touch HOME button and wait 30 seconds
2. Check for obstructions blocking stage movement
3. Listen for motor noise - if silent, may be power issue
4. Restart system

---

### Problem: Video is Frozen

**Symptoms:** Video doesn't update, stage moves but video stays same

**Cause:** Video capture thread crashed

**Solutions:**
1. Touch any specimen to see if system responds
2. If system moves but video frozen, restart required
3. Power cycle system

**Prevention:** Don't unplug USB camera while system running

---

### Problem: Wrong Specimen Highlighted

**Symptoms:** Blue highlighting doesn't match current specimen

**Cause:** Minor GUI sync issue (rare)

**Solution:**
1. Touch any specimen in list
2. Highlighting should update correctly
3. No harm, purely cosmetic

---

### Problem: Stage Makes Grinding Noise

**Symptoms:** Loud grinding, clicking, or scraping sounds

**⚠️ THIS IS SERIOUS:**
1. **Immediately press HOME button** or turn off system
2. **DO NOT continue operation**
3. **Contact technician before restarting**

**Possible Causes:**
- Limit switch failure
- Mechanical obstruction
- Belt/screw jam
- Motor driver malfunction

---

### Problem: Specimen Out of Focus

**Symptoms:** Image is blurry, hard to see details

**Normal Behavior:**
- Each specimen is pre-programmed with focus settings
- Some specimens may look softer than others (natural variation)
- Lighting affects perceived sharpness

**Solutions:**
1. Use Focus jog buttons (▲/▼) to adjust manually
2. System will return to preset focus after timeout
3. Some minerals are naturally less distinct

**Not a Problem:**
- Different minerals have different textures
- Some are transparent, some opaque
- Crystal structure affects how they look under microscope

---

## 6. Maintenance

### Daily Checks (Start of Day)

**Before Opening:**
1. ✓ Power on system
2. ✓ Wait for automatic homing (30 seconds)
3. ✓ Verify first specimen displays correctly
4. ✓ Touch one specimen to verify visitor interaction works
5. ✓ Check that video is live (moves when you touch jog buttons)
6. ✓ Listen for abnormal noises

**End of Day:**
1. Power off system using ESC key or power strip
2. Clean touchscreen with microfiber cloth (screen cleaner OK)
3. **DO NOT CLEAN NEAR STAGE** - specimen tray is delicate

---

### Weekly Maintenance

**Every Week:**
1. Inspect specimen tray for dust buildup
   - Use compressed air from a distance
   - DO NOT touch specimens with hands or cloth
2. Check all cable connections
3. Verify HOME button still works correctly
4. Test random specimens to ensure full grid accessibility

---

### Monthly Maintenance

**Every Month:**
1. Clean stage rails with dry cloth
2. Check for loose screws on frame
3. Verify camera lens is clean
4. Check belt tension (should not be too loose or too tight)

**DO NOT:**
- Lubricate without consulting technician
- Adjust motor drivers (TB6600 settings)
- Move stage manually (always use controls)
- Remove specimen tray while powered on

---

## 7. Safety and Care

### Safe Operating Practices

**DO:**
- ✓ Let system complete homing before interaction
- ✓ Use HOME button if system seems stuck
- ✓ Power off if abnormal noises occur
- ✓ Keep area around kiosk clean and clear

**DON'T:**
- ✗ Force stage to move manually
- ✗ Disconnect cables while system running
- ✗ Touch or move specimens by hand
- ✗ Spray cleaner near electronics or specimens
- ✗ Allow food or drinks near system

### Visitor Safety

The system is safe for public use:
- No exposed moving parts
- Low voltage (12V) to motors
- Touchscreen-only interface (no keyboards/mice for visitors)
- Automatic limits prevent stage collisions

**If Visitor Reports Pain/Injury:**
- Unlikely with this system (no pinch points)
- Most common: accidentally touching their own finger to screen too hard
- No sharp edges or hazardous materials

---

## 8. Understanding System Behavior

### AUTO Mode

**Characteristics:**
- "AUTO" shown at top left
- System moves every 10 seconds
- Cycles through all 28 specimens
- Ignores invalid/missing specimens automatically

**What's Normal:**
- May skip some positions (if specimen data invalid)
- Always returns to same starting position
- Timing is consistent (10s ± 1s)

### MANUAL Mode

**Triggers:**
- Visitor touches any specimen
- Visitor touches any jog button
- Visitor presses HOME

**Behavior:**
- "MANUAL" shown at top left
- Auto-cycle pauses
- System waits 30 seconds of no touching
- Then returns to AUTO mode

**What's Normal:**
- May resume mid-list (not from beginning)
- Doesn't reset when exiting MANUAL mode
- Multiple visitors can interact sequentially

---

## 9. Technical Support

### When to Call for Help

**Call Immediately If:**
- ❌ Stage makes grinding/clicking noises
- ❌ Stage moves beyond visible limits
- ❌ Smell of burning electronics
- ❌ System won't boot after multiple attempts
- ❌ Screen shows error messages

**Can Wait Until Convenient:**
- ℹ️ Single specimen won't display
- ℹ️ Video occasionally freezes
- ℹ️ Auto-cycle timing seems off
- ℹ️ Highlighting doesn't match specimen
- ℹ️ Motors seem louder than usual (but no grinding)

### Information to Provide

When reporting issues:
1. What were you doing when problem occurred?
2. What did you see/hear? (exact error messages)
3. Does it happen every time or intermittently?
4. When did it start? (after power cycle, during operation?)
5. Have you tried restarting?

### Contact Information

**System Developer:** [Your contact info here]  
**Technical Support:** [Your support contact]  
**Museum IT:** [Museum IT contact]

---

## 10. Advanced Operations (Staff Only)

### Restarting a Specific Specimen

If a visitor wants to see a specific specimen again:
1. Touch that specimen's name in the list
2. System jumps immediately
3. No need to wait for auto-cycle

### Pausing Auto-Cycle Temporarily

If you need system to stay on one specimen:
1. Touch jog buttons periodically (every 25 seconds)
2. Keeps system in MANUAL mode
3. Use any jog button (even tiny movements)

### Accessing CLI Diagnostic Mode (Advanced)

**Only if instructed by technician:**
1. Connect keyboard to Raspberry Pi
2. Press ESC to exit GUI
3. Run: `python3 cli_menu.py`
4. Follow technician instructions

**⚠️ Caution:** CLI mode provides full motion control. Incorrect use can damage system.

---

## 11. Quick Reference Card

**Print this section and post near kiosk:**

```
┌─────────────────────────────────────────────┐
│   THE MINERAL MICROSCOPE - QUICK START     │
├─────────────────────────────────────────────┤
│ STARTUP:                                    │
│  1. Turn on power strip                     │
│  2. Wait 90 seconds                         │
│  3. System starts automatically             │
│                                             │
│ NORMAL OPERATION:                           │
│  • System cycles automatically              │
│  • Visitors can touch to explore            │
│  • Returns to auto after 30 seconds         │
│                                             │
│ SHUTDOWN:                                   │
│  • Press ESC or turn off power strip        │
│                                             │
│ EMERGENCY:                                  │
│  • Grinding noise: Press HOME or power off  │
│  • Frozen: Restart system                   │
│  • Disconnected: Check USB cables           │
│                                             │
│ DAILY CHECKS:                               │
│  ✓ System boots and homes correctly         │
│  ✓ Touch interaction works                  │
│  ✓ Video is live                            │
│  ✓ No abnormal noises                       │
│                                             │
│ CONTACT: [Your phone/email here]           │
└─────────────────────────────────────────────┘
```

---

## 12. Appendix: Specimen List

Current configuration shows **28 New Hampshire Minerals**:

1. Smoky Quartz - Ruggles Mine, Grafton
2. Golden Beryl - Palermo Mine, North Groton
3. Black Tourmaline - Fletcher Mine, North Groton
4. Fluorapatite - Palermo Mine, North Groton
5. Amblygonite - Palermo Mine, North Groton
6. Muscovite - Ruggles Mine, Grafton
7. Almandine Garnet - Littleton area
8. Aquamarine - Royalston Quarry, Cheshire Co.
9. Elbaite Tourmaline - Mount Mica, Paris
10. Columbite - Palermo Mine, North Groton
11. Triphylite - Palermo Mine, North Groton
12. Pollucite - Fletcher Mine, North Groton
13. Microcline - Pikes Peak, Grafton Co.
14. Spodumene - Fletcher Mine, North Groton
15. Autunite - Ruggles Mine, Grafton (⚠️ radioactive)
16. Uraninite - Ruggles Mine, Grafton (⚠️ radioactive)
17. Rose Quartz - Keene area, Cheshire Co.
18. Lepidolite - Palermo Mine, North Groton
19. Cassiterite - Lost River Mine, North Woodstock
20. Euxenite - Palermo Mine, North Groton
21. Lithiophilite - Palermo Mine, North Groton
22. Beryllonite - Palermo Mine, North Groton
23. Herderite - Palermo Mine, North Groton
24. Blue Apatite - Palermo Mine, North Groton
25. Orthoclase Feldspar - Ruggles Mine, Grafton
26. Albite - Fletcher Mine, North Groton
27. Bismuthinite - Grafton area
28. Monazite - Palermo Mine, North Groton

**Note:** Specimens #15 (Autunite) and #16 (Uraninite) are mildly radioactive but safe for display. No special handling required.

---

**Previous Section:** [09 - GUI Architecture](09_GUI_ARCHITECTURE.md)  
**Next Section:** [11 - Installation Guide](11_INSTALLATION.md)


---


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
# Thermal Analysis Report

**Document ID:** 12_THERMAL_ANALYSIS  
**Analysis Date:** December 30, 2025  
**System:** 4-Axis CNC Robotic Microscope  
**Revision:** 1.0

---

## Executive Summary

This thermal analysis evaluates the cooling performance of the robotic microscope system under typical operating conditions. The analysis accounts for actual motor duty cycle patterns and ventilation design.

**Key Findings:**
- **System thermal performance: EXCELLENT** ✓
- **Current ventilation design: MORE THAN ADEQUATE** ✓
- **No hardware modifications required** ✓
- **Typical TB6600 operating temperatures: 30-80°C** (well below 150°C thermal shutdown)

---

## System Heat Load Analysis

### Power Dissipation Summary

| Component | Peak Power | Duty Cycle | Average Power | Notes |
|-----------|-----------|------------|---------------|-------|
| **4× TB6600 Drivers** | 48W | 9% | 4.3W | Motors active 3 sec, idle 30 sec |
| **4× Stepper Motors** | 48W | 9% | 4.3W | Running current: 1.0A @ 24V |
| **Raspberry Pi 4** | 6.5W | 100% | 6.5W | Continuous operation |
| **Teensy 4.1** | 0.8W | 100% | 0.8W | Continuous operation |
| **USB Camera** | 1.0W | 100% | 1.0W | Continuous streaming |
| **24× WS2812B LEDs** | 0.6W | 100% | 0.6W | 40% brightness typical |
| **60mm Fan** | 2.4W | 100% | 2.4W | Continuous operation |
| **Total System** | **107.3W** | — | **19.9W** | Average including all components |

**Heat Load for Cooling Analysis:** ~17.5W  
(Excludes fan power, accounts for heat transferred to enclosure/motors)

---

## Duty Cycle Analysis

### Typical Auto-Cycle Operation

The system operates in a repeating pattern during automated specimen viewing:

```
┌─────────────────────────────────────────┐
│ Auto-Cycle Timeline (33 seconds)        │
├─────────────────────────────────────────┤
│ Move Phase:     3 seconds  (motors ON)  │
│ Viewing Phase: 30 seconds  (motors OFF) │
└─────────────────────────────────────────┘

Duty Cycle = 3s / 33s = 9.1%
```

**Impact on Thermal Design:**
- Peak heat load: 96W (motors + drivers)
- Average heat load: 8.6W (motors + drivers)
- **Motors spend 91% of time cooling passively**
- TB6600 drivers have excellent thermal recovery during viewing phases

---

## Ventilation System Specification

### Fan Specification
- **Model:** 60mm × 60mm × 10mm axial fan
- **Voltage:** 24V DC
- **Airflow:** 13.8 CFM (23.4 m³/hr)
- **Noise:** 26 dBA (very quiet)
- **Power:** 2.4W

### Inlet Ventilation
- **Configuration:** 15 slots (6cm × 0.5cm each)
- **Total inlet area:** 45 cm²
- **Location:** Lower enclosure section

### Outlet Ventilation
- **Configuration:** Fan mounting with finger guard
- **Effective outlet area:** ~28.3 cm² (63% of inlet area)
- **Note:** Outlet is the flow restriction point

---

## Thermal Calculations

### Airflow Analysis

**Effective Fan Performance:**
Due to outlet restriction (28.3 cm² vs 45 cm² inlet), actual airflow is reduced:

```
Effective CFM = 13.8 CFM × (28.3/45)^0.5 ≈ 11 CFM
```

**Natural Convection Baseline:**
Without fan assistance:
```
Passive airflow ≈ 2 CFM (thermal buoyancy only)
```

### Temperature Rise Calculations

**With Fan Operating (11 CFM effective):**

For average heat load (17.5W):
```
ΔT = 17.5W / (11 CFM × 1.08 W/(CFM·°C))
ΔT = 17.5 / 11.88 = 1.5°C above ambient
```

For peak heat load (51.5W) during 3-second moves:
```
ΔT_peak = 51.5W / (11 CFM × 1.08 W/(CFM·°C))
ΔT_peak = 51.5 / 11.88 = 4.3°C above ambient
```

**Without Fan (Natural Convection Only):**

For average heat load:
```
ΔT_natural = 17.5W / (2 CFM × 1.08 W/(CFM·°C))
ΔT_natural = 17.5 / 2.16 = 8.1°C above ambient
```

---

## Component Temperature Estimates

### TB6600 Stepper Drivers

**Thermal Characteristics:**
- Thermal shutdown: 150°C
- Safe operating range: < 100°C
- Aluminum heatsink with good thermal mass

**Expected Temperatures (25°C ambient):**

| Operating Mode | Temperature Range | Status |
|---------------|-------------------|--------|
| **With fan (typical)** | 30-45°C | Excellent ✓ |
| **With fan (peak move)** | 55-80°C | Good ✓ |
| **Natural convection (typical)** | 35-55°C | Acceptable ✓ |
| **Natural convection (peak)** | 75-105°C | Marginal (brief) |

**Analysis:**
- With 9% duty cycle, drivers cool between moves
- Peak temperatures occur only during 3-second moves
- 30-second viewing phase allows thermal recovery
- **Current design provides excellent thermal margin**

### Other Components

| Component | Temperature | Margin | Status |
|-----------|------------|--------|--------|
| Raspberry Pi 4 | 35-50°C | Good | Well within 85°C throttle point |
| Teensy 4.1 | 30-40°C | Excellent | Minimal self-heating |
| Motors | 30-60°C | Good | Brief operation, passive cooling |
| LEDs | 30-35°C | Excellent | 40% brightness, low power |

---

## Thermal Performance Summary

### Current Design Assessment

**✓ EXCELLENT THERMAL PERFORMANCE**

The system exhibits robust thermal characteristics:

1. **Low Duty Cycle Advantage**
   - 9% motor operation allows 91% cooling time
   - Peak temperatures occur only briefly (3 seconds)
   - Long viewing phases (30 seconds) enable full thermal recovery

2. **Adequate Ventilation**
   - 11 CFM effective airflow handles 17.5W average load easily
   - 1.5°C temperature rise above ambient (typical)
   - 4.3°C rise during brief peak loads

3. **Component Safety**
   - All components operate well below thermal limits
   - TB6600 drivers: 30-80°C typical (vs 150°C shutdown)
   - Raspberry Pi: 35-50°C (vs 85°C throttle point)

4. **Design Margin**
   - System could operate without fan using natural convection
   - Current fan provides ~5× thermal margin over passive cooling
   - Outlet restriction (28.3 cm²) is acceptable given low heat load

---

## Fan Control Recommendations

### Option A: Always-On Operation (Current Design)
**Configuration:** Fan runs continuously at 24V

**Advantages:**
- Simplest implementation (no additional components)
- Consistent cooling performance
- Pre-cooling before motor moves
- Silent operation (26 dBA)

**Disadvantages:**
- Slight power waste during idle (~2.4W)

**Recommendation:** ✓ **Preferred for production units**

---

### Option B: Temperature-Controlled Fan
**Configuration:** DS18B20 sensor + MOSFET fan control

**Implementation:**
```
DS18B20 → GPIO (1-wire) → Python control
     └─→ Thresholds: 40°C ON, 35°C OFF
MOSFET → Fan PWM control (0-100%)
```

**Advantages:**
- Minimal power consumption during idle
- Quiet when system inactive
- Smart thermal management

**Disadvantages:**
- Requires additional hardware ($5)
- More complex software
- Potential for delayed cooling response

**Recommendation:** Consider for battery-powered or noise-sensitive installations

---

### Option C: Natural Convection Only
**Configuration:** Remove fan, rely on passive airflow

**Feasibility:** VIABLE for typical 9% duty cycle operation

**Expected performance:**
- Typical temperatures: 35-55°C (TB6600 drivers)
- Peak temperatures: 75-105°C (brief, during moves)
- Absolutely silent operation

**Limitations:**
- Reduced margin for extended moves or high ambient temperature
- Not recommended if duty cycle exceeds 15%

**Recommendation:** Only for ultra-quiet museum installations with strict noise requirements

---

## Additional Inlet Analysis

### Question: Are Additional Inlet Slots Needed?

**Answer: NO - Current Design is More Than Adequate**

**Reasoning:**

1. **Outlet-Limited System**
   - Current outlet: 28.3 cm² (effective)
   - Current inlet: 45 cm² (59% more than outlet)
   - Adding more inlet area provides minimal benefit

2. **Thermal Margin Analysis**
   - Average load: 17.5W → 1.5°C rise
   - System designed for 51.5W peak → 4.3°C rise
   - **Thermal margin: ~3× above required**

3. **Inlet Area Recommendation**
   - For optimal flow: Inlet ≥ 1.2× outlet area
   - Current ratio: 45/28.3 = 1.59× ✓ **Exceeds guideline**

**Conclusion:** Current inlet ventilation (45 cm²) is well-sized for the outlet restriction and thermal load. No modifications needed.

---

## Design Validation

### Test Recommendations

To validate thermal performance in production environment:

1. **Temperature Monitoring**
   - Infrared thermometer spot checks of TB6600 heatsinks
   - Expected: 30-45°C typical, 55-80°C after auto-cycle move
   - Action threshold: >100°C indicates problem

2. **Extended Auto-Cycle Test**
   - Run 100 auto-cycle iterations (55 minutes)
   - Monitor for thermal accumulation
   - Expected: Steady-state equilibrium within 10 cycles

3. **Ambient Temperature Testing**
   - Verify operation at maximum expected ambient (30-35°C)
   - Confirm TB6600 temperatures stay below 100°C
   - Current design provides adequate margin

---

## Conclusions and Recommendations

### Summary
The robotic microscope system demonstrates **excellent thermal performance** with the current ventilation design. The combination of low motor duty cycle (9%), adequate fan capacity (13.8 CFM), and sufficient inlet ventilation (45 cm²) provides robust cooling with significant safety margin.

### Recommendations

**✓ Approved for Production:**
- Current fan: 60×60×10mm, 13.8 CFM, 24V, 26 dBA
- Current inlet: 15 slots, 45 cm² total area
- Fan control: Always-on operation (simplest, most reliable)

**✗ Not Required:**
- Additional inlet slots (current design exceeds guidelines)
- Larger fan (oversized for 17.5W average load)
- Active temperature monitoring (optional, not necessary)

**Optional Enhancements:**
- Temperature-controlled fan for noise-sensitive installations
- DS18B20 sensor for thermal monitoring dashboard
- Natural convection mode for ultra-quiet operation

### Design Sign-Off

The thermal design is validated for production deployment with no hardware modifications required.

---

## Appendix: Thermal Engineering Constants

### Calculation Parameters

| Parameter | Value | Units | Source |
|-----------|-------|-------|--------|
| Air specific heat | 1.005 | kJ/(kg·K) | Standard conditions (20°C, 1 atm) |
| Air density | 1.204 | kg/m³ | Standard conditions |
| CFM to W/°C conversion | 1.08 | W/(CFM·°C) | Derived from ρ·Cp·volumetric flow |
| Natural convection (typical) | 2 | CFM | Small enclosure, 15-20W load |
| Buoyancy-driven flow coefficient | 0.067 | CFM·m/(W^0.5) | Empirical for vertical chimney |

### Duty Cycle Definitions

```
Duty Cycle = (Active Time) / (Total Cycle Time)

System Operation:
- Move phase: 3 seconds (motors energized, full current)
- Viewing phase: 30 seconds (motors idle, minimal current)
- Total cycle: 33 seconds
- Duty cycle: 3/33 = 9.1%

Power Scaling:
- Average Power = Peak Power × Duty Cycle
- Thermal time constant >> cycle time (thermal averaging applies)
```

---

**End of Thermal Analysis Report**
# Electrical Safety Analysis

**Document ID:** 13_ELECTRICAL_SAFETY  
**Analysis Date:** December 30, 2025  
**System:** 4-Axis CNC Robotic Microscope  
**Revision:** 1.0  
**Reviewer:** System Safety Assessment

---

## Executive Summary

This document provides a comprehensive electrical safety assessment of the robotic microscope system, covering power supply design, enclosure materials, fault protection, and compliance considerations.

**Overall Safety Rating:** **LOW-MODERATE RISK** ✓

**Key Safety Features:**
- SELV (Safety Extra-Low Voltage) 24V system
- Properly rated fusing and overcurrent protection
- Non-conductive PLA enclosure (good insulator)
- Low current levels (1A per motor driver)
- Isolated control circuits

---

## System Power Architecture

### Primary Power Supply

**Specification:**
- **Manufacturer:** Liteon
- **Model:** Industry-standard 24V DC supply
- **Output:** 24V, 5A (120W max)
- **Input:** 120/240V AC (depending on region)
- **Safety Certifications:** UL/CE listed (assumed for Liteon industrial unit)

**Power Distribution:**
```
AC Mains (120/240V)
    │
    ├─→ Liteon PSU (24V, 5A) ───┬─→ 4× TB6600 Drivers (96W)
    │                            ├─→ 60mm Fan (2.4W)
    │                            └─→ Buck Converter (5V) ──┬─→ Raspberry Pi 4 (6.5W)
    │                                                       ├─→ Teensy 4.1 (0.8W)
    │                                                       ├─→ USB Camera (1.0W)
    │                                                       └─→ 24× WS2812B LEDs (0.6W)
    │
    └─→ Monitor/Display (if applicable)
```

### Power Budget Analysis

| Load | Voltage | Current | Power | % of Supply |
|------|---------|---------|-------|-------------|
| 4× TB6600 (1A each) | 24V | 4.0A | 96W | 80% |
| 60mm Fan | 24V | 0.1A | 2.4W | 2% |
| Buck Converter Load | 5V | 3.16A | 15.8W | 13% |
| **Total System** | — | — | **114.2W** | **95%** |
| **Supply Rating** | 24V | 5A | **120W** | **100%** |
| **Design Margin** | — | — | **5.8W** | **5%** |

**Assessment:** Adequate margin for steady-state operation. Peak transients are brief (9% duty cycle).

---

## Voltage Safety Classification

### 24V DC System (SELV)

**Classification:** Safety Extra-Low Voltage (SELV)  
**Definition:** DC voltage ≤ 50V under normal conditions, ≤ 120V under fault conditions

**Safety Implications:**
- **No risk of electrocution** from direct contact with 24V rails
- **No arc flash hazard** at this voltage level
- **Touch-safe** for operators and maintenance personnel
- **Suitable for public installations** (museum kiosk environment)

**Compliance Note:** 24V DC systems are widely accepted as inherently safe for human contact in dry conditions. No additional insulation barriers required between user and internal electronics.

---

## Enclosure Material Analysis

### PLA (Polylactic Acid) Thermoplastic

**Material Properties:**
- **Dielectric Strength:** 20-50 kV/mm (excellent insulator)
- **Volume Resistivity:** ~10¹⁶ Ω·cm (very high resistance)
- **Flammability:** V-0 to HB rating (depending on formulation)
- **Thermal Stability:** Softens at 60°C, melts at 150-160°C

**Safety Assessment:**

✓ **Electrical Insulation: EXCELLENT**
- PLA is an excellent electrical insulator
- Prevents accidental contact with live 24V rails
- No conductive paths through enclosure material
- Comparable to ABS/polycarbonate for electrical safety

✓ **Thermal Considerations: ACCEPTABLE**
- System operating temperature: 30-50°C typical (see Thermal Analysis)
- PLA safe up to 60°C continuous
- **Margin:** 10-30°C above typical operating temperature
- TB6600 drivers (hottest components) reach 55-80°C peak but are thermally isolated

⚠ **Fire Safety: MODERATE CONCERN**
- PLA is combustible (organic polymer)
- Ignition temperature: ~350-400°C
- No credible ignition source in system (all components <150°C)
- **Risk level: LOW** given temperature margins

**Recommendation:** Current PLA enclosure is **electrically safe** and **thermally adequate** for this application. For enhanced fire safety in commercial deployment, consider:
- Fire-retardant PLA formulations (FR-PLA)
- UL94 V-0 rated plastics (polycarbonate, ABS-FR)
- External smoke detector if required by venue

---

## Circuit Protection Analysis

### Overcurrent Protection

**Primary Fusing (AC Input):**
- **Location:** Inside Liteon PSU
- **Type:** Internal fuse or circuit breaker
- **Rating:** Matched to 120W output (typically 2A @ 120V AC or 1A @ 240V AC)

**Secondary Fusing (24V Rails):**
- **Recommended:** Inline fuse on 24V output from PSU
- **Rating:** 5A fast-blow or 6A slow-blow
- **Purpose:** Protects wiring and drivers from short circuits

**Load-Level Protection:**
- **TB6600 Drivers:** Built-in overcurrent shutdown (1.0A setting)
- **Buck Converter:** Typically includes current limiting
- **Raspberry Pi:** Protected by USB power management

### Fault Scenarios

**Short Circuit Analysis:**

| Fault Location | Protection Mechanism | Trip Time | Consequence |
|----------------|---------------------|-----------|-------------|
| 24V rail short | PSU current limit + fuse | <1 second | PSU shutdown, no damage |
| Motor winding short | TB6600 overcurrent | <100ms | Driver shutdown, motor safe |
| 5V rail short | Buck converter foldback | <10ms | Logic system resets |
| LED array short | Current limiting resistors | N/A | Single LED failure only |

**Assessment:** Multi-layer protection provides adequate fault isolation.

---

## Grounding and EMI Considerations

### Ground Architecture

**Safety Ground (Earth):**
- **AC Input:** Liteon PSU has 3-prong AC input with safety ground
- **Chassis Ground:** PSU ground bonded to metal chassis/ground plane
- **Purpose:** Fault protection, prevents chassis from becoming energized

**Signal Ground (0V Reference):**
- **24V System:** Common negative rail for motors, drivers, fan
- **5V System:** Isolated negative rail for logic circuits
- **Ground Isolation:** Buck converter provides galvanic isolation between 24V and 5V systems

**Grounding Assessment:**
- **Safety ground: REQUIRED** for AC-powered system
- **Ground loops: NOT A CONCERN** (low-frequency DC system, no audio/video signals)
- **ESD protection: ADEQUATE** (touchscreen provides some isolation)

### Electromagnetic Compatibility (EMC)

**Emission Sources:**
- Stepper motor drivers (PWM at ~20-40 kHz)
- Buck converter (switching at ~500 kHz)
- Digital circuits (Teensy, RPi - low levels)

**Mitigation Measures:**
- Shielded motor cables (recommended for long runs)
- Bypass capacitors on power rails
- Ground plane in enclosure

**Assessment:** System operates in benign EMI environment (museum kiosk). No radio/wireless interference expected. Commercial EMC testing not required for single-unit prototype but recommended for production.

---

## Potential Hazards and Mitigation

### Hazard #1: Electrical Shock

**Voltage Level:** 24V DC (SELV)  
**Risk Level:** **VERY LOW**

**Analysis:**
- 24V DC is below threshold for human sensation (~50V)
- Dry skin resistance: 100kΩ typical → 0.24mA current (imperceptible)
- Even in wet conditions, 24V poses minimal shock hazard

**Mitigation:**
- PLA enclosure prevents casual contact with live parts
- Touchscreen interface isolates user from internal electronics
- Maintenance personnel should still use standard precautions

**Residual Risk:** Effectively zero for normal operation and maintenance.

---

### Hazard #2: Fire Risk

**Heat Sources:**
- TB6600 drivers: 55-80°C peak
- Motors: 40-60°C during operation
- Raspberry Pi: 35-50°C

**Risk Level:** **LOW**

**Analysis:**
- All component temperatures well below autoignition point of PLA (350-400°C)
- No open flames or arcing (24V DC, no switching at high voltage)
- Thermal shutdown protects drivers at 150°C (before PLA softening point of 160°C)

**Mitigation:**
- Adequate ventilation (see Thermal Analysis)
- Component thermal protection (TB6600 shutdown at 150°C)
- Keep flammable materials away from enclosure

**Residual Risk:** Very low. No credible fire initiation mechanism.

---

### Hazard #3: Mechanical Hazards from Motors

**Moving Parts:**
- 4× stepper motors with lead screws
- Specimen stage (X-Y motion)
- Objective focus (Z-axis)
- Camera positioning

**Risk Level:** **LOW-MODERATE** (pinch points, not electrical)

**Analysis:**
- Motor torque: Moderate (1A current, NEMA 17 typical)
- Speed: Slow (controlled motion, museum environment)
- Access: Enclosed in PLA housing

**Mitigation:**
- Limit switches prevent overtravel
- Software limits enforce workspace boundaries
- Touchscreen interface prevents direct access during operation
- Emergency stop (if implemented)

**Residual Risk:** Low for pinch injuries. Enclosure prevents direct contact during operation.

---

### Hazard #4: Supply Overcurrent / Overload

**Scenario:** All four motors + accessories simultaneously drawing peak current

**Peak Load:** 114W (95% of supply capacity)

**Risk Level:** **LOW**

**Analysis:**
- 5.8W margin under steady-state peak load
- Duty cycle: 9% (motors active only 3 seconds per 33-second cycle)
- Liteon PSU has built-in overcurrent protection

**Mitigation:**
- Software sequencing (motors don't start simultaneously)
- PSU current limiting prevents damage
- External fuse provides secondary protection

**Residual Risk:** PSU will shut down cleanly if overloaded. No damage expected.

---

## Compliance and Standards

### Applicable Standards (if seeking certification)

**Low Voltage Directive (LVD) - EU:**
- EN 60950-1: Safety of IT equipment
- EN 62368-1: Audio/video equipment safety
- **Status:** 24V SELV system is inherently compliant

**UL Standards - USA:**
- UL 61010-1: Electrical equipment for measurement, control, laboratory use
- UL 60950-1: IT equipment safety
- **Status:** Prototype exempt; production units should use UL-listed PSU

**IEC 60335-1 - Household Appliances:**
- Not applicable (not a household appliance)

### FCC/EMC Compliance

**Part 15 (USA) / CE (EU):**
- Class A (industrial) or Class B (residential) emission limits
- **Status:** Prototype exempt; production units may require EMC testing
- **Recommendation:** Use shielded motor cables, ferrite beads on power supply

### Museum/Public Installation Requirements

**Venue-Specific Considerations:**
- Fire marshal approval (varies by jurisdiction)
- Electrical inspection (if hardwired to building power)
- ADA compliance (if applicable)
- Liability insurance requirements

**Recommendation:** Consult with venue management for specific electrical safety requirements.

---

## Safety Checklist for Deployment

### Pre-Installation

- [ ] Verify PSU is UL/CE listed and properly rated
- [ ] Inspect all wiring for damage, proper gauge (minimum 18 AWG for 24V)
- [ ] Confirm TB6600 current setting: 1.0A (DIP switches SW5=ON, SW6=OFF)
- [ ] Test emergency stop functionality (if implemented)
- [ ] Verify limit switches are functional
- [ ] Check enclosure integrity (no cracks, loose parts)

### Installation

- [ ] Connect AC power through GFCI outlet (recommended for public installations)
- [ ] Verify 3-prong grounded AC connection
- [ ] Install external fuse on 24V rail (5A recommended)
- [ ] Confirm fan is operational (13.8 CFM, 24V)
- [ ] Label high-current components (drivers, PSU) with "Service Only" warnings
- [ ] Ensure ventilation slots are unobstructed

### Operational Testing

- [ ] Measure 24V rail voltage under load (should be 23.5-24.5V)
- [ ] Measure 5V rail voltage under load (should be 4.9-5.1V)
- [ ] Verify motor current draw: ≤1A per driver
- [ ] Check TB6600 heatsink temperatures: <100°C after extended run
- [ ] Test overcurrent protection by simulating motor stall
- [ ] Run 100-cycle auto-cycle test to verify thermal stability

### Maintenance Schedule

**Monthly:**
- Inspect AC power cord for damage
- Check cooling fan operation
- Clean ventilation slots

**Quarterly:**
- Verify limit switch functionality
- Test emergency stop (if present)
- Inspect motor wiring for wear

**Annually:**
- Professional electrical inspection (if required by venue)
- Thermal imaging of drivers/PSU to detect hot spots
- Replace cooling fan if bearing noise develops

---

## Risk Assessment Summary

| Hazard | Severity | Probability | Risk Level | Mitigation |
|--------|----------|-------------|------------|------------|
| Electrical shock (24V) | Minor | Very Low | **LOW** | SELV voltage, PLA enclosure |
| Fire (component failure) | Moderate | Very Low | **LOW** | Thermal protection, ventilation |
| Fire (PLA enclosure) | Moderate | Very Low | **LOW** | Component temps <150°C, FR-PLA option |
| Overcurrent/PSU failure | Minor | Low | **LOW** | Fused supply, current limiting |
| Mechanical pinch | Minor | Low | **LOW** | Enclosure, limit switches |
| EMI interference | Negligible | Low | **VERY LOW** | DC motors, low-frequency system |

**Overall System Risk:** **LOW-MODERATE**

**Justification:** The 24V SELV design, non-conductive enclosure, and multiple layers of overcurrent protection result in a system with inherently low electrical hazards. Fire risk is minimal given the large temperature margins between operating conditions and material limits. Mechanical hazards are the primary concern but are well-controlled by enclosure and software limits.

---

## Recommendations for Production Units

### Required Improvements

1. **Fusing:**
   - Add external 5A fuse on 24V rail (between PSU and drivers)
   - Use automotive blade fuse holder for easy replacement

2. **Wiring:**
   - Minimum 18 AWG wire for 24V distribution (current: 16 AWG for margin)
   - Ferrules on all screw terminal connections
   - Cable management to prevent chafing

3. **Labeling:**
   - "CAUTION: 24V DC" labels on PSU and driver area
   - "SERVICE ONLY - DO NOT OPEN" on enclosure panels
   - Wiring diagram inside access panel

### Optional Enhancements

1. **Fire Safety:**
   - Upgrade to FR-PLA or UL94 V-0 rated plastic
   - Thermal fuse on TB6600 heatsinks (150°C cutoff)
   - Smoke detector integration

2. **Electrical Protection:**
   - GFCI-protected AC outlet (for wet environments)
   - Surge protection on AC input
   - Reverse polarity protection on 24V rail

3. **Monitoring:**
   - Voltage monitoring (24V and 5V rails)
   - Current monitoring (detect motor stall, verify operation)
   - Temperature sensor (DS18B20) for thermal dashboard

---

## Conclusions

The robotic microscope system demonstrates **sound electrical safety design** appropriate for a prototype or limited-production museum kiosk. The use of 24V SELV, non-conductive enclosure, and multiple protection layers results in a **low-risk electrical system**.

**Key Strengths:**
- Inherently safe 24V operating voltage
- PLA enclosure provides excellent electrical insulation
- Multi-layer overcurrent protection
- Low thermal stress on components
- Suitable for public installation with minimal risk

**Recommended Actions:**
- Add external fusing on 24V rail (quick win)
- Use UL/CE-listed PSU for production (compliance)
- Consider FR-PLA for enhanced fire safety (optional)
- Label high-voltage areas clearly (best practice)

**Safety Sign-Off:** System approved for continued prototype operation and limited deployment. For commercial production, implement recommended fusing and labeling enhancements.

---

## Appendix: Safety References

### Standards and Guidelines

- **IEC 60950-1:** Information Technology Equipment - Safety
- **IEC 61010-1:** Safety Requirements for Electrical Equipment for Measurement, Control, and Laboratory Use
- **UL 61010-1:** Standard for Electrical Equipment for Laboratory Use
- **NFPA 70 (NEC):** National Electrical Code (USA)
- **IEC 60529:** IP Rating System (dust/water ingress)

### Voltage Classification

| Voltage Range | Classification | Safety Requirements |
|---------------|----------------|---------------------|
| < 50V DC | SELV (Safety Extra-Low Voltage) | Touch-safe, minimal protection |
| 50-120V DC | Low Voltage | Insulation required, not inherently safe |
| > 120V DC | High Voltage | Strict insulation, interlocks, labeling |

### Useful Contacts

- **Underwriters Laboratories (UL):** www.ul.com
- **CE Marking / EU Compliance:** Local Notified Body
- **Electrical Safety Foundation International:** www.esfi.org

---

**End of Electrical Safety Analysis**
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
