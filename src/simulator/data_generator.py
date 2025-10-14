import numpy as np
import time
import logging
from typing import Dict, List, Tuple, Optional
from ..models.physiological_model import PhysiologicalModel

class DataGenerator:
    """
    Generates realistic PPG waveform data based on physiological models
    and sensor configuration.
    """
    
    def __init__(self, physio_model: PhysiologicalModel):
        self.physio_model = physio_model
        self.sample_rate = 1000  # Hz
        self.time_index = 0.0
        self.last_update_time = time.time()
        
        # Signal parameters
        self.baseline_red = 50000
        self.baseline_ir = 48000
        self.respiratory_phase = 0.0
        
        # Motion artifact simulation
        self.motion_artifact_active = False
        self.motion_start_time = 0
        self.motion_duration = 0
        
        self.setup_logging()
        self.initialize_waveform_parameters()
    
    def setup_logging(self):
        """Setup logging for data generator"""
        self.logger = logging.getLogger('DataGenerator')
    
    def initialize_waveform_parameters(self):
        """Initialize waveform generation parameters"""
        self.heart_rate = self.physio_model.heart_rate_bpm
        self.respiratory_rate = self.physio_model.respiratory_rate
        self.pulse_amplitude_red = self.physio_model.pulse_amplitude_red
        self.pulse_amplitude_ir = self.physio_model.pulse_amplitude_ir
        self.noise_level = self.physio_model.noise_level
    
    def generate_data_point(self) -> Dict[str, any]:
        """
        Generate a single data point with red and IR PPG waveforms
        
        Returns:
            Dict containing timestamp, PPG data, and vital signs
        """
        current_time = time.time()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Update time index for waveform generation
        self.time_index += dt
        
        # Get current physiological parameters
        self._update_parameters_from_model()
        
        # Generate PPG waveforms
        red_ppg, ir_ppg = self._generate_ppg_waveforms()
        
        # Add motion artifacts if applicable
        red_ppg, ir_ppg = self._add_motion_artifacts(red_ppg, ir_ppg)
        
        # Add sensor noise
        red_ppg = self._add_sensor_noise(red_ppg)
        ir_ppg = self._add_sensor_noise(ir_ppg)
        
        # Calculate derived vital signs
        heart_rate, spo2 = self._calculate_vital_signs(red_ppg, ir_ppg)
        
        data_point = {
            'timestamp': current_time,
            'red_ppg': int(red_ppg),
            'ir_ppg': int(ir_ppg),
            'heart_rate': heart_rate,
            'spO2': spo2,
            'sample_rate': self.sample_rate,
            'activity': self.physio_model.activity,
            'condition': self.physio_model.condition
        }
        
        return data_point
    
    def _generate_ppg_waveforms(self) -> Tuple[float, float]:
        """
        Generate synchronized red and IR PPG waveforms
        
        Returns:
            Tuple of (red_ppg, ir_ppg) values
        """
        # Calculate fundamental frequencies
        heart_rate_hz = self.heart_rate / 60.0  # Convert BPM to Hz
        respiratory_hz = self.respiratory_rate / 60.0
        
        # Update respiratory phase
        self.respiratory_phase += 2 * np.pi * respiratory_hz / self.sample_rate
        self.respiratory_phase %= 2 * np.pi
        
        # Generate cardiac pulse waveform
        t = self.time_index * heart_rate_hz * 2 * np.pi
        
        # Fundamental pulse shape (systolic peak)
        pulse_waveform = np.sin(t) ** 3
        
        # Add diastolic notch for more realistic waveform
        diastolic_notch = 0.3 * np.sin(2 * t - np.pi/4) ** 2
        
        # Combine components
        cardiac_signal = pulse_waveform + diastolic_notch
        
        # Add respiratory modulation (baseline wander)
        respiratory_modulation = 0.1 * np.sin(self.respiratory_phase)
        
        # Generate red and IR signals with different amplitudes and slight phase differences
        red_signal = (self.baseline_red + 
                     self.pulse_amplitude_red * cardiac_signal * (1 + 0.05 * respiratory_modulation))
        
        ir_signal = (self.baseline_ir + 
                    self.pulse_amplitude_ir * cardiac_signal * (1 + 0.05 * respiratory_modulation) *
                    (1.0 + 0.02 * np.sin(t * 0.5)))  # Slight different modulation for IR
        
        return red_signal, ir_signal
    
    def _add_motion_artifacts(self, red_ppg: float, ir_ppg: float) -> Tuple[float, float]:
        """
        Add realistic motion artifacts to PPG signals
        
        Args:
            red_ppg: Original red PPG value
            ir_ppg: Original IR PPG value
            
        Returns:
            Tuple of (red_ppg, ir_ppg) with motion artifacts
        """
        current_time = time.time()
        
        # Check if we should start a new motion artifact
        if (not self.motion_artifact_active and 
            np.random.random() < self.physio_model.motion_artifact_probability):
            self.motion_artifact_active = True
            self.motion_start_time = current_time
            self.motion_duration = np.random.uniform(0.1, 2.0)
        
        # Apply motion artifact if active
        if self.motion_artifact_active:
            artifact_time = current_time - self.motion_start_time
            
            if artifact_time < self.motion_duration:
                # Create motion artifact (combination of low and high frequency components)
                motion_freq1 = 2.0  # Hz - gross movement
                motion_freq2 = 8.0  # Hz - tremor/vibration
                
                motion_artifact = (
                    0.7 * np.sin(2 * np.pi * motion_freq1 * artifact_time) +
                    0.3 * np.sin(2 * np.pi * motion_freq2 * artifact_time)
                ) * self.pulse_amplitude_red * 0.5
                
                red_ppg += motion_artifact
                ir_ppg += motion_artifact * 1.1  # Slightly different for IR
            else:
                self.motion_artifact_active = False
        
        return red_ppg, ir_ppg
    
    def _add_sensor_noise(self, signal: float) -> float:
        """
        Add realistic sensor noise to the signal
        
        Args:
            signal: Original signal value
            
        Returns:
            Signal value with added noise
        """
        # White noise
        white_noise = np.random.normal(0, self.noise_level * self.pulse_amplitude_red)
        
        # 1/f noise (flicker noise) - more realistic for sensors
        flicker_noise = np.random.normal(0, self.noise_level * self.pulse_amplitude_red * 0.3)
        
        # Power line interference (50/60 Hz)
        power_line_noise = (0.05 * self.pulse_amplitude_red * 
                          np.sin(2 * np.pi * 50 * self.time_index))
        
        return signal + white_noise + flicker_noise + power_line_noise
    
    def _calculate_vital_signs(self, red_ppg: float, ir_ppg: float) -> Tuple[float, float]:
        """
        Calculate heart rate and SpO2 from PPG signals
        
        Args:
            red_ppg: Red PPG value
            ir_ppg: IR PPG value
            
        Returns:
            Tuple of (heart_rate, spO2)
        """
        # For simulation purposes, we'll use the model values with some noise
        # In a real implementation, this would involve signal processing algorithms
        
        heart_rate = (self.heart_rate + 
                     np.random.normal(0, 1.0) +  # Small random variation
                     2.0 * np.sin(2 * np.pi * self.respiratory_rate/60 * self.time_index))  # Respiratory sinus arrhythmia
        
        # SpO2 calculation based on ratio of ratios
        # Simplified model - in reality this requires careful calibration
        ac_red = self.pulse_amplitude_red
        ac_ir = self.pulse_amplitude_ir
        dc_red = self.baseline_red
        dc_ir = self.baseline_ir
        
        # Ratio of ratios (simplified)
        R = (ac_red / dc_red) / (ac_ir / dc_ir)
        
        # Empirical SpO2 calculation (simplified)
        spo2 = 110.0 - 25.0 * R
        spo2 = max(70.0, min(100.0, spo2))  # Clamp to realistic range
        
        # Add small random variation
        spo2 += np.random.normal(0, 0.5)
        
        return round(heart_rate, 1), round(spo2, 1)
    
    def _update_parameters_from_model(self):
        """Update generator parameters from physiological model"""
        self.heart_rate = self.physio_model.heart_rate_bpm
        self.respiratory_rate = self.physio_model.respiratory_rate
        self.pulse_amplitude_red = self.physio_model.pulse_amplitude_red
        self.pulse_amplitude_ir = self.physio_model.pulse_amplitude_ir
        self.noise_level = self.physio_model.noise_level
    
    def set_sample_rate(self, sample_rate: int):
        """Set the sample rate for data generation"""
        self.sample_rate = sample_rate
        self.logger.info(f"Sample rate set to {sample_rate} Hz")