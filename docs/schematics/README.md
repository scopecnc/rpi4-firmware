# Robotic Microscope Schematics

This directory contains Graphviz DOT files for system schematics and diagrams.

## Files

1. **01_system_overview.dot** - High-level system architecture showing all major components
2. **02_power_distribution.dot** - Detailed power routing with budget calculations
3. **03_signal_details.dot** - Pin-level signal connections and wiring details

## Generating PDFs

### Prerequisites

Install Graphviz:
```bash
# Debian/Ubuntu
sudo apt install graphviz

# macOS
brew install graphviz

# Verify installation
dot -V
```

### Generate Individual PDFs

```bash
cd /home/scope/scope/schematics

# System overview
dot -Tpdf 01_system_overview.dot -o 01_system_overview.pdf

# Power distribution
dot -Tpdf 02_power_distribution.dot -o 02_power_distribution.pdf

# Signal details
dot -Tpdf 03_signal_details.dot -o 03_signal_details.pdf
```

### Generate All at Once

```bash
cd /home/scope/scope/schematics
for file in *.dot; do
    dot -Tpdf "$file" -o "${file%.dot}.pdf"
done
```

### Generate Other Formats

Graphviz supports many output formats:

```bash
# PNG (raster image)
dot -Tpng 01_system_overview.dot -o 01_system_overview.png

# SVG (vector, web-friendly)
dot -Tsvg 01_system_overview.dot -o 01_system_overview.svg

# PostScript
dot -Tps 01_system_overview.dot -o 01_system_overview.ps
```

## Viewing Without Installing

You can view DOT files online without installing Graphviz:
- https://dreampuf.github.io/GraphvizOnline/
- Paste the DOT file contents and it will render

## Editing

The DOT files are plain text and can be edited with any text editor:
- Add/remove nodes
- Change labels
- Modify colors and styling
- Adjust layout parameters

After editing, regenerate the PDF to see changes.

## Schematic Details

### 01 - System Overview
- All major system components
- Power distribution paths (24V, 5V, GND)
- Control signal connections
- Component interconnections
- Legend for signal types

### 02 - Power Distribution
- Complete power path from wall to loads
- Fusing and protection
- Bus bar connections
- 24V → 5V conversion
- Power budget table with calculations
- Current consumption breakdown
- Safety notes

### 03 - Signal Details
- Complete Teensy 4.1 pinout table
- RPi4 GPIO assignments
- UART connection detail (RPi ↔ Teensy)
- LED ring with SN74AHCT125N level shifter schematic
- TB6600 driver wiring (all 4 axes)
- Limit switch connections (all 8 switches)
- Camera connection
- External connector summary (JST-SM types)

## Notes

- **Pin 22 for F_MIN**: Hardware fix, do not change to pin 17 (I2C interference)
- **ENA_ALL logic**: Active LOW (LOW = enabled, HIGH = disabled)
- **3.3V/5V logic**: Teensy outputs 3.3V, TB6600 accepts 3.3V, LED ring needs 5V (hence level shifter)
- **Microstepping**: 1/16 on all TB6600 drivers (calibrated to 400 steps/mm)
- **Limit switches**: Normally Open (NO), use internal pull-ups

## Integration with Documentation

These schematics complement the markdown documentation in `/docs/`:
- 03_HARDWARE_SPECIFICATION.md - Detailed hardware specs and pinouts
- 08_RPI4_INTEGRATION.md - RPi4 UART configuration and Python code
- 02_SYSTEM_ARCHITECTURE.md - Software architecture and protocols

---

**Version:** 1.0  
**Date:** December 30, 2025  
**Format:** Graphviz DOT → PDF
