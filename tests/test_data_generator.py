"""
Tests for Data Generator
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from simulator.data_generator import DataGenerator
from models.physiological_model import PhysiologicalModel

class TestDataGenerator:
    """Test cases for DataGenerator class"""
    
    def test_data_generator_initialization(self):
        """Test data generator initialization"""
        physio_model = PhysiologicalModel()
        generator = DataGenerator(physio_model)
        
        assert generator.physio_model == physio_model
        assert generator.sample_rate == 1000
        assert generator.time_index == 0.0
    
    def test_data_point_generation(self):
        """Test generating individual data points"""
        physio_model = PhysiologicalModel()
        generator = DataGenerator(physio_model)
        
        data_point = generator.generate_data_point()
        
        # Check required fields
        assert 'timestamp' in data_point
        assert 'red_ppg' in data_point
        assert 'ir_ppg' in data_point
        assert 'heart_rate' in data_point
        assert 'spO2' in data_point
        assert 'activity' in data_point
        assert 'condition' in data_point
        
        # Check data types and reasonable ranges
        assert isinstance(data_point['red_ppg'], int)
        assert isinstance(data_point['ir_ppg'], int)
        assert isinstance(data_point['heart_rate'], float)
        assert isinstance(data_point['spO2'], float)
        
        # PPG values should be positive
        assert data_point['red_ppg'] > 0
        assert data_point['ir_ppg'] > 0
        
        # Heart rate should be in physiological range
        assert 30 <= data_point['heart_rate'] <= 220
        
        # SpO2 should be in reasonable range
        assert 70 <= data_point['spO2'] <= 100
    
    def test_ppg_waveform_generation(self):
        """Test PPG waveform generation"""
        physio_model = PhysiologicalModel()
        generator = DataGenerator(physio_model)
        
        # Generate multiple samples to check waveform pattern
        samples_red = []
        samples_ir = []
        
        for _ in range(100):  # Generate 100 samples
            data_point = generator.generate_data_point()
            samples_red.append(data_point['red_ppg'])
            samples_ir.append(data_point['ir_ppg'])
        
        # Should have some variation (not constant)
        assert len(set(samples_red)) > 1
        assert len(set(samples_ir)) > 1
        
        # Red and IR should be correlated but not identical
        assert samples_red != samples_ir
    
    def test_motion_artifact_simulation(self):
        """Test motion artifact generation"""
        physio_model = PhysiologicalModel()
        
        # Set high probability for motion artifacts
        physio_model.update_parameters({
            'motion_artifact_probability': 1.0,
            'noise_level': 0.01  # Low noise to see artifacts clearly
        })
        
        generator = DataGenerator(physio_model)
        
        # Generate samples and check for artifacts
        samples_with_artifacts = 0
        baseline_red = generator.baseline_red
        
        for _ in range(200):  # Generate enough samples to likely get artifacts
            data_point = generator.generate_data_point()
            red_ppg = data_point['red_ppg']
            
            # Check for significant deviation from baseline (possible artifact)
            if abs(red_ppg - baseline_red) > generator.pulse_amplitude_red * 0.3:
                samples_with_artifacts += 1
        
        # Should have detected some motion artifacts
        assert samples_with_artifacts > 0
    
    def test_noise_addition(self):
        """Test that noise is properly added to signals"""
        physio_model = PhysiologicalModel()
        
        # Set specific noise level
        physio_model.update_parameters({
            'noise_level': 0.1
        })
        
        generator = DataGenerator(physio_model)
        
        # Generate multiple samples with same parameters
        samples = []
        for _ in range(50):
            data_point = generator.generate_data_point()
            samples.append(data_point['red_ppg'])
        
        # Should have variation due to noise
        sample_variance = max(samples) - min(samples)
        assert sample_variance > 0
    
    def test_vital_sign_calculation(self):
        """Test heart rate and SpO2 calculation"""
        physio_model = PhysiologicalModel()
        generator = DataGenerator(physio_model)
        
        # Test with known parameters
        test_hr = 80.0
        test_spo2 = 97.5
        
        physio_model.update_parameters({
            'heart_rate_bpm': test_hr,
            'spo2_percent': test_spo2
        })
        
        data_point = generator.generate_data_point()
        
        # Calculated values should be close to model values
        assert abs(data_point['heart_rate'] - test_hr) < 10  # Allow some variation
        assert abs(data_point['spO2'] - test_spo2) < 5       # Allow some variation
    
    def test_sample_rate_configuration(self):
        """Test sample rate configuration"""
        physio_model = PhysiologicalModel()
        generator = DataGenerator(physio_model)
        
        new_sample_rate = 500
        generator.set_sample_rate(new_sample_rate)
        
        assert generator.sample_rate == new_sample_rate

if __name__ == "__main__":
    pytest.main([__file__, "-v"])