#!/usr/bin/env python3
"""
Robotic Microscope GUI - Touch Kiosk Interface
Museum-quality interface for automated mineral specimen viewing
"""

import sys
import time
import json
import threading
import subprocess
import os
import glob
import cv2
import argparse
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QTextEdit,
                             QGridLayout, QLineEdit, QComboBox, QFileDialog, QMessageBox,
                             QGroupBox, QSizePolicy, QSlider, QDialog, QProgressBar)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPoint, QRect, QMutex, pyqtSlot, QThread, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QFont, QPen, QBrush, QKeyEvent

from motion_controller import MotionController
from led_controller import get_led_controller, MIN_BRIGHTNESS_PERCENT, MAX_BRIGHTNESS_PERCENT, DEFAULT_BRIGHTNESS_PERCENT
from video_thread import VideoThread
from specimen_grid import SpecimenPosition
from teensy_protocol import MessageType
from sounds import play_startup_chime, play_warning_beep


class SpecimenCard(QFrame):
    """Touch-friendly specimen card widget"""
    
    clicked = pyqtSignal(int)  # Emits specimen index
    
    def __init__(self, index: int, specimen: SpecimenPosition, parent=None):
        super().__init__(parent)
        self.index = index
        self.specimen = specimen
        self.is_current = False
        
        # Styling
        self.setFixedHeight(80)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(2)
        self.setCursor(Qt.PointingHandCursor)
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Specimen name (large, bold)
        name_label = QLabel(specimen.mineral_name)
        name_font = QFont("Liberation Sans", 13, QFont.Bold)
        name_label.setFont(name_font)
        name_label.setWordWrap(True)
        
        # Location (smaller)
        location_label = QLabel(specimen.location)
        location_font = QFont("Liberation Sans", 10)
        location_label.setFont(location_font)
        location_label.setStyleSheet("color: #888;")
        
        layout.addWidget(name_label)
        layout.addWidget(location_label)
        self.setLayout(layout)
        
        self.update_style()
    
    def set_current(self, is_current: bool):
        """Mark this card as current specimen"""
        self.is_current = is_current
        self.update_style()
        self.update()  # Schedule repaint, don't force immediate
    
    def update_style(self):
        """Update visual style based on state"""
        if self.is_current:
            self.setStyleSheet("""
                SpecimenCard {
                    background-color: rgba(50, 150, 255, 180);
                    border: 3px solid #3296FF;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                SpecimenCard {
                    background-color: rgba(40, 40, 40, 200);
                    border: 2px solid #555;
                    border-radius: 8px;
                }
                SpecimenCard:hover {
                    background-color: rgba(60, 60, 60, 220);
                    border: 2px solid #888;
                }
            """)
    
    def mousePressEvent(self, event):
        """Handle touch/click"""
        self.clicked.emit(self.index)


class JogButton(QPushButton):
    """Touch-friendly jog button with press/release signals"""
    
    pressed_signal = pyqtSignal()
    released_signal = pyqtSignal()
    
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setMinimumSize(60, 60)
        self.setFont(QFont("Liberation Sans", 20, QFont.Bold))
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 60, 60, 200);
                border: 2px solid #666;
                border-radius: 8px;
                color: white;
            }
            QPushButton:pressed {
                background-color: rgba(50, 150, 255, 220);
                border: 3px solid #3296FF;
            }
        """)
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.pressed_signal.emit()
    
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.released_signal.emit()


class BrightnessSlider(QWidget):
    """
    Touch-friendly brightness slider for LED ring control.
    
    Museum-quality widget with large touch target and clear visual feedback.
    Range: 20% - 70% (hardware limited to prevent overheating)
    """
    
    brightness_changed = pyqtSignal(int)  # Emits brightness percentage
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(70)
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._emit_brightness)
        self._pending_value = DEFAULT_BRIGHTNESS_PERCENT
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)
        
        # Title and value label
        header = QHBoxLayout()
        title = QLabel("☀ Brightness")
        title.setFont(QFont("Liberation Sans", 11, QFont.Bold))
        title.setStyleSheet("color: #FFA;")
        header.addWidget(title)
        
        self.value_label = QLabel(f"{DEFAULT_BRIGHTNESS_PERCENT}%")
        self.value_label.setFont(QFont("Liberation Sans", 11, QFont.Bold))
        self.value_label.setStyleSheet("color: #FFA;")
        self.value_label.setAlignment(Qt.AlignRight)
        header.addWidget(self.value_label)
        
        layout.addLayout(header)
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(MIN_BRIGHTNESS_PERCENT)
        self.slider.setMaximum(MAX_BRIGHTNESS_PERCENT)
        self.slider.setValue(DEFAULT_BRIGHTNESS_PERCENT)
        self.slider.setFixedHeight(35)  # Large touch target
        self.slider.valueChanged.connect(self._on_value_changed)
        
        # Touch-friendly slider styling
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #444;
                height: 16px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #333, stop:1 #666);
                border-radius: 8px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFE066, stop:0.5 #FFCC00, stop:1 #CC9900);
                border: 2px solid #AA8800;
                width: 28px;
                margin: -8px 0;
                border-radius: 14px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFEE88, stop:0.5 #FFDD22, stop:1 #DDAA00);
                border: 2px solid #CCAA00;
            }
            QSlider::handle:horizontal:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFF99, stop:0.5 #FFEE44, stop:1 #EEBB00);
                border: 3px solid #FFCC00;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #665500, stop:1 #AA8800);
                border: 1px solid #554400;
                border-radius: 8px;
            }
        """)
        
        layout.addWidget(self.slider)
        self.setLayout(layout)
    
    def _on_value_changed(self, value: int):
        """Handle slider value change - debounced to prevent glitchy updates"""
        self.value_label.setText(f"{value}%")
        self._pending_value = value
        # Debounce: wait 50ms before emitting to batch rapid changes
        self._debounce_timer.start(50)
    
    def _emit_brightness(self):
        """Emit the brightness value after debounce delay"""
        self.brightness_changed.emit(self._pending_value)
    
    def set_value(self, percent: int):
        """Set slider value programmatically"""
        # Block signals to prevent feedback loop
        self.slider.blockSignals(True)
        self.slider.setValue(percent)
        self.value_label.setText(f"{percent}%")
        self.slider.blockSignals(False)
    
    def get_value(self) -> int:
        """Get current slider value"""
        return self.slider.value()


class StartupSplash(QWidget):
    """Startup splash screen with diagnostic mode prompt"""
    
    enter_diagnostic_mode = pyqtSignal()
    enter_normal_mode = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: black;")
        self.countdown = 10
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        
    def showEvent(self, event):
        """Start countdown when shown"""
        super().showEvent(event)
        self.countdown = 10
        self.timer.start(1000)  # Update every second
        self.setFocus()  # Ensure we get keyboard events
        
    def update_countdown(self):
        """Update countdown timer"""
        self.countdown -= 1
        if self.countdown <= 0:
            self.timer.stop()
            self.enter_normal_mode.emit()
        self.update()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key presses"""
        key = event.text().upper()
        if key == 'Y':
            self.timer.stop()
            self.enter_diagnostic_mode.emit()
        elif key == 'N':
            self.timer.stop()
            self.enter_normal_mode.emit()
    
    def paintEvent(self, event):
        """Draw splash screen"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Title
        painter.setPen(QPen(QColor(255, 255, 255)))
        title_font = QFont("Liberation Serif", 42, QFont.Bold)
        painter.setFont(title_font)
        title_text = "Robotic Microscope System"
        title_width = painter.fontMetrics().width(title_text)
        painter.drawText((self.width() - title_width) // 2, 150, title_text)
        
        # Subtitle
        subtitle_font = QFont("Liberation Sans", 18)
        painter.setFont(subtitle_font)
        subtitle_text = "Initializing..."
        subtitle_width = painter.fontMetrics().width(subtitle_text)
        painter.drawText((self.width() - subtitle_width) // 2, 200, subtitle_text)
        
        # Prompt box
        box_width = 800
        box_height = 300
        box_x = (self.width() - box_width) // 2
        box_y = 350
        
        painter.fillRect(box_x, box_y, box_width, box_height, QColor(40, 40, 40, 230))
        painter.setPen(QPen(QColor(100, 150, 255), 3))
        painter.drawRect(box_x, box_y, box_width, box_height)
        
        # Prompt text
        painter.setPen(QPen(QColor(255, 255, 255)))
        prompt_font = QFont("Liberation Sans", 24, QFont.Bold)
        painter.setFont(prompt_font)
        prompt_text = "Enter Diagnostic Mode?"
        prompt_width = painter.fontMetrics().width(prompt_text)
        painter.drawText((self.width() - prompt_width) // 2, box_y + 70, prompt_text)
        
        # Instructions
        painter.setPen(QPen(QColor(200, 200, 200)))
        inst_font = QFont("Liberation Sans", 16)
        painter.setFont(inst_font)
        
        instructions = [
            "Press 'Y' to enter Diagnostic Mode (recommended)",
            "Press 'N' to skip and start normally",
            f"Auto-starting in {self.countdown} seconds..."
        ]
        
        y_pos = box_y + 130
        for inst in instructions:
            inst_width = painter.fontMetrics().width(inst)
            painter.drawText((self.width() - inst_width) // 2, y_pos, inst)
            y_pos += 40
        
        # Countdown indicator
        if self.countdown <= 3:
            painter.setPen(QPen(QColor(255, 165, 0)))
        countdown_font = QFont("Liberation Sans", 48, QFont.Bold)
        painter.setFont(countdown_font)
        countdown_text = str(self.countdown)
        countdown_width = painter.fontMetrics().width(countdown_text)
        painter.drawText((self.width() - countdown_width) // 2, box_y + 270, countdown_text)


class DiagnosticOverlay(QWidget):
    """Diagnostic test overlay"""
    
    exit_diagnostics = pyqtSignal()
    enter_calibration = pyqtSignal()
    log_signal = pyqtSignal(str)  # Thread-safe logging
    
    # Available step sizes for jog mode (mm)
    STEP_SIZES = [0.5, 1.0, 10.0, 20.0, 30.0]
    
    def __init__(self, motion_controller, parent=None):
        super().__init__(parent)
        self.motion = motion_controller
        self.test_running = False
        self.test_abort = False  # Flag to abort running tests
        self.homed = False
        
        # Jog step size (default 0.5mm)
        self.current_step_size = 0.5
        self.step_buttons = {}  # Reference to step size buttons for styling
        
        # Connect log signal
        self.log_signal.connect(self._log_internal)
        
        self.setStyleSheet("background-color: rgba(0, 0, 0, 230);")
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Title
        title = QLabel("DIAGNOSTIC TEST MODE")
        title.setFont(QFont("Liberation Sans", 32, QFont.Bold))
        title.setStyleSheet("color: #3296FF;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Output display
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Liberation Mono", 11))
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 2px solid #3296FF;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.output)
        
        # Menu
        self.menu_text = QLabel(
            "[ 1 ] Confirm Communication with Teensy\n"
            "[ 2 ] Limit Switch Test\n"
            "[ 3 ] Fast Home\n"
            "[ 4 ] Manual Motor Jog Controls\n"
            "[ 5 ] Specimen Calibration Mode\n"
            "[ Q ] Quit Diagnostics and Start GUI\n"
            "[ ESC ] Abort Running Test / Exit Jog Mode"
        )
        self.menu_text.setFont(QFont("Liberation Mono", 14, QFont.Bold))
        self.menu_text.setStyleSheet("color: white; background-color: #2a2a2a; padding: 15px; border-radius: 5px;")
        layout.addWidget(self.menu_text)
        
        # Jog controls (hidden by default)
        self.jog_widget = self.create_diagnostic_jog_controls()
        self.jog_widget.hide()
        layout.addWidget(self.jog_widget)
        
        self.jog_mode = False
        self.jog_timers = {}
        
        self.setLayout(layout)
        
    def showEvent(self, event):
        """When shown, display welcome message"""
        super().showEvent(event)
        self.log("=== DIAGNOSTIC TEST MODE ===")
        self.log("Select a test by pressing the corresponding number key.")
        self.log("Press 'Q' to exit diagnostics and start the GUI.\n")
        self.setFocus()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle diagnostic menu selection"""
        key = event.text().upper()
        
        # Allow ESC to abort running tests or exit jog mode
        if event.key() == Qt.Key_Escape:
            if self.jog_mode:
                self.exit_jog_mode()
                return
            if self.test_running:
                self.log("\n⚠ Test aborted by user")
                self.test_abort = True
                self.test_running = False
            return
        
        if self.test_running or self.jog_mode:
            return  # Ignore other input during tests or jog mode
        
        if key == 'Q':
            self.exit_diagnostics.emit()
        elif key == '1':
            self.test_communication()
        elif key == '2':
            self.test_limit_switches()
        elif key == '3':
            self.test_fast_home()
        elif key == '4':
            self.enter_jog_mode()
        elif key == '5':
            self.enter_calibration.emit()
    
    def log(self, message: str):
        """Thread-safe logging - can be called from any thread"""
        self.log_signal.emit(message)
    
    @pyqtSlot(str)
    def _log_internal(self, message: str):
        """Internal log method - must only be called from main thread"""
        self.output.append(message)
        self.output.verticalScrollBar().setValue(
            self.output.verticalScrollBar().maximum()
        )
    
    @pyqtSlot()
    def test_communication(self):
        """Test 1: Confirm communication with Teensy"""
        self.test_running = True
        self.log("\n--- Test 1: Communication Test ---")
        
        def run_test():
            try:
                # Test if already connected
                if self.motion.connected:
                    self.log("✓ Already connected to Teensy")
                else:
                    self.log("Attempting to connect...")
                    if self.motion.connect():
                        self.log("✓ Successfully connected to Teensy")
                    else:
                        self.log("✗ Failed to connect to Teensy")
                        self.test_running = False
                        return
                
                # Send ping
                self.log("Sending PING...")
                if self.motion.protocol.send_command("!PING"):
                    time.sleep(0.3)
                    msg = self.motion.protocol.read_line(timeout=2.0)
                    if msg and msg.valid:
                        self.log(f"✓ Response: {msg.content}")
                        self.log("✓ Communication test PASSED")
                    else:
                        self.log("✗ No valid response received")
                else:
                    self.log("✗ Failed to send PING")
            except Exception as e:
                self.log(f"✗ Error: {e}")
            finally:
                self.test_running = False
        
        # Run in separate thread to avoid blocking GUI
        threading.Thread(target=run_test, daemon=True).start()
    
    @pyqtSlot()
    def test_limit_switches(self):
        """Test 2: Test all limit switches using Teensy's built-in limit switch test"""
        self.test_running = True
        self.test_abort = False
        self.log("\n--- Test 2: Limit Switch Test ---")
        self.log("This test uses Teensy's built-in limit switch monitor.")
        self.log("Press each switch when prompted. Press ESC to abort.\n")
        
        switches = [
            ("X_MIN", "X-axis minimum"),
            ("X_MAX", "X-axis maximum"),
            ("Y_MIN", "Y-axis minimum"),
            ("Y_MAX", "Y-axis maximum"),
            ("Z_MIN", "Z-axis minimum"),
            ("Z_MAX", "Z-axis maximum"),
            ("F_MIN", "Focus minimum"),
            ("F_MAX", "Focus maximum"),
        ]
        
        def run_test():
            try:
                # Pause watchdog to prevent interference with diagnostic mode
                self.motion.watchdog_paused = True
                
                # Auto-connect if needed
                if not self.motion.connected:
                    self.log("Connecting to Teensy...")
                    if not self.motion.connect():
                        self.log("✗ Failed to connect to Teensy")
                        return
                    self.log("✓ Connected")
                
                # Enter Teensy diagnostic mode
                self.log("Entering Teensy diagnostic mode...")
                self.motion.protocol.flush_input()
                if not self.motion.protocol.send_command("!DIAG_ENTER"):
                    self.log("✗ Failed to send DIAG_ENTER command")
                    return
                
                # Wait for ACK
                time.sleep(0.3)
                ack_received = False
                for _ in range(10):
                    msg = self.motion.protocol.read_line(timeout=0.5)
                    if msg and msg.valid:
                        if 'ACK' in msg.content and 'ENTERING_DIAGNOSTIC' in msg.content:
                            ack_received = True
                            break
                
                if not ack_received:
                    self.log("✗ Failed to enter diagnostic mode")
                    return
                
                self.log("✓ Entered Teensy diagnostic mode")
                
                # Flush menu output
                time.sleep(0.5)
                while self.motion.protocol.ser.in_waiting > 0:
                    self.motion.protocol.read_line(timeout=0.1)
                
                # Send command 6 to start limit switch test
                self.log("Starting limit switch monitor (Teensy menu option 6)...")
                self.motion.protocol.flush_input()
                if not self.motion.protocol.send_command("!DIAG_CMD 6"):
                    self.log("✗ Failed to send limit switch test command")
                    return
                
                # Wait for "Listening for limit switches" message
                time.sleep(0.3)
                for _ in range(10):
                    msg = self.motion.protocol.read_line(timeout=0.3)
                    if msg and msg.valid and 'Listening' in msg.content:
                        self.log("✓ Teensy limit switch monitor active")
                        break
                
                # Now test each switch
                detected_switches = set()
                
                for switch_name, description in switches:
                    if self.test_abort:
                        break
                    
                    if switch_name in detected_switches:
                        continue  # Already detected
                    
                    self.log(f"\nPress {description} ({switch_name}) switch...")
                    
                    # Monitor for switch trigger
                    start_time = time.time()
                    detected = False
                    
                    while time.time() - start_time < 30.0:
                        if self.test_abort:
                            break
                            
                        msg = self.motion.protocol.read_line(timeout=0.1)
                        if msg and msg.valid:
                            content = msg.content
                            # Look for "[OK] X_MAX triggered!" style messages
                            if 'triggered' in content:
                                # Extract switch name from message like "[OK] X_MAX triggered!"
                                for sw_name, sw_desc in switches:
                                    if sw_name in content:
                                        detected_switches.add(sw_name)
                                        if sw_name == switch_name:
                                            self.log(f"✓ {switch_name} detected!")
                                            detected = True
                                        else:
                                            self.log(f"  (Also detected: {sw_name})")
                                        break
                                if detected:
                                    break
                        time.sleep(0.05)
                    
                    if self.test_abort:
                        break
                        
                    if not detected:
                        self.log(f"✗ {switch_name} - TIMEOUT")
                
                # Exit limit switch test mode (send T to return to menu)
                self.log("\nReturning to diagnostic menu...")
                self.motion.protocol.send_command("!DIAG_CMD T")
                time.sleep(0.3)
                
                # Flush any remaining output
                while self.motion.protocol.ser.in_waiting > 0:
                    self.motion.protocol.read_line(timeout=0.1)
                
                # Exit Teensy diagnostic mode
                self.log("Exiting Teensy diagnostic mode...")
                self.motion.protocol.flush_input()
                self.motion.protocol.send_command("!DIAG_EXIT")
                time.sleep(0.3)
                
                # Flush exit response
                for _ in range(5):
                    msg = self.motion.protocol.read_line(timeout=0.3)
                    if not msg:
                        break
                
                self.log("✓ Exited diagnostic mode")
                
                if not self.test_abort:
                    # Summary
                    self.log(f"\n--- Summary: {len(detected_switches)}/8 switches detected ---")
                    for sw_name, sw_desc in switches:
                        status = "✓" if sw_name in detected_switches else "✗"
                        self.log(f"  {status} {sw_name}")
                    self.log("\n✓ Limit switch test complete")
                    
            except Exception as e:
                self.log(f"✗ Error: {e}")
                import traceback
                self.log(traceback.format_exc())
            finally:
                self.motion.watchdog_paused = False  # Resume watchdog
                self.test_running = False
        
        threading.Thread(target=run_test, daemon=True).start()
    
    @pyqtSlot()
    def test_fast_home(self):
        """Test 3: Fast home"""
        self.test_running = True
        self.log("\n--- Test 3: Fast Home ---")
        
        def run_test():
            try:
                if not self.motion.connected:
                    self.log("✗ Not connected to Teensy. Run Test 1 first.")
                    self.test_running = False
                    return
                
                self.log("Sending HOME_FAST command...")
                if not self.motion.protocol.send_command("!HOME_FAST"):
                    self.log("✗ Failed to send command")
                    self.test_running = False
                    return
                
                self.log("Homing in progress... (this may take up to 2 minutes)")
                
                # Wait for completion
                start_time = time.time()
                timeout = 120.0
                last_ping = time.time()
                
                while time.time() - start_time < timeout:
                    # Send periodic ping
                    if time.time() - last_ping > 2.0:
                        self.motion.protocol.send_command("!PING")
                        last_ping = time.time()
                    
                    msg = self.motion.protocol.read_line(timeout=0.5)
                    if msg and msg.valid:
                        if 'COMPLETE' in msg.content:
                            self.log(f"✓ {msg.content}")
                            self.log("✓ Homing complete!")
                            self.homed = True
                            break
                        elif 'ACK' in msg.content and 'HOMING' in msg.content:
                            self.log(f"  {msg.content}")
                
                if time.time() - start_time >= timeout:
                    self.log("✗ Homing timeout")
            except Exception as e:
                self.log(f"✗ Error: {e}")
            finally:
                self.test_running = False
        
        threading.Thread(target=run_test, daemon=True).start()
    
    @pyqtSlot()
    def test_motor_jog(self):
        """Test 4: Manual Motor Jog - replaced with enter_jog_mode"""
        self.enter_jog_mode()
    
    def enter_jog_mode(self):
        """Enter manual jog control mode"""
        if not self.homed:
            reply = QMessageBox.warning(
                self,
                "Not Homed - Warning",
                "System has not been homed!\n\n"
                "Jogging without homing may cause unexpected behavior or collisions.\n\n"
                "Continue anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                self.log("\nManual jog mode cancelled.")
                return
        
        self.log("\n--- Manual Jog Mode ---")
        self.log("Use the jog pad below to move motors.")
        self.log("Press ESC to exit jog mode.\n")
        
        self.jog_mode = True
        self.menu_text.hide()
        self.jog_widget.show()
        self.output.setMaximumHeight(200)  # Reduce output height to make room
    
    def exit_jog_mode(self):
        """Exit manual jog control mode"""
        # Stop any active jogs
        for axis in list(self.jog_timers.keys()):
            self.stop_diag_jog(axis)
        
        self.log("Exiting jog mode...\n")
        self.jog_mode = False
        self.jog_widget.hide()
        self.menu_text.show()
        self.output.setMaximumHeight(16777215)  # Reset to unlimited
    
    def create_diagnostic_jog_controls(self) -> QWidget:
        """Create jog control pad for diagnostic mode with selectable step sizes"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Instructions
        inst = QLabel("Hold buttons to jog motors • Release to stop • Press ESC to exit")
        inst.setFont(QFont("Liberation Sans", 12))
        inst.setStyleSheet("color: yellow; padding: 10px;")
        inst.setAlignment(Qt.AlignCenter)
        layout.addWidget(inst)
        
        # Step size selector
        step_layout = QHBoxLayout()
        step_label = QLabel("Step Size:")
        step_label.setFont(QFont("Liberation Sans", 12, QFont.Bold))
        step_label.setStyleSheet("color: white;")
        step_layout.addWidget(step_label)
        
        self.step_buttons = {}
        for size in self.STEP_SIZES:
            # Format label: show as integer if whole number
            if size == int(size):
                label = f"{int(size)}mm"
            else:
                label = f"{size}mm"
            btn = QPushButton(label)
            btn.setFixedSize(70, 40)
            btn.setFont(QFont("Liberation Sans", 11, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, s=size: self.set_step_size(s))
            self.step_buttons[size] = btn
            step_layout.addWidget(btn)
        
        step_layout.addStretch()
        layout.addLayout(step_layout)
        
        # Update button styles to show current selection
        self.update_step_button_styles()
        
        # X/Y controls (D-pad style)
        xy_group = QHBoxLayout()
        xy_layout = QVBoxLayout()
        xy_layout.setSpacing(5)
        
        # Row 1: Y+
        row1 = QHBoxLayout()
        row1.addStretch()
        y_plus_btn = JogButton("▲ Y+")
        y_plus_btn.pressed_signal.connect(lambda: self.start_diag_jog('Y', 1))
        y_plus_btn.released_signal.connect(lambda: self.stop_diag_jog('Y'))
        row1.addWidget(y_plus_btn)
        row1.addStretch()
        
        # Row 2: X-, Center, X+
        row2 = QHBoxLayout()
        x_minus_btn = JogButton("◄ X-")
        x_minus_btn.pressed_signal.connect(lambda: self.start_diag_jog('X', -1))
        x_minus_btn.released_signal.connect(lambda: self.stop_diag_jog('X'))
        row2.addWidget(x_minus_btn)
        
        center_label = QLabel("X/Y")
        center_label.setAlignment(Qt.AlignCenter)
        center_label.setFixedSize(80, 60)
        center_label.setStyleSheet("background-color: rgba(40, 40, 40, 150); border-radius: 8px; color: white;")
        center_label.setFont(QFont("Liberation Sans", 12, QFont.Bold))
        row2.addWidget(center_label)
        
        x_plus_btn = JogButton("X+ ►")
        x_plus_btn.pressed_signal.connect(lambda: self.start_diag_jog('X', 1))
        x_plus_btn.released_signal.connect(lambda: self.stop_diag_jog('X'))
        row2.addWidget(x_plus_btn)
        
        # Row 3: Y-
        row3 = QHBoxLayout()
        row3.addStretch()
        y_minus_btn = JogButton("▼ Y-")
        y_minus_btn.pressed_signal.connect(lambda: self.start_diag_jog('Y', -1))
        y_minus_btn.released_signal.connect(lambda: self.stop_diag_jog('Y'))
        row3.addWidget(y_minus_btn)
        row3.addStretch()
        
        xy_layout.addLayout(row1)
        xy_layout.addLayout(row2)
        xy_layout.addLayout(row3)
        xy_group.addLayout(xy_layout)
        
        # Z/F controls (vertical strip)
        zf_layout = QVBoxLayout()
        
        # Z controls
        z_label = QLabel("Z (Focus)")
        z_label.setAlignment(Qt.AlignCenter)
        z_label.setFont(QFont("Liberation Sans", 11, QFont.Bold))
        z_label.setStyleSheet("color: white;")
        zf_layout.addWidget(z_label)
        
        z_plus_btn = JogButton("▲ Z+")
        z_plus_btn.setFixedSize(100, 50)
        z_plus_btn.pressed_signal.connect(lambda: self.start_diag_jog('Z', 1))
        z_plus_btn.released_signal.connect(lambda: self.stop_diag_jog('Z'))
        zf_layout.addWidget(z_plus_btn)
        
        z_minus_btn = JogButton("▼ Z-")
        z_minus_btn.setFixedSize(100, 50)
        z_minus_btn.pressed_signal.connect(lambda: self.start_diag_jog('Z', -1))
        z_minus_btn.released_signal.connect(lambda: self.stop_diag_jog('Z'))
        zf_layout.addWidget(z_minus_btn)
        
        zf_layout.addSpacing(20)
        
        # F controls
        f_label = QLabel("F (Zoom)")
        f_label.setAlignment(Qt.AlignCenter)
        f_label.setFont(QFont("Liberation Sans", 11, QFont.Bold))
        f_label.setStyleSheet("color: white;")
        zf_layout.addWidget(f_label)
        
        f_plus_btn = JogButton("▲ F+")
        f_plus_btn.setFixedSize(100, 50)
        f_plus_btn.pressed_signal.connect(lambda: self.start_diag_jog('F', 1))
        f_plus_btn.released_signal.connect(lambda: self.stop_diag_jog('F'))
        zf_layout.addWidget(f_plus_btn)
        
        f_minus_btn = JogButton("▼ F-")
        f_minus_btn.setFixedSize(100, 50)
        f_minus_btn.pressed_signal.connect(lambda: self.start_diag_jog('F', -1))
        f_minus_btn.released_signal.connect(lambda: self.stop_diag_jog('F'))
        zf_layout.addWidget(f_minus_btn)
        
        xy_group.addLayout(zf_layout)
        layout.addLayout(xy_group)
        
        widget.setLayout(layout)
        return widget
    
    def set_step_size(self, size: float):
        """Set the jog step size"""
        self.current_step_size = size
        self.update_step_button_styles()
        self.log(f"Step size set to {size}mm")
    
    def update_step_button_styles(self):
        """Update step size button styles to highlight current selection"""
        for size, btn in self.step_buttons.items():
            if size == self.current_step_size:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(50, 150, 255, 220);
                        border: 2px solid #3296FF;
                        border-radius: 5px;
                        color: white;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(60, 60, 60, 200);
                        border: 2px solid #666;
                        border-radius: 5px;
                        color: white;
                    }
                    QPushButton:hover {
                        background-color: rgba(80, 80, 80, 220);
                        border: 2px solid #888;
                    }
                """)
    
    def start_diag_jog(self, axis: str, direction: int):
        """Start jogging axis in diagnostic mode
        
        Args:
            axis: 'X', 'Y', 'Z', or 'F'
            direction: 1 for positive, -1 for negative
        """
        if not self.motion.connected:
            self.log(f"✗ Cannot jog - not connected to Teensy")
            return
        
        # Calculate actual increment from step size and direction
        increment = self.current_step_size * direction
        
        # Immediate single jog
        cmd = f"!JOG {axis}{increment:+.2f}"
        self.motion.protocol.send_command(cmd)
        self.log(f"Jog {axis} {increment:+.1f}mm")
        
        # Setup continuous jog timer (only for small steps)
        # For large steps (>5mm), don't repeat - single press = single move
        if self.current_step_size <= 5.0:
            def continuous_jog():
                cmd = f"!JOG {axis}{increment:+.2f}"
                self.motion.protocol.send_command(cmd)
            
            # Adjust timer interval based on step size
            interval = max(200, int(300 * self.current_step_size))  # Longer interval for bigger steps
            timer = QTimer()
            timer.timeout.connect(continuous_jog)
            timer.start(interval)
            self.jog_timers[axis] = timer
    
    def stop_diag_jog(self, axis: str):
        """Stop jogging axis in diagnostic mode"""
        if axis in self.jog_timers:
            self.jog_timers[axis].stop()
            del self.jog_timers[axis]


class GridCell(QPushButton):
    """Clickable cell in the calibration grid"""
    
    cell_clicked = pyqtSignal(int, int)  # row, col
    
    def __init__(self, row: int, col: int, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.status = "empty"  # empty, calibrated, modified
        self.setFixedSize(70, 50)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self._on_click)
        self.update_style()
        
    def _on_click(self):
        self.cell_clicked.emit(self.row, self.col)
    
    def set_status(self, status: str):
        """Set cell status: 'empty', 'calibrated', 'modified', 'selected'"""
        self.status = status
        self.update_style()
    
    def update_style(self):
        colors = {
            "empty": ("#555", "#888", "#aaa"),      # gray
            "calibrated": ("#2a5", "#3b6", "#4c7"), # green
            "modified": ("#a85", "#b96", "#ca7"),   # orange/yellow
            "selected": ("#37f", "#48f", "#59f"),   # blue
        }
        bg, hover, pressed = colors.get(self.status, colors["empty"])
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                border: 2px solid #333;
                border-radius: 5px;
                color: white;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:pressed {{
                background-color: {pressed};
            }}
        """)


class CalibrationOverlay(QWidget):
    """Specimen calibration mode overlay for creating/editing JSON files"""
    
    exit_calibration = pyqtSignal()
    homing_complete = pyqtSignal(bool)  # Signal for thread-safe homing completion
    
    def __init__(self, motion_controller, video_thread, parent=None):
        super().__init__(parent)
        self.motion = motion_controller
        self.video = video_thread
        self.grid_data = {}  # {(row,col): specimen_dict}
        self.modified_cells = set()  # Cells saved but not committed to JSON
        self.deleted_cells = set()  # Cells pending deletion (were in JSON, now removed)
        self.current_cell = (0, 0)
        self.unsaved_changes = False
        self.current_file_path = None
        self.is_jogging = False
        self.jog_timer = None
        self.current_frame = None  # Store latest video frame
        self.jog_enabled = False  # Track if jog is enabled
        
        # Connect homing signal to handler
        self.homing_complete.connect(self.on_home_complete)
        
        # Connect to video thread signal
        if self.video:
            self.video.frame_ready.connect(self.on_frame_ready)
        
        # Common values for dropdowns (will be populated from loaded JSON)
        self.known_minerals = set()
        self.known_locations = set()
        self.known_collectors = set()
        
        # Force opaque black background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(0, 0, 0))
        self.setPalette(palette)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #444;
                border: 2px solid #666;
                border-radius: 5px;
                color: white;
                padding: 5px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #555;
                border-color: #888;
            }
            QPushButton:pressed {
                background-color: #333;
            }
            QComboBox {
                background-color: #333;
                border: 2px solid #555;
                border-radius: 4px;
                color: white;
                padding: 5px;
                min-height: 25px;
            }
            QComboBox:hover {
                border-color: #777;
            }
            QComboBox QAbstractItemView {
                background-color: #333;
                color: white;
                selection-background-color: #3296FF;
            }
            QLabel {
                color: white;
            }
        """)
        self.init_ui()
        
    def init_ui(self):
        """Build the calibration interface"""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # === LEFT SIDE: Grid + Metadata ===
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        
        # Title
        title = QLabel("SPECIMEN CALIBRATION MODE")
        title.setFont(QFont("Liberation Sans", 28, QFont.Bold))
        title.setStyleSheet("color: #3296FF;")
        title.setAlignment(Qt.AlignCenter)
        left_panel.addWidget(title)
        
        # Connection/Homing status bar
        status_bar = QHBoxLayout()
        status_bar.setSpacing(15)
        
        self.connection_label = QLabel("⚪ Not Homed")
        self.connection_label.setFont(QFont("Liberation Sans", 12, QFont.Bold))
        self.connection_label.setStyleSheet("color: #f55;")
        status_bar.addWidget(self.connection_label)
        
        self.home_btn = QPushButton("🏠 Connect & Home")
        self.home_btn.setFixedHeight(40)
        self.home_btn.setFixedWidth(200)
        self.home_btn.clicked.connect(self.do_home)
        self.home_btn.setStyleSheet("background-color: #664; font-size: 14px; font-weight: bold;")
        status_bar.addWidget(self.home_btn)
        
        status_bar.addStretch()
        left_panel.addLayout(status_bar)
        
        # Big warning message
        self.homing_warning = QLabel("⚠️  MUST HOME BEFORE JOGGING  ⚠️")
        self.homing_warning.setFont(QFont("Liberation Sans", 18, QFont.Bold))
        self.homing_warning.setStyleSheet("""
            color: #ff0; 
            background-color: #530; 
            padding: 15px; 
            border: 3px solid #f80;
            border-radius: 8px;
        """)
        self.homing_warning.setAlignment(Qt.AlignCenter)
        left_panel.addWidget(self.homing_warning)
        
        # Grid overview
        grid_group = QGroupBox("Specimen Grid (4 rows × 7 columns)")
        grid_group.setFont(QFont("Liberation Sans", 12, QFont.Bold))
        grid_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)
        
        # Row labels
        for row in range(4):
            lbl = QLabel(f"R{row}")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #888;")
            grid_layout.addWidget(lbl, row + 1, 0)
        
        # Column labels
        for col in range(7):
            lbl = QLabel(f"C{col}")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #888;")
            grid_layout.addWidget(lbl, 0, col + 1)
        
        # Grid cells
        self.grid_cells = {}
        for row in range(4):
            for col in range(7):
                cell = GridCell(row, col)
                cell.setText(f"{row},{col}")
                cell.cell_clicked.connect(self.on_cell_clicked)
                self.grid_cells[(row, col)] = cell
                grid_layout.addWidget(cell, row + 1, col + 1)
        
        grid_group.setLayout(grid_layout)
        left_panel.addWidget(grid_group)
        
        # Legend and cell action buttons
        legend_action_layout = QHBoxLayout()
        legend_action_layout.setSpacing(15)
        
        # Legend on the left
        for status, text in [("empty", "Empty"), ("calibrated", "Calibrated"), 
                             ("modified", "Modified"), ("selected", "Selected")]:
            indicator = QLabel(f"● {text}")
            colors = {"empty": "#555", "calibrated": "#2a5", "modified": "#a85", "selected": "#37f"}
            indicator.setStyleSheet(f"color: {colors[status]}; font-weight: bold;")
            legend_action_layout.addWidget(indicator)
        
        legend_action_layout.addStretch()
        
        # Cell action buttons on the right
        self.goto_btn = QPushButton("📍 Go To Cell")
        self.goto_btn.setFixedSize(130, 35)
        self.goto_btn.clicked.connect(self.goto_current_cell)
        self.goto_btn.setStyleSheet("background-color: #446; font-size: 12px; font-weight: bold;")
        legend_action_layout.addWidget(self.goto_btn)
        
        self.save_cell_btn = QPushButton("✓ Save Cell Data")
        self.save_cell_btn.setFixedSize(150, 35)
        self.save_cell_btn.clicked.connect(self.save_cell_data)
        self.save_cell_btn.setStyleSheet("background-color: #464; font-size: 12px; font-weight: bold;")
        legend_action_layout.addWidget(self.save_cell_btn)
        
        self.delete_cell_btn = QPushButton("✗ Delete Cell Data")
        self.delete_cell_btn.setFixedSize(150, 35)
        self.delete_cell_btn.clicked.connect(self.delete_cell_data)
        self.delete_cell_btn.setStyleSheet("background-color: #643; font-size: 12px; font-weight: bold;")
        legend_action_layout.addWidget(self.delete_cell_btn)
        
        left_panel.addLayout(legend_action_layout)
        
        # Metadata entry
        meta_group = QGroupBox("Specimen Metadata")
        meta_group.setFont(QFont("Liberation Sans", 12, QFont.Bold))
        meta_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        meta_layout = QGridLayout()
        meta_layout.setSpacing(10)
        
        # Mineral name
        meta_layout.addWidget(QLabel("Mineral Name:"), 0, 0)
        self.mineral_combo = QComboBox()
        self.mineral_combo.setEditable(True)
        self.mineral_combo.setMinimumWidth(250)
        self.mineral_combo.currentTextChanged.connect(self.on_metadata_changed)
        meta_layout.addWidget(self.mineral_combo, 0, 1)
        
        # Location
        meta_layout.addWidget(QLabel("Location:"), 1, 0)
        self.location_combo = QComboBox()
        self.location_combo.setEditable(True)
        self.location_combo.setMinimumWidth(250)
        self.location_combo.currentTextChanged.connect(self.on_metadata_changed)
        meta_layout.addWidget(self.location_combo, 1, 1)
        
        # Collector
        meta_layout.addWidget(QLabel("Collector:"), 2, 0)
        self.collector_combo = QComboBox()
        self.collector_combo.setEditable(True)
        self.collector_combo.setMinimumWidth(250)
        self.collector_combo.currentTextChanged.connect(self.on_metadata_changed)
        meta_layout.addWidget(self.collector_combo, 2, 1)
        
        meta_group.setLayout(meta_layout)
        left_panel.addWidget(meta_group)
        
        # File operations
        file_layout = QHBoxLayout()
        file_layout.setSpacing(10)
        
        self.load_btn = QPushButton("📂 Load JSON")
        self.load_btn.setFixedHeight(40)
        self.load_btn.clicked.connect(self.load_json)
        file_layout.addWidget(self.load_btn)
        
        self.save_btn = QPushButton("💾 Save JSON")
        self.save_btn.setFixedHeight(40)
        self.save_btn.clicked.connect(self.save_json)
        file_layout.addWidget(self.save_btn)
        
        self.set_default_btn = QPushButton("⭐ Set as Default")
        self.set_default_btn.setFixedHeight(40)
        self.set_default_btn.setStyleSheet("background-color: #546; font-size: 12px; font-weight: bold;")
        self.set_default_btn.clicked.connect(self.set_as_default_tray)
        file_layout.addWidget(self.set_default_btn)
        
        self.new_btn = QPushButton("📄 New Blank")
        self.new_btn.setFixedHeight(40)
        self.new_btn.clicked.connect(self.new_blank)
        file_layout.addWidget(self.new_btn)
        
        self.exit_btn = QPushButton("🚪 Exit")
        self.exit_btn.setFixedHeight(40)
        self.exit_btn.setStyleSheet("background-color: #633;")
        self.exit_btn.clicked.connect(self.on_exit)
        file_layout.addWidget(self.exit_btn)
        
        left_panel.addLayout(file_layout)
        
        # Status bar
        self.status_label = QLabel("Ready - Connect and Home, then load or create JSON")
        self.status_label.setStyleSheet("color: #aaa; font-style: italic; padding: 5px;")
        left_panel.addWidget(self.status_label)
        
        left_panel.addStretch()
        main_layout.addLayout(left_panel, stretch=1)
        
        # === RIGHT SIDE: Video + Controls ===
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)
        
        # Large video preview
        self.video_label = QLabel()
        self.video_label.setFixedSize(800, 600)
        self.video_label.setStyleSheet("background-color: #111; border: 3px solid #555;")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setText("Video Preview\n(Connect and Home first)")
        self.video_label.setFont(QFont("Liberation Sans", 14))
        right_panel.addWidget(self.video_label, alignment=Qt.AlignCenter)
        
        # Current position display (compact horizontal)
        pos_layout = QHBoxLayout()
        pos_layout.setSpacing(20)
        
        self.cell_label = QLabel("Cell: [0, 0]")
        self.cell_label.setFont(QFont("Liberation Sans", 14, QFont.Bold))
        self.cell_label.setStyleSheet("color: #3296FF;")
        pos_layout.addWidget(self.cell_label)
        
        # Position readouts
        self.x_label = QLabel("X: 0.0")
        self.x_label.setFont(QFont("Liberation Mono", 12))
        pos_layout.addWidget(self.x_label)
        
        self.y_label = QLabel("Y: 0.0")
        self.y_label.setFont(QFont("Liberation Mono", 12))
        pos_layout.addWidget(self.y_label)
        
        self.z_label = QLabel("Z: 0.0")
        self.z_label.setFont(QFont("Liberation Mono", 12))
        pos_layout.addWidget(self.z_label)
        
        self.f_label = QLabel("F: 0.0")
        self.f_label.setFont(QFont("Liberation Mono", 12))
        pos_layout.addWidget(self.f_label)
        
        self.offset_label = QLabel("Offset: X=+0.0 Y=+0.0")
        self.offset_label.setStyleSheet("color: #888;")
        pos_layout.addWidget(self.offset_label)
        
        pos_layout.addStretch()
        right_panel.addLayout(pos_layout)
        
        # Step size selector
        step_layout = QHBoxLayout()
        step_label = QLabel("Step Size:")
        step_label.setStyleSheet("font-weight: bold; color: #AAA;")
        step_layout.addWidget(step_label)
        
        self.step_sizes = [0.1, 0.5, 2.0, 5.0]  # Available step sizes in mm
        self.current_step_size = 0.5  # Default step size
        self.step_buttons = []
        
        for size in self.step_sizes:
            btn = QPushButton(f"{size}")
            btn.setFixedSize(55, 45)
            btn.setCheckable(True)
            btn.setChecked(size == self.current_step_size)
            btn.clicked.connect(lambda checked, s=size: self.set_step_size(s))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #333;
                    border: 2px solid #555;
                    border-radius: 6px;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:checked {
                    background-color: #3296FF;
                    border: 2px solid #5AF;
                }
                QPushButton:hover {
                    border-color: #888;
                }
            """)
            step_layout.addWidget(btn)
            self.step_buttons.append(btn)
        
        step_layout.addWidget(QLabel("mm"))
        step_layout.addStretch()
        right_panel.addLayout(step_layout)
        
        # Jog controls (horizontal layout)
        jog_layout = QHBoxLayout()
        jog_layout.setSpacing(30)
        
        # X/Y jog (D-pad style)
        xy_widget = QWidget()
        xy_grid = QGridLayout()
        xy_grid.setSpacing(5)
        
        xy_label = QLabel("X/Y Stage")
        xy_label.setAlignment(Qt.AlignCenter)
        xy_label.setStyleSheet("font-weight: bold;")
        xy_grid.addWidget(xy_label, 0, 0, 1, 3)
        
        self.y_plus_jog = QPushButton("▲")
        self.y_plus_jog.setFixedSize(60, 60)
        self.y_plus_jog.pressed.connect(lambda: self.start_jog('Y', 1))
        self.y_plus_jog.released.connect(self.stop_jog)
        xy_grid.addWidget(self.y_plus_jog, 1, 1)
        
        self.x_minus_jog = QPushButton("◄")
        self.x_minus_jog.setFixedSize(60, 60)
        self.x_minus_jog.pressed.connect(lambda: self.start_jog('X', -1))
        self.x_minus_jog.released.connect(self.stop_jog)
        xy_grid.addWidget(self.x_minus_jog, 2, 0)
        
        self.x_plus_jog = QPushButton("►")
        self.x_plus_jog.setFixedSize(60, 60)
        self.x_plus_jog.pressed.connect(lambda: self.start_jog('X', 1))
        self.x_plus_jog.released.connect(self.stop_jog)
        xy_grid.addWidget(self.x_plus_jog, 2, 2)
        
        self.y_minus_jog = QPushButton("▼")
        self.y_minus_jog.setFixedSize(60, 60)
        self.y_minus_jog.pressed.connect(lambda: self.start_jog('Y', -1))
        self.y_minus_jog.released.connect(self.stop_jog)
        xy_grid.addWidget(self.y_minus_jog, 3, 1)
        
        xy_widget.setLayout(xy_grid)
        jog_layout.addWidget(xy_widget)
        
        # Z (Focus) jog
        z_widget = QWidget()
        z_vbox = QVBoxLayout()
        z_label = QLabel("Z Focus")
        z_label.setAlignment(Qt.AlignCenter)
        z_label.setStyleSheet("font-weight: bold;")
        z_vbox.addWidget(z_label)
        
        self.z_plus_jog = QPushButton("▲")
        self.z_plus_jog.setFixedSize(60, 60)
        self.z_plus_jog.pressed.connect(lambda: self.start_jog('Z', 1))
        self.z_plus_jog.released.connect(self.stop_jog)
        z_vbox.addWidget(self.z_plus_jog, alignment=Qt.AlignCenter)
        
        self.z_minus_jog = QPushButton("▼")
        self.z_minus_jog.setFixedSize(60, 60)
        self.z_minus_jog.pressed.connect(lambda: self.start_jog('Z', -1))
        self.z_minus_jog.released.connect(self.stop_jog)
        z_vbox.addWidget(self.z_minus_jog, alignment=Qt.AlignCenter)
        
        z_widget.setLayout(z_vbox)
        jog_layout.addWidget(z_widget)
        
        # F (Zoom) jog
        f_widget = QWidget()
        f_vbox = QVBoxLayout()
        f_label = QLabel("F Zoom")
        f_label.setAlignment(Qt.AlignCenter)
        f_label.setStyleSheet("font-weight: bold;")
        f_vbox.addWidget(f_label)
        
        self.f_plus_jog = QPushButton("▲")
        self.f_plus_jog.setFixedSize(60, 60)
        self.f_plus_jog.pressed.connect(lambda: self.start_jog('F', 1))
        self.f_plus_jog.released.connect(self.stop_jog)
        f_vbox.addWidget(self.f_plus_jog, alignment=Qt.AlignCenter)
        
        self.f_minus_jog = QPushButton("▼")
        self.f_minus_jog.setFixedSize(60, 60)
        self.f_minus_jog.pressed.connect(lambda: self.start_jog('F', -1))
        self.f_minus_jog.released.connect(self.stop_jog)
        f_vbox.addWidget(self.f_minus_jog, alignment=Qt.AlignCenter)
        
        f_widget.setLayout(f_vbox)
        jog_layout.addWidget(f_widget)
        
        jog_layout.addStretch()
        
        # Navigation buttons (prev/next cell)
        nav_widget = QWidget()
        nav_vbox = QVBoxLayout()
        nav_vbox.setSpacing(10)
        
        nav_label = QLabel("Navigate")
        nav_label.setAlignment(Qt.AlignCenter)
        nav_label.setStyleSheet("font-weight: bold;")
        nav_vbox.addWidget(nav_label)
        
        # Navigation
        nav_hbox = QHBoxLayout()
        self.prev_btn = QPushButton("←")
        self.prev_btn.setFixedSize(50, 40)
        self.prev_btn.clicked.connect(self.prev_cell)
        nav_hbox.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("→")
        self.next_btn.setFixedSize(50, 40)
        self.next_btn.clicked.connect(self.next_cell)
        nav_hbox.addWidget(self.next_btn)
        
        nav_vbox.addLayout(nav_hbox)
        nav_widget.setLayout(nav_vbox)
        jog_layout.addWidget(nav_widget)
        
        right_panel.addLayout(jog_layout)
        
        # Brightness slider for LED ring
        self.brightness_slider = BrightnessSlider()
        self.brightness_slider.brightness_changed.connect(self._on_brightness_changed)
        right_panel.addWidget(self.brightness_slider)
        
        main_layout.addLayout(right_panel, stretch=1)
        
        self.setLayout(main_layout)
        
        # Collect all jog buttons for easy enable/disable
        self.jog_buttons = [
            self.x_plus_jog, self.x_minus_jog,
            self.y_plus_jog, self.y_minus_jog,
            self.z_plus_jog, self.z_minus_jog,
            self.f_plus_jog, self.f_minus_jog,
            self.goto_btn
        ]
        
        # Initially disable jog buttons
        self.set_jog_enabled(False)
        
        # Video update timer
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.update_video_preview)
        
        # Position update timer
        self.pos_timer = QTimer()
        self.pos_timer.timeout.connect(self.update_position_display)
    
    def _on_brightness_changed(self, percent: int):
        """Handle brightness slider change in calibration mode"""
        led = get_led_controller()
        led.set_brightness(percent)
    
    def showEvent(self, event):
        """Sync brightness slider with LED controller when overlay opens"""
        super().showEvent(event)
        led = get_led_controller()
        current_brightness = led.get_brightness()
        self.brightness_slider.set_value(current_brightness)
    
    def set_jog_enabled(self, enabled: bool):
        """Enable or disable all jog buttons"""
        self.jog_enabled = enabled
        print(f"DEBUG: set_jog_enabled({enabled})")
        for btn in self.jog_buttons:
            btn.setEnabled(enabled)
            if enabled:
                btn.setStyleSheet("background-color: #444; color: white;")
            else:
                btn.setStyleSheet("background-color: #333; color: #666;")
        
        # Re-apply special colors
        if enabled:
            self.goto_btn.setStyleSheet("background-color: #446; font-size: 14px; color: white;")
            self.save_cell_btn.setStyleSheet("background-color: #464; font-size: 14px; color: white;")
    
    def do_home(self):
        """Connect (if needed) and home all axes"""
        self.home_btn.setEnabled(False)
        self.status_label.setText("Connecting...")
        QApplication.processEvents()
        
        # Connect first if not connected
        if not self.motion.connected:
            if not self.motion.connect():
                self.status_label.setText("Connection failed - check USB cable")
                self.connection_label.setText("🔴 Connection Failed")
                self.connection_label.setStyleSheet("color: #f55;")
                self.home_btn.setEnabled(True)
                return
            
        self.connection_label.setText("🟡 Connected - Homing...")
        self.connection_label.setStyleSheet("color: #ff0;")
        self.status_label.setText("Homing all axes... Please wait...")
        QApplication.processEvents()
        
        def run_home():
            def progress(msg):
                print(f"DEBUG home progress: {msg}")
                QTimer.singleShot(0, lambda: self.status_label.setText(f"Homing: {msg}"))
            
            print("DEBUG: Starting motion.home()")
            success = self.motion.home(progress)
            print(f"DEBUG: motion.home() returned {success}")
            # Use signal for thread-safe callback (QTimer.singleShot can fail from threads)
            self.homing_complete.emit(success)
        
        threading.Thread(target=run_home, daemon=True).start()
    
    def on_home_complete(self, success: bool):
        """Called when homing completes"""
        print(f"DEBUG: on_home_complete({success})")
        if success:
            self.homing_warning.hide()
            self.connection_label.setText("🟢 Homed")
            self.connection_label.setStyleSheet("color: #5f5;")
            self.home_btn.setText("✓ Homed")
            self.home_btn.setStyleSheet("background-color: #363; font-size: 14px;")
            self.set_jog_enabled(True)
            self.status_label.setText("Homed! Ready to calibrate - Load JSON or create new")
        else:
            self.status_label.setText("Homing failed! Check limit switches.")
            self.connection_label.setText("🔴 Home Failed")
            self.connection_label.setStyleSheet("color: #f55;")
            self.home_btn.setEnabled(True)
        
    def showEvent(self, event):
        """Called when overlay is shown"""
        super().showEvent(event)
        self.video_timer.start(33)  # ~30 FPS
        self.pos_timer.start(200)   # 5 Hz position updates
        self.select_cell(0, 0)
        self.setFocus()
        
    def hideEvent(self, event):
        """Called when overlay is hidden"""
        super().hideEvent(event)
        self.video_timer.stop()
        self.pos_timer.stop()
        self.stop_jog()
    
    def update_video_preview(self):
        """Update the video preview label with current frame"""
        if self.current_frame is not None:
            # Scale to preview size (800x600)
            scaled = self.current_frame.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.video_label.setPixmap(scaled)
    
    def on_frame_ready(self, q_image: QImage):
        """Receive video frames from VideoThread"""
        self.current_frame = QPixmap.fromImage(q_image)
    
    def update_position_display(self):
        """Update position readouts"""
        x, y, z, f = self.motion.get_current_position()
        self.x_label.setText(f"{x:.2f} mm")
        self.y_label.setText(f"{y:.2f} mm")
        self.z_label.setText(f"{z:.2f} mm")
        self.f_label.setText(f"{f:.2f} mm")
        
        # Calculate offset from nominal
        row, col = self.current_cell
        nominal_x = 19.5 + (col * 39.0)
        nominal_y = 22.5 + (row * 43.0)
        offset_x = x - nominal_x
        offset_y = y - nominal_y
        self.offset_label.setText(f"Offset from nominal: X={offset_x:+.2f}  Y={offset_y:+.2f}")
    
    def on_cell_clicked(self, row: int, col: int):
        """Handle grid cell click"""
        self.select_cell(row, col)
    
    def select_cell(self, row: int, col: int):
        """Select a cell for editing"""
        # Update previous cell's visual state
        prev_row, prev_col = self.current_cell
        prev_cell = self.grid_cells.get((prev_row, prev_col))
        if prev_cell:
            if (prev_row, prev_col) in self.modified_cells:
                prev_cell.set_status("modified")
            elif (prev_row, prev_col) in self.deleted_cells:
                prev_cell.set_status("modified")  # Pending deletion shows as modified
            elif (prev_row, prev_col) in self.grid_data:
                prev_cell.set_status("calibrated")
            else:
                prev_cell.set_status("empty")
        
        # Select new cell
        self.current_cell = (row, col)
        self.grid_cells[(row, col)].set_status("selected")
        
        # Update cell label
        self.cell_label.setText(f"Cell: [{row}, {col}]")
        
        # Load cell data if exists
        if (row, col) in self.grid_data:
            data = self.grid_data[(row, col)]
            self.mineral_combo.setCurrentText(data.get("mineral_name", ""))
            self.location_combo.setCurrentText(data.get("location", ""))
            self.collector_combo.setCurrentText(data.get("collector", ""))
        else:
            self.mineral_combo.setCurrentText("")
            self.location_combo.setCurrentText("")
            self.collector_combo.setCurrentText("")
    
    def goto_current_cell(self):
        """Move to the nominal position of the current cell"""
        row, col = self.current_cell
        
        # Check if we have saved position data for this cell
        if (row, col) in self.grid_data:
            data = self.grid_data[(row, col)]
            nominal_x = 19.5 + (col * 39.0)
            nominal_y = 22.5 + (row * 43.0)
            x = nominal_x + data.get("x_offset_mm", 0)
            y = nominal_y + data.get("y_offset_mm", 0)
            z = data.get("focus_mm", 10.0)
            f = data.get("zoom_mm", 5.0)
        else:
            # Use nominal position with defaults
            x = 19.5 + (col * 39.0)
            y = 22.5 + (row * 43.0)
            z = 10.0  # Default focus
            f = 5.0   # Default zoom
        
        self.status_label.setText(f"Moving to cell [{row}, {col}]...")
        
        # Move in background thread
        def do_move():
            success = self.motion.move_to_position(x, y, z, f)
            if success:
                QTimer.singleShot(0, lambda: self.status_label.setText(f"At cell [{row}, {col}] - Use jog to fine-tune"))
            else:
                QTimer.singleShot(0, lambda: self.status_label.setText("Move failed!"))
        
        threading.Thread(target=do_move, daemon=True).start()
    
    def save_cell_data(self):
        """Save current position and metadata to the cell"""
        row, col = self.current_cell
        x, y, z, f = self.motion.get_current_position()
        
        # Calculate offsets from nominal
        nominal_x = 19.5 + (col * 39.0)
        nominal_y = 22.5 + (row * 43.0)
        x_offset = x - nominal_x
        y_offset = y - nominal_y
        
        # Get metadata
        mineral = self.mineral_combo.currentText().strip()
        location = self.location_combo.currentText().strip()
        collector = self.collector_combo.currentText().strip()
        
        if not mineral:
            QMessageBox.warning(self, "Missing Data", "Please enter a mineral name.")
            return
        
        # Save to grid data
        self.grid_data[(row, col)] = {
            "row": row,
            "col": col,
            "mineral_name": mineral,
            "location": location or "Unknown",
            "collector": collector or "Unknown",
            "x_offset_mm": round(x_offset, 2),
            "y_offset_mm": round(y_offset, 2),
            "focus_mm": round(z, 2),
            "zoom_mm": round(f, 2)
        }
        
        # Update known values for dropdowns
        self.known_minerals.add(mineral)
        if location:
            self.known_locations.add(location)
        if collector:
            self.known_collectors.add(collector)
        self.update_dropdowns()
        
        # Mark cell as modified (saved but not committed to JSON)
        self.modified_cells.add((row, col))
        self.deleted_cells.discard((row, col))  # Remove from deleted if it was there
        self.unsaved_changes = True
        
        self.status_label.setText(f"Cell [{row}, {col}] saved - Remember to Save JSON when done!")
        
        # Update grid colors (will show as modified when deselected)
        self.update_grid_status()
    
    def delete_cell_data(self):
        """Delete data for the current cell"""
        row, col = self.current_cell
        
        if (row, col) not in self.grid_data and (row, col) not in self.modified_cells:
            self.status_label.setText(f"Cell [{row}, {col}] has no data to delete")
            return
        
        # Remove from grid_data
        if (row, col) in self.grid_data:
            del self.grid_data[(row, col)]
        
        # Remove from modified (no longer has pending save)
        self.modified_cells.discard((row, col))
        
        # Add to deleted cells (shows as modified until JSON saved)
        self.deleted_cells.add((row, col))
        self.unsaved_changes = True
        
        # Clear the metadata fields
        self.mineral_combo.setCurrentText("")
        self.location_combo.setCurrentText("")
        self.collector_combo.setCurrentText("")
        
        self.status_label.setText(f"Cell [{row}, {col}] deleted - Save JSON to commit deletion")
        self.update_grid_status()
    
    def update_grid_status(self):
        """Update grid cell colors based on data"""
        for (row, col), cell in self.grid_cells.items():
            if (row, col) == self.current_cell:
                cell.set_status("selected")
            elif (row, col) in self.modified_cells:
                cell.set_status("modified")  # Saved but not committed to JSON
            elif (row, col) in self.deleted_cells:
                cell.set_status("modified")  # Pending deletion - shows as modified
            elif (row, col) in self.grid_data:
                cell.set_status("calibrated")  # Committed to JSON
            else:
                cell.set_status("empty")
    
    def update_dropdowns(self):
        """Update dropdown options with known values"""
        # Save current text
        mineral_text = self.mineral_combo.currentText()
        location_text = self.location_combo.currentText()
        collector_text = self.collector_combo.currentText()
        
        # Update combos
        self.mineral_combo.clear()
        self.mineral_combo.addItems(sorted(self.known_minerals))
        self.mineral_combo.setCurrentText(mineral_text)
        
        self.location_combo.clear()
        self.location_combo.addItems(sorted(self.known_locations))
        self.location_combo.setCurrentText(location_text)
        
        self.collector_combo.clear()
        self.collector_combo.addItems(sorted(self.known_collectors))
        self.collector_combo.setCurrentText(collector_text)
    
    def on_metadata_changed(self):
        """Track when metadata is modified"""
        pass  # Could mark cell as modified here
    
    def set_step_size(self, size: float):
        """Set the current jog step size"""
        self.current_step_size = size
        # Update button states
        for btn in self.step_buttons:
            btn.setChecked(float(btn.text()) == size)
        print(f"Step size set to {size} mm")
    
    def start_jog(self, axis: str, direction: int):
        """Start continuous jogging
        
        Args:
            axis: 'X', 'Y', 'Z', or 'F'
            direction: +1 for positive, -1 for negative
        """
        distance = direction * self.current_step_size
        print(f"DEBUG: start_jog({axis}, dir={direction}, step={self.current_step_size}, dist={distance}) - jog_enabled={self.jog_enabled}")
        
        if not self.jog_enabled:
            self.status_label.setText("Must home before jogging!")
            return
        
        self.is_jogging = True
        self._jog_in_progress = False  # Prevent re-entrancy
        
        def do_jog():
            if self.is_jogging and not self._jog_in_progress:
                self._jog_in_progress = True
                try:
                    self.motion.jog(axis, distance)
                finally:
                    self._jog_in_progress = False
        
        # Immediate first jog
        do_jog()
        
        # Setup timer for repeated jogging (500ms to allow jog to complete)
        self.jog_timer = QTimer()
        self.jog_timer.timeout.connect(do_jog)
        self.jog_timer.start(500)  # Repeat every 500ms (must be longer than jog duration)
    
    def stop_jog(self):
        """Stop continuous jogging"""
        self.is_jogging = False
        if self.jog_timer:
            self.jog_timer.stop()
            self.jog_timer = None
    
    def prev_cell(self):
        """Go to previous cell in grid"""
        row, col = self.current_cell
        col -= 1
        if col < 0:
            col = 6
            row -= 1
        if row < 0:
            row = 3
        self.select_cell(row, col)
    
    def next_cell(self):
        """Go to next cell in grid"""
        row, col = self.current_cell
        col += 1
        if col > 6:
            col = 0
            row += 1
        if row > 3:
            row = 0
        self.select_cell(row, col)
    
    def set_as_default_tray(self):
        """Set the currently loaded JSON file as the default tray for startup"""
        if not self.current_file_path:
            QMessageBox.warning(self, "No File Loaded", 
                              "No JSON file is currently loaded.\nLoad a file first, then set it as default.")
            return
        
        try:
            set_default_tray_config(self.current_file_path)
            filename = os.path.basename(self.current_file_path)
            self.status_label.setText(f"✓ '{filename}' set as default tray (will load on next startup)")
            msg = QMessageBox(self)
            msg.setWindowTitle("Default Set")
            msg.setText(f"'{filename}' will now load automatically on startup.")
            msg.setIcon(QMessageBox.Information)
            msg.setStyleSheet("""
                QMessageBox { background-color: #2d2d2d; }
                QMessageBox QLabel { color: white; font-size: 14px; }
                QPushButton { background-color: #444; color: white; border: 1px solid #666; padding: 8px 20px; min-width: 80px; }
                QPushButton:hover { background-color: #555; }
            """)
            msg.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to set default:\n{e}")
    
    def load_json(self):
        """Load specimen data from JSON file"""
        if self.unsaved_changes:
            msg = QMessageBox(self)
            msg.setWindowTitle("Unsaved Changes")
            msg.setText("You have unsaved changes. Load anyway?\\n\\nAll unsaved changes will be LOST!")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            msg.setStyleSheet("""
                QMessageBox { background-color: #2d2d2d; }
                QMessageBox QLabel { color: white; font-size: 14px; }
                QPushButton { background-color: #444; color: white; border: 1px solid #666; padding: 8px 20px; min-width: 80px; }
                QPushButton:hover { background-color: #555; }
            """)
            if msg.exec_() == QMessageBox.No:
                return
        
        dialog = QFileDialog(self, "Load Specimen JSON", "/home/scope/scope", "JSON Files (*.json)")
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setStyleSheet("""
            QFileDialog { background-color: #2d2d2d; color: white; }
            QLabel { color: white; }
            QLineEdit { background-color: #333; color: white; border: 1px solid #555; }
            QListView { background-color: #333; color: white; }
            QTreeView { background-color: #333; color: white; }
            QPushButton { background-color: #444; color: white; border: 1px solid #666; padding: 5px; }
            QComboBox { background-color: #333; color: white; }
        """)
        if dialog.exec_() == QFileDialog.Accepted:
            file_path = dialog.selectedFiles()[0]
        else:
            return
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.grid_data.clear()
            self.known_minerals.clear()
            self.known_locations.clear()
            self.known_collectors.clear()
            
            for spec in data.get("specimens", []):
                row = spec.get("row", 0)
                col = spec.get("col", 0)
                self.grid_data[(row, col)] = spec
                
                # Track known values
                if spec.get("mineral_name"):
                    self.known_minerals.add(spec["mineral_name"])
                if spec.get("location"):
                    self.known_locations.add(spec["location"])
                if spec.get("collector"):
                    self.known_collectors.add(spec["collector"])
            
            self.current_file_path = file_path
            self.unsaved_changes = False
            self.modified_cells.clear()  # Loaded data is already committed
            self.deleted_cells.clear()  # No pending deletions
            self.update_dropdowns()
            self.update_grid_status()
            self.status_label.setText(f"Loaded {len(self.grid_data)} specimens from {file_path.split('/')[-1]}")
            
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load JSON:\n{e}")
    
    def save_json(self):
        """Save specimen data to JSON file"""
        if not self.grid_data:
            QMessageBox.warning(self, "No Data", "No specimen data to save.")
            return
        
        dialog = QFileDialog(self, "Save Specimen JSON")
        dialog.setDirectory(self.current_file_path or "/home/scope/scope")
        dialog.setNameFilter("JSON Files (*.json)")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setStyleSheet("""
            QFileDialog { background-color: #2d2d2d; color: white; }
            QLabel { color: white; }
            QLineEdit { background-color: #333; color: white; border: 1px solid #555; }
            QListView { background-color: #333; color: white; }
            QTreeView { background-color: #333; color: white; }
            QPushButton { background-color: #444; color: white; border: 1px solid #666; padding: 5px; }
            QComboBox { background-color: #333; color: white; }
        """)
        if dialog.exec_() != QFileDialog.Accepted:
            return
        file_path = dialog.selectedFiles()[0]
        
        # Auto-add .json extension if not provided
        if not file_path.lower().endswith('.json'):
            file_path += '.json'
        
        try:
            # Sort by row, then col
            specimens = sorted(self.grid_data.values(), key=lambda s: (s["row"], s["col"]))
            
            data = {"specimens": specimens}
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.current_file_path = file_path
            self.unsaved_changes = False
            self.modified_cells.clear()  # All cells now committed to JSON
            self.deleted_cells.clear()  # Deletions now committed
            self.update_grid_status()  # Update colors to show calibrated (or empty for deleted)
            self.status_label.setText(f"Saved {len(specimens)} specimens to {file_path.split('/')[-1]}")
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save JSON:\n{e}")
    
    def new_blank(self):
        """Start with a blank grid"""
        if self.unsaved_changes:
            msg = QMessageBox(self)
            msg.setWindowTitle("Unsaved Changes")
            msg.setText("You have unsaved changes. Create new anyway?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            msg.setStyleSheet("""
                QMessageBox { background-color: #2d2d2d; }
                QMessageBox QLabel { color: white; font-size: 14px; }
                QPushButton { background-color: #444; color: white; border: 1px solid #666; padding: 8px 20px; min-width: 80px; }
                QPushButton:hover { background-color: #555; }
            """)
            if msg.exec_() == QMessageBox.No:
                return
        
        self.grid_data.clear()
        self.modified_cells.clear()
        self.deleted_cells.clear()
        self.current_file_path = None
        self.unsaved_changes = False
        self.known_minerals.clear()
        self.known_locations.clear()
        self.known_collectors.clear()
        self.update_dropdowns()
        self.update_grid_status()
        self.select_cell(0, 0)
        self.status_label.setText("New blank grid - Start calibrating!")
    
    def on_exit(self):
        """Handle exit button"""
        if self.unsaved_changes:
            msg = QMessageBox(self)
            msg.setWindowTitle("Unsaved Changes")
            msg.setText("You have unsaved changes. Exit anyway?\n\nAll unsaved changes will be LOST!")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            msg.setStyleSheet("""
                QMessageBox { background-color: #2d2d2d; }
                QMessageBox QLabel { color: white; font-size: 14px; }
                QPushButton { background-color: #444; color: white; border: 1px solid #666; padding: 8px 20px; min-width: 80px; }
                QPushButton:hover { background-color: #555; }
            """)
            if msg.exec_() == QMessageBox.No:
                return
        
        self.exit_calibration.emit()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key_Escape:
            self.on_exit()
        elif event.key() == Qt.Key_Left:
            self.prev_cell()
        elif event.key() == Qt.Key_Right:
            self.next_cell()
        elif event.key() == Qt.Key_G:
            self.goto_current_cell()
        elif event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
            self.save_json()


class VideoWidget(QWidget):
    """Video display widget with overlays"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_frame = None
        self.specimen_info = None
        self.position = (0.0, 0.0, 0.0, 0.0)  # X, Y, Z, F
        self.state = "DISCONNECTED"
        self.is_auto_mode = True
        
        # Thread safety lock for video frame updates
        self.frame_mutex = QMutex()
        
        # Scale bar parameters (FOV calibration)
        # Calibrated 2026-01-06 using micrometer:
        # - F=0 (zoomed out): ~2.8mm across 60% of screen width
        # - F=11.5 (zoomed in): ~0.5mm across ruler span
        self.f_max = 11.5    # Maximum F value (fully zoomed in)
        self.fov_min = 4.7   # mm FOV at F=0 (zoomed out)
        self.fov_max = 0.83  # mm FOV at F=11.5 (zoomed in)
        
        # Debug counters
        self._frame_received_count = 0
        self._update_scheduled_count = 0
        self._update_executed_count = 0
        self._paint_count = 0
        
        self.setMinimumSize(1670, 1080)
    
    def _do_update(self):
        """Wrapper for update() to track execution"""
        self._update_executed_count += 1
        if self._update_executed_count % 100 == 0:
            print(f"[VideoWidget DEBUG] update() executed #{self._update_executed_count}, "
                  f"visible={self.isVisible()}, enabled={self.updatesEnabled()}, "
                  f"paints={self._paint_count}")
        self.update()
    
    def set_video_frame(self, q_image: QImage):
        """Update video frame (thread-safe)"""
        self._frame_received_count += 1
        
        self.frame_mutex.lock()
        try:
            if self.video_frame is None:
                print(f"First video frame received: {q_image.width()}x{q_image.height()}")
            self.video_frame = QPixmap.fromImage(q_image)
        finally:
            self.frame_mutex.unlock()
        
        self._update_scheduled_count += 1
        # Use QTimer to ensure update happens on main thread
        QTimer.singleShot(0, self._do_update)
    
    def set_specimen_info(self, specimen: SpecimenPosition):
        """Set current specimen info for overlay (thread-safe)"""
        import threading
        thread_id = threading.current_thread().ident
        print(f"[VideoWidget] Setting specimen info: {specimen.mineral_name} (thread {thread_id})")
        self.specimen_info = specimen
        print(f"[VideoWidget] Queuing update() call")
        # Use QTimer to ensure update happens on main thread
        QTimer.singleShot(0, self.update)
        print(f"[VideoWidget] Update queued")
    
    def set_position(self, x: float, y: float, z: float, f: float):
        """Update position display (thread-safe)"""
        print(f"[VideoWidget] Setting position: X={x:.1f} Y={y:.1f} Z={z:.1f} F={f:.1f}")
        self.position = (x, y, z, f)
        # Use QTimer to ensure update happens on main thread
        QTimer.singleShot(0, self.update)
    
    def set_state(self, state: str):
        """Update state display (thread-safe)"""
        print(f"[VideoWidget] Setting state: {state}")
        self.state = state
        # Use QTimer to ensure update happens on main thread
        QTimer.singleShot(0, self.update)
    
    def set_auto_mode(self, is_auto: bool):
        """Update auto/manual mode indicator (thread-safe)"""
        self.is_auto_mode = is_auto
        # Use QTimer to ensure update happens on main thread
        QTimer.singleShot(0, self.update)
    
    def paintEvent(self, event):
        """Draw video frame and overlays"""
        self._paint_count += 1
        if self._paint_count % 100 == 0:
            print(f"[paintEvent] #{self._paint_count} (frames_recv={self._frame_received_count}, "
                  f"updates_sched={self._update_scheduled_count}, updates_exec={self._update_executed_count})")
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Lock frame access
        self.frame_mutex.lock()
        current_frame = self.video_frame
        self.frame_mutex.unlock()
        
        # Draw video frame (or black background)
        if current_frame:
            # Scale to fill entire widget (crop if needed to avoid black bars)
            scaled_pixmap = current_frame.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            # Center and crop if larger than widget
            x_offset = (self.width() - scaled_pixmap.width()) // 2
            y_offset = (self.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
        else:
            # Black background
            painter.fillRect(self.rect(), QColor(0, 0, 0))
        
        # Draw overlays
        self._draw_title_banner(painter)
        self._draw_status_bar(painter)
        self._draw_specimen_info(painter)
        self._draw_scale_ruler(painter)
    
    def _draw_title_banner(self, painter: QPainter):
        """Draw consolidated title banner with status and position"""
        # Semi-transparent background banner
        banner_height = 70
        painter.fillRect(0, 0, self.width(), banner_height, QColor(0, 0, 0, 200))
        
        # LEFT: Status indicator and state
        painter.setPen(Qt.NoPen)
        if self.state in ["IDLE", "MOVING"]:
            painter.setBrush(QBrush(QColor(0, 255, 0)))  # Green
        elif self.state == "CONNECTED":
            painter.setBrush(QBrush(QColor(255, 255, 0)))  # Yellow
        else:
            painter.setBrush(QBrush(QColor(255, 0, 0)))  # Red
        painter.drawEllipse(15, 25, 20, 20)
        
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = QFont("Liberation Sans", 11, QFont.Bold)
        painter.setFont(font)
        painter.drawText(45, 37, self.state)
        
        # Auto/Manual mode below status
        mode_text = "AUTO" if self.is_auto_mode else "MANUAL"
        mode_color = QColor(0, 255, 0) if self.is_auto_mode else QColor(255, 165, 0)
        painter.setPen(QPen(mode_color))
        font = QFont("Liberation Sans", 9)
        painter.setFont(font)
        painter.drawText(45, 52, mode_text)
        
        # CENTER: Main title and subtitle
        painter.setPen(QPen(QColor(255, 255, 255)))
        title_font = QFont("Liberation Serif", 28, QFont.Bold)
        painter.setFont(title_font)
        title_text = "The Mineral Microscope"
        title_width = painter.fontMetrics().width(title_text)
        title_x = (self.width() - title_width) // 2
        painter.drawText(title_x, 35, title_text)
        
        painter.setPen(QPen(QColor(200, 200, 200)))
        subtitle_font = QFont("Liberation Sans", 11)
        painter.setFont(subtitle_font)
        subtitle_text = "Brought to you by Tom Mortimer (https://mindatnh.org/)"
        subtitle_width = painter.fontMetrics().width(subtitle_text)
        subtitle_x = (self.width() - subtitle_width) // 2
        painter.drawText(subtitle_x, 55, subtitle_text)
        
        # RIGHT: Position display
        x, y, z, f = self.position
        painter.setPen(QPen(QColor(255, 255, 255)))
        pos_font = QFont("Liberation Sans", 11)
        painter.setFont(pos_font)
        pos_lines = [
            f"X: {x:.1f}mm",
            f"Y: {y:.1f}mm",
            f"Z: {z:.1f}mm",
            f"F: {f:.1f}mm"
        ]
        right_margin = 15
        line_height = 14
        start_y = 20
        for i, line in enumerate(pos_lines):
            line_width = painter.fontMetrics().width(line)
            painter.drawText(self.width() - line_width - right_margin, start_y + i * line_height, line)
    
    def _draw_status_bar(self, painter: QPainter):
        """Status bar now integrated into title banner"""
        pass
    
    def _draw_specimen_info(self, painter: QPainter):
        """Draw specimen info card (right side)"""
        if not self.specimen_info:
            print("[_draw_specimen_info] No specimen info to draw")
            return
        print(f"[_draw_specimen_info] Drawing card for {self.specimen_info.mineral_name}")
        
        # Card dimensions and position (adjusted for title banner)
        card_width = 300
        card_height = 150
        card_x = self.width() - card_width - 20
        card_y = 90  # Below consolidated title banner
        
        # Semi-transparent background with rounded corners
        painter.setBrush(QBrush(QColor(20, 20, 20, 200)))
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawRoundedRect(card_x, card_y, card_width, card_height, 10, 10)
        
        # Specimen name (reduced 25%: 18 -> 13.5)
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = QFont("Liberation Sans", 14, QFont.Bold)
        painter.setFont(font)
        
        # Word wrap mineral name if needed
        fm = painter.fontMetrics()
        name_rect = QRect(card_x + 15, card_y + 15, card_width - 30, 50)
        painter.drawText(name_rect, Qt.AlignLeft | Qt.TextWordWrap, self.specimen_info.mineral_name)
        
        # Location (reduced 25%: 14 -> 10.5)
        font = QFont("Liberation Sans", 11)
        painter.setFont(font)
        location_rect = QRect(card_x + 15, card_y + 70, card_width - 30, 35)
        painter.drawText(location_rect, Qt.AlignLeft | Qt.TextWordWrap, self.specimen_info.location)
        
        # Collector (reduced 25%: 14 -> 10.5)
        font = QFont("Liberation Sans", 10)
        painter.setFont(font)
        painter.setPen(QPen(QColor(180, 180, 180)))
        painter.drawText(card_x + 15, card_y + 120, f"Collected by: {self.specimen_info.collector}")
    
    def _draw_scale_ruler(self, painter: QPainter):
        """Draw scale ruler with dynamic ticks (bottom center)"""
        # Calculate current field of view based on F position
        x, y, z, f = self.position
        f_ratio = f / self.f_max if f <= self.f_max else 1.0  # Normalize F to 0-1
        current_fov_mm = self.fov_min - (self.fov_min - self.fov_max) * f_ratio
        
        # Ruler dimensions
        ruler_width_px = int(self.width() * 0.4)  # 40% of screen width
        ruler_height = 50
        ruler_x = (self.width() - ruler_width_px) // 2
        ruler_y = self.height() - ruler_height - 20
        
        # Semi-transparent background
        painter.fillRect(ruler_x - 20, ruler_y, ruler_width_px + 40, ruler_height, 
                        QColor(0, 0, 0, 150))
        
        # Determine tick spacing (smart rounding)
        # Ruler represents a fraction of FOV
        ruler_fov_fraction = 0.6  # Ruler shows 60% of FOV
        ruler_represents_mm = current_fov_mm * ruler_fov_fraction
        
        # Choose nice tick intervals
        if ruler_represents_mm > 20:
            tick_interval_mm = 10
        elif ruler_represents_mm > 10:
            tick_interval_mm = 5
        elif ruler_represents_mm > 5:
            tick_interval_mm = 2
        elif ruler_represents_mm > 2:
            tick_interval_mm = 1
        else:
            tick_interval_mm = 0.5
        
        # Calculate pixels per mm
        px_per_mm = ruler_width_px / ruler_represents_mm
        
        # Draw ticks and labels
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        font = QFont("Liberation Sans", 12, QFont.Bold)
        painter.setFont(font)
        
        num_ticks = int(ruler_represents_mm / tick_interval_mm) + 1
        for i in range(num_ticks):
            tick_value_mm = i * tick_interval_mm
            if tick_value_mm > ruler_represents_mm:
                break
            
            tick_x = ruler_x + int(tick_value_mm * px_per_mm)
            
            # Draw tick mark
            painter.drawLine(tick_x, ruler_y + 10, tick_x, ruler_y + 30)
            
            # Draw label
            label = f"{tick_value_mm:.1f}mm" if tick_interval_mm < 1 else f"{int(tick_value_mm)}mm"
            # Remove trailing .0 for whole numbers
            if label.endswith(".0mm"):
                label = label.replace(".0mm", "mm")
            
            text_width = painter.fontMetrics().width(label)
            painter.drawText(tick_x - text_width // 2, ruler_y + 45, label)
        
        # Draw horizontal line
        painter.drawLine(ruler_x, ruler_y + 20, ruler_x + ruler_width_px, ruler_y + 20)


class MicroscopeGUI(QMainWindow):
    """Main GUI window"""
    
    # Signal for thread-safe specimen change notification (emitted from background thread)
    specimen_changed_signal = pyqtSignal(int, object)  # index, specimen
    
    def __init__(self, tray_config_path: str, enable_save: bool = False):
        super().__init__()
        self.tray_config_path = tray_config_path
        self.enable_save = enable_save  # Command-line flag for saving stacked images
        
        # Connect signal to slot (thread-safe UI update)
        self.specimen_changed_signal.connect(self._update_specimen_highlight)
        
        # Controllers
        self.motion = MotionController(tray_config_path)
        self.motion.on_limit_hit = lambda: play_warning_beep()
        self.video = VideoThread()  # Uses /dev/video0 for HDMI-to-CSI capture
        
        # Initialize LED ring controller
        self.led = get_led_controller()
        self.led.initialize()
        
        # UI state
        self.jog_timers = {}  # Active jog timers for continuous movement
        self._jog_in_progress = {}  # Re-entrancy protection per axis
        self.current_step_size = 0.5  # Default step size in mm
        self.diagnostic_mode = False
        self.startup_complete = False
        
        # Focus stacking state
        self.focus_stack_thread = None
        self.focus_stack_cache_dir = os.path.join(os.path.dirname(__file__), "image_stack_cache")
        self._in_auto_transition = False  # Track if rainbow transition is active
        self._was_manual_mode = False  # Track mode transitions for LED reset
        
        # Setup UI
        self.init_ui()
        
        # Setup callbacks
        self.motion.on_position_update = self.on_position_update
        self.motion.on_state_change = self.on_state_change
        self.motion.on_specimen_change = self.on_specimen_change
        self.motion.on_auto_transition_start = self._on_auto_transition_start
        self.motion.on_auto_transition_end = self._on_auto_transition_end
        
        # Connect video thread
        self.video.frame_ready.connect(self.video_widget.set_video_frame)
        self.video.status_update.connect(self._on_video_status)
        
        # Start video (initializes HDMI capture pipeline)
        self.video.start()
        
        # Auto-mode update timer
        self.auto_mode_timer = QTimer()
        self.auto_mode_timer.timeout.connect(self.update_auto_mode_indicator)
        self.auto_mode_timer.start(500)  # Update every 500ms
        
        # Show startup splash
        self.show_startup_splash()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Robotic Microscope")
        self.setGeometry(0, 0, 1920, 1080)
        
        # Main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left panel (specimen list + jog controls)
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)
        
        # Video display widget
        self.video_widget = VideoWidget()
        main_layout.addWidget(self.video_widget, stretch=1)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Create overlays (initially hidden)
        self.startup_splash = StartupSplash(self)
        self.startup_splash.setGeometry(0, 0, 1920, 1080)
        self.startup_splash.enter_diagnostic_mode.connect(self.enter_diagnostic_mode)
        self.startup_splash.enter_normal_mode.connect(self.enter_normal_mode)
        self.startup_splash.hide()
        
        self.diagnostic_overlay = DiagnosticOverlay(self.motion, self)
        self.diagnostic_overlay.setGeometry(0, 0, 1920, 1080)
        self.diagnostic_overlay.exit_diagnostics.connect(self.exit_diagnostic_mode)
        self.diagnostic_overlay.enter_calibration.connect(self.enter_calibration_mode)
        self.diagnostic_overlay.hide()
        
        self.calibration_overlay = CalibrationOverlay(self.motion, self.video, self)
        self.calibration_overlay.setGeometry(0, 0, 1920, 1080)
        self.calibration_overlay.exit_calibration.connect(self.exit_calibration_mode)
        self.calibration_overlay.hide()
        
        # Dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000;
            }
            QWidget {
                color: white;
            }
        """)
        
        # Fullscreen
        self.showFullScreen()
    
    def show_startup_splash(self):
        """Show startup splash screen"""
        self.startup_splash.show()
        self.startup_splash.raise_()
    
    def enter_diagnostic_mode(self):
        """Enter diagnostic test mode"""
        print("Entering diagnostic mode...")
        self.startup_splash.hide()
        self.diagnostic_mode = True
        self.diagnostic_overlay.show()
        self.diagnostic_overlay.raise_()
        self.diagnostic_overlay.setFocus()
    
    def enter_normal_mode(self):
        """Enter normal GUI mode"""
        print("Entering normal mode...")
        self.startup_splash.hide()
        self.diagnostic_mode = False
        
        # Start normal startup sequence if not already done
        if not self.startup_complete:
            QTimer.singleShot(500, self.startup_sequence)
    
    def exit_diagnostic_mode(self):
        """Exit diagnostic mode and start normal GUI"""
        print("Exiting diagnostic mode...")
        self.diagnostic_overlay.hide()
        self.diagnostic_mode = False
        
        # Start normal startup sequence
        if not self.startup_complete:
            QTimer.singleShot(500, self.startup_sequence)
    
    def enter_calibration_mode(self):
        """Enter specimen calibration mode from diagnostic menu"""
        print("Entering calibration mode...")
        self.diagnostic_overlay.hide()
        self.calibration_overlay.show()
        self.calibration_overlay.raise_()
        self.calibration_overlay.setFocus()
    
    def exit_calibration_mode(self):
        """Exit calibration mode and return to diagnostic menu"""
        print("Exiting calibration mode...")
        self.calibration_overlay.hide()
        self.diagnostic_overlay.show()
        self.diagnostic_overlay.raise_()
        self.diagnostic_overlay.setFocus()
    
    def create_left_panel(self) -> QWidget:
        """Create left panel with specimen list and jog controls"""
        panel = QWidget()
        panel.setFixedWidth(230)
        panel.setStyleSheet("background-color: rgba(20, 20, 20, 240);")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title / Home button
        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_label = QLabel("SPECIMENS")
        title_label.setFont(QFont("Liberation Sans", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        
        home_btn = QPushButton("HOME")
        home_btn.setFixedSize(80, 40)
        home_btn.clicked.connect(self.home_axes)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(home_btn)
        title_widget.setLayout(title_layout)
        layout.addWidget(title_widget)
        
        # Specimen list (scrollable)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        list_widget = QWidget()
        self.specimen_list_layout = QVBoxLayout()
        self.specimen_list_layout.setSpacing(5)
        self.specimen_list_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create specimen cards
        self.specimen_cards = []
        for idx, specimen in enumerate(self.motion.get_all_specimens()):
            card = SpecimenCard(idx, specimen)
            card.clicked.connect(self.on_specimen_selected)
            self.specimen_cards.append(card)
            self.specimen_list_layout.addWidget(card)
        
        self.specimen_list_layout.addStretch()
        list_widget.setLayout(self.specimen_list_layout)
        scroll_area.setWidget(list_widget)
        
        layout.addWidget(scroll_area, stretch=1)
        
        # Jog controls
        jog_widget = self.create_jog_controls()
        layout.addWidget(jog_widget)
        
        panel.setLayout(layout)
        return panel
    
    def create_jog_controls(self) -> QWidget:
        """Create jog control buttons and brightness slider"""
        widget = QWidget()
        widget.setFixedHeight(520)  # Increased height to accommodate step size selector and focus stack button
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("JOG CONTROLS")
        title.setFont(QFont("Liberation Sans", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Step size selector
        step_layout = QHBoxLayout()
        step_label = QLabel("Step:")
        step_label.setFont(QFont("Liberation Sans", 9))
        step_layout.addWidget(step_label)
        
        self.step_sizes = [0.1, 0.5, 2.0, 5.0]
        self.step_buttons = {}
        for size in self.step_sizes:
            btn = QPushButton(f"{size}")
            btn.setFixedSize(40, 28)
            btn.clicked.connect(self._make_step_callback(size))
            step_layout.addWidget(btn)
            self.step_buttons[size] = btn
        
        # Set initial button styles
        self._update_step_button_styles()
        
        step_layout.addWidget(QLabel("mm"))
        layout.addLayout(step_layout)
        
        # X/Y controls (D-pad style)
        xy_layout = QVBoxLayout()
        xy_layout.setSpacing(5)
        
        # Row 1: Y+
        row1 = QHBoxLayout()
        row1.addStretch()
        self.y_plus_btn = JogButton("▲")
        self.y_plus_btn.pressed_signal.connect(lambda: self.start_jog('Y', 1))
        self.y_plus_btn.released_signal.connect(lambda: self.stop_jog('Y'))
        row1.addWidget(self.y_plus_btn)
        row1.addStretch()
        
        # Row 2: X-, Center, X+
        row2 = QHBoxLayout()
        self.x_minus_btn = JogButton("◄")
        self.x_minus_btn.pressed_signal.connect(lambda: self.start_jog('X', -1))
        self.x_minus_btn.released_signal.connect(lambda: self.stop_jog('X'))
        row2.addWidget(self.x_minus_btn)
        
        center_label = QLabel("X/Y")
        center_label.setAlignment(Qt.AlignCenter)
        center_label.setFixedSize(60, 60)
        center_label.setStyleSheet("background-color: rgba(40, 40, 40, 150); border-radius: 8px;")
        center_label.setFont(QFont("Liberation Sans", 10, QFont.Bold))
        row2.addWidget(center_label)
        
        self.x_plus_btn = JogButton("►")
        self.x_plus_btn.pressed_signal.connect(lambda: self.start_jog('X', 1))
        self.x_plus_btn.released_signal.connect(lambda: self.stop_jog('X'))
        row2.addWidget(self.x_plus_btn)
        
        # Row 3: Y-
        row3 = QHBoxLayout()
        row3.addStretch()
        self.y_minus_btn = JogButton("▼")
        self.y_minus_btn.pressed_signal.connect(lambda: self.start_jog('Y', -1))
        self.y_minus_btn.released_signal.connect(lambda: self.stop_jog('Y'))
        row3.addWidget(self.y_minus_btn)
        row3.addStretch()
        
        xy_layout.addLayout(row1)
        xy_layout.addLayout(row2)
        xy_layout.addLayout(row3)
        
        layout.addLayout(xy_layout)
        
        # Z/F controls (vertical strip)
        zf_layout = QHBoxLayout()
        
        # Z controls
        z_col = QVBoxLayout()
        z_label = QLabel("Focus")
        z_label.setAlignment(Qt.AlignCenter)
        z_label.setFont(QFont("Liberation Sans", 10))
        z_label.setStyleSheet("background-color: transparent;")
        z_label.setMaximumHeight(15)
        z_col.addWidget(z_label)
        z_col.addSpacing(3)
        
        self.z_plus_btn = JogButton("▲")
        self.z_plus_btn.setFixedSize(75, 38)
        self.z_plus_btn.pressed_signal.connect(lambda: self.start_jog('Z', 1))
        self.z_plus_btn.released_signal.connect(lambda: self.stop_jog('Z'))
        z_col.addWidget(self.z_plus_btn)
        
        self.z_minus_btn = JogButton("▼")
        self.z_minus_btn.setFixedSize(75, 38)
        self.z_minus_btn.pressed_signal.connect(lambda: self.start_jog('Z', -1))
        self.z_minus_btn.released_signal.connect(lambda: self.stop_jog('Z'))
        z_col.addWidget(self.z_minus_btn)
        
        zf_layout.addLayout(z_col)
        
        # F controls
        f_col = QVBoxLayout()
        f_label = QLabel("Zoom")
        f_label.setAlignment(Qt.AlignCenter)
        f_label.setFont(QFont("Liberation Sans", 10))
        f_label.setStyleSheet("background-color: transparent;")
        f_label.setMaximumHeight(15)
        f_col.addWidget(f_label)
        f_col.addSpacing(3)
        
        self.f_plus_btn = JogButton("▲")
        self.f_plus_btn.setFixedSize(75, 38)
        self.f_plus_btn.pressed_signal.connect(lambda: self.start_jog('F', 1))
        self.f_plus_btn.released_signal.connect(lambda: self.stop_jog('F'))
        f_col.addWidget(self.f_plus_btn)
        
        self.f_minus_btn = JogButton("▼")
        self.f_minus_btn.setFixedSize(75, 38)
        self.f_minus_btn.pressed_signal.connect(lambda: self.start_jog('F', -1))
        self.f_minus_btn.released_signal.connect(lambda: self.stop_jog('F'))
        f_col.addWidget(self.f_minus_btn)
        
        zf_layout.addLayout(f_col)
        
        layout.addLayout(zf_layout)
        
        # Focus Stack buttons (side by side)
        stack_btn_layout = QHBoxLayout()
        stack_btn_layout.setSpacing(6)
        
        # Crystal Clear button (standard focus stack)
        focus_stack_btn = QPushButton("📷 Take Stacked\n    Picture...")
        focus_stack_btn.setFixedHeight(60)
        focus_stack_btn.setFont(QFont("Liberation Sans", 10, QFont.Bold))
        focus_stack_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(100, 160, 220, 230),
                    stop:1 rgba(60, 120, 180, 230));
                border: 2px solid #64A0DC;
                border-radius: 10px;
                color: white;
                text-align: left;
                padding-left: 8px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(120, 180, 240, 250),
                    stop:1 rgba(80, 140, 200, 250));
                border: 2px solid #78B4F0;
            }
            QPushButton:pressed {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(60, 120, 180, 230),
                    stop:1 rgba(40, 100, 160, 230));
            }
        """)
        focus_stack_btn.clicked.connect(self._on_focus_stack_clicked)
        stack_btn_layout.addWidget(focus_stack_btn)
        
        # Giga Crystal Clear button (tiled focus stack)
        giga_stack_btn = QPushButton("🔬 Take Tiled\n    Stacked Picture...")
        giga_stack_btn.setFixedHeight(60)
        giga_stack_btn.setFont(QFont("Liberation Sans", 10, QFont.Bold))
        giga_stack_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(180, 100, 220, 230),
                    stop:1 rgba(140, 60, 180, 230));
                border: 2px solid #B464DC;
                border-radius: 10px;
                color: white;
                text-align: left;
                padding-left: 8px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(200, 120, 240, 250),
                    stop:1 rgba(160, 80, 200, 250));
                border: 2px solid #C878F0;
            }
            QPushButton:pressed {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(140, 60, 180, 230),
                    stop:1 rgba(120, 40, 160, 230));
            }
        """)
        giga_stack_btn.clicked.connect(self._on_giga_focus_stack_clicked)
        stack_btn_layout.addWidget(giga_stack_btn)
        
        layout.addLayout(stack_btn_layout)
        
        # Brightness slider for LED ring
        self.brightness_slider = BrightnessSlider()
        self.brightness_slider.brightness_changed.connect(self._on_brightness_changed)
        layout.addWidget(self.brightness_slider)
        
        widget.setLayout(layout)
        return widget
    
    def set_step_size(self, size: float):
        """Set the current jog step size"""
        self.current_step_size = size
        self._update_step_button_styles()
        print(f"[GUI] Step size set to {size} mm")
    
    def _make_step_callback(self, size: float):
        """Create a callback function for a step size button"""
        def callback(checked=False):
            print(f"[DEBUG] Step button clicked: {size}")
            self.set_step_size(size)
        return callback
    
    def _update_step_button_styles(self):
        """Update step button styles to show current selection"""
        for s, btn in self.step_buttons.items():
            if abs(s - self.current_step_size) < 0.01:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3296FF;
                        border: 2px solid #5AF;
                        border-radius: 4px;
                        color: white;
                        font-size: 11px;
                        font-weight: bold;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #333;
                        border: 2px solid #555;
                        border-radius: 4px;
                        color: white;
                        font-size: 11px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        border-color: #888;
                    }
                """)
    
    def startup_sequence(self):
        """Connect and home on startup"""
        # Connect to Teensy
        if not self.motion.connect():
            print("ERROR: Failed to connect to Teensy")
            return
        
        # Home all axes
        def progress_callback(message):
            print(f"Homing: {message}")
        
        # Pass processEvents as idle_callback to keep GUI responsive during homing
        if not self.motion.home(progress_callback, idle_callback=QApplication.processEvents):
            print("ERROR: Homing failed")
            return
        
        print("Startup complete - ready for operation")
        self.startup_complete = True
        play_startup_chime()
        
        # DEBUG: Print widget state after homing
        print(f"[DEBUG] VideoWidget state after homing:")
        print(f"[DEBUG]   visible={self.video_widget.isVisible()}")
        print(f"[DEBUG]   updatesEnabled={self.video_widget.updatesEnabled()}")
        print(f"[DEBUG]   isActiveWindow={self.isActiveWindow()}")
        print(f"[DEBUG]   frames_recv={self.video_widget._frame_received_count}")
        print(f"[DEBUG]   updates_sched={self.video_widget._update_scheduled_count}")
        print(f"[DEBUG]   updates_exec={self.video_widget._update_executed_count}")
        print(f"[DEBUG]   paint_count={self.video_widget._paint_count}")
        
        # Start auto-cycle only if specimens are loaded
        specimen_count = self.motion.get_specimen_count()
        if specimen_count > 0:
            print(f"Starting auto-cycle with {specimen_count} specimens")
            self.motion.start_auto_cycle()
            # Force initial UI update after short delay to ensure auto-cycle has started
            QTimer.singleShot(500, self.force_initial_highlight)
        else:
            print("No specimens loaded - staying idle after homing")
    
    def force_initial_highlight(self):
        """Force update of specimen highlighting (called after startup)"""
        current_index = self.motion.current_specimen_index
        if current_index is not None and 0 <= current_index < len(self.specimen_cards):
            print(f"[GUI] Forcing initial highlight for specimen {current_index}")
            for i, card in enumerate(self.specimen_cards):
                card.set_current(i == current_index)
    
    def home_axes(self):
        """Home all axes (button callback)"""
        self.motion.mark_user_interaction()
        
        def progress_callback(message):
            print(f"Homing: {message}")
        
        # Pass processEvents as idle_callback to keep GUI responsive during homing
        self.motion.home(progress_callback, idle_callback=QApplication.processEvents)
    
    def on_specimen_selected(self, index: int):
        """Handle specimen selection from list"""
        self.motion.mark_user_interaction()
        success = self.motion.move_to_specimen(index)
        if not success:
            print(f"Failed to move to specimen {index} - may be out of bounds")
    
    def start_jog(self, axis: str, direction: float):
        """Start jogging axis (continuous while button held)
        
        Args:
            axis: 'X', 'Y', 'Z', or 'F'
            direction: positive or negative value indicating direction (sign used, magnitude from step_size)
        """
        self.motion.mark_user_interaction()
        
        # Calculate increment from step size and direction sign
        sign = 1 if direction > 0 else -1
        increment = sign * self.current_step_size
        
        # Initialize re-entrancy protection for this axis
        self._jog_in_progress[axis] = False
        
        def do_jog():
            if axis not in self._jog_in_progress:
                return  # Jog was stopped
            if not self._jog_in_progress[axis]:
                self._jog_in_progress[axis] = True
                try:
                    # Run jog in background thread to keep video responsive
                    import threading
                    def jog_thread():
                        try:
                            self.motion.jog(axis, increment)
                        finally:
                            if axis in self._jog_in_progress:
                                self._jog_in_progress[axis] = False
                    
                    thread = threading.Thread(target=jog_thread, daemon=True)
                    thread.start()
                except Exception as e:
                    print(f"[JOG] Error: {e}")
                    if axis in self._jog_in_progress:
                        self._jog_in_progress[axis] = False
        
        # Immediate first jog
        do_jog()
        
        # Setup continuous jog timer (500ms to allow jog to complete)
        timer = QTimer()
        timer.timeout.connect(do_jog)
        timer.start(500)  # Repeat every 500ms (must be longer than jog duration)
        self.jog_timers[axis] = timer
    
    def stop_jog(self, axis: str):
        """Stop jogging axis"""
        # Remove re-entrancy flag first to signal jog should stop
        if axis in self._jog_in_progress:
            del self._jog_in_progress[axis]
        
        if axis in self.jog_timers:
            self.jog_timers[axis].stop()
            del self.jog_timers[axis]
    
    def on_position_update(self, x: float, y: float, z: float, f: float):
        """Callback for position updates"""
        try:
            print(f"[GUI] Position update: X={x:.1f} Y={y:.1f} Z={z:.1f} F={f:.1f}")
            self.video_widget.set_position(x, y, z, f)
        except Exception as e:
            print(f"ERROR in on_position_update: {e}")
    
    @pyqtSlot(str)
    def _on_video_status(self, message: str):
        """Handle status updates from video thread (HDMI capture)"""
        print(f"[VIDEO] {message}")
    
    def on_state_change(self, state: str):
        """Callback for state changes"""
        try:
            print(f"[GUI] State change: {state}")
            self.video_widget.set_state(state)
        except Exception as e:
            print(f"ERROR in on_state_change: {e}")
    
    def on_specimen_change(self, index: int, specimen: SpecimenPosition):
        """Callback for specimen changes (called from background thread)"""
        try:
            print(f"[GUI] Specimen change: {index} - {specimen.mineral_name}")
            # Update video overlay
            self.video_widget.set_specimen_info(specimen)
            
            # Emit signal for thread-safe card highlighting
            self.specimen_changed_signal.emit(index, specimen)
        except Exception as e:
            print(f"ERROR in on_specimen_change: {e}")
            import traceback
            traceback.print_exc()
    
    @pyqtSlot(int, object)
    def _update_specimen_highlight(self, index: int, specimen: SpecimenPosition):
        """Thread-safe slot for updating specimen card highlighting"""
        try:
            print(f"[GUI] Updating card highlighting for index {index}")
            for i, card in enumerate(self.specimen_cards):
                card.set_current(i == index)
        except Exception as e:
            print(f"ERROR in _update_specimen_highlight: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_auto_transition_start(self):
        """Called when auto-cycle begins moving to next specimen - start rainbow effect"""
        self._in_auto_transition = True
        print("[LED] Auto-cycle transition starting - rainbow effect")
        self.led.start_rainbow_transition()
    
    def _on_auto_transition_end(self):
        """Called when auto-cycle completes move - return to white"""
        self._in_auto_transition = False
        print("[LED] Auto-cycle transition complete - returning to white")
        self.led.stop_rainbow_transition()
    
    def update_auto_mode_indicator(self):
        """Update AUTO/MANUAL mode indicator and handle LED brightness reset"""
        is_auto = self.motion.is_auto_mode()
        self.video_widget.set_auto_mode(is_auto)
        
        # When returning to auto mode, reset brightness to default
        # BUT don't interrupt an active rainbow transition
        if is_auto and hasattr(self, '_was_manual_mode') and self._was_manual_mode:
            if not self._in_auto_transition:  # Don't interrupt rainbow!
                print("[LED] Returning to auto mode - resetting brightness to default")
                self.led.reset_to_default()
                self.brightness_slider.set_value(DEFAULT_BRIGHTNESS_PERCENT)
        
        self._was_manual_mode = not is_auto
    
    def _on_brightness_changed(self, percent: int):
        """Handle brightness slider change"""
        self.motion.mark_user_interaction()  # User is interacting
        self.led.set_brightness(percent)
    
    def _on_focus_stack_clicked(self):
        """Handle focus stack button click"""
        # Check if already running
        if self.focus_stack_thread and self.focus_stack_thread.isRunning():
            QMessageBox.warning(self, "Focus Stack Running", "A focus stack operation is already in progress.")
            return
        
        # Pause auto-advance immediately when user shows interest in focus stacking
        # This prevents frustrating specimen changes while user is setting up
        self.motion.pause_auto_cycle()
        
        # Get current position
        x, y, current_z, f = self.motion.get_current_position()
        
        # Check if we have enough Z travel (need 2.0mm downward towards specimen)
        # Z decreases as we move towards specimen, so need current_z >= required_travel
        required_travel = 2.0  # total travel range for stacking
        
        if current_z < required_travel:
            msg = f"""Insufficient Z travel for focus stack.

Required: {required_travel:.1f}mm downward
Available: {current_z:.1f}mm

Please move the Z axis to a higher position (further from the specimen) and try again."""
            QMessageBox.warning(self, "Insufficient Z Travel", msg)
            # Resume auto-advance since we're not proceeding
            self.motion.resume_auto_cycle()
            return
        
        # Show pre-operation prompt using styled dialog
        confirm_dialog = QDialog(self)
        confirm_dialog.setWindowTitle("Focus Stack")
        confirm_dialog.setModal(True)
        confirm_dialog.setFixedSize(500, 400)
        confirm_dialog.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 10px 20px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #5d5d5d;
            }
            QPushButton#yesBtn {
                background-color: #2d5a2d;
            }
            QPushButton#yesBtn:hover {
                background-color: #3d6a3d;
            }
        """)
        
        layout = QVBoxLayout()
        
        msg_label = QLabel("""<h3>📷 Take a Crystal Clear Photo</h3>
<p>Minerals have complex 3D surfaces that can't all be in focus at once. <b>Focus stacking</b> solves this 
by capturing multiple photos at different depths and combining them into one super-sharp image where 
everything is perfectly in focus!</p>
<p><b>Before starting:</b></p>
<ul>
<li>Position the microscope at the HIGHEST focus point (furthest from the specimen surface)</li>
<li>Ensure your specimen is in view</li>
</ul>
<p>All controls will be locked and auto-advance will be paused during the operation.</p>""")
        msg_label.setWordWrap(True)
        msg_label.setFont(QFont("Liberation Sans", 11))
        layout.addWidget(msg_label)
        
        # Image count selection
        from PyQt5.QtWidgets import QRadioButton, QButtonGroup
        count_label = QLabel("<b>Number of images to stack:</b>")
        count_label.setFont(QFont("Liberation Sans", 11))
        layout.addWidget(count_label)
        
        count_layout = QHBoxLayout()
        count_group = QButtonGroup(confirm_dialog)
        
        radio_1 = QRadioButton("1 (no stacking)")
        radio_1.setStyleSheet("QRadioButton { color: #ffffff; font-size: 12px; } QRadioButton::indicator { background-color: #3d3d3d; border: 1px solid #666666; border-radius: 6px; width: 12px; height: 12px; } QRadioButton::indicator:checked { background-color: #64b5f6; }")
        count_group.addButton(radio_1, 1)
        count_layout.addWidget(radio_1)
        
        radio_10 = QRadioButton("10 (default)")
        radio_10.setStyleSheet("QRadioButton { color: #ffffff; font-size: 12px; } QRadioButton::indicator { background-color: #3d3d3d; border: 1px solid #666666; border-radius: 6px; width: 12px; height: 12px; } QRadioButton::indicator:checked { background-color: #64b5f6; }")
        radio_10.setChecked(True)
        count_group.addButton(radio_10, 10)
        count_layout.addWidget(radio_10)
        
        radio_20 = QRadioButton("20 (fine)")
        radio_20.setStyleSheet("QRadioButton { color: #ffffff; font-size: 12px; } QRadioButton::indicator { background-color: #3d3d3d; border: 1px solid #666666; border-radius: 6px; width: 12px; height: 12px; } QRadioButton::indicator:checked { background-color: #64b5f6; }")
        count_group.addButton(radio_20, 20)
        count_layout.addWidget(radio_20)
        
        layout.addLayout(count_layout)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        no_btn = QPushButton("No")
        no_btn.clicked.connect(confirm_dialog.reject)
        btn_layout.addWidget(no_btn)
        
        yes_btn = QPushButton("Yes")
        yes_btn.setObjectName("yesBtn")
        yes_btn.clicked.connect(confirm_dialog.accept)
        btn_layout.addWidget(yes_btn)
        
        layout.addLayout(btn_layout)
        confirm_dialog.setLayout(layout)
        
        if confirm_dialog.exec_() == QDialog.Accepted:
            selected_count = count_group.checkedId()
            self._start_focus_stack(current_z, selected_count)
        else:
            # User cancelled - resume auto-advance
            self.motion.resume_auto_cycle()
    
    def _start_focus_stack(self, start_z: float, num_images: int = 10):
        """Start focus stack operation in background thread"""
        # Auto-advance already paused in _on_focus_stack_clicked
        
        # Create cache directory if needed
        os.makedirs(self.focus_stack_cache_dir, exist_ok=True)
        
        # Get current specimen info for branding
        current_index = self.motion.current_specimen_index
        current_specimen = None
        if current_index is not None and 0 <= current_index < len(self.motion.grid.specimens):
            current_specimen = self.motion.grid.specimens[current_index]
        self._stack_specimen_info = current_specimen
        
        # Store F position for scale bar calibration on output image
        x, y, z, f = self.motion.get_current_position()
        self._stack_f_position = f
        
        # Stack parameters: keep total travel at 2.0mm, adjust step size
        if num_images <= 1:
            num_images = 1
            z_step = 0.0
        else:
            z_step = 2.0 / num_images  # e.g. 10->0.2mm, 20->0.1mm
        
        # Create progress dialog with thumbnail grid
        self.focus_stack_progress = FocusStackProgressDialog(self, num_images, z_step)
        self.focus_stack_progress.aborted.connect(self._abort_focus_stack)
        
        # Create and start worker thread
        self.focus_stack_thread = FocusStackThread(
            motion_controller=self.motion,
            video_thread=self.video,
            cache_dir=self.focus_stack_cache_dir,
            start_z=start_z,
            num_images=num_images,
            z_step=z_step
        )
        
        self.focus_stack_thread.status_update.connect(self.focus_stack_progress.update_status)
        self.focus_stack_thread.thumbnail_captured.connect(self.focus_stack_progress.add_thumbnail)
        self.focus_stack_thread.finished_signal.connect(self._on_focus_stack_complete)
        self.focus_stack_thread.error_signal.connect(self._on_focus_stack_error)
        
        # Lock controls
        self._lock_controls(True)
        
        # Show progress dialog and start thread
        self.focus_stack_progress.show()
        self.focus_stack_thread.start()
    
    def _abort_focus_stack(self):
        """Abort focus stack operation"""
        if self.focus_stack_thread and self.focus_stack_thread.isRunning():
            self.focus_stack_thread.abort()
    
    def _on_focus_stack_complete(self, result_path: str, start_z: float):
        """Handle successful focus stack completion"""
        self.focus_stack_progress.close()
        self._lock_controls(False)
        
        # Return Z to starting position by jogging back up
        # (We moved down 10 steps of 0.2mm = 2.0mm total during capture)
        try:
            self.motion.jog('z', 2.0)  # Jog Z back up (positive = away from specimen)
        except Exception as e:
            print(f"Warning: Could not return Z to start position: {e}")
        
        # Show result (blocking) - auto-advance resumes AFTER user closes dialog
        if os.path.exists(result_path):
            self._show_stacked_result(result_path)
        else:
            QMessageBox.warning(self, "Focus Stack", "Stacking completed but result file not found.")
        
        # Resume auto-advance AFTER user has viewed and closed the result
        self.motion.resume_auto_cycle()
    
    def _on_focus_stack_error(self, error_msg: str, start_z: float):
        """Handle focus stack error"""
        self.focus_stack_progress.close()
        self._lock_controls(False)
        
        # Return Z to starting position by jogging back up
        # (We may have moved partway through the stack)
        try:
            x, y, current_z, f = self.motion.get_current_position()
            z_to_return = start_z - current_z  # How much to jog back up
            if z_to_return > 0:
                self.motion.jog('z', z_to_return)
        except Exception as e:
            print(f"Warning: Could not return Z to start position: {e}")
        
        # Show styled error dialog (QMessageBox has white-on-white issues)
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle("Focus Stack Error")
        error_dialog.setModal(True)
        error_dialog.setFixedSize(450, 200)
        error_dialog.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #5a3030;
                color: #ffffff;
                border: 1px solid #7a4040;
                border-radius: 4px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #7a4040;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Error icon and title
        title_label = QLabel("❌ Focus Stack Failed")
        title_label.setFont(QFont("Liberation Sans", 14, QFont.Bold))
        title_label.setStyleSheet("color: #ff6b6b;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Error message
        msg_label = QLabel(error_msg)
        msg_label.setFont(QFont("Liberation Sans", 10))
        msg_label.setWordWrap(True)
        msg_label.setAlignment(Qt.AlignCenter)
        msg_label.setStyleSheet("color: #e0e0e0; margin: 15px;")
        layout.addWidget(msg_label)
        
        layout.addStretch()
        
        # OK button
        ok_btn = QPushButton("OK")
        ok_btn.setFixedWidth(100)
        ok_btn.clicked.connect(error_dialog.accept)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        error_dialog.setLayout(layout)
        error_dialog.exec_()
        
        # Resume auto-advance after user acknowledges error
        self.motion.resume_auto_cycle()
    
    # ==================== GIGA CRYSTAL CLEAR (Tiled Focus Stacking) ====================
    
    def _on_giga_focus_stack_clicked(self):
        """Handle giga focus stack button click"""
        # Check if already running
        if hasattr(self, 'giga_focus_stack_thread') and self.giga_focus_stack_thread and self.giga_focus_stack_thread.isRunning():
            QMessageBox.warning(self, "Giga Focus Stack Running", "A giga focus stack operation is already in progress.")
            return
        
        if self.focus_stack_thread and self.focus_stack_thread.isRunning():
            QMessageBox.warning(self, "Focus Stack Running", "A focus stack operation is already in progress.")
            return
        
        # Pause auto-advance immediately
        self.motion.pause_auto_cycle()
        
        # Get current position
        x, y, current_z, f = self.motion.get_current_position()
        
        # Check Z travel (need 2.0mm downward)
        required_travel = 2.0
        if current_z < required_travel:
            msg = f"""Insufficient Z travel for giga focus stack.

Required: {required_travel:.1f}mm downward
Available: {current_z:.1f}mm

Please move the Z axis to a higher position (further from the specimen) and try again."""
            QMessageBox.warning(self, "Insufficient Z Travel", msg)
            self.motion.resume_auto_cycle()
            return
        
        # Calculate FOV and tile spacing based on current F position
        f_max = 11.5
        fov_min = 4.7
        fov_max = 0.83
        f_ratio = min(f / f_max, 1.0) if f_max > 0 else 0.0
        fov_mm = fov_min - (fov_min - fov_max) * f_ratio
        
        # Tile spacing: 70% of FOV (30% overlap)
        tile_spacing_mm = fov_mm * 0.70
        
        # Show confirmation dialog
        confirm_dialog = QDialog(self)
        confirm_dialog.setWindowTitle("Giga Focus Stack")
        confirm_dialog.setModal(True)
        confirm_dialog.setFixedSize(520, 420)
        confirm_dialog.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 10px 20px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #5d5d5d;
            }
            QPushButton#yesBtn {
                background-color: #3d2d5a;
            }
            QPushButton#yesBtn:hover {
                background-color: #4d3d6a;
            }
        """)
        
        layout = QVBoxLayout()
        
        msg_label = QLabel(f"""<h3>🔬 Take a Giga Crystal Clear Photo</h3>
<p>This advanced mode captures a <b>3×3 grid of tiles</b> at each focus level, then stitches them together 
for a <b>much larger field of view</b> while keeping everything crystal clear!</p>
<p><b>Current settings:</b></p>
<ul>
<li>FOV: {fov_mm:.2f}mm → Final image: ~{fov_mm * 2.4:.1f}mm across</li>
<li>Tile spacing: {tile_spacing_mm:.2f}mm (30% overlap)</li>
</ul>
<p>All controls will be locked during the operation.</p>""")
        msg_label.setWordWrap(True)
        msg_label.setFont(QFont("Liberation Sans", 10))
        layout.addWidget(msg_label)
        
        # Image count selection
        from PyQt5.QtWidgets import QRadioButton, QButtonGroup
        giga_count_label = QLabel("<b>Number of images per tile to stack:</b>")
        giga_count_label.setFont(QFont("Liberation Sans", 10))
        layout.addWidget(giga_count_label)
        
        giga_count_layout = QHBoxLayout()
        giga_count_group = QButtonGroup(confirm_dialog)
        
        giga_radio_1 = QRadioButton("1 (no stacking)")
        giga_radio_1.setStyleSheet("QRadioButton { color: #ffffff; font-size: 12px; } QRadioButton::indicator { background-color: #3d3d3d; border: 1px solid #666666; border-radius: 6px; width: 12px; height: 12px; } QRadioButton::indicator:checked { background-color: #b464dc; }")
        giga_count_group.addButton(giga_radio_1, 1)
        giga_count_layout.addWidget(giga_radio_1)
        
        giga_radio_10 = QRadioButton("10 (default)")
        giga_radio_10.setStyleSheet("QRadioButton { color: #ffffff; font-size: 12px; } QRadioButton::indicator { background-color: #3d3d3d; border: 1px solid #666666; border-radius: 6px; width: 12px; height: 12px; } QRadioButton::indicator:checked { background-color: #b464dc; }")
        giga_radio_10.setChecked(True)
        giga_count_group.addButton(giga_radio_10, 10)
        giga_count_layout.addWidget(giga_radio_10)
        
        giga_radio_20 = QRadioButton("20 (fine)")
        giga_radio_20.setStyleSheet("QRadioButton { color: #ffffff; font-size: 12px; } QRadioButton::indicator { background-color: #3d3d3d; border: 1px solid #666666; border-radius: 6px; width: 12px; height: 12px; } QRadioButton::indicator:checked { background-color: #b464dc; }")
        giga_count_group.addButton(giga_radio_20, 20)
        giga_count_layout.addWidget(giga_radio_20)
        
        layout.addLayout(giga_count_layout)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        no_btn = QPushButton("No")
        no_btn.clicked.connect(confirm_dialog.reject)
        btn_layout.addWidget(no_btn)
        
        yes_btn = QPushButton("Yes")
        yes_btn.setObjectName("yesBtn")
        yes_btn.clicked.connect(confirm_dialog.accept)
        btn_layout.addWidget(yes_btn)
        
        layout.addLayout(btn_layout)
        confirm_dialog.setLayout(layout)
        
        if confirm_dialog.exec_() == QDialog.Accepted:
            selected_count = giga_count_group.checkedId()
            self._start_giga_focus_stack(x, y, current_z, f, tile_spacing_mm, selected_count)
        else:
            self.motion.resume_auto_cycle()
    
    def _start_giga_focus_stack(self, start_x: float, start_y: float, start_z: float, 
                                 f_position: float, tile_spacing_mm: float, num_z_steps: int = 10):
        """Start giga focus stack operation"""
        # Create cache directory
        giga_cache_dir = os.path.join(self.focus_stack_cache_dir, "giga_tiles")
        os.makedirs(giga_cache_dir, exist_ok=True)
        
        # Store specimen info and F position for branding
        current_index = self.motion.current_specimen_index
        if current_index is not None and 0 <= current_index < len(self.motion.grid.specimens):
            self._giga_specimen_info = self.motion.grid.specimens[current_index]
        else:
            self._giga_specimen_info = None
        self._giga_f_position = f_position
        
        # Parameters: keep total travel at 2.0mm, adjust step size
        if num_z_steps <= 1:
            num_z_steps = 1
            z_step = 0.0
        else:
            z_step = 2.0 / num_z_steps  # e.g. 10->0.2mm, 20->0.1mm
        num_tiles = 9  # 3x3
        
        # Create progress dialog
        self.giga_focus_stack_progress = GigaFocusStackProgressDialog(self, num_z_steps, z_step)
        self.giga_focus_stack_progress.aborted.connect(self._abort_giga_focus_stack)
        
        # Create worker thread
        self.giga_focus_stack_thread = GigaFocusStackThread(
            motion_controller=self.motion,
            video_thread=self.video,
            cache_dir=giga_cache_dir,
            start_x=start_x,
            start_y=start_y,
            start_z=start_z,
            tile_spacing=tile_spacing_mm,
            num_z_steps=num_z_steps,
            z_step=z_step
        )
        
        self.giga_focus_stack_thread.status_update.connect(self.giga_focus_stack_progress.update_status)
        self.giga_focus_stack_thread.tile_start.connect(self.giga_focus_stack_progress.start_tile)
        self.giga_focus_stack_thread.z_captured.connect(self.giga_focus_stack_progress.add_z_thumbnail)
        self.giga_focus_stack_thread.tile_stacked.connect(self.giga_focus_stack_progress.add_stacked_tile)
        self.giga_focus_stack_thread.progress_update.connect(self.giga_focus_stack_progress.set_progress)
        self.giga_focus_stack_thread.finished_signal.connect(self._on_giga_focus_stack_complete)
        self.giga_focus_stack_thread.error_signal.connect(self._on_giga_focus_stack_error)
        
        # Lock controls
        self._lock_controls(True)
        
        # Show progress dialog and start
        self.giga_focus_stack_progress.show()
        self.giga_focus_stack_thread.start()
    
    def _abort_giga_focus_stack(self):
        """Abort giga focus stack operation"""
        if hasattr(self, 'giga_focus_stack_thread') and self.giga_focus_stack_thread and self.giga_focus_stack_thread.isRunning():
            self.giga_focus_stack_thread.abort()
    
    def _on_giga_focus_stack_complete(self, result_path: str, start_x: float, start_y: float, start_z: float):
        """Handle successful giga focus stack completion"""
        self.giga_focus_stack_progress.close()
        self._lock_controls(False)
        
        # Return to start position
        try:
            self.motion.jog('z', 2.0)  # Z back up
            time.sleep(0.2)
            # Return XY to center (we may have moved during tiling)
            current_x, current_y, _, _ = self.motion.get_current_position()
            x_delta = start_x - current_x
            y_delta = start_y - current_y
            if abs(x_delta) > 0.01:
                self.motion.jog('x', x_delta)
            if abs(y_delta) > 0.01:
                self.motion.jog('y', y_delta)
        except Exception as e:
            print(f"Warning: Could not return to start position: {e}")
        
        # Show result
        if os.path.exists(result_path):
            self._show_giga_stacked_result(result_path)
        else:
            QMessageBox.warning(self, "Giga Focus Stack", "Stacking completed but result file not found.")
        
        self.motion.resume_auto_cycle()
    
    def _on_giga_focus_stack_error(self, error_msg: str, start_x: float, start_y: float, start_z: float):
        """Handle giga focus stack error"""
        self.giga_focus_stack_progress.close()
        self._lock_controls(False)
        
        # Return to start position
        try:
            current_x, current_y, current_z, _ = self.motion.get_current_position()
            z_delta = start_z - current_z
            if z_delta > 0:
                self.motion.jog('z', z_delta)
            x_delta = start_x - current_x
            y_delta = start_y - current_y
            if abs(x_delta) > 0.01:
                self.motion.jog('x', x_delta)
            if abs(y_delta) > 0.01:
                self.motion.jog('y', y_delta)
        except Exception as e:
            print(f"Warning: Could not return to start position: {e}")
        
        # Show error dialog
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle("Giga Focus Stack Error")
        error_dialog.setModal(True)
        error_dialog.setFixedSize(500, 220)
        error_dialog.setStyleSheet("""
            QDialog { background-color: #2b2b2b; }
            QLabel { color: #ffffff; }
            QPushButton {
                background-color: #5a3030;
                color: #ffffff;
                border: 1px solid #7a4040;
                border-radius: 4px;
                padding: 8px 20px;
            }
            QPushButton:hover { background-color: #7a4040; }
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel("❌ Giga Focus Stack Failed")
        title_label.setFont(QFont("Liberation Sans", 14, QFont.Bold))
        title_label.setStyleSheet("color: #ff6b6b;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        msg_label = QLabel(error_msg)
        msg_label.setFont(QFont("Liberation Sans", 10))
        msg_label.setWordWrap(True)
        msg_label.setAlignment(Qt.AlignCenter)
        msg_label.setStyleSheet("color: #e0e0e0; margin: 15px;")
        layout.addWidget(msg_label)
        
        layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.setFixedWidth(100)
        ok_btn.clicked.connect(error_dialog.accept)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        error_dialog.setLayout(layout)
        error_dialog.exec_()
        
        self.motion.resume_auto_cycle()
    
    def _show_giga_stacked_result(self, result_path: str):
        """Show giga stacked image result"""
        # Apply branding (with giga-specific label)
        branded_path = self._add_branding_to_image(result_path, giga_mode=True)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("✨ Your Giga Crystal Clear Photo")
        dialog.setModal(True)
        dialog.resize(1200, 850)
        dialog.setStyleSheet("""
            QDialog { background-color: #1a1a2e; }
            QLabel { color: #ffffff; }
            QPushButton {
                background-color: #3d3d5c;
                color: #ffffff;
                border: 1px solid #5555aa;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4d4d7a;
                border: 1px solid #7777cc;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        title_label = QLabel("✨ Your Giga Crystal Clear Photo is Ready!")
        title_label.setFont(QFont("Liberation Sans", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #b464dc; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        pixmap = QPixmap(branded_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(1160, 700, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label = QLabel()
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(image_label)
        else:
            layout.addWidget(QLabel("Error: Could not load giga stacked image."))
        
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save As...")
        save_btn.setFixedHeight(40)
        save_btn.clicked.connect(lambda: self._save_stacked_image(branded_path, dialog))
        button_layout.addWidget(save_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(40)
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec_()
    
    # ==================== END GIGA CRYSTAL CLEAR ====================

    def _show_stacked_result(self, result_path: str):
        """Show stacked image result with branding and offer to save"""
        # Apply branding overlays to the result image
        branded_path = self._add_branding_to_image(result_path)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("✨ Your Crystal Clear Photo")
        dialog.setModal(True)
        dialog.resize(1200, 800)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #3d3d5c;
                color: #ffffff;
                border: 1px solid #5555aa;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4d4d7a;
                border: 1px solid #7777cc;
            }
            QPushButton:pressed {
                background-color: #2d2d4a;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("✨ Your Crystal Clear Photo is Ready!")
        title_label.setFont(QFont("Liberation Sans", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #64b5f6; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Load and display branded image
        pixmap = QPixmap(branded_path)
        if not pixmap.isNull():
            # Scale to fit dialog
            scaled_pixmap = pixmap.scaled(1160, 650, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label = QLabel()
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(image_label)
        else:
            layout.addWidget(QLabel("Error: Could not load stacked image."))
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save As...")
        save_btn.setFixedHeight(40)
        save_btn.clicked.connect(lambda: self._save_stacked_image(branded_path, dialog))
        button_layout.addWidget(save_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(40)
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def _save_stacked_image(self, source_path: str, parent_dialog: QDialog):
        """Save stacked image to user-selected location"""
        from datetime import datetime
        
        # Generate default filename with mineral name and timestamp
        default_name = "mineral_photo"
        if hasattr(self, '_stack_specimen_info') and self._stack_specimen_info:
            # Clean mineral name for filename
            mineral = self._stack_specimen_info.mineral_name.replace(" ", "_").replace(",", "")
            mineral = ''.join(c for c in mineral if c.isalnum() or c == '_')[:30]
            default_name = mineral
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"{default_name}_{timestamp}.jpg"
        
        save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stacked_pictures")
        os.makedirs(save_dir, exist_ok=True)
        
        file_path, _ = QFileDialog.getSaveFileName(
            parent_dialog,
            "Save Your Crystal Clear Photo",
            os.path.join(save_dir, default_filename),
            "JPEG Images (*.jpg *.jpeg)"
        )
        
        if file_path:
            try:
                import shutil
                shutil.copy2(source_path, file_path)
                QMessageBox.information(parent_dialog, "Save Successful", f"Image saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(parent_dialog, "Save Failed", f"Could not save image:\n{e}")
    
    def _add_branding_to_image(self, source_path: str, giga_mode: bool = False) -> str:
        """Add branding overlays to stacked image"""
        import numpy as np
        from datetime import datetime
        
        # Load the source image
        img = cv2.imread(source_path)
        if img is None:
            return source_path
        
        height, width = img.shape[:2]
        
        # Create branded version path
        branded_path = source_path.replace('.jpg', '_branded.jpg').replace('.png', '_branded.png')
        
        # Semi-transparent overlay for header
        overlay = img.copy()
        
        # Header bar (top)
        header_height = 60
        cv2.rectangle(overlay, (0, 0), (width, header_height), (30, 30, 40), -1)
        
        # Footer bar (bottom)
        footer_height = 50
        cv2.rectangle(overlay, (0, height - footer_height), (width, height), (30, 30, 40), -1)
        
        # Blend overlay
        alpha = 0.85
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
        
        # Header text - Title (left)
        font = cv2.FONT_HERSHEY_SIMPLEX
        title_text = "THE MINERAL MICROSCOPE"
        cv2.putText(img, title_text, (20, 40), font, 1.0, (100, 180, 255), 2, cv2.LINE_AA)
        
        # Header text - Attribution (right)
        attribution = "Brought to you by Tom Mortimer of mindatnh.org"
        attr_size = cv2.getTextSize(attribution, font, 0.6, 1)[0]
        cv2.putText(img, attribution, (width - attr_size[0] - 20, 40), 
                   font, 0.6, (180, 180, 200), 1, cv2.LINE_AA)
        
        # Add calibrated scale bar to bottom-left area (above footer)
        f_max = 11.5
        fov_min = 4.7   # mm at F=0 
        fov_max = 0.83  # mm at F=11.5
        
        # Get F position at time of capture (stored when stack started)
        f_position = 0.0
        if giga_mode and hasattr(self, '_giga_f_position'):
            f_position = self._giga_f_position
        elif hasattr(self, '_stack_f_position'):
            f_position = self._stack_f_position
        
        # Calculate current FOV based on F position (same formula as live view)
        f_ratio = min(f_position / f_max, 1.0) if f_max > 0 else 0.0
        calibrated_fov_mm = fov_min - (fov_min - fov_max) * f_ratio
        
        # For giga mode: FOV is ~2.4x larger due to 3x3 tiling with 30% overlap
        # For standard: use original calculation
        if giga_mode:
            # Giga: 3 tiles * 70% spacing = 2.4x FOV coverage
            giga_fov_multiplier = 2.4
            stacked_fov_mm = calibrated_fov_mm * giga_fov_multiplier
            px_per_mm = width / stacked_fov_mm
        else:
            fov_reference_px = 668 / 0.6  # = 1113px corresponds to calibrated FOV
            stacked_fov_mm = calibrated_fov_mm * (1920 / fov_reference_px)
            px_per_mm = width / stacked_fov_mm
        
        print(f"[ScaleBar] F={f_position:.1f}, calibrated_FOV={calibrated_fov_mm:.2f}mm, stacked_FOV={stacked_fov_mm:.2f}mm, giga={giga_mode}")
        print(f"[ScaleBar] px_per_mm={px_per_mm:.1f}, image={width}x{height}")
        
        # Use same tick interval logic as live ruler for easy comparison
        ruler_represents_mm = stacked_fov_mm * 0.4  # Show reasonable portion
        
        # Same logic as _draw_scale_ruler for tick intervals
        if ruler_represents_mm > 20:
            scale_mm = 10.0
        elif ruler_represents_mm > 10:
            scale_mm = 5.0
        elif ruler_represents_mm > 5:
            scale_mm = 2.0
        elif ruler_represents_mm > 2:
            scale_mm = 1.0
        else:
            scale_mm = 0.5
        
        bar_length_px = int(scale_mm * px_per_mm)
        print(f"[ScaleBar] Drawing {scale_mm}mm bar = {bar_length_px}px")
        
        # Format label (same as live ruler)
        if scale_mm >= 1.0:
            scale_label = f"{int(scale_mm)}mm"
        else:
            scale_label = f"{scale_mm}mm"
        
        self._add_scale_bar(img, 20, height - footer_height - 30, bar_length_px, scale_label)
        
        # Mineral info card (upper right corner)
        specimen_info = None
        if giga_mode and hasattr(self, '_giga_specimen_info'):
            specimen_info = self._giga_specimen_info
        elif hasattr(self, '_stack_specimen_info'):
            specimen_info = self._stack_specimen_info
        
        if specimen_info:
            card_width = 350
            card_height = 90
            card_x = width - card_width - 15
            card_y = header_height + 15
            
            # Card background
            card_overlay = img.copy()
            cv2.rectangle(card_overlay, (card_x, card_y), 
                         (card_x + card_width, card_y + card_height), (40, 35, 30), -1)
            cv2.rectangle(card_overlay, (card_x, card_y), 
                         (card_x + card_width, card_y + card_height), (100, 140, 180), 2)
            cv2.addWeighted(card_overlay, 0.9, img, 0.1, 0, img)
            
            # Mineral name
            mineral_text = specimen_info.mineral_name[:35] + "..." if len(specimen_info.mineral_name) > 35 else specimen_info.mineral_name
            cv2.putText(img, mineral_text, (card_x + 10, card_y + 28), 
                       font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Location
            loc_text = specimen_info.location[:40] + "..." if len(specimen_info.location) > 40 else specimen_info.location
            cv2.putText(img, loc_text, (card_x + 10, card_y + 52), 
                       font, 0.5, (180, 200, 220), 1, cv2.LINE_AA)
            
            # Collector
            collector_text = f"Collector: {specimen_info.collector}"
            cv2.putText(img, collector_text, (card_x + 10, card_y + 75), 
                       font, 0.45, (150, 170, 190), 1, cv2.LINE_AA)
        
        # Footer - timestamp (left)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        cv2.putText(img, timestamp, (20, height - 18), 
                   font, 0.5, (150, 150, 160), 1, cv2.LINE_AA)
        
        # Footer - technique label (center)
        if giga_mode:
            technique = "Giga Crystal Clear | 3x3 Tiles × 10 Z-Steps"
        else:
            technique = "Focus Stacked | 10 Images"
        tech_size = cv2.getTextSize(technique, font, 0.5, 1)[0]
        cv2.putText(img, technique, ((width - tech_size[0]) // 2, height - 18), 
                   font, 0.5, (150, 150, 160), 1, cv2.LINE_AA)
        
        # Save branded image
        cv2.imwrite(branded_path, img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        return branded_path
    
    def _add_qr_code(self, img, url: str, x: int, y: int, size: int):
        """Add a QR code to the image at specified position"""
        try:
            import qrcode
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=2,
                border=1,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            # Create QR image (PIL)
            qr_img = qr.make_image(fill_color="white", back_color=(30, 30, 40))
            
            # Convert to numpy array
            qr_array = np.array(qr_img.convert('RGB'))
            qr_array = cv2.cvtColor(qr_array, cv2.COLOR_RGB2BGR)
            
            # Resize to desired size
            qr_resized = cv2.resize(qr_array, (size, size), interpolation=cv2.INTER_NEAREST)
            
            # Place on image
            img[y:y+size, x:x+size] = qr_resized
            
        except ImportError:
            # qrcode not installed - draw a placeholder box with text
            cv2.rectangle(img, (x, y), (x+size, y+size), (60, 60, 80), -1)
            cv2.rectangle(img, (x, y), (x+size, y+size), (100, 100, 120), 2)
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img, "QR", (x + size//3, y + size//2 + 5), 
                       font, 0.5, (180, 180, 200), 1, cv2.LINE_AA)
            cv2.putText(img, "mindatnh.org", (x + 5, y + size - 8), 
                       font, 0.25, (150, 150, 170), 1, cv2.LINE_AA)
    
    def _add_scale_bar(self, img, x: int, y: int, bar_length: int, label: str):
        """Add a scale bar with label to the image"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        bar_height = 6
        
        # Draw scale bar (white with black outline for visibility)
        cv2.rectangle(img, (x-1, y-1), (x + bar_length + 1, y + bar_height + 1), (0, 0, 0), -1)
        cv2.rectangle(img, (x, y), (x + bar_length, y + bar_height), (255, 255, 255), -1)
        
        # End caps
        cv2.line(img, (x, y - 3), (x, y + bar_height + 3), (255, 255, 255), 2)
        cv2.line(img, (x + bar_length, y - 3), (x + bar_length, y + bar_height + 3), (255, 255, 255), 2)
        
        # Label
        label_size = cv2.getTextSize(label, font, 0.4, 1)[0]
        label_x = x + (bar_length - label_size[0]) // 2
        cv2.putText(img, label, (label_x, y - 8), font, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
    
    def _lock_controls(self, locked: bool):
        """Lock/unlock all interactive controls during focus stack operation"""
        # Disable specimen cards
        for card in self.specimen_cards:
            card.setEnabled(not locked)
        
        # Disable jog buttons
        for btn in [self.x_plus_btn, self.x_minus_btn, self.y_plus_btn, self.y_minus_btn,
                    self.z_plus_btn, self.z_minus_btn, self.f_plus_btn, self.f_minus_btn]:
            btn.setEnabled(not locked)
        
        # Disable step size buttons
        for btn in self.step_buttons.values():
            btn.setEnabled(not locked)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard shortcuts for main window"""
        # Q to quit (only in normal mode, not diagnostic/calibration)
        if event.key() == Qt.Key_Q:
            if not self.diagnostic_mode and self.startup_complete:
                self.close()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Cleanup on close"""
        print("Closing application...")
        
        # Stop LED ring
        if self.led:
            print("Cleaning up LED ring...")
            self.led.cleanup()
        
        # Stop video first
        if self.video:
            print("Stopping video thread...")
            self.video.stop()
        
        # Stop motion controller
        if self.motion:
            print("Disconnecting motion controller...")
            self.motion.disconnect()
        
        print("Cleanup complete")
        event.accept()


class FocusStackProgressDialog(QDialog):
    """Enhanced progress dialog with educational text and thumbnail grid"""
    
    aborted = pyqtSignal()
    
    def __init__(self, parent=None, num_images=10, z_step=0.2):
        super().__init__(parent)
        self.num_images = num_images
        self.z_step = z_step
        self.thumbnail_labels = []
        self.glow_timers = []
        
        self.setWindowTitle("✨ Creating Your Crystal Clear Photo")
        self.setModal(True)
        if num_images > 10:
            self.setFixedSize(700, 650)
        else:
            self.setFixedSize(700, 520)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
            }
            QLabel {
                color: #e0e0e0;
            }
            QProgressBar {
                background-color: #2d2d4a;
                border: 1px solid #4a4a7a;
                border-radius: 6px;
                text-align: center;
                color: #ffffff;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a90d9, stop:1 #64b5f6);
                border-radius: 4px;
            }
            QPushButton {
                background-color: #5a3030;
                color: #ffffff;
                border: 1px solid #7a4040;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7a4040;
                border: 1px solid #9a5050;
            }
            QPushButton:pressed {
                background-color: #4a2020;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 15, 20, 15)
        
        # Educational header
        title_label = QLabel("🔬 Focus Stacking in Progress")
        title_label.setFont(QFont("Liberation Sans", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #64b5f6; margin-bottom: 5px;")
        main_layout.addWidget(title_label)
        
        # Educational text explaining what's happening
        edu_text = QLabel(
            "We're capturing multiple photos at different focus depths, then combining them\n"
            "into one super-sharp image. This technique lets you see every detail in focus!"
        )
        edu_text.setFont(QFont("Liberation Sans", 10))
        edu_text.setAlignment(Qt.AlignCenter)
        edu_text.setStyleSheet("color: #a0a0c0; margin-bottom: 10px;")
        edu_text.setWordWrap(True)
        main_layout.addWidget(edu_text)
        
        # Thumbnail grid (2 rows x 5 columns)
        thumb_frame = QFrame()
        thumb_frame.setStyleSheet("""
            QFrame {
                background-color: #252540;
                border: 1px solid #3a3a5a;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        thumb_layout = QGridLayout()
        thumb_layout.setHorizontalSpacing(8)
        thumb_layout.setVerticalSpacing(12)
        thumb_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create thumbnail placeholders with labels
        for i in range(num_images):
            row = i // 5
            col = i % 5
            
            # Container for thumbnail + label
            container = QWidget()
            container_layout = QVBoxLayout()
            container_layout.setSpacing(2)
            container_layout.setContentsMargins(0, 0, 0, 0)
            
            # Thumbnail label (will hold the image)
            thumb_label = QLabel()
            if num_images > 10:
                thumb_label.setFixedSize(110, 68)
            else:
                thumb_label.setFixedSize(110, 82)
            thumb_label.setStyleSheet("""
                QLabel {
                    background-color: #1a1a30;
                    border: 2px solid #3a3a5a;
                    border-radius: 4px;
                }
            """)
            thumb_label.setAlignment(Qt.AlignCenter)
            thumb_label.setText("...")
            container_layout.addWidget(thumb_label)
            
            # Z-offset label
            z_offset = -i * z_step
            z_label = QLabel(f"{z_offset:+.1f}mm")
            z_label.setFont(QFont("Liberation Sans", 8))
            z_label.setAlignment(Qt.AlignCenter)
            z_label.setStyleSheet("color: #8080a0; border: none; background: transparent;")
            container_layout.addWidget(z_label)
            
            container.setLayout(container_layout)
            thumb_layout.addWidget(container, row, col)
            self.thumbnail_labels.append(thumb_label)
        
        thumb_frame.setLayout(thumb_layout)
        main_layout.addWidget(thumb_frame)
        
        # Status label
        self.status_label = QLabel("Preparing camera...")
        self.status_label.setFont(QFont("Liberation Sans", 11))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #ffffff; margin-top: 5px;")
        main_layout.addWidget(self.status_label)
        
        # Progress bar (determinate during capture, indeterminate during stacking)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(num_images)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # Abort button
        abort_btn = QPushButton("Cancel")
        abort_btn.setFixedHeight(40)
        abort_btn.setFixedWidth(120)
        abort_btn.clicked.connect(self._on_abort)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(abort_btn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def add_thumbnail(self, index: int, pixmap: QPixmap):
        """Add a captured thumbnail with pop-in animation and glow effect"""
        if 0 <= index < len(self.thumbnail_labels):
            thumb_label = self.thumbnail_labels[index]
            
            # Scale pixmap to fit
            scaled = pixmap.scaled(106, 78, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            thumb_label.setPixmap(scaled)
            
            # Add glow border effect
            thumb_label.setStyleSheet("""
                QLabel {
                    background-color: #1a1a30;
                    border: 2px solid #64b5f6;
                    border-radius: 4px;
                }
            """)
            
            # Remove glow after 400ms
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self._remove_glow(index))
            timer.start(400)
            self.glow_timers.append(timer)
            
            # Update progress bar
            self.progress_bar.setValue(index + 1)
    
    def _remove_glow(self, index: int):
        """Remove glow effect from thumbnail"""
        if 0 <= index < len(self.thumbnail_labels):
            self.thumbnail_labels[index].setStyleSheet("""
                QLabel {
                    background-color: #1a1a30;
                    border: 2px solid #4a90d9;
                    border-radius: 4px;
                }
            """)
    
    def update_status(self, status: str):
        """Update status message"""
        self.status_label.setText(status)
        
        # Switch to indeterminate mode during alignment/stacking
        if "Aligning" in status or "stacking" in status.lower():
            self.progress_bar.setMaximum(0)
    
    def _on_abort(self):
        """Handle abort button click"""
        self.status_label.setText("Aborting... please wait")
        self.aborted.emit()


class FocusStackThread(QThread):
    """Background thread for focus stack image capture and processing"""
    
    status_update = pyqtSignal(str)
    thumbnail_captured = pyqtSignal(int, QPixmap)  # index, thumbnail pixmap
    finished_signal = pyqtSignal(str, float)  # result_path, start_z
    error_signal = pyqtSignal(str, float)  # error_msg, start_z
    
    def __init__(self, motion_controller, video_thread, cache_dir: str, 
                 start_z: float, num_images: int, z_step: float):
        super().__init__()
        self.motion = motion_controller
        self.video_thread = video_thread
        self.cache_dir = cache_dir
        self.start_z = start_z
        self.num_images = num_images
        self.z_step = z_step
        self.should_abort = False
    
    def abort(self):
        """Request abort of operation"""
        self.should_abort = True
    
    def _frame_to_pixmap(self, frame):
        """Convert numpy frame (RGB) to QPixmap for thumbnail display"""
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(qimg)
    
    def run(self):
        """Execute focus stack operation"""
        try:
            # Capture phase
            image_paths = []
            for i in range(self.num_images):
                if self.should_abort:
                    self._cleanup_and_return("Operation aborted by user")
                    return
                
                self.status_update.emit(f"📸 Capturing image {i+1} of {self.num_images}...")
                
                # Grab frame from video thread (thread-safe)
                frame = self.video_thread.get_current_frame()
                if frame is not None:
                    # Emit thumbnail for progress dialog (RGB format for Qt)
                    thumbnail_pixmap = self._frame_to_pixmap(frame)
                    self.thumbnail_captured.emit(i, thumbnail_pixmap)
                    
                    # Convert RGB to BGR for cv2.imwrite (TC358743 outputs RGB3, 
                    # but OpenCV expects BGR format for saving)
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    # Save frame
                    img_path = os.path.join(self.cache_dir, f"img_{i+1:02d}.png")
                    cv2.imwrite(img_path, frame_bgr)
                    image_paths.append(img_path)
                else:
                    self._cleanup_and_return("Video capture not available - no frame received")
                    return
                
                # Move Z axis towards specimen (except after last image)
                # Negative Z = moving down towards specimen
                if i < self.num_images - 1:
                    try:
                        self.motion.jog('z', -self.z_step)
                        time.sleep(0.15)  # Settle time
                    except Exception as e:
                        self._cleanup_and_return(f"Motion error: {e}")
                        return
            
            if self.should_abort:
                self._cleanup_and_return("Operation aborted by user")
                return
            
            # Stacking phase - skip if only 1 image
            if self.num_images == 1:
                # No stacking needed, just use the single image as result
                result_path = os.path.join(self.cache_dir, "stacked.jpg")
                frame_bgr = cv2.imread(image_paths[0])
                cv2.imwrite(result_path, frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
            else:
                self.status_update.emit("✨ Aligning and combining images... (this takes ~30s)")
                result_path = os.path.join(self.cache_dir, "stacked.jpg")
            
                # Call focus-stack with memory-saving options for RPi4
                # Note: focus-stack uses --option=value syntax, not --option value
                try:
                    cmd = [
                        "focus-stack",
                        f"--output={result_path}",
                        "--threads=2",      # Limit threads to reduce memory
                        "--batchsize=4",    # Smaller batches to reduce memory
                        "--no-opencl",      # Disable GPU to save memory
                        "--consistency=1",  # Slightly faster with minimal quality loss
                        "--jpgquality=90",  # Slightly lower quality to save memory
                    ] + sorted(image_paths)
                    print(f"[FocusStack] Running: {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                    print(f"[FocusStack] Exit code: {result.returncode}")
                    if result.stdout:
                        print(f"[FocusStack] stdout: {result.stdout}")
                    if result.stderr:
                        print(f"[FocusStack] stderr: {result.stderr}")
                    
                    if result.returncode != 0:
                        error_msg = result.stderr if result.stderr else "Unknown error"
                        self._cleanup_and_return(f"focus-stack failed: {error_msg}")
                        return
                except subprocess.TimeoutExpired:
                    self._cleanup_and_return("Stacking operation timed out (>60s)")
                    return
                except FileNotFoundError:
                    self._cleanup_and_return("focus-stack tool not found. Please install it.")
                    return
                except Exception as e:
                    self._cleanup_and_return(f"Stacking error: {e}")
                    return
            
            if self.should_abort:
                self._cleanup_and_return("Operation aborted by user")
                return
            
            # Success
            self.status_update.emit("✨ Your crystal clear photo is ready!")
            time.sleep(0.5)  # Brief delay to show completion message
            self.finished_signal.emit(result_path, self.start_z)
            
        except Exception as e:
            self._cleanup_and_return(f"Unexpected error: {e}")
    
    def _cleanup_and_return(self, error_msg: str):
        """Clean up and emit error"""
        # Clean up cached images
        try:
            for img_file in glob.glob(os.path.join(self.cache_dir, "img_*.png")):
                os.remove(img_file)
        except Exception:
            pass
        
        self.error_signal.emit(error_msg, self.start_z)


class GigaFocusStackProgressDialog(QDialog):
    """Progress dialog for giga (tiled) focus stacking - stack then stitch approach
    
    Left panel: 2x5 grid showing Z-stack progress for current tile
    Right panel: 3x3 grid showing completed stacked tiles
    """
    
    aborted = pyqtSignal()
    
    def __init__(self, parent=None, num_z_steps=10, z_step=0.2):
        super().__init__(parent)
        self.num_z_steps = num_z_steps
        self.z_step = z_step
        self.z_labels = []  # 2x5 grid for current tile's Z levels
        self.tile_labels = []  # 3x3 grid for completed stacked tiles
        self.glow_timers = []
        self.current_tile_index = 0
        
        self.setWindowTitle("🔬 Creating Your Giga Crystal Clear Photo")
        self.setModal(True)
        self.setFixedSize(950, 580)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
            }
            QLabel {
                color: #e0e0e0;
            }
            QProgressBar {
                background-color: #2d2d4a;
                border: 1px solid #4a4a7a;
                border-radius: 6px;
                text-align: center;
                color: #ffffff;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9a4ad9, stop:1 #b464f6);
                border-radius: 4px;
            }
            QPushButton {
                background-color: #5a3030;
                color: #ffffff;
                border: 1px solid #7a4040;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7a4040;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 12, 15, 12)
        
        # Title
        title_label = QLabel("🔬 Giga Focus Stacking in Progress")
        title_label.setFont(QFont("Liberation Sans", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #b464f6; margin-bottom: 5px;")
        main_layout.addWidget(title_label)
        
        # Educational text
        edu_text = QLabel(
            "Focus stacking each tile first for sharp images, then stitching into a panorama.\n"
            "This creates one ultra-sharp wide-area image!"
        )
        edu_text.setFont(QFont("Liberation Sans", 9))
        edu_text.setAlignment(Qt.AlignCenter)
        edu_text.setStyleSheet("color: #a0a0c0; margin-bottom: 8px;")
        main_layout.addWidget(edu_text)
        
        # Main content: two side-by-side grids
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # LEFT: 2x5 Z-stack grid for current tile
        left_frame = QFrame()
        left_frame.setStyleSheet("""
            QFrame {
                background-color: #252540;
                border: 1px solid #3a3a5a;
                border-radius: 8px;
            }
        """)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(10, 8, 10, 8)
        
        left_title = QLabel("Current Tile - Z Stack")
        left_title.setFont(QFont("Liberation Sans", 10, QFont.Bold))
        left_title.setAlignment(Qt.AlignCenter)
        left_title.setStyleSheet("color: #b0b0d0; border: none; background: transparent;")
        left_layout.addWidget(left_title)
        
        self.tile_progress_label = QLabel("Tile: --")
        self.tile_progress_label.setFont(QFont("Liberation Sans", 9))
        self.tile_progress_label.setAlignment(Qt.AlignCenter)
        self.tile_progress_label.setStyleSheet("color: #8080a0; border: none; background: transparent;")
        left_layout.addWidget(self.tile_progress_label)
        
        # 2x5 grid for Z levels
        z_grid = QGridLayout()
        z_grid.setSpacing(6)
        
        for i in range(num_z_steps):
            row = i // 5
            col = i % 5
            
            container = QWidget()
            container_layout = QVBoxLayout()
            container_layout.setSpacing(2)
            container_layout.setContentsMargins(0, 0, 0, 0)
            
            z_label = QLabel()
            z_label.setFixedSize(85, 63)
            z_label.setStyleSheet("""
                QLabel {
                    background-color: #1a1a30;
                    border: 2px solid #3a3a5a;
                    border-radius: 4px;
                }
            """)
            z_label.setAlignment(Qt.AlignCenter)
            z_label.setText("...")
            container_layout.addWidget(z_label)
            
            z_offset = -i * z_step
            offset_label = QLabel(f"{z_offset:+.1f}mm")
            offset_label.setFont(QFont("Liberation Sans", 7))
            offset_label.setAlignment(Qt.AlignCenter)
            offset_label.setStyleSheet("color: #8080a0; border: none; background: transparent;")
            container_layout.addWidget(offset_label)
            
            container.setLayout(container_layout)
            z_grid.addWidget(container, row, col)
            self.z_labels.append(z_label)
        
        left_layout.addLayout(z_grid)
        left_frame.setLayout(left_layout)
        content_layout.addWidget(left_frame)
        
        # RIGHT: 3x3 grid for completed stacked tiles
        right_frame = QFrame()
        right_frame.setStyleSheet("""
            QFrame {
                background-color: #252540;
                border: 1px solid #3a3a5a;
                border-radius: 8px;
            }
        """)
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 8, 10, 8)
        
        right_title = QLabel("Stacked Tiles")
        right_title.setFont(QFont("Liberation Sans", 10, QFont.Bold))
        right_title.setAlignment(Qt.AlignCenter)
        right_title.setStyleSheet("color: #b0b0d0; border: none; background: transparent;")
        right_layout.addWidget(right_title)
        
        # 3x3 grid for stacked tiles
        tile_grid = QGridLayout()
        tile_grid.setSpacing(8)
        
        # Grid positions: 0=top-left, 4=center, 8=bottom-right
        for i in range(9):
            row = i // 3
            col = i % 3
            
            tile_label = QLabel()
            tile_label.setFixedSize(120, 90)
            tile_label.setStyleSheet("""
                QLabel {
                    background-color: #1a1a30;
                    border: 2px solid #3a3a5a;
                    border-radius: 4px;
                }
            """)
            tile_label.setAlignment(Qt.AlignCenter)
            tile_label.setText("...")
            tile_grid.addWidget(tile_label, row, col)
            self.tile_labels.append(tile_label)
        
        right_layout.addLayout(tile_grid)
        right_frame.setLayout(right_layout)
        content_layout.addWidget(right_frame)
        
        main_layout.addLayout(content_layout)
        
        # Status label
        self.status_label = QLabel("Preparing camera...")
        self.status_label.setFont(QFont("Liberation Sans", 10))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #ffffff; margin-top: 5px;")
        main_layout.addWidget(self.status_label)
        
        # Progress bar (9 tiles × 10 Z each + stitching)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)  # Percentage
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # Abort button
        abort_btn = QPushButton("Cancel")
        abort_btn.setFixedHeight(36)
        abort_btn.setFixedWidth(120)
        abort_btn.clicked.connect(self._on_abort)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(abort_btn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def start_tile(self, tile_index: int, tile_num: int):
        """Called when starting a new tile - clears Z-stack grid and highlights tile position"""
        self.current_tile_index = tile_index
        self.tile_progress_label.setText(f"Tile: {tile_num}/9 (position {tile_index + 1})")
        
        # Clear all Z thumbnails
        for z_label in self.z_labels:
            z_label.setText("...")
            z_label.setPixmap(QPixmap())
            z_label.setStyleSheet("""
                QLabel {
                    background-color: #1a1a30;
                    border: 2px solid #3a3a5a;
                    border-radius: 4px;
                }
            """)
        
        # Highlight current tile position in 3x3 grid (show it's being worked on)
        if 0 <= tile_index < len(self.tile_labels):
            self.tile_labels[tile_index].setStyleSheet("""
                QLabel {
                    background-color: #2a2a50;
                    border: 2px solid #b464f6;
                    border-radius: 4px;
                }
            """)
            self.tile_labels[tile_index].setText("⏳")
    
    def add_z_thumbnail(self, z_index: int, pixmap: QPixmap):
        """Add a captured Z-level thumbnail with glow effect"""
        if 0 <= z_index < len(self.z_labels):
            z_label = self.z_labels[z_index]
            scaled = pixmap.scaled(81, 59, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            z_label.setPixmap(scaled)
            
            # Glow effect
            z_label.setStyleSheet("""
                QLabel {
                    background-color: #1a1a30;
                    border: 2px solid #b464f6;
                    border-radius: 4px;
                }
            """)
            
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self._remove_z_glow(z_index))
            timer.start(300)
            self.glow_timers.append(timer)
    
    def _remove_z_glow(self, z_index: int):
        """Remove glow from Z thumbnail"""
        if 0 <= z_index < len(self.z_labels):
            self.z_labels[z_index].setStyleSheet("""
                QLabel {
                    background-color: #1a1a30;
                    border: 2px solid #6a4a9a;
                    border-radius: 4px;
                }
            """)
    
    def add_stacked_tile(self, tile_index: int, pixmap: QPixmap):
        """Add a completed stacked tile thumbnail"""
        if 0 <= tile_index < len(self.tile_labels):
            tile_label = self.tile_labels[tile_index]
            scaled = pixmap.scaled(116, 86, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            tile_label.setPixmap(scaled)
            
            # Success glow effect (blue)
            tile_label.setStyleSheet("""
                QLabel {
                    background-color: #1a1a30;
                    border: 2px solid #64b5f6;
                    border-radius: 4px;
                }
            """)
            
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self._remove_tile_glow(tile_index))
            timer.start(500)
            self.glow_timers.append(timer)
    
    def _remove_tile_glow(self, tile_index: int):
        """Remove glow from completed tile"""
        if 0 <= tile_index < len(self.tile_labels):
            self.tile_labels[tile_index].setStyleSheet("""
                QLabel {
                    background-color: #1a1a30;
                    border: 2px solid #4a6a9a;
                    border-radius: 4px;
                }
            """)
    
    def update_status(self, status: str):
        """Update status message"""
        self.status_label.setText(status)
    
    def set_progress(self, percent: int):
        """Set progress bar percentage"""
        self.progress_bar.setValue(percent)
        
        # Switch to indeterminate for final stacking
        if percent >= 95:
            self.progress_bar.setMaximum(0)
    
    def _on_abort(self):
        """Handle abort button"""
        self.status_label.setText("Aborting... please wait")
        self.aborted.emit()


class GigaFocusStackThread(QThread):
    """Background thread for giga (tiled) focus stack - stack then stitch approach
    
    For each tile position:
      1. Capture 10 Z levels
      2. Stack them with focus-stack
      3. Move to next tile
    Finally stitch all 9 stacked tiles together
    """
    
    status_update = pyqtSignal(str)
    tile_start = pyqtSignal(int, int)  # tile_index, tile_num (1-9)
    z_captured = pyqtSignal(int, QPixmap)  # z_index, thumbnail
    tile_stacked = pyqtSignal(int, QPixmap)  # tile_index, stacked thumbnail
    progress_update = pyqtSignal(int)  # percentage
    finished_signal = pyqtSignal(str, float, float, float)  # result_path, start_x, start_y, start_z
    error_signal = pyqtSignal(str, float, float, float)  # error_msg, start_x, start_y, start_z
    
    # Spiral order from center (position 4/index 4 in 0-indexed)
    # Grid positions:  0  1  2
    #                  3  4  5  (4 = center)
    #                  6  7  8
    # Spiral: center(4) → left(3) → up-left(0) → up(1) → up-right(2) → right(5) → down-right(8) → down(7) → down-left(6)
    SPIRAL_ORDER = [4, 3, 0, 1, 2, 5, 8, 7, 6]
    
    # XY offsets from center (in units of tile_spacing)
    # Position 4 is center (0, 0)
    # Y is inverted due to microscope optics: +Y stage movement captures top of image
    TILE_OFFSETS = [
        (-1, 1),  (0, 1),  (1, 1),    # positions 0, 1, 2 (top row in final image)
        (-1, 0),  (0, 0),  (1, 0),    # positions 3, 4, 5 (middle row)
        (-1, -1), (0, -1), (1, -1)    # positions 6, 7, 8 (bottom row in final image)
    ]
    
    def __init__(self, motion_controller, video_thread, cache_dir: str,
                 start_x: float, start_y: float, start_z: float,
                 tile_spacing: float, num_z_steps: int, z_step: float):
        super().__init__()
        self.motion = motion_controller
        self.video_thread = video_thread
        self.cache_dir = cache_dir
        self.start_x = start_x
        self.start_y = start_y
        self.start_z = start_z
        self.tile_spacing = tile_spacing
        self.num_z_steps = num_z_steps
        self.z_step = z_step
        self.should_abort = False
    
    def abort(self):
        """Request abort"""
        self.should_abort = True
    
    def _frame_to_pixmap(self, frame):
        """Convert numpy frame (RGB) to QPixmap"""
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(qimg)
    
    def _move_to_tile(self, tile_index: int):
        """Move to tile position relative to center"""
        offset_x, offset_y = self.TILE_OFFSETS[tile_index]
        target_x = self.start_x + offset_x * self.tile_spacing
        target_y = self.start_y + offset_y * self.tile_spacing
        
        current_x, current_y, _, _ = self.motion.get_current_position()
        dx = target_x - current_x
        dy = target_y - current_y
        
        if abs(dx) > 0.01:
            self.motion.jog('x', dx)
            time.sleep(0.1)
        if abs(dy) > 0.01:
            self.motion.jog('y', dy)
            time.sleep(0.1)
        
        time.sleep(0.05)  # Settle
    
    def _stitch_tiles(self, tile_paths: list, output_path: str) -> bool:
        """Stitch 9 tiles into a panorama using OpenCV"""
        import numpy as np
        
        # Load all tiles
        tiles = []
        for path in tile_paths:
            img = cv2.imread(path)
            if img is None:
                print(f"[Stitch] Failed to load: {path}")
                return False
            tiles.append(img)
        
        if len(tiles) != 9:
            print(f"[Stitch] Expected 9 tiles, got {len(tiles)}")
            return False
        
        # Tile arrangement (after spiral capture, sorted by position):
        # 0  1  2
        # 3  4  5
        # 6  7  8
        
        h, w = tiles[0].shape[:2]
        
        # Calculate overlap in pixels (30% overlap means 70% unique)
        overlap_ratio = 0.30
        overlap_px = int(w * overlap_ratio)
        unique_w = w - overlap_px
        unique_h = h - overlap_px
        
        # Output size: 3 tiles wide/tall with overlap
        out_w = w + 2 * unique_w
        out_h = h + 2 * unique_h
        
        print(f"[Stitch] Tile size: {w}x{h}, overlap: {overlap_px}px, output: {out_w}x{out_h}")
        
        # Try OpenCV Stitcher first (feature-based, handles small misalignments)
        try:
            stitcher = cv2.Stitcher_create(cv2.Stitcher_SCANS)
            
            # Arrange tiles in rows for stitcher
            # Row 0: tiles 0, 1, 2
            # Row 1: tiles 3, 4, 5
            # Row 2: tiles 6, 7, 8
            
            # Stitch each row first
            row_results = []
            for row in range(3):
                row_tiles = [tiles[row * 3 + col] for col in range(3)]
                status, row_pano = stitcher.stitch(row_tiles)
                if status == cv2.Stitcher_OK:
                    row_results.append(row_pano)
                else:
                    print(f"[Stitch] Row {row} stitching failed with status {status}, falling back to simple blend")
                    break
            
            # If rows succeeded, stitch rows together
            if len(row_results) == 3:
                # Rotate rows 90° to stitch vertically as horizontal
                rotated = [cv2.rotate(r, cv2.ROTATE_90_CLOCKWISE) for r in row_results]
                status, final = stitcher.stitch(rotated)
                if status == cv2.Stitcher_OK:
                    # Rotate back
                    result = cv2.rotate(final, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    cv2.imwrite(output_path, result, [cv2.IMWRITE_PNG_COMPRESSION, 3])
                    print(f"[Stitch] OpenCV stitcher succeeded: {result.shape}")
                    return True
                else:
                    print(f"[Stitch] Final stitch failed with status {status}, falling back")
        except Exception as e:
            print(f"[Stitch] OpenCV stitcher error: {e}, falling back to simple blend")
        
        # Fallback: Simple placement with alpha blending in overlap regions
        result = np.zeros((out_h, out_w, 3), dtype=np.uint8)
        weight = np.zeros((out_h, out_w), dtype=np.float32)
        
        for idx, tile in enumerate(tiles):
            row = idx // 3
            col = idx % 3
            
            # Calculate position
            x = col * unique_w
            y = row * unique_h
            
            # Create weight mask (feathered edges)
            tile_weight = np.ones((h, w), dtype=np.float32)
            feather = overlap_px // 2
            
            # Feather edges
            for i in range(feather):
                alpha = i / feather
                tile_weight[i, :] *= alpha  # Top
                tile_weight[-(i+1), :] *= alpha  # Bottom
                tile_weight[:, i] *= alpha  # Left
                tile_weight[:, -(i+1)] *= alpha  # Right
            
            # Add to result with blending
            for c in range(3):
                result[y:y+h, x:x+w, c] = (
                    result[y:y+h, x:x+w, c] * weight[y:y+h, x:x+w] +
                    tile[:, :, c] * tile_weight
                ) / (weight[y:y+h, x:x+w] + tile_weight + 1e-6)
            
            weight[y:y+h, x:x+w] += tile_weight
        
        cv2.imwrite(output_path, result.astype(np.uint8), [cv2.IMWRITE_PNG_COMPRESSION, 3])
        print(f"[Stitch] Simple blend succeeded: {result.shape}")
        return True
    
    def run(self):
        """Execute giga focus stack operation - stack then stitch approach"""
        try:
            stacked_tile_paths = []
            total_captures = 9 * self.num_z_steps  # 90 captures
            captures_done = 0
            
            # For each tile position in spiral order
            for tile_num, tile_pos in enumerate(self.SPIRAL_ORDER):
                if self.should_abort:
                    self._cleanup_and_return("Operation aborted by user")
                    return
                
                # Signal start of new tile
                self.tile_start.emit(tile_pos, tile_num + 1)
                self.status_update.emit(f"📸 Tile {tile_num + 1}/9 - Moving to position...")
                
                # Move to tile position
                self._move_to_tile(tile_pos)
                time.sleep(0.2)  # Settle time after XY move
                
                # Capture Z-stack for this tile
                z_frame_paths = []
                start_z = self.start_z  # Remember starting Z for this tile
                
                for z_idx in range(self.num_z_steps):
                    if self.should_abort:
                        self._cleanup_and_return("Operation aborted by user")
                        return
                    
                    self.status_update.emit(f"📸 Tile {tile_num + 1}/9 - Z {z_idx + 1}/{self.num_z_steps}")
                    
                    # Capture frame
                    frame = self.video_thread.get_current_frame()
                    
                    if frame is not None:
                        # Emit thumbnail
                        thumbnail = self._frame_to_pixmap(frame)
                        self.z_captured.emit(z_idx, thumbnail)
                        
                        # Save frame (convert RGB to BGR for OpenCV)
                        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        z_path = os.path.join(self.cache_dir, f"tile{tile_pos}_z{z_idx:02d}.png")
                        cv2.imwrite(z_path, frame_bgr)
                        z_frame_paths.append(z_path)
                    else:
                        self._cleanup_and_return("Video capture not available")
                        return
                    
                    captures_done += 1
                    # Progress: 80% for captures, 15% for stacking, 5% for final stitch
                    progress = int((captures_done / total_captures) * 80)
                    self.progress_update.emit(progress)
                    
                    # Move Z down for next level (except after last)
                    if z_idx < self.num_z_steps - 1:
                        self.motion.jog('z', -self.z_step)
                        time.sleep(0.12)
                
                # Return Z to starting position for next tile
                current_x, current_y, current_z, _ = self.motion.get_current_position()
                z_return = self.start_z - current_z
                if abs(z_return) > 0.01:
                    self.motion.jog('z', z_return)
                    time.sleep(0.15)
                
                if self.should_abort:
                    self._cleanup_and_return("Operation aborted by user")
                    return
                
                # Stack this tile's Z-frames
                self.status_update.emit(f"✨ Stacking tile {tile_num + 1}/9...")
                stacked_path = os.path.join(self.cache_dir, f"tile{tile_pos}_stacked.jpg")
                
                try:
                    cmd = [
                        "focus-stack",
                        f"--output={stacked_path}",
                        "--threads=2",
                        "--batchsize=4",
                        "--no-opencl",
                        "--consistency=1",
                        "--jpgquality=95",
                    ] + sorted(z_frame_paths)
                    print(f"[GigaTile{tile_pos}] Running: {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    
                    if result.returncode != 0:
                        error_msg = result.stderr if result.stderr else "Unknown error"
                        self._cleanup_and_return(f"Tile {tile_num + 1} stacking failed: {error_msg}")
                        return
                except subprocess.TimeoutExpired:
                    self._cleanup_and_return(f"Tile {tile_num + 1} stacking timed out")
                    return
                except Exception as e:
                    self._cleanup_and_return(f"Tile stacking error: {e}")
                    return
                
                # Clean up Z-frame files
                for path in z_frame_paths:
                    try:
                        os.remove(path)
                    except:
                        pass
                
                # Show stacked tile thumbnail
                stacked_img = cv2.imread(stacked_path)
                if stacked_img is not None:
                    stacked_rgb = cv2.cvtColor(stacked_img, cv2.COLOR_BGR2RGB)
                    h, w = stacked_rgb.shape[:2]
                    qimg = QImage(stacked_rgb.data, w, h, 3 * w, QImage.Format_RGB888)
                    self.tile_stacked.emit(tile_pos, QPixmap.fromImage(qimg))
                
                stacked_tile_paths.append((tile_pos, stacked_path))
                
                # Update progress for stacking phase
                stacking_progress = 80 + int(((tile_num + 1) / 9) * 15)
                self.progress_update.emit(stacking_progress)
            
            if self.should_abort:
                self._cleanup_and_return("Operation aborted by user")
                return
            
            # Return to center position
            self._move_to_tile(4)
            
            # Sort stacked tiles by position for stitching
            stacked_tile_paths.sort(key=lambda x: x[0])
            sorted_paths = [p[1] for p in stacked_tile_paths]
            
            # Final stitching of all 9 stacked tiles
            self.status_update.emit("🧵 Stitching tiles into panorama...")
            self.progress_update.emit(95)
            
            result_path = os.path.join(self.cache_dir, "giga_stacked.jpg")
            
            if not self._stitch_tiles(sorted_paths, result_path):
                self._cleanup_and_return("Failed to stitch tiles into panorama")
                return
            
            # Clean up stacked tile files
            for _, path in stacked_tile_paths:
                try:
                    os.remove(path)
                except:
                    pass
            
            self.status_update.emit("✨ Your giga crystal clear photo is ready!")
            self.progress_update.emit(100)
            time.sleep(0.5)
            self.finished_signal.emit(result_path, self.start_x, self.start_y, self.start_z)
            
        except Exception as e:
            self._cleanup_and_return(f"Unexpected error: {e}")
    
    def _cleanup_and_return(self, error_msg: str):
        """Clean up and emit error"""
        try:
            # Clean up any remaining files (stack-then-stitch naming)
            for pattern in ["tile*_z*.png", "tile*_stacked.jpg"]:
                for f in glob.glob(os.path.join(self.cache_dir, pattern)):
                    try:
                        os.remove(f)
                    except:
                        pass
        except:
            pass
        
        self.error_signal.emit(error_msg, self.start_x, self.start_y, self.start_z)


DEFAULT_TRAY_CONF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "default_tray.conf")

def get_default_tray_config() -> str:
    """Read the default tray config path from default_tray.conf"""
    if os.path.exists(DEFAULT_TRAY_CONF):
        with open(DEFAULT_TRAY_CONF, 'r') as f:
            path = f.read().strip()
            if path and os.path.exists(path):
                return path
    # Fallback: look for any .json file in the scope directory
    scope_dir = os.path.dirname(os.path.abspath(__file__))
    json_files = sorted(glob.glob(os.path.join(scope_dir, "*.json")))
    if json_files:
        return json_files[0]
    return None

def set_default_tray_config(path: str):
    """Write the default tray config path to default_tray.conf"""
    with open(DEFAULT_TRAY_CONF, 'w') as f:
        f.write(path + '\n')


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Robotic Microscope GUI")
    parser.add_argument("tray_config", nargs='?', default=None,
                       help="Path to tray configuration JSON file (optional, uses default_tray.conf)")
    parser.add_argument("--enable-save", action="store_true", 
                       help="Enable saving of stacked images (for private use)")
    
    args = parser.parse_args()
    
    # Determine tray config: CLI arg > default_tray.conf > first .json found
    tray_config = args.tray_config
    if not tray_config:
        tray_config = get_default_tray_config()
    if not tray_config:
        print("ERROR: No tray config JSON found. Provide one as argument or create default_tray.conf")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    window = MicroscopeGUI(tray_config, enable_save=args.enable_save)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
