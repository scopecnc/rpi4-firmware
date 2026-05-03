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
