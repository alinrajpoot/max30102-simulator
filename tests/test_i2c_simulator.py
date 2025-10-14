"""
Tests for I2C Protocol Simulator
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from protocols.i2c_simulator import I2CProtocolSimulator
from config.register_map import *

class TestI2CProtocolSimulator:
    """Test cases for I2CProtocolSimulator class"""
    
    def test_i2c_initialization(self):
        """Test I2C protocol simulator initialization"""
        i2c = I2CProtocolSimulator()
        
        assert i2c.device_address == 0x57
        assert i2c.i2c_bus_available == True
        assert len(i2c.registers) > 0
        assert i2c.fifo_size == 32
    
    def test_register_operations(self):
        """Test basic register read/write operations"""
        i2c = I2CProtocolSimulator()
        
        # Test successful write/read
        success = i2c.write_register(REG_LED1_PA, 0x24)
        assert success == True
        
        value = i2c.read_register(REG_LED1_PA)
        assert value == 0x24
        
        # Test failed operations
        i2c.set_bus_availability(False)
        success = i2c.write_register(REG_LED1_PA, 0x30)
        assert success == False
        
        value = i2c.read_register(REG_LED1_PA)
        assert value is None
        
        # Restore bus availability
        i2c.set_bus_availability(True)
    
    def test_burst_operations(self):
        """Test burst read/write operations"""
        i2c = I2CProtocolSimulator()
        
        # Test burst write
        registers_to_write = [REG_LED1_PA, REG_LED2_PA, REG_PILOT_PA]
        values_to_write = [0x20, 0x30, 0x40]
        
        success = i2c.write_registers_burst(REG_LED1_PA, values_to_write)
        assert success == True
        
        # Test burst read
        values_read = i2c.read_registers_burst(REG_LED1_PA, 3)
        assert values_read == values_to_write
    
    def test_fifo_operations(self):
        """Test FIFO buffer operations"""
        i2c = I2CProtocolSimulator()
        
        # Push samples to FIFO
        i2c.push_sample_to_fifo(10000, 9500)
        i2c.push_sample_to_fifo(11000, 10500)
        
        # Check FIFO status
        status = i2c.get_device_status()
        assert status['fifo_samples'] == 2
        
        # Read samples back
        samples = i2c.read_fifo_samples(2)
        assert len(samples) == 2
        assert samples[0] == (10000, 9500)
        assert samples[1] == (11000, 10500)
        
        # FIFO should be empty now
        status = i2c.get_device_status()
        assert status['fifo_samples'] == 0
    
    def test_fifo_overflow(self):
        """Test FIFO overflow handling"""
        i2c = I2CProtocolSimulator()
        
        # Fill FIFO beyond capacity
        for i in range(i2c.fifo_size + 5):
            i2c.push_sample_to_fifo(10000 + i, 9500 + i)
        
        # Should have overflow counter incremented
        assert i2c.registers[REG_OVF_COUNTER] > 0
        assert len(i2c.fifo_buffer) <= i2c.fifo_size
    
    def test_device_reset(self):
        """Test device reset via I2C command"""
        i2c = I2CProtocolSimulator()
        
        # Change some registers
        i2c.write_register(REG_LED1_PA, 0x30)
        i2c.write_register(REG_LED2_PA, 0x40)
        
        # Store original operation counts
        original_writes = i2c.write_operations
        
        # Perform reset
        i2c.write_register(REG_MODE_CONFIG, 0x40)  # Reset bit
        
        # Check registers reset to defaults
        assert i2c.registers[REG_LED1_PA] == DEFAULT_REGISTER_VALUES[REG_LED1_PA]
        assert i2c.registers[REG_LED2_PA] == DEFAULT_REGISTER_VALUES[REG_LED2_PA]
        
        # Check statistics reset
        assert i2c.write_operations == 0
        assert i2c.read_operations == 0
        assert i2c.errors == 0
    
    def test_communication_delay(self):
        """Test communication delay simulation"""
        i2c = I2CProtocolSimulator()
        
        import time
        
        # Set a measurable delay
        test_delay = 0.01  # 10ms
        i2c.set_communication_delay(test_delay)
        
        start_time = time.time()
        
        # Perform multiple operations
        for _ in range(5):
            i2c.write_register(REG_LED1_PA, 0x20)
            i2c.read_register(REG_LED1_PA)
        
        elapsed_time = time.time() - start_time
        
        # Should have taken at least the total delay time
        expected_min_time = 10 * test_delay  # 5 writes + 5 reads
        assert elapsed_time >= expected_min_time
    
    def test_sample_rate_configuration(self):
        """Test sample rate configuration via registers"""
        i2c = I2CProtocolSimulator()
        
        # Configure for 1000 samples/sec
        spo2_config = (SPO2_SR_1000 << 2) | (SPO2_ADC_RANGE_4096 << 5) | LED_PW_411
        i2c.write_register(REG_SPO2_CONFIG, spo2_config)
        
        status = i2c.get_device_status()
        assert status['sample_rate'] == 1000

if __name__ == "__main__":
    pytest.main([__file__, "-v"])