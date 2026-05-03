#!/usr/bin/env python3
"""
Video Thread - OpenCV video capture worker for PyQt5
Captures from HDMI input via TC358743 CSI-2 bridge (Geekworm X630)

This module handles:
- EDID loading for HDMI negotiation
- DV timing lock for stable capture
- Frame capture and conversion for Qt display
"""

import cv2
import numpy as np
import subprocess
import time
import os
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage


class VideoThread(QThread):
    """Video capture worker thread for HDMI-to-CSI capture"""
    
    # Signal emitted when new frame is available
    frame_ready = pyqtSignal(QImage)
    # Signal emitted on status updates
    status_update = pyqtSignal(str)
    
    # Default device for TC358743 CSI capture
    DEFAULT_DEVICE = "/dev/video0"
    
    # Path to EDID file for 1080p50 (compatible with 2-lane CSI on Pi 4)
    EDID_FILE = os.path.join(os.path.dirname(__file__), "1080P50EDID_official.txt")
    
    def __init__(self, device: str = None):
        """Initialize video thread
        
        Args:
            device: Video device path (default: /dev/video0 for CSI capture)
        """
        super().__init__()
        self.device = device or self.DEFAULT_DEVICE
        self.running = False
        self.cap = None
        self._initialized = False
        self._current_frame = None  # Thread-safe frame storage
        self._frame_lock = None  # Will be initialized in run()
        
    def _run_v4l2_ctl(self, args: list, timeout: float = 5.0) -> tuple:
        """Run v4l2-ctl command and return (success, output)"""
        cmd = ["v4l2-ctl", "-d", self.device] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def _load_edid(self) -> bool:
        """Load EDID file to configure HDMI input capabilities"""
        if not os.path.exists(self.EDID_FILE):
            self.status_update.emit(f"WARNING: EDID file not found: {self.EDID_FILE}")
            return False
        
        success, output = self._run_v4l2_ctl([f"--set-edid=file={self.EDID_FILE}"])
        if success:
            self.status_update.emit("EDID loaded successfully")
        else:
            self.status_update.emit(f"WARNING: Failed to load EDID: {output}")
        return success
    
    def _query_dv_timings(self) -> dict:
        """Query current DV timings from HDMI input"""
        success, output = self._run_v4l2_ctl(["--query-dv-timings"])
        if not success:
            return None
        
        timings = {}
        for line in output.split('\n'):
            if ':' in line:
                key, _, value = line.partition(':')
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                timings[key] = value
        return timings
    
    def _lock_dv_timings(self) -> bool:
        """Lock DV timings to detected HDMI signal"""
        success, output = self._run_v4l2_ctl(["--set-dv-bt-timings", "query"])
        if success:
            self.status_update.emit("DV timings locked")
        else:
            self.status_update.emit(f"WARNING: Failed to lock DV timings: {output}")
        return success
    
    def _initialize_capture(self) -> bool:
        """Initialize HDMI capture pipeline
        
        This must be called before opening the video device.
        Handles EDID loading and DV timing synchronization.
        """
        self.status_update.emit(f"Initializing HDMI capture on {self.device}...")
        
        # Check device exists
        if not os.path.exists(self.device):
            self.status_update.emit(f"ERROR: Device {self.device} not found")
            return False
        
        # Load EDID (advertise supported modes to HDMI source)
        self._load_edid()
        
        # Wait for HDMI signal to stabilize after EDID change
        time.sleep(1.0)  # Increased from 0.5s
        
        # Query current timings (with retry)
        timings = None
        for attempt in range(3):
            timings = self._query_dv_timings()
            if timings:
                width = timings.get('active_width', 'unknown')
                height = timings.get('active_height', 'unknown')
                self.status_update.emit(f"Detected HDMI signal: {width}x{height}")
                break
            else:
                self.status_update.emit(f"Waiting for HDMI signal (attempt {attempt + 1}/3)...")
                time.sleep(0.5)
        
        if not timings:
            self.status_update.emit("WARNING: Could not query HDMI timings - check cable connection")
        
        # Lock timings (critical step!) - with retry
        for attempt in range(3):
            if self._lock_dv_timings():
                break
            self.status_update.emit(f"Retrying DV timing lock (attempt {attempt + 1}/3)...")
            time.sleep(0.5)
        else:
            self.status_update.emit("ERROR: Failed to lock DV timings after 3 attempts")
            return False
        
        # Brief delay for timing lock to take effect
        time.sleep(0.5)  # Increased from 0.3s
        
        self._initialized = True
        return True
        
    def run(self):
        """Main thread loop - capture and emit frames"""
        import threading
        self._frame_lock = threading.Lock()
        self.running = True
        
        # Initialize HDMI capture pipeline
        if not self._initialize_capture():
            self.status_update.emit("ERROR: HDMI capture initialization failed")
            return
        
        # Open camera with V4L2 backend (with retry)
        for attempt in range(3):
            self.cap = cv2.VideoCapture(self.device, cv2.CAP_V4L2)
            if self.cap.isOpened():
                break
            self.status_update.emit(f"Retrying camera open (attempt {attempt + 1}/3)...")
            time.sleep(0.5)
        
        if not self.cap.isOpened():
            self.status_update.emit(f"ERROR: Could not open device {self.device} after 3 attempts")
            return
        
        # Set capture format - TC358743 outputs RGB24
        # Note: We request the format but the actual format is determined by HDMI input
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        self.status_update.emit(f"Camera opened: {actual_width}x{actual_height} @ {actual_fps:.1f} FPS")
        
        # Frame counter for periodic status updates
        frame_count = 0
        last_status_time = time.time()
        
        while self.running:
            if not self.cap or not self.cap.isOpened():
                self.status_update.emit("WARNING: Camera closed unexpectedly")
                break
                
            ret, frame = self.cap.read()
            if not ret:
                self.status_update.emit("WARNING: Failed to read frame - HDMI signal lost?")
                time.sleep(0.1)  # Brief delay before retry
                continue
            
            # Store frame for thread-safe access (for focus stacking)
            with self._frame_lock:
                self._current_frame = frame.copy()
            
            try:
                # TC358743 outputs RGB3 format (confirmed by v4l2-ctl)
                # V4L2 reports: Pixel Format: 'RGB3' (24-bit RGB 8-8-8), Colorspace: sRGB
                # 
                # Testing color pipeline - try NO conversion first
                # If colors are still wrong, we may need BGR2RGB or RGB2BGR
                # 
                # IMPORTANT: Must make a copy because OpenCV reuses the frame buffer
                # Option A: No conversion (if RGB3 is read directly as RGB)
                frame_rgb = frame.copy()
                # Option B: BGR2RGB (if OpenCV reads RGB3 as BGR)
                # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Option C: RGB2BGR (if data is RGB but QImage expects BGR)
                # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # Convert to QImage
                height, width, channels = frame_rgb.shape
                bytes_per_line = channels * width
                q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
                
                # Emit signal with frame (only if still running)
                if self.running:
                    self.frame_ready.emit(q_image.copy())
                
                frame_count += 1
                
                # Periodic status update (every 10 seconds)
                now = time.time()
                if now - last_status_time >= 10.0:
                    fps = frame_count / (now - last_status_time)
                    self.status_update.emit(f"Capture running: {fps:.1f} FPS")
                    frame_count = 0
                    last_status_time = now
                    
            except Exception as e:
                self.status_update.emit(f"WARNING: Error processing frame: {e}")
                continue
        
        # Cleanup
        if self.cap:
            self.cap.release()
            self.cap = None
        self.status_update.emit("Video capture stopped")
    
    def stop(self):
        """Stop video capture thread"""
        self.running = False
        self.wait(2000)  # Wait up to 2 seconds for thread to finish
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def get_current_frame(self):
        """Get the current frame in a thread-safe manner.
        
        Returns:
            numpy.ndarray: Copy of the current frame, or None if not available
        """
        if self._frame_lock is None:
            return None
        with self._frame_lock:
            if self._current_frame is not None:
                return self._current_frame.copy()
            return None


def init_hdmi_capture(device: str = "/dev/video0", edid_file: str = None) -> bool:
    """Standalone function to initialize HDMI capture
    
    Can be called at system startup (e.g., from systemd service)
    to prepare the capture pipeline before the GUI starts.
    
    Args:
        device: Video device path
        edid_file: Path to EDID file (optional)
        
    Returns:
        True if initialization successful
    """
    if edid_file is None:
        edid_file = os.path.join(os.path.dirname(__file__), "1080P50EDID_official.txt")
    
    print(f"Initializing HDMI capture on {device}...")
    
    # Check device exists
    if not os.path.exists(device):
        print(f"ERROR: Device {device} not found")
        return False
    
    # Load EDID
    if os.path.exists(edid_file):
        result = subprocess.run(
            ["v4l2-ctl", "-d", device, f"--set-edid=file={edid_file}"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("EDID loaded successfully")
        else:
            print(f"WARNING: Failed to load EDID: {result.stderr}")
    
    time.sleep(0.5)
    
    # Query timings
    result = subprocess.run(
        ["v4l2-ctl", "-d", device, "--query-dv-timings"],
        capture_output=True,
        text=True
    )
    print(f"Detected timings:\n{result.stdout}")
    
    # Lock timings
    result = subprocess.run(
        ["v4l2-ctl", "-d", device, "--set-dv-bt-timings", "query"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("DV timings locked successfully")
        return True
    else:
        print(f"ERROR: Failed to lock DV timings: {result.stderr}")
        return False


if __name__ == "__main__":
    # When run directly, initialize the capture pipeline
    import sys
    device = sys.argv[1] if len(sys.argv) > 1 else "/dev/video0"
    success = init_hdmi_capture(device)
    sys.exit(0 if success else 1)
