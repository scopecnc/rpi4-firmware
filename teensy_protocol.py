"""
Teensy 4.1 Motion Controller Protocol Layer
Low-level communication primitives for serial protocol
"""

import serial
import time
from typing import Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class MessageType(Enum):
    """Protocol message types"""
    COMMAND = '!'      # Master → Slave
    RESPONSE = '@'     # Slave → Master
    EVENT = '#'        # Slave → Master (unsolicited)


class ResponseType(Enum):
    """Response message types"""
    ACK = 'ACK'
    NACK = 'NACK'
    STATUS = 'STATUS'
    COMPLETE = 'COMPLETE'


@dataclass
class ProtocolMessage:
    """Parsed protocol message"""
    msg_type: MessageType
    content: str
    checksum: str
    valid: bool
    raw: str


class TeensyProtocol:
    """Low-level protocol handler for Teensy communication"""
    
    def __init__(self, port: str = '/dev/serial0', baudrate: int = 115200, timeout: float = 0.1):
        """
        Initialize protocol handler
        
        Args:
            port: Serial port device (default: /dev/serial0 for RPi GPIO UART)
            baudrate: Baud rate (default: 115200)
            timeout: Read timeout in seconds (default: 0.1)
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None
        self.connected = False
        self.quiet_mode = False  # Suppress debug output when True
        
    def open(self) -> bool:
        """
        Open serial connection
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            self.connected = True
            print(f"[Protocol] Opened {self.port} at {self.baudrate} baud")
            return True
        except Exception as e:
            print(f"[Protocol] Failed to open {self.port}: {e}")
            self.connected = False
            return False
    
    def close(self):
        """Close serial connection"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.connected = False
            print("[Protocol] Serial port closed")
    
    @staticmethod
    def calculate_checksum(message: str) -> str:
        """
        Calculate XOR checksum for protocol message
        
        Args:
            message: Message string (without checksum)
            
        Returns:
            2-digit hex checksum string
        """
        checksum = 0
        for char in message:
            checksum ^= ord(char)
        return f"{checksum:02X}"
    
    @staticmethod
    def add_checksum(message: str) -> str:
        """
        Add checksum to message
        
        Args:
            message: Message string (e.g., "!PING")
            
        Returns:
            Message with checksum (e.g., "!PING*1F\n")
        """
        checksum = TeensyProtocol.calculate_checksum(message)
        return f"{message}*{checksum}\n"
    
    @staticmethod
    def validate_message(line: str) -> Tuple[bool, str, str]:
        """
        Validate received message checksum
        
        Args:
            line: Received line including checksum
            
        Returns:
            Tuple of (valid, message_without_checksum, received_checksum)
        """
        line = line.strip()
        
        if '*' not in line:
            return False, line, ""
        
        message, checksum_part = line.rsplit('*', 1)
        message = message.rstrip()  # Remove trailing space before *
        received_checksum = checksum_part.strip().upper()
        calculated_checksum = TeensyProtocol.calculate_checksum(message)
        
        if received_checksum == calculated_checksum:
            return True, message, received_checksum
        else:
            return False, message, received_checksum
    
    def parse_message(self, line: str) -> ProtocolMessage:
        """
        Parse a received message
        
        Args:
            line: Raw line from serial
            
        Returns:
            ProtocolMessage object
        """
        valid, content, checksum = self.validate_message(line)
        
        if not content:
            return ProtocolMessage(
                msg_type=None,
                content="",
                checksum="",
                valid=False,
                raw=line
            )
        
        # Determine message type
        msg_type = None
        if content.startswith('!'):
            msg_type = MessageType.COMMAND
        elif content.startswith('@'):
            msg_type = MessageType.RESPONSE
        elif content.startswith('#'):
            msg_type = MessageType.EVENT
        
        return ProtocolMessage(
            msg_type=msg_type,
            content=content,
            checksum=checksum,
            valid=valid,
            raw=line.strip()
        )
    
    def send_command(self, command: str) -> bool:
        """
        Send a command to Teensy
        
        Args:
            command: Command string (e.g., "!PING")
            
        Returns:
            True if sent successfully
        """
        if not self.ser or not self.ser.is_open:
            print("[Protocol] Error: Serial port not open")
            return False
        
        try:
            message = self.add_checksum(command)
            self.ser.write(message.encode('utf-8'))
            self.ser.flush()
            if not self.quiet_mode:
                print(f"[TX] {message.strip()}")
            return True
        except Exception as e:
            print(f"[Protocol] Send error: {e}")
            return False
    
    def read_line(self, timeout: Optional[float] = None) -> Optional[ProtocolMessage]:
        """
        Read one line from serial
        
        Args:
            timeout: Optional timeout override (None uses default)
            
        Returns:
            ProtocolMessage if line received, None if timeout
        """
        if not self.ser or not self.ser.is_open:
            return None
        
        # Temporarily override timeout if specified
        original_timeout = self.ser.timeout
        if timeout is not None:
            self.ser.timeout = timeout
        
        try:
            if self.ser.in_waiting > 0 or timeout is not None:
                line = self.ser.readline().decode('utf-8', errors='ignore')
                if line:
                    msg = self.parse_message(line)
                    if not self.quiet_mode:
                        print(f"[RX] {msg.raw} {'✓' if msg.valid else '✗ CHECKSUM'}")
                    return msg
        except Exception as e:
            print(f"[Protocol] Read error: {e}")
        finally:
            # Restore original timeout
            if timeout is not None:
                self.ser.timeout = original_timeout
        
        return None
    
    def read_all_pending(self) -> list[ProtocolMessage]:
        """
        Read all pending messages from serial buffer
        
        Returns:
            List of ProtocolMessage objects
        """
        messages = []
        while self.ser and self.ser.in_waiting > 0:
            msg = self.read_line()
            if msg:
                messages.append(msg)
            else:
                break
        return messages
    
    def wait_for_boot(self, timeout: float = 5.0) -> bool:
        """
        Wait for #BOOT message from Teensy
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if BOOT received, False if timeout
        """
        print(f"[Protocol] Waiting for #BOOT message (timeout: {timeout}s)...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            msg = self.read_line(timeout=0.5)
            if msg and msg.valid and msg.msg_type == MessageType.EVENT:
                if 'BOOT' in msg.content:
                    print(f"[Protocol] Teensy ready: {msg.content}")
                    return True
            time.sleep(0.1)
        
        print("[Protocol] Timeout waiting for #BOOT")
        return False
    
    def flush_input(self):
        """Flush input buffer"""
        if self.ser and self.ser.is_open:
            self.ser.reset_input_buffer()
            print("[Protocol] Input buffer flushed")
    
    def flush_all(self):
        """Flush both input and output buffers"""
        if self.ser and self.ser.is_open:
            # Wait for any pending output to be transmitted
            self.ser.flush()
            # Clear input buffer
            self.ser.reset_input_buffer()
            print("[Protocol] Input/output buffers flushed")


# Test functions
def test_checksum():
    """Test checksum calculation"""
    print("\n=== Checksum Tests ===")
    
    test_cases = [
        ("!PING", "1F"),
        ("!MOVE X100 Y50", "3A"),
        ("@ACK 42 SLAVE=v1.2", "2F"),
    ]
    
    for message, expected in test_cases:
        calculated = TeensyProtocol.calculate_checksum(message)
        status = "✓" if calculated == expected else "✗"
        print(f"{status} '{message}' → *{calculated} (expected: *{expected})")


def test_message_parsing():
    """Test message parsing"""
    print("\n=== Message Parsing Tests ===")
    
    protocol = TeensyProtocol()
    
    test_messages = [
        "!PING *1F\n",
        "@ACK 42 *1F\n",
        "#BOOT FW=v1.2 AXES=4 *1E\n",
        "!PING *FF\n",  # Bad checksum
    ]
    
    for msg in test_messages:
        parsed = protocol.parse_message(msg)
        print(f"  {parsed.raw}")
        print(f"    Type: {parsed.msg_type}, Valid: {parsed.valid}, Content: {parsed.content}")


if __name__ == "__main__":
    print("Teensy Protocol Layer - Test Mode")
    test_checksum()
    test_message_parsing()
