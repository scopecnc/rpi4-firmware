# Focus Stacking Feature

## Overview

The focus stacking feature automatically captures multiple images at different focus depths and combines them into a single image with extended depth of field. This is particularly useful for mineral specimens with complex 3D surface features.

## Installation

The focus-stack tool by Petteri Aimonen is required. It has been installed on the RPi4:

```bash
# Dependencies (already installed)
sudo apt-get install build-essential cmake libopencv-dev

# Clone and build focus-stack (already done)
cd /tmp
git clone https://github.com/PetteriAimonen/focus-stack.git
cd focus-stack
make -j4
sudo cp build/focus-stack /usr/local/bin/
```

Verify installation:
```bash
focus-stack --version
```

## Usage

### Museum/Public Mode (Default)

For public installations where storage should not fill up:

```bash
python3 scope_gui.py mindatnh_tray1.json
```

In this mode:
- Stacked images are displayed but NOT saved permanently
- Images are cached in `./image_stack_cache/` with common filenames
- Cache is overwritten on each run

### Private Mode (Save Enabled)

For private use where users want to save results:

```bash
python3 scope_gui.py mindatnh_tray1.json --enable-save
```

In this mode:
- Stacked images can be saved to user-selected locations
- A "Save As..." button appears in the result dialog

## Operation

### Pre-Operation Checklist

1. **Position the microscope** at the HIGHEST focus point (closest to specimen surface)
2. **Ensure the specimen** is in view and properly illuminated
3. **Check Z travel** - you need at least 1.0mm of downward travel available

### Focus Stack Process

1. Click the **"Generate Stacked Image"** button in the jog controls area
2. Review the pre-operation prompt and confirm
3. Wait for the operation to complete (~30-60 seconds):
   - 10 images captured at 0.1mm Z-axis steps
   - Automatic alignment and stacking
4. Review the result in the popup dialog
5. Save if desired (private mode only)

### During Operation

- All controls are locked
- Progress updates are shown
- Click **"Abort"** to stop the operation at any time
- Z axis automatically returns to starting position

## Technical Details

### Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Number of images | 10 | Fixed for simplicity |
| Z-step size | 0.1mm | Downward (toward specimen) |
| Total Z travel | 1.0mm | 10 × 0.1mm |
| Processing time | ~20-30s | On RPi4 with 1080p images |

### File Locations

- **Cache directory**: `./image_stack_cache/`
- **Intermediate images**: `img_01.png`, `img_02.png`, ... `img_10.png` (overwritten each run)
- **Result**: `stacked.jpg` (overwritten each run unless saved)

### Error Handling

If an error occurs:
- All controls are unlocked
- Z axis returns to starting position
- Cache images are cleaned up
- Error message is displayed

Common errors:
- **Insufficient Z travel**: Move to a higher starting position
- **Camera not available**: Check HDMI connection
- **focus-stack not found**: Install the tool (see Installation above)
- **Stacking timeout**: Reduce number of images or check system performance

## Integration with Existing GUI

The focus stacking feature is fully integrated:
- Button added to jog controls area (between Z/F controls and brightness slider)
- Jog controls area height increased from 420px to 520px
- No changes to specimen selection or other functionality
- Thread-safe implementation with proper control locking

## Future Enhancements

Potential improvements for future versions:
- Configurable number of images and Z-step size
- Real-time progress bar (instead of indeterminate)
- Preview mode showing individual captured images
- Adjustable stacking algorithm parameters
- Batch processing of multiple specimens

---

**Date Added**: January 7, 2026  
**Software Version**: scope_gui.py with focus stacking v1.0  
**Dependencies**: focus-stack 1.3-33-gd8532c8, OpenCV 4.10.0
