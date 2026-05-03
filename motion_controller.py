#!/usr/bin/env python3
"""
Motion Controller - High-level wrapper around teensy_protocol
Handles connection, watchdog, auto-cycle logic, and position tracking
"""

import time
import threading
from typing import Optional, Tuple, Callable
from teensy_protocol import TeensyProtocol
from specimen_grid import SpecimenGrid, SpecimenPosition


class MotionController:
    """High-level motion controller with auto-cycle support"""
    
    def __init__(self, tray_config_path: str):
        """Initialize motion controller
        
        Args:
            tray_config_path: Path to specimen tray JSON configuration
        """
        self.protocol = TeensyProtocol()
        self.grid = SpecimenGrid(tray_config_path)
        
        # Connection state
        self.connected = False
        self.homed = False
        self.current_state = "DISCONNECTED"
        
        # Position tracking
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = 0.0
        self.current_f = 0.0
        
        # Auto-cycle state
        self.auto_cycle_enabled = True
        self.auto_cycle_paused = False  # Explicit pause for long operations
        self.current_specimen_index = 0
        self.last_user_interaction = time.time()
        self.user_interaction_timeout = 30.0  # seconds
        self.specimen_view_duration = 15.0  # seconds per specimen
        self.last_specimen_change = time.time()
        
        # Threading
        self.watchdog_thread = None
        self.auto_cycle_thread = None
        self.running = False
        self.watchdog_paused = False  # Allow pausing watchdog for diagnostics
        
        # Callbacks
        self.on_position_update: Optional[Callable] = None
        self.on_state_change: Optional[Callable] = None
        self.on_specimen_change: Optional[Callable] = None
        self.on_limit_hit: Optional[Callable] = None  # Called when soft/hard limit blocks movement
        self.is_homing = False  # Suppress limit warnings during homing
        self.on_auto_transition_start: Optional[Callable] = None  # Called when auto-cycle moves begin
        self.on_auto_transition_end: Optional[Callable] = None    # Called when auto-cycle moves complete
        
    def connect(self) -> bool:
        """Connect to Teensy and establish protocol connection
        
        Returns:
            True if connection successful
        """
        # Open serial port
        if not self.protocol.open():
            return False
        
        # Flush any stale messages
        self.protocol.flush_all()
        time.sleep(0.1)
        
        # Send CONNECT command
        if not self.protocol.send_command("!CONNECT MASTER=GUI_v1.0"):
            return False
        
        # Wait for ACK
        time.sleep(0.3)
        response = self.protocol.read_line(timeout=2.0)
        if not response or not response.valid or 'ACK' not in response.content:
            return False
        
        self.connected = True
        self.current_state = "CONNECTED"
        
        # Start watchdog thread
        self.running = True
        self.watchdog_thread = threading.Thread(target=self._watchdog_loop, daemon=True)
        self.watchdog_thread.start()
        
        if self.on_state_change:
            self.on_state_change("CONNECTED")
        
        return True
    
    def disconnect(self):
        """Disconnect from Teensy"""
        self.running = False
        
        if self.watchdog_thread:
            self.watchdog_thread.join(timeout=1.0)
        
        if self.auto_cycle_thread:
            self.auto_cycle_thread.join(timeout=1.0)
        
        self.protocol.close()
        self.connected = False
        self.current_state = "DISCONNECTED"
        
        if self.on_state_change:
            self.on_state_change("DISCONNECTED")
    
    def home(self, progress_callback: Optional[Callable[[str], None]] = None,
             idle_callback: Optional[Callable[[], None]] = None) -> bool:
        """Home all axes using fast parallel homing
        
        Args:
            progress_callback: Optional callback for progress updates (called at start/end)
            idle_callback: Optional callback called during wait loop (~every 0.5s)
                          Use this to keep GUI responsive (e.g., QApplication.processEvents)
            
        Returns:
            True if homing successful
        """
        if not self.connected:
            return False
        
        if progress_callback:
            progress_callback("Homing all axes...")
        
        self.is_homing = True
        
        # Send HOME_FAST command
        if not self.protocol.send_command("!HOME_FAST"):
            self.is_homing = False
            return False
        
        # Wait for completion
        time.sleep(0.5)
        start_time = time.time()
        timeout = 120.0
        last_ping = time.time()
        
        while time.time() - start_time < timeout:
            # Call idle callback to keep caller responsive (e.g., GUI event processing)
            if idle_callback:
                idle_callback()
            
            # Send periodic ping to prevent watchdog timeout
            if time.time() - last_ping > 2.0:
                self.protocol.send_command("!PING")
                last_ping = time.time()
            
            msg = self.protocol.read_line(timeout=0.5)
            if msg and msg.valid:
                print(f"DEBUG home msg: '{msg.content}'")
                # Check for various completion messages
                if 'COMPLETE' in msg.content or 'HOME_DONE' in msg.content or 'HOMING_COMPLETE' in msg.content:
                    print("DEBUG: Homing complete detected!")
                    self.homed = True
                    self.is_homing = False
                    self.current_x = 0.0
                    self.current_y = 0.0
                    self.current_z = 0.0
                    self.current_f = 0.0
                    self.current_state = "IDLE"
                    
                    if progress_callback:
                        progress_callback("Homing complete")
                    if self.on_position_update:
                        self.on_position_update(0.0, 0.0, 0.0, 0.0)
                    if self.on_state_change:
                        self.on_state_change("IDLE")
                    
                    return True
                elif 'COMM_LOST' in msg.content or 'BOOT' in msg.content:
                    self.is_homing = False
                    if progress_callback:
                        progress_callback("Connection lost during homing")
                    return False
        
        self.is_homing = False
        if progress_callback:
            progress_callback("Homing timeout")
        return False
    
    def move_to_position(self, x: float, y: float, z: float, f: float) -> bool:
        """Move to absolute position
        
        Args:
            x, y, z, f: Target positions in mm
            
        Returns:
            True if move successful
        """
        if not self.connected or not self.homed:
            return False
        
        # Validate position
        valid, error_msg = self.grid.validate_position(x, y, z, f)
        if not valid:
            print(f"Position validation failed: {error_msg}")
            return False
        
        # Send move command
        move_cmd = f"!MOVE X{x:.2f} Y{y:.2f} Z{z:.2f} F{f:.2f}"
        if not self.protocol.send_command(move_cmd):
            return False
        
        # Wait for ACK
        time.sleep(0.2)
        ack_msg = self.protocol.read_line(timeout=2.0)
        if not ack_msg or not ack_msg.valid or 'ACK' not in ack_msg.content:
            return False
        
        self.current_state = "MOVING"
        if self.on_state_change:
            self.on_state_change("MOVING")
        
        # Wait for completion
        start_time = time.time()
        timeout = 30.0
        last_ping = time.time()
        
        while time.time() - start_time < timeout:
            # Send periodic ping
            if time.time() - last_ping > 2.0:
                self.protocol.send_command("!PING")
                last_ping = time.time()
            
            msg = self.protocol.read_line(timeout=0.5)
            if msg and msg.valid:
                if 'COMPLETE' in msg.content:
                    self.current_x = x
                    self.current_y = y
                    self.current_z = z
                    self.current_f = f
                    self.current_state = "IDLE"
                    
                    if self.on_position_update:
                        self.on_position_update(x, y, z, f)
                    if self.on_state_change:
                        self.on_state_change("IDLE")
                    
                    return True
                elif 'COMM_LOST' in msg.content or 'BOOT' in msg.content:
                    return False
        
        return False
    
    def move_to_specimen(self, index: int) -> bool:
        """Move to specimen by index
        
        Args:
            index: Specimen index (0-based)
            
        Returns:
            True if move successful
        """
        specimens = list(self.grid.get_specimens())
        if index < 0 or index >= len(specimens):
            return False
        
        specimen = specimens[index]
        x, y, z, f = self.grid.calculate_position(specimen)
        
        if self.move_to_position(x, y, z, f):
            self.current_specimen_index = index
            if self.on_specimen_change:
                self.on_specimen_change(index, specimen)
            return True
        
        return False
    
    def jog(self, axis: str, distance: float) -> bool:
        """Jog axis by relative distance
        
        Args:
            axis: 'X', 'Y', 'Z', or 'F'
            distance: Relative distance in mm
            
        Returns:
            True if jog successful (COMPLETE received with position)
        """
        if not self.connected or not self.homed:
            return False
        
        # Pre-check soft limits
        target_x = self.current_x + (distance if axis.upper() == 'X' else 0)
        target_y = self.current_y + (distance if axis.upper() == 'Y' else 0)
        target_z = self.current_z + (distance if axis.upper() == 'Z' else 0)
        target_f = self.current_f + (distance if axis.upper() == 'F' else 0)
        
        valid, error_msg = self.grid.validate_position(target_x, target_y, target_z, target_f)
        if not valid:
            print(f"[Jog] Soft limit: {error_msg}")
            if self.on_limit_hit and not self.is_homing:
                self.on_limit_hit()
            return False
        
        # Send jog command
        jog_cmd = f"!JOG {axis} {distance:.2f}"
        if not self.protocol.send_command(jog_cmd):
            return False
        
        # Wait for JOG-specific ACK (contains "JOGGING")
        # Skip any PING ACKs that may be in the buffer
        start_time = time.time()
        timeout = 1.0
        
        while time.time() - start_time < timeout:
            msg = self.protocol.read_line(timeout=0.2)
            if not msg:
                continue
            
            if not msg.valid:
                print(f"[Jog] Checksum error: {msg.raw}")
                continue
            
            if 'NACK' in msg.content:
                print(f"[Jog] Command rejected: {msg.content}")
                if self.on_limit_hit and not self.is_homing:
                    self.on_limit_hit()
                return False
            
            # Look for JOGGING ACK specifically (skip PING ACKs)
            if 'JOGGING' in msg.content:
                # Got our ACK, now wait for COMPLETE
                break
            
            # Skip other ACKs (likely PING responses)
            if 'ACK' in msg.content and 'UPTIME' in msg.content:
                continue
        else:
            print(f"[Jog] Timeout waiting for JOGGING ACK")
            return False
        
        # Wait for COMPLETE with position
        # Larger jogs take longer - scale timeout with distance
        start_time = time.time()
        timeout = 3.0  # Increased from 1.0s to handle larger jogs (e.g., 5mm)
        
        while time.time() - start_time < timeout:
            msg = self.protocol.read_line(timeout=0.2)
            if not msg:
                continue
            
            if not msg.valid:
                print(f"[Jog] Checksum error in response: {msg.raw}")
                continue
            
            if 'COMPLETE' in msg.content:
                # Parse position from COMPLETE: @COMPLETE <seq> X=# Y=# Z=# F=#
                pos = self._parse_position(msg.content)
                if pos:
                    self.current_x = pos['X']
                    self.current_y = pos['Y']
                    self.current_z = pos['Z']
                    self.current_f = pos['F']
                    
                    if self.on_position_update:
                        self.on_position_update(self.current_x, self.current_y,
                                               self.current_z, self.current_f)
                    return True
                else:
                    print(f"[Jog] COMPLETE received but couldn't parse position: {msg.content}")
                    return False
            
            elif 'NACK' in msg.content:
                print(f"[Jog] Motion failed: {msg.content}")
                if self.on_limit_hit and not self.is_homing:
                    self.on_limit_hit()
                return False
        
        print(f"[Jog] Timeout waiting for COMPLETE")
        return False
    
    def _parse_position(self, content: str) -> Optional[dict]:
        """Parse position from a message containing X=# Y=# Z=# F=#
        
        Returns:
            Dict with X, Y, Z, F keys if all found, None otherwise
        """
        try:
            pos = {}
            parts = content.split()
            for part in parts:
                if '=' in part:
                    key, val = part.split('=', 1)
                    if key in ['X', 'Y', 'Z', 'F']:
                        pos[key] = float(val)
            
            if 'X' in pos and 'Y' in pos and 'Z' in pos and 'F' in pos:
                return pos
        except Exception as e:
            print(f"[Parse] Error parsing position: {e}")
        
        return None
    
    def mark_user_interaction(self):
        """Mark that user has interacted (pauses auto-cycle for 30s)"""
        self.last_user_interaction = time.time()
    
    def pause_auto_cycle(self):
        """Explicitly pause auto-cycle (for long operations like focus stacking)"""
        self.auto_cycle_paused = True
    
    def resume_auto_cycle(self):
        """Resume auto-cycle after explicit pause, resetting user interaction timer"""
        self.auto_cycle_paused = False
        self.mark_user_interaction()  # Give user 30s before resuming
    
    def start_auto_cycle(self):
        """Start auto-cycle thread"""
        if not self.auto_cycle_thread or not self.auto_cycle_thread.is_alive():
            self.auto_cycle_enabled = True
            self.auto_cycle_thread = threading.Thread(target=self._auto_cycle_loop, daemon=True)
            self.auto_cycle_thread.start()
    
    def stop_auto_cycle(self):
        """Stop auto-cycle"""
        self.auto_cycle_enabled = False
    
    def _watchdog_loop(self):
        """Watchdog thread - sends PING every 2 seconds"""
        while self.running:
            time.sleep(2.0)
            if self.connected and not self.watchdog_paused:
                self.protocol.send_command("!PING")
    
    def _auto_cycle_loop(self):
        """Auto-cycle thread - cycles through specimens"""
        while self.running and self.auto_cycle_enabled:
            time.sleep(0.5)  # Check every 500ms
            
            if not self.connected or not self.homed:
                continue
            
            # Skip if explicitly paused (for long operations like focus stacking)
            if self.auto_cycle_paused:
                continue
            
            # Skip if no specimens loaded
            specimen_count = self.grid.get_specimen_count()
            if specimen_count == 0:
                continue  # No specimens to cycle through
            
            # Check if user has interacted recently
            time_since_interaction = time.time() - self.last_user_interaction
            if time_since_interaction < self.user_interaction_timeout:
                continue  # User is in control
            
            # Check if it's time to move to next specimen
            time_at_specimen = time.time() - self.last_specimen_change
            if time_at_specimen >= self.specimen_view_duration:
                # Move to next specimen
                next_index = (self.current_specimen_index + 1) % specimen_count
                
                # Signal transition start (for LED effect)
                transition_start_time = time.time()
                print(f"[AUTO] Starting transition to specimen {next_index}")
                if self.on_auto_transition_start:
                    self.on_auto_transition_start()
                
                # Brief delay for LED to start rainbow
                time.sleep(0.1)
                
                # Try up to specimen_count times to find a valid specimen
                attempts = 0
                while attempts < specimen_count:
                    if self.move_to_specimen(next_index):
                        self.last_specimen_change = time.time()
                        # Signal transition end (return to white LED)
                        transition_duration = time.time() - transition_start_time
                        print(f"[AUTO] Transition complete after {transition_duration:.2f}s")
                        if self.on_auto_transition_end:
                            self.on_auto_transition_end()
                        break  # Success
                    else:
                        # Skip this specimen and try next
                        print(f"Skipping specimen {next_index} (out of bounds)")
                        next_index = (next_index + 1) % specimen_count
                        attempts += 1
                else:
                    # All attempts failed, still signal end
                    transition_duration = time.time() - transition_start_time
                    print(f"[AUTO] All attempts failed after {transition_duration:.2f}s")
                    if self.on_auto_transition_end:
                        self.on_auto_transition_end()
    
    def get_specimen_count(self) -> int:
        """Get total number of specimens"""
        return self.grid.get_specimen_count()
    
    def get_specimen(self, index: int) -> Optional[SpecimenPosition]:
        """Get specimen by index"""
        specimens = list(self.grid.get_specimens())
        if 0 <= index < len(specimens):
            return specimens[index]
        return None
    
    def get_all_specimens(self) -> list:
        """Get all specimens"""
        return list(self.grid.get_specimens())
    
    def get_current_position(self) -> Tuple[float, float, float, float]:
        """Get current position (X, Y, Z, F)"""
        return (self.current_x, self.current_y, self.current_z, self.current_f)
    
    def is_auto_mode(self) -> bool:
        """Check if in auto-cycle mode (no recent user interaction)"""
        time_since_interaction = time.time() - self.last_user_interaction
        return time_since_interaction >= self.user_interaction_timeout
