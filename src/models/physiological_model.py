import json
import logging
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from .scenarios import ScenarioManager

@dataclass
class PhysiologicalState:
    """Data class representing the current physiological state"""
    age: int = 30
    gender: str = "male"  # "male" or "female"
    weight_kg: float = 70.0
    height_cm: float = 175.0
    activity: str = "resting"
    condition: str = "normal"
    fitness_level: str = "average"
    
    # Vital signs
    heart_rate_bpm: float = 72.0
    spo2_percent: float = 98.0
    respiratory_rate: int = 16
    
    # Waveform parameters
    pulse_amplitude_red: int = 10000
    pulse_amplitude_ir: int = 9500
    baseline_red: int = 50000
    baseline_ir: int = 48000
    noise_level: float = 0.05
    
    # Motion artifacts
    motion_artifact_probability: float = 0.1
    motion_artifact_duration: float = 0.5
    
    # Heart rate variability
    heart_rate_variability: str = "normal"
    pulse_rhythm: str = "regular"
    pulse_quality: str = "normal"

class PhysiologicalModel:
    """
    Models human physiological responses based on parameters like age, gender,
    activity level, and medical conditions. Provides realistic parameter adjustments.
    """
    
    def __init__(self):
        self.state = PhysiologicalState()
        self.scenario_manager = ScenarioManager()
        self.setup_logging()
        
        # Physiological response curves and relationships
        self._setup_physiological_relationships()
    
    def setup_logging(self):
        """Setup logging for the physiological model"""
        self.logger = logging.getLogger('PhysiologicalModel')
    
    def _setup_physiological_relationships(self):
        """Initialize physiological response curves and relationships"""
        # Age-based adjustments
        self.age_factors = {
            'heart_rate': lambda age: 208 - (0.7 * age),  # Max heart rate formula
            'baseline_hr': lambda age: 72 - (age - 30) * 0.1,  # Slight decrease with age
            'respiratory_rate': lambda age: 16 - (age - 30) * 0.02
        }
        
        # Gender adjustments
        self.gender_factors = {
            'male': {'hr_offset': 0, 'amplitude_factor': 1.0},
            'female': {'hr_offset': 5, 'amplitude_factor': 0.9}  # Slightly higher HR, lower amplitude
        }
        
        # Activity level effects
        self.activity_effects = {
            'resting': {
                'heart_rate_factor': 1.0,
                'respiratory_factor': 1.0,
                'amplitude_factor': 1.0,
                'noise_factor': 0.2
            },
            'walking': {
                'heart_rate_factor': 1.3,
                'respiratory_factor': 1.5,
                'amplitude_factor': 1.2,
                'noise_factor': 0.5
            },
            'running': {
                'heart_rate_factor': 1.9,
                'respiratory_factor': 2.0,
                'amplitude_factor': 1.5,
                'noise_factor': 0.8
            },
            'sleeping': {
                'heart_rate_factor': 0.8,
                'respiratory_factor': 0.6,
                'amplitude_factor': 0.7,
                'noise_factor': 0.1
            },
            'sex_time': {
                'heart_rate_factor': 1.8,
                'respiratory_factor': 1.8,
                'amplitude_factor': 1.4,
                'noise_factor': 0.6
            }
        }
        
        # Fitness level adjustments
        self.fitness_effects = {
            'athletic': {'hr_factor': 0.8, 'hrv': 'high'},
            'average': {'hr_factor': 1.0, 'hrv': 'normal'},
            'sedentary': {'hr_factor': 1.1, 'hrv': 'low'}
        }
    
    def update_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Update physiological parameters and recalculate dependent values
        
        Args:
            parameters: Dictionary of parameters to update
            
        Returns:
            bool: Success status
        """
        try:
            # Update basic parameters
            for key, value in parameters.items():
                if hasattr(self.state, key):
                    setattr(self.state, key, value)
            
            # Recalculate dependent physiological parameters
            self._recalculate_physiology()
            
            self.logger.info(f"Updated parameters: {list(parameters.keys())}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating parameters: {e}")
            return False
    
    def set_scenario(self, scenario_name: str) -> bool:
        """
        Apply a pre-defined scenario to the physiological model
        
        Args:
            scenario_name: Name of the scenario to apply
            
        Returns:
            bool: Success status
        """
        scenario = self.scenario_manager.get_scenario(scenario_name)
        if not scenario:
            self.logger.error(f"Scenario not found: {scenario_name}")
            return False
        
        try:
            # Update physiological parameters from scenario
            physio_params = scenario.get('physiological', {})
            self.update_parameters(physio_params)
            
            # Update activity and condition if specified
            if 'description' in scenario:
                self.state.condition = scenario_name
                if any(activity in scenario_name for activity in ['walking', 'running', 'sleeping', 'sex']):
                    self.state.activity = scenario_name.split('_')[0]
            
            self.logger.info(f"Applied scenario: {scenario_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying scenario {scenario_name}: {e}")
            return False
    
    def _recalculate_physiology(self):
        """Recalculate dependent physiological parameters based on current state"""
        # Base calculations
        base_hr = self.age_factors['baseline_hr'](self.state.age)
        base_rr = self.age_factors['respiratory_rate'](self.state.age)
        
        # Apply gender adjustments
        gender_adj = self.gender_factors.get(self.state.gender, self.gender_factors['male'])
        base_hr += gender_adj['hr_offset']
        
        # Apply activity effects
        activity_eff = self.activity_effects.get(self.state.activity, self.activity_effects['resting'])
        self.state.heart_rate_bpm = base_hr * activity_eff['heart_rate_factor']
        self.state.respiratory_rate = int(base_rr * activity_eff['respiratory_factor'])
        
        # Apply fitness level
        fitness_eff = self.fitness_effects.get(self.state.fitness_level, self.fitness_effects['average'])
        self.state.heart_rate_bpm *= fitness_eff['hr_factor']
        self.state.heart_rate_variability = fitness_eff['hrv']
        
        # Apply amplitude adjustments
        self.state.pulse_amplitude_red = int(10000 * activity_eff['amplitude_factor'] * gender_adj['amplitude_factor'])
        self.state.pulse_amplitude_ir = int(self.state.pulse_amplitude_red * 0.95)
        
        # Apply noise adjustments
        self.state.noise_level = 0.05 * activity_eff['noise_factor']
        
        # Condition-specific overrides
        self._apply_condition_effects()
        
        # Ensure realistic ranges
        self._clamp_to_physiological_ranges()
    
    def _apply_condition_effects(self):
        """Apply specific effects based on medical condition"""
        condition_effects = {
            'heart_attack': {
                'heart_rate_bpm': 45,
                'spo2_percent': 85,
                'respiratory_rate': 8,
                'pulse_amplitude_red': 5000,
                'pulse_amplitude_ir': 4500,
                'noise_level': 0.1,
                'pulse_rhythm': 'irregular',
                'pulse_quality': 'weak'
            },
            'extreme_anxiety': {
                'heart_rate_bpm': 120,
                'spo2_percent': 95,
                'respiratory_rate': 25,
                'pulse_amplitude_red': 12000,
                'pulse_amplitude_ir': 11500,
                'noise_level': 0.15,
                'heart_rate_variability': 'low'
            },
            'shock': {
                'heart_rate_bpm': 140,
                'spo2_percent': 82,
                'respiratory_rate': 35,
                'pulse_amplitude_red': 3000,
                'pulse_amplitude_ir': 2800,
                'noise_level': 0.25,
                'pulse_quality': 'weak'
            },
            'fear': {
                'heart_rate_bpm': 110,
                'spo2_percent': 96,
                'respiratory_rate': 22,
                'pulse_amplitude_red': 11000,
                'pulse_amplitude_ir': 10500,
                'noise_level': 0.12,
                'heart_rate_variability': 'very_low'
            }
        }
        
        if self.state.condition in condition_effects:
            effects = condition_effects[self.state.condition]
            for param, value in effects.items():
                if hasattr(self.state, param):
                    setattr(self.state, param, value)
    
    def _clamp_to_physiological_ranges(self):
        """Ensure all parameters stay within physiologically possible ranges"""
        # Heart rate limits
        self.state.heart_rate_bpm = max(30, min(220, self.state.heart_rate_bpm))
        
        # SpO2 limits
        self.state.spo2_percent = max(70, min(100, self.state.spo2_percent))
        
        # Respiratory rate limits
        self.state.respiratory_rate = max(6, min(60, self.state.respiratory_rate))
        
        # Amplitude limits
        self.state.pulse_amplitude_red = max(1000, min(20000, self.state.pulse_amplitude_red))
        self.state.pulse_amplitude_ir = max(1000, min(20000, self.state.pulse_amplitude_ir))
        
        # Noise level limits
        self.state.noise_level = max(0.01, min(1.0, self.state.noise_level))
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get the current physiological state as a dictionary
        
        Returns:
            Dictionary containing all current physiological parameters
        """
        return asdict(self.state)
    
    def reset_to_defaults(self):
        """Reset the physiological model to default values"""
        self.state = PhysiologicalState()
        self._recalculate_physiology()
        self.logger.info("Reset to default physiological parameters")
    
    def simulate_stress_response(self, stress_level: float):
        """
        Simulate a stress response with adjustable intensity
        
        Args:
            stress_level: 0.0 (no stress) to 1.0 (extreme stress)
        """
        stress_level = max(0.0, min(1.0, stress_level))
        
        # Linear interpolation between normal and extreme stress
        normal_hr = 72
        stress_hr = 120
        
        self.state.heart_rate_bpm = normal_hr + (stress_hr - normal_hr) * stress_level
        self.state.respiratory_rate = int(16 + (25 - 16) * stress_level)
        self.state.noise_level = 0.05 + (0.15 - 0.05) * stress_level
        
        self.logger.info(f"Applied stress response: level {stress_level:.2f}")
    
    def get_physiological_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current physiological state
        
        Returns:
            Dictionary with key physiological metrics
        """
        return {
            'age': self.state.age,
            'gender': self.state.gender,
            'activity': self.state.activity,
            'condition': self.state.condition,
            'heart_rate': self.state.heart_rate_bpm,
            'spo2': self.state.spo2_percent,
            'respiratory_rate': self.state.respiratory_rate,
            'fitness_level': self.state.fitness_level,
            'heart_rate_variability': self.state.heart_rate_variability
        }