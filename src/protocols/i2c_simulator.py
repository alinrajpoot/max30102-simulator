import logging
import struct
import time
from typing import List, Optional, Tuple, Dict, Any
from ...config.register_map import *

class I2CProtocolSimulator:
    """
    Simulates I2C communication protocol for MAX30102 sensor.
    Handles register reads/writes, FIFO operations, and device communication.
    """
    
    def __init__(self, device_address: int = 0x57):
        self.device_address = device_address  # MAX30102 default I2C address
        self.registers = DEFAULT_REGISTER_VALUES.copy()
        self.fifo_buffer = []
        self.fifo_size = 32  # 32 samples in FIFO
        self.i2c_bus_available = True
        self.communication_delay = 0.001  # Simulate I2C communication delay
        
        # Statistics
        self.read_operations = 0
        self.write_operations = 0
        self.errors = 0
        
        self.setup_logging()
        self._initialize_device()
    
    def setup_logging(self):
        """Setup logging for I2C protocol simulator"""
        self.logger = logging.getLogger('I2CProtocol')
    
    def _initialize_device(self):
        """Initialize the MAX30102 device with default register values"""
        self.logger.info(f"Initializing I2C device at address 0x{self.device_address:02X}")
        
        # Clear FIFO
        self.fifo_buffer.clear()
        
        # Set default operating mode
        self.registers[REG_MODE_CONFIG] = MODE_SPO2
        self.registers[REG_SPO2_CONFIG] = 0x27  # 100 samples/sec, 4096 ADC range
        
        self.logger.info("I2C device initialized with default registers")
    
    def write_register(self, register: int, value: int) -> bool:
        """
        Simulate writing to a MAX30102 register over I2C
        
        Args:
            register: Register address to write to
            value: Value to write (0-255)
            
        Returns:
            bool: Success status
        """
        if not self.i2c_bus_available:
            self.logger.error("I2C bus not available")
            self.errors += 1
            return False
        
        if register not in self.registers:
            self.logger.warning(f"Attempt to write to invalid register: 0x{register:02X}")
            self.errors += 1
            return False
        
        try:
            # Simulate I2C communication delay
            time.sleep(self.communication_delay)
            
            # Handle special register behaviors
            if register == REG_MODE_CONFIG:
                self._handle_mode_config_write(value)
            elif register == REG_FIFO_CONFIG:
                self._handle_fifo_config_write(value)
            elif register == REG_FIFO_WR_PTR:
                self._handle_fifo_write_pointer(value)
            elif register == REG_FIFO_RD_PTR:
                self._handle_fifo_read_pointer(value)
            elif register == REG_SPO2_CONFIG:
                self._handle_spo2_config_write(value)
            else:
                # Normal register write
                self.registers[register] = value & 0xFF
            
            self.write_operations += 1
            self.logger.debug(f"I2C Write: REG[0x{register:02X}] = 0x{value:02X}")
            return True
            
        except Exception as e:
            self.logger.error(f"I2C write error: {e}")
            self.errors += 1
            return False
    
    def read_register(self, register: int) -> Optional[int]:
        """
        Simulate reading from a MAX30102 register over I2C
        
        Args:
            register: Register address to read from
            
        Returns:
            Optional[int]: Register value or None if error
        """
        if not self.i2c_bus_available:
            self.logger.error("I2C bus not available")
            self.errors += 1
            return None
        
        if register not in self.registers:
            self.logger.warning(f"Attempt to read from invalid register: 0x{register:02X}")
            self.errors += 1
            return None
        
        try:
            # Simulate I2C communication delay
            time.sleep(self.communication_delay)
            
            value = self.registers[register]
            
            # Handle special register behaviors
            if register == REG_FIFO_DATA:
                value = self._handle_fifo_data_read()
            elif register == REG_INTR_STATUS_1:
                value = self._handle_interrupt_status_read()
            
            self.read_operations += 1
            self.logger.debug(f"I2C Read: REG[0x{register:02X}] = 0x{value:02X}")
            return value
            
        except Exception as e:
            self.logger.error(f"I2C read error: {e}")
            self.errors += 1
            return None
    
    def read_registers_burst(self, start_register: int, count: int) -> Optional[List[int]]:
        """
        Simulate burst read of multiple registers over I2C
        
        Args:
            start_register: Starting register address
            count: Number of registers to read
            
        Returns:
            Optional[List[int]]: List of register values or None if error
        """
        if not self.i2c_bus_available:
            self.logger.error("I2C bus not available")
            self.errors += 1
            return None
        
        try:
            # Simulate I2C communication delay
            time.sleep(self.communication_delay * count)
            
            values = []
            for i in range(count):
                register = start_register + i
                if register in self.registers:
                    value = self.registers[register]
                    
                    # Handle special register behaviors for each register
                    if register == REG_FIFO_DATA:
                        value = self._handle_fifo_data_read()
                    
                    values.append(value)
                else:
                    self.logger.warning(f"Invalid register in burst read: 0x{register:02X}")
                    values.append(0x00)
            
            self.read_operations += 1  # Count as one operation
            self.logger.debug(f"I2C Burst Read: REG[0x{start_register:02X}], {count} bytes")
            return values
            
        except Exception as e:
            self.logger.error(f"I2C burst read error: {e}")
            self.errors += 1
            return None
    
    def write_registers_burst(self, start_register: int, values: List[int]) -> bool:
        """
        Simulate burst write to multiple registers over I2C
        
        Args:
            start_register: Starting register address
            values: List of values to write
            
        Returns:
            bool: Success status
        """
        if not self.i2c_bus_available:
            self.logger.error("I2C bus not available")
            self.errors += 1
            return False
        
        try:
            # Simulate I2C communication delay
            time.sleep(self.communication_delay * len(values))
            
            for i, value in enumerate(values):
                register = start_register + i
                if register in self.registers:
                    self.registers[register] = value & 0xFF
                    
                    # Handle special register behaviors
                    if register == REG_MODE_CONFIG:
                        self._handle_mode_config_write(value)
                    elif register == REG_FIFO_CONFIG:
                        self._handle_fifo_config_write(value)
                else:
                    self.logger.warning(f"Invalid register in burst write: 0x{register:02X}")
            
            self.write_operations += 1  # Count as one operation
            self.logger.debug(f"I2C Burst Write: REG[0x{start_register:02X}], {len(values)} bytes")
            return True
            
        except Exception as e:
            self.logger.error(f"I2C burst write error: {e}")
            self.errors += 1
            return False
    
    def push_sample_to_fifo(self, red_sample: int, ir_sample: int):
        """
        Push a new PPG sample to the FIFO buffer
        
        Args:
            red_sample: Red LED PPG sample (18-bit)
            ir_sample: IR LED PPG sample (18-bit)
        """
        # Convert 18-bit samples to 3-byte format
        red_bytes = [
            (red_sample >> 16) & 0x03,  # MSB (bits 17-16)
            (red_sample >> 8) & 0xFF,   # Middle byte (bits 15-8)
            red_sample & 0xFF           # LSB (bits 7-0)
        ]
        
        ir_bytes = [
            (ir_sample >> 16) & 0x03,   # MSB (bits 17-16)
            (ir_sample >> 8) & 0xFF,    # Middle byte (bits 15-8)
            ir_sample & 0xFF            # LSB (bits 7-0)
        ]
        
        sample_data = red_bytes + ir_bytes  # 6 bytes total per sample
        
        # Check FIFO overflow
        if len(self.fifo_buffer) >= self.fifo_size:
            self.registers[REG_OVF_COUNTER] = (self.registers[REG_OVF_COUNTER] + 1) & 0x1F
            if self.fifo_buffer:
                self.fifo_buffer.pop(0)  # Remove oldest sample
        
        # Add new sample to FIFO
        self.fifo_buffer.append(sample_data)
        
        # Update FIFO pointers and status
        self._update_fifo_pointers()
        
        # Set FIFO data ready interrupt
        if len(self.fifo_buffer) > 0:
            self.registers[REG_INTR_STATUS_1] |= 0x10  # Set FIFO almost full flag
    
    def read_fifo_samples(self, sample_count: int) -> List[Tuple[int, int]]:
        """
        Read samples from FIFO and convert back to 18-bit values
        
        Args:
            sample_count: Number of samples to read
            
        Returns:
            List of (red_sample, ir_sample) tuples
        """
        samples = []
        
        for _ in range(min(sample_count, len(self.fifo_buffer))):
            if self.fifo_buffer:
                sample_data = self.fifo_buffer.pop(0)
                
                # Convert 6 bytes back to two 18-bit samples
                red_sample = (sample_data[0] << 16) | (sample_data[1] << 8) | sample_data[2]
                ir_sample = (sample_data[3] << 16) | (sample_data[4] << 8) | sample_data[5]
                
                samples.append((red_sample, ir_sample))
        
        # Update FIFO pointers after reading
        self._update_fifo_pointers()
        
        return samples
    
    def _handle_mode_config_write(self, value: int):
        """Handle writes to MODE_CONFIG register"""
        if value & 0x40:  # Reset bit
            self._handle_device_reset()
        else:
            self.registers[REG_MODE_CONFIG] = value & 0x8F  # Clear reserved bits
            
            # Handle shutdown mode
            if value & 0x80:
                self.logger.info("Device entering shutdown mode")
            else:
                self.logger.info("Device exiting shutdown mode")
    
    def _handle_fifo_config_write(self, value: int):
        """Handle writes to FIFO_CONFIG register"""
        self.registers[REG_FIFO_CONFIG] = value & 0xFF
        
        # Extract FIFO averaging
        average_bits = (value >> 5) & 0x07
        averaging_map = {0: 1, 1: 2, 2: 4, 3: 8, 4: 16, 5: 32}
        self.averaging_samples = averaging_map.get(average_bits, 1)
        
        # Extract FIFO rollover
        self.fifo_rollover = bool(value & 0x10)
        
        self.logger.debug(f"FIFO config: averaging={self.averaging_samples}, rollover={self.fifo_rollover}")
    
    def _handle_spo2_config_write(self, value: int):
        """Handle writes to SPO2_CONFIG register"""
        self.registers[REG_SPO2_CONFIG] = value & 0xFC  # Clear reserved bits
        
        # Extract sample rate
        sr_bits = (value >> 2) & 0x07
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
        
        self.sample_rate = sample_rates.get(sr_bits, 100)
        self.logger.debug(f"SpO2 config: sample_rate={self.sample_rate}Hz")
    
    def _handle_fifo_write_pointer(self, value: int):
        """Handle writes to FIFO_WR_PTR register"""
        self.registers[REG_FIFO_WR_PTR] = value % (self.fifo_size * 6)
    
    def _handle_fifo_read_pointer(self, value: int):
        """Handle writes to FIFO_RD_PTR register"""
        self.registers[REG_FIFO_RD_PTR] = value % (self.fifo_size * 6)
    
    def _handle_fifo_data_read(self) -> int:
        """Handle reads from FIFO_DATA register"""
        if not self.fifo_buffer:
            return 0x00
        
        rd_ptr = self.registers[REG_FIFO_RD_PTR]
        wr_ptr = self.registers[REG_FIFO_WR_PTR]
        
        # Check if FIFO is empty
        if rd_ptr == wr_ptr and self.registers[REG_OVF_COUNTER] == 0:
            return 0x00
        
        # Calculate sample and byte indices
        sample_index = (rd_ptr // 6) % self.fifo_size
        byte_index = rd_ptr % 6
        
        if sample_index < len(self.fifo_buffer):
            value = self.fifo_buffer[sample_index][byte_index]
            
            # Advance read pointer
            self.registers[REG_FIFO_RD_PTR] = (rd_ptr + 1) % (self.fifo_size * 6)
            
            return value
        
        return 0x00
    
    def _handle_interrupt_status_read(self) -> int:
        """Handle reads from INTR_STATUS register"""
        value = self.registers[REG_INTR_STATUS_1]
        
        # Clear the status bits on read (simplified behavior)
        # In real device, specific bits are cleared by reading specific registers
        self.registers[REG_INTR_STATUS_1] = 0x00
        
        return value
    
    def _handle_device_reset(self):
        """Handle device reset"""
        self.logger.info("Performing device reset")
        
        # Reset all registers to default values
        self.registers = DEFAULT_REGISTER_VALUES.copy()
        
        # Clear FIFO
        self.fifo_buffer.clear()
        
        # Reset statistics
        self.read_operations = 0
        self.write_operations = 0
        self.errors = 0
        
        self.logger.info("Device reset complete")
    
    def _update_fifo_pointers(self):
        """Update FIFO write pointer based on current buffer state"""
        samples_in_fifo = len(self.fifo_buffer)
        self.registers[REG_FIFO_WR_PTR] = (samples_in_fifo * 6) % (self.fifo_size * 6)
        
        # Set/clear FIFO almost full flag
        fifo_almost_full_level = self.registers[REG_FIFO_CONFIG] & 0x0F
        
        if samples_in_fifo >= fifo_almost_full_level:
            self.registers[REG_INTR_STATUS_1] |= 0x10  # Set FIFO almost full
        else:
            self.registers[REG_INTR_STATUS_1] &= ~0x10  # Clear FIFO almost full
    
    def get_device_status(self) -> Dict[str, Any]:
        """
        Get current device status and statistics
        
        Returns:
            Dictionary with device status information
        """
        return {
            'device_address': f"0x{self.device_address:02X}",
            'fifo_samples': len(self.fifo_buffer),
            'sample_rate': getattr(self, 'sample_rate', 100),
            'averaging_samples': getattr(self, 'averaging_samples', 1),
            'fifo_rollover': getattr(self, 'fifo_rollover', True),
            'read_operations': self.read_operations,
            'write_operations': self.write_operations,
            'error_count': self.errors,
            'operating_mode': self.registers[REG_MODE_CONFIG] & 0x07,
            'power_state': 'shutdown' if (self.registers[REG_MODE_CONFIG] & 0x80) else 'active'
        }
    
    def set_communication_delay(self, delay: float):
        """
        Set the simulated I2C communication delay
        
        Args:
            delay: Delay in seconds
        """
        self.communication_delay = max(0.0, delay)
        self.logger.debug(f"I2C communication delay set to {delay:.4f}s")
    
    def set_bus_availability(self, available: bool):
        """
        Set I2C bus availability
        
        Args:
            available: Whether the I2C bus is available
        """
        self.i2c_bus_available = available
        status = "available" if available else "unavailable"
        self.logger.debug(f"I2C bus set to {status}")