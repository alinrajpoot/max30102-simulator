import time
import logging
from typing import Dict, List, Optional, Tuple
from ...config.register_map import *

class MAX30102Device:
    """
    MAX30102 device simulator that mimics register-level communication
    and maintains device state.
    """
    
    def __init__(self):
        self.registers = DEFAULT_REGISTER_VALUES.copy()
        self.fifo_buffer = []
        self.fifo_size = 32  # 32-sample FIFO
        self.sample_count = 0
        self.temperature = 37.0  # Default body temperature
        
        # Device state
        self.power_on = True
        self.reset_pending = False
        
        self.setup_logging()
        self.initialize_device()
    
    def setup_logging(self):
        """Setup logging for the device"""
        self.logger = logging.getLogger('MAX30102Device')
    
    def initialize_device(self):
        """Initialize the device with default settings"""
        self.logger.info("Initializing MAX30102 simulator")
        self._update_fifo_pointers()
    
    def write_register(self, register: int, value: int) -> bool:
        """
        Write a value to a device register
        
        Args:
            register: Register address to write to
            value: Value to write
            
        Returns:
            bool: Success status
        """
        if register not in DEFAULT_REGISTER_VALUES:
            self.logger.warning(f"Attempt to write to invalid register: 0x{register:02X}")
            return False
        
        # Handle special register behaviors
        if register == REG_MODE_CONFIG:
            if value & 0x40:  # Reset bit
                self._handle_reset()
                return True
            if value & 0x80:  # Shutdown bit
                self.power_on = not bool(value & 0x80)
        
        elif register == REG_FIFO_CONFIG:
            # Update FIFO configuration
            self._update_fifo_config(value)
        
        self.registers[register] = value & 0xFF
        self.logger.debug(f"Write register 0x{register:02X} = 0x{value:02X}")
        return True
    
    def read_register(self, register: int) -> Optional[int]:
        """
        Read a value from a device register
        
        Args:
            register: Register address to read from
            
        Returns:
            Optional[int]: Register value or None if invalid register
        """
        if register == REG_FIFO_DATA:
            return self._read_fifo_data()
        
        if register not in self.registers:
            self.logger.warning(f"Attempt to read from invalid register: 0x{register:02X}")
            return None
        
        value = self.registers[register]
        self.logger.debug(f"Read register 0x{register:02X} = 0x{value:02X}")
        return value
    
    def read_fifo_burst(self, count: int) -> List[int]:
        """
        Read multiple samples from FIFO in burst mode
        
        Args:
            count: Number of samples to read
            
        Returns:
            List[int]: FIFO data bytes
        """
        data = []
        for _ in range(min(count, len(self.fifo_buffer))):
            if self.fifo_buffer:
                sample = self.fifo_buffer.pop(0)
                data.extend(sample)
                self._update_fifo_pointers()
        
        return data
    
    def push_sample_to_fifo(self, red_sample: int, ir_sample: int):
        """
        Push a new sample to the FIFO buffer
        
        Args:
            red_sample: Red LED sample value
            ir_sample: IR LED sample value
        """
        if len(self.fifo_buffer) >= self.fifo_size:
            # FIFO overflow
            self.registers[REG_OVF_COUNTER] = (self.registers[REG_OVF_COUNTER] + 1) & 0x1F
            if self.fifo_buffer:
                self.fifo_buffer.pop(0)
        
        # Convert samples to 3-byte format (18-bit samples)
        sample_bytes = [
            (red_sample >> 16) & 0x03,
            (red_sample >> 8) & 0xFF,
            red_sample & 0xFF,
            (ir_sample >> 16) & 0x03,
            (ir_sample >> 8) & 0xFF,
            ir_sample & 0xFF
        ]
        
        self.fifo_buffer.append(sample_bytes)
        self._update_fifo_pointers()
        self.sample_count += 1
    
    def _read_fifo_data(self) -> Optional[int]:
        """Read one byte from FIFO data register"""
        if not self.fifo_buffer:
            return 0x00
        
        # FIFO data register cycles through the 6 bytes of the current sample
        rd_ptr = self.registers[REG_FIFO_RD_PTR]
        wr_ptr = self.registers[REG_FIFO_WR_PTR]
        
        if rd_ptr == wr_ptr and self.registers[REG_OVF_COUNTER] == 0:
            return 0x00  # FIFO empty
        
        sample_index = (rd_ptr // 6) % self.fifo_size
        byte_index = rd_ptr % 6
        
        if sample_index < len(self.fifo_buffer):
            value = self.fifo_buffer[sample_index][byte_index]
            
            # Advance read pointer
            self.registers[REG_FIFO_RD_PTR] = (rd_ptr + 1) % (self.fifo_size * 6)
            
            return value
        
        return 0x00
    
    def _update_fifo_pointers(self):
        """Update FIFO write and read pointers"""
        samples_in_fifo = len(self.fifo_buffer)
        self.registers[REG_FIFO_WR_PTR] = (samples_in_fifo * 6) % (self.fifo_size * 6)
        
        # Calculate available samples
        available_samples = samples_in_fifo
        if available_samples > 0:
            self.registers[REG_INTR_STATUS_1] |= 0x10  # Set FIFO almost full flag
        else:
            self.registers[REG_INTR_STATUS_1] &= ~0x10
    
    def _update_fifo_config(self, config: int):
        """Update FIFO configuration based on register value"""
        # Extract FIFO averaging
        average_bits = (config >> 5) & 0x07
        averaging_map = {0: 1, 1: 2, 2: 4, 3: 8, 4: 16, 5: 32}
        self.averaging = averaging_map.get(average_bits, 1)
        
        # Extract FIFO rollover
        self.fifo_rollover = bool(config & 0x10)
        
    def _handle_reset(self):
        """Handle device reset"""
        self.logger.info("Device reset triggered")
        self.registers = DEFAULT_REGISTER_VALUES.copy()
        self.fifo_buffer.clear()
        self.sample_count = 0
        self._update_fifo_pointers()
        self.reset_pending = True
    
    def get_status(self) -> Dict[str, any]:
        """Get current device status"""
        return {
            'power_on': self.power_on,
            'fifo_samples': len(self.fifo_buffer),
            'sample_count': self.sample_count,
            'temperature': self.temperature,
            'mode': self.registers[REG_MODE_CONFIG] & 0x07
        }
    
    def get_sample_rate(self) -> int:
        """Calculate current sample rate based on configuration"""
        spo2_config = self.registers[REG_SPO2_CONFIG]
        sr_bits = (spo2_config >> 2) & 0x07
        
        sample_rates = {
            SPO2_SR_50: 50,
            SPO2_SR_100: 100,
            SPO2_SR_200: 200,
            SPO2_SR_400: 400,
            SPO2_SR_800: 800,
            SPO2_SR_1000: 1000,
            SPO2_SR_1600: 1600,
            SPO2_SR_3200: 3200
        }
        
        return sample_rates.get(sr_bits, 100)