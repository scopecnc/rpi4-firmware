#!/usr/bin/env python3
"""
LED Ring Controller - NeoPixel/WS2812B Ring Light Control
Controls 24-LED ring on GPIO10 (SPI MOSI) for specimen illumination

Note: Requires root permissions for GPIO access (run with sudo)
"""

import time
import threading
from typing import Optional, Callable
from colorsys import hsv_to_rgb

try:
    from rpi_ws281x import PixelStrip, Color
    LED_AVAILABLE = True
except ImportError:
    LED_AVAILABLE = False
    print("[LED] Warning: rpi_ws281x not installed - LED control disabled")


# Hardware Configuration
LED_COUNT = 24              # Number of LEDs in ring
LED_PIN = 10                # GPIO10 (Pin 19, SPI MOSI)
LED_FREQ_HZ = 800000        # Standard WS2812B frequency
LED_DMA = 5                 # DMA channel (avoid 10 - conflicts)
LED_INVERT = False          # No signal inversion

# Brightness limits (to prevent overheating)
MIN_BRIGHTNESS_PERCENT = 20
MAX_BRIGHTNESS_PERCENT = 70
DEFAULT_BRIGHTNESS_PERCENT = 40


class LEDRingController:
    """
    Controller for NeoPixel LED ring illumination.
    
    Manages brightness, transitions, and provides thread-safe access
    for GUI integration. Limits brightness to prevent overheating.
    """
    
    def __init__(self):
        """Initialize LED ring controller"""
        self.strip: Optional[PixelStrip] = None
        self.initialized = False
        self.current_brightness_percent = DEFAULT_BRIGHTNESS_PERCENT
        self._lock = threading.Lock()
        self._transition_thread: Optional[threading.Thread] = None
        self._stop_transition = False
        
        # Callbacks
        self.on_brightness_change: Optional[Callable[[int], None]] = None
        
    def initialize(self) -> bool:
        """
        Initialize the LED strip hardware.
        
        Returns:
            True if initialization successful, False otherwise
        """
        if not LED_AVAILABLE:
            print("[LED] Library not available - running in simulation mode")
            self.initialized = True  # Allow operation without hardware
            return True
        
        try:
            # Calculate initial brightness (0-255 from percentage)
            brightness = self._percent_to_brightness(self.current_brightness_percent)
            
            self.strip = PixelStrip(
                LED_COUNT,
                LED_PIN,
                LED_FREQ_HZ,
                LED_DMA,
                LED_INVERT,
                brightness
            )
            self.strip.begin()
            self.initialized = True
            print(f"[LED] Initialized - {LED_COUNT} LEDs on GPIO{LED_PIN}")
            
            # Set initial white light
            self.set_white()
            return True
            
        except Exception as e:
            print(f"[LED] Initialization failed: {e}")
            print("[LED] Continuing without LED control")
            self.initialized = True  # Allow GUI to work without LEDs
            return False
    
    def _percent_to_brightness(self, percent: int) -> int:
        """Convert percentage (20-70) to brightness value (0-255)"""
        # Clamp to valid range
        percent = max(MIN_BRIGHTNESS_PERCENT, min(MAX_BRIGHTNESS_PERCENT, percent))
        # Linear mapping: 20% -> 51, 70% -> 179
        return int((percent / 100.0) * 255)
    
    def _set_all_pixels(self, color: 'Color'):
        """Set all pixels to a color (internal)"""
        if self.strip:
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, color)
            self.strip.show()
    
    def set_brightness(self, percent: int, stop_transition: bool = False):
        """
        Set brightness level (20-70%).
        
        Args:
            percent: Brightness percentage (will be clamped to 20-70)
            stop_transition: If True, stop any ongoing rainbow transition
        """
        # Only stop transition if explicitly requested
        if stop_transition:
            self._stop_transition = True
        
        # Clamp to valid range
        percent = max(MIN_BRIGHTNESS_PERCENT, min(MAX_BRIGHTNESS_PERCENT, percent))
        self.current_brightness_percent = percent
        
        if self.strip:
            brightness = self._percent_to_brightness(percent)
            self.strip.setBrightness(brightness)
            # Only call show() if NO transition is running
            # This prevents flickering from concurrent show() calls
            if not self._is_transition_active():
                self.strip.show()
        
        print(f"[LED] Brightness set to {percent}%")
        
        if self.on_brightness_change:
            self.on_brightness_change(percent)
    
    def _is_transition_active(self) -> bool:
        """Check if a rainbow transition is currently running"""
        return (self._transition_thread is not None and 
                self._transition_thread.is_alive() and 
                not self._stop_transition)
    
    def get_brightness(self) -> int:
        """Get current brightness percentage"""
        return self.current_brightness_percent
    
    def set_white(self):
        """Set all LEDs to white at current brightness - stops any transition"""
        print("[LED] >>> set_white called")
        self._stop_transition = True
        # Wait for transition thread to notice and exit
        if self._transition_thread and self._transition_thread.is_alive():
            self._transition_thread.join(timeout=0.1)
        if self.strip:
            self._set_all_pixels(Color(255, 255, 255))
            print("[LED] set_white: pixels set and show() called")
        else:
            print("[LED] set_white: NO STRIP!")
        print("[LED] <<< set_white done")
    
    def turn_off(self):
        """Turn off all LEDs"""
        self._stop_transition = True
        if self._transition_thread and self._transition_thread.is_alive():
            self._transition_thread.join(timeout=0.1)
        if self.strip:
            self._set_all_pixels(Color(0, 0, 0))
        print("[LED] Turned off")
    
    def reset_to_default(self):
        """Reset brightness to default (40%) and set white"""
        self.set_brightness(DEFAULT_BRIGHTNESS_PERCENT)
        self.set_white()
        print("[LED] Reset to default")
    
    def start_rainbow_transition(self, on_complete: Optional[Callable] = None):
        """
        Start rainbow fade transition effect.
        All LEDs cycle through colors together during specimen transitions.
        
        Args:
            on_complete: Optional callback when transition completes (not used - runs until stopped)
        """
        print("[LED] Starting rainbow transition")
        self._stop_transition = False
        
        # Stop any existing transition thread
        if self._transition_thread and self._transition_thread.is_alive():
            self._stop_transition = True
            self._transition_thread.join(timeout=0.2)
            self._stop_transition = False
        
        # Start new rainbow thread
        self._transition_thread = threading.Thread(
            target=self._rainbow_transition_loop,
            args=(on_complete,),
            daemon=True
        )
        self._transition_thread.start()
    
    def stop_rainbow_transition(self):
        """Stop rainbow transition and return to white"""
        print("[LED] Stopping rainbow transition")
        self._stop_transition = True
        if self._transition_thread and self._transition_thread.is_alive():
            self._transition_thread.join(timeout=0.3)
        self.set_white()
        print("[LED] Returned to white")
    
    def set_blue(self):
        """Set all LEDs to blue at current brightness"""
        self._stop_transition = True
        if self.strip:
            self._set_all_pixels(Color(0, 0, 255))
            print("[LED] Set to blue")
    
    def _rainbow_transition_loop(self, on_complete: Optional[Callable]):
        """
        Rainbow fade effect - ALL LEDs fade through colors together.
        Runs continuously until stopped.
        
        Creates a smooth synchronized color fade across all LEDs.
        """
        print("[LED] Rainbow loop starting...")
        
        if not self.strip:
            # Simulation mode - just wait briefly
            print("[LED] No strip - simulation mode")
            time.sleep(0.5)
            if on_complete and not self._stop_transition:
                on_complete()
            return
        
        try:
            # Continuous rainbow fade - all LEDs same color, cycling through hues
            step_delay = 0.015  # ~15ms per step for smooth animation
            hue = 0
            loop_count = 0
            
            while not self._stop_transition:
                # All LEDs show the same color, cycling through the rainbow
                rgb = hsv_to_rgb(hue / 360.0, 1.0, 1.0)
                color = Color(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
                
                for i in range(self.strip.numPixels()):
                    self.strip.setPixelColor(i, color)
                self.strip.show()
                
                # Increment hue (0-359 degrees)
                hue = (hue + 3) % 360  # Faster cycling for more visible effect
                loop_count += 1
                time.sleep(step_delay)
            
            print(f"[LED] Rainbow loop exited (after {loop_count} loops)")
            
            # Transition stopped externally
            if on_complete and not self._stop_transition:
                on_complete()
                
        except Exception as e:
            print(f"[LED] Rainbow transition error: {e}")
            import traceback
            traceback.print_exc()
    
    def _wheel(self, pos: int) -> 'Color':
        """
        Generate rainbow colors across 0-255 positions.
        
        Args:
            pos: Position in color wheel (0-255)
            
        Returns:
            Color object for that position
        """
        if not LED_AVAILABLE:
            return None
            
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)
    
    def cleanup(self):
        """Clean up resources - call on application exit"""
        print("[LED] Cleaning up...")
        self._stop_transition = True
        
        if self._transition_thread and self._transition_thread.is_alive():
            self._transition_thread.join(timeout=1.0)
        
        self.turn_off()
        print("[LED] Cleanup complete")


# Singleton instance for global access
_led_controller: Optional[LEDRingController] = None


def get_led_controller() -> LEDRingController:
    """
    Get the global LED controller instance.
    
    Returns:
        LEDRingController singleton instance
    """
    global _led_controller
    if _led_controller is None:
        _led_controller = LEDRingController()
    return _led_controller
