"""
Tests for MAX30102 Device Simulator
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from simulator.max30102_device import MAX30102Device
from config.register_map import *

class TestMAX30102Device:
    """Test cases for MAX30102Device class"""
    
    def test_device_initialization(self):
        """Test device initialization with default registers"""
        device = MAX30102Device()
        
        # Check some key registers
        assert device.registers[REG_MODE_CONFIG] == MODE_SPO2
        assert device.registers[REG_PART_ID] == 0x15  # MAX30102 part ID
        assert device.registers[REG_REV_ID] == 0x02   # Revision ID
    
    def test_register_write_read(self):
        """Test basic register write and read operations"""
        device = MAX30102Device()
        
        # Test valid register write/read
        success = device.write_register(REG_LED1_PA, 0x20)
        assert success == True
        
        value = device.read_register(REG_LED1_PA)
        assert value == 0x20
        
        # Test invalid register
        success = device.write_register(0xFF, 0x10)  # Invalid register
        assert success == False
        
        value = device.read_register(0xFF)  # Invalid register
        assert value is None
    
    def test_fifo_operations(self):
        """Test FIFO buffer operations"""
        device = MAX30102Device()
        
        # Push samples to FIFO
        device.push_sample_to_fifo(10000, 9500)
        device.push_sample_to_fifo(11000, 10500)
        
        # Check FIFO status
        status = device.get_status()
        assert status['fifo_samples'] == 2
        
        # Test FIFO overflow
        for i in range(40):  # More than FIFO size
            device.push_sample_to_fifo(10000 + i, 9500 + i)
        
        status = device.get_status()
        assert status['fifo_samples'] <= device.fifo_size
        assert device.registers[REG_OVF_COUNTER] > 0  # Should have overflows
    
    def test_device_reset(self):
        """Test device reset functionality"""
        device = MAX30102Device()
        
        # Change some registers
        device.write_register(REG_LED1_PA, 0x30)
        device.write_register(REG_LED2_PA, 0x40)
        
        # Perform reset
        device.write_register(REG_MODE_CONFIG, 0x40)  # Reset bit
        
        # Check registers are back to defaults
        assert device.registers[REG_LED1_PA] == DEFAULT_REGISTER_VALUES[REG_LED1_PA]
        assert device.registers[REG_LED2_PA] == DEFAULT_REGISTER_VALUES[REG_LED2_PA]
        assert len(device.fifo_buffer) == 0
    
    def test_sample_rate_calculation(self):
        """Test sample rate calculation from configuration"""
        device = MAX30102Device()
        
        # Test different sample rate configurations
        sample_rates = [
            (SPO2_SR_50, 50),
            (SPO2_SR_100, 100),
            (SPO2_SR_200, 200),
            (SPO2_SR_400, 400),
            (SPO2_SR_800, 800),
            (SPO2_SR_1000, 1000),
        ]
        
        for sr_bits, expected_rate in sample_rates:
            # Configure sample rate
            spo2_config = (sr_bits << 2) | (SPO2_ADC_RANGE_4096 << 5) | LED_PW_411
            device.write_register(REG_SPO2_CONFIG, spo2_config)
            
            calculated_rate = device.get_sample_rate()
            assert calculated_rate == expected_rate
    
    def test_power_management(self):
        """Test device power on/off functionality"""
        device = MAX30102Device()
        
        # Initially should be powered on
        assert device.power_on == True
        
        # Turn off
        device.write_register(REG_MODE_CONFIG, 0x80)  # Shutdown bit
        assert device.power_on == False
        
        # Turn back on
        device.write_register(REG_MODE_CONFIG, MODE_SPO2)
        assert device.power_on == True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])