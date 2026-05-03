# Raspberry Pi 4 HDMI Capture Bring‑Up Summary

This document summarizes the **system-level (non-Python)** configuration changes and behaviors that were required to get a working HDMI capture pipeline on a Raspberry Pi 4.

It focuses on OS, driver, and V4L2 behavior rather than application code.

---

## 1. HDMI Capture Defaults to a Fallback Mode on Boot

**Observed behavior**
- After boot, `/dev/video0` reported:
  - Resolution: **640×480**
  - Pixel format: `UYVY`
- This occurred even when:
  - EDID advertised 1920×1080
  - OpenCV attempted to set resolution
  - `v4l2-ctl --set-fmt-video` was used

**Reason**
- HDMI capture bridges typically boot into a **safe fallback mode**
- Timing is not locked until:
  - HDMI signal is stable
  - EDID handshake completes
  - The driver explicitly probes the input

Result: the driver exposes **VGA (640×480)** until timing lock occurs.

---

## 2. EDID Was Present but Not Automatically Applied

**Confirmed**
- EDID correctly advertised **1920×1080 @ 50 Hz**
- Tools could read the EDID successfully

**Key insight**
- EDID being readable does **not** mean the driver has switched to that mode
- The capture device does **not automatically latch EDID timings on reboot**

EDID was advertised, but **inactive**.

---

## 3. `--set-fmt-video` Does Not Control HDMI Timing

Command attempted:
```bash
v4l2-ctl --set-fmt-video=width=1920,height=1080,pixelformat=UYVY
```

**Why it failed**
- HDMI resolution is controlled by **DV timings**, not V4L2 format negotiation
- Until timing is locked:
  - Width/height requests are ignored
  - The driver continues outputting the fallback mode

This is expected for CSI HDMI bridges and HDMI receiver chips.

---

## 4. Critical Fix: Forcing DV Timing Detection

The following command resolved the issue:
```bash
v4l2-ctl --device=/dev/video0 --set-dv-bt-timings query
```

**What this does**
- Forces the driver to:
  - Re-probe the HDMI input
  - Measure pixel clock
  - Lock to the actual incoming signal
  - Reconfigure the capture pipeline

**After running this**
- `/dev/video0` reports **1920×1080**
- `ffplay /dev/video0` works correctly
- OpenCV is able to receive valid frames

This is the **key system-level action**.

---

## 5. Timing Lock Is Not Persistent Across Reboot

**Important behavior**
- DV timing lock is **lost on reboot**
- Must be re-applied:
  - On every boot, or
  - Before opening the capture device

Common solutions:
- `systemd` service
- `rc.local`
- Startup script
- Application-level `subprocess` call

---

## 6. OpenCV Uses GStreamer by Default

Log output showed:
```
OpenCV | GStreamer warning: unable to start pipeline
```

**Implications**
- OpenCV prefers the **GStreamer backend**
- GStreamer is sensitive to:
  - Timing changes
  - Device resets
  - Format negotiation order

**Required sequencing**
1. Set DV timings
2. Wait briefly (≈ 0.5–1 s)
3. Open `/dev/video0`

Opening the device too early results in capture failure.

---

## 7. No Kernel or Driver Rebuilds Were Required

**Not required**
- Kernel recompilation
- Custom drivers
- Device tree overlay changes
- OpenCV rebuild

The issue was entirely related to:
- HDMI timing initialization
- Driver state at boot
- Capture startup ordering

---

## Final Checklist

✔ HDMI capture hardware connected  
✔ EDID present and correct  
✔ `/dev/video0` exists  
✔ DV timings explicitly queried  
✔ Timing locked before first capture  

---

## Recommended Next Steps

- Create a `systemd` unit to auto-run DV timing query at boot
- Force OpenCV to use the V4L2 backend instead of GStreamer
- Handle HDMI hot‑plug events gracefully
- Explicitly verify pixel format negotiation

---

*Document generated for reproducibility and future reference.*
