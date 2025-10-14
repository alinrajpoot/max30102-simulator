"""
Tests for Physiological Model
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.physiological_model import PhysiologicalModel, PhysiologicalState
from models.scenarios import ScenarioManager

class TestPhysiologicalModel:
    """Test cases for PhysiologicalModel class"""
    
    def test_initial_state(self):
        """Test that model initializes with correct default state"""
        model = PhysiologicalModel()
        state = model.get_current_state()
        
        assert state['age'] == 30
        assert state['gender'] == 'male'
        assert state['activity'] == 'resting'
        assert state['condition'] == 'normal'
        assert 60 <= state['heart_rate_bpm'] <= 80  # Reasonable resting HR
    
    def test_parameter_update(self):
        """Test updating physiological parameters"""
        model = PhysiologicalModel()
        
        # Update parameters
        success = model.update_parameters({
            'age': 25,
            'gender': 'female',
            'activity': 'walking'
        })
        
        assert success == True
        
        state = model.get_current_state()
        assert state['age'] == 25
        assert state['gender'] == 'female'
        assert state['activity'] == 'walking'
    
    def test_scenario_application(self):
        """Test applying pre-defined scenarios"""
        model = PhysiologicalModel()
        
        # Apply running scenario
        success = model.set_scenario('running')
        assert success == True
        
        state = model.get_current_state()
        assert state['heart_rate_bpm'] > 100  # Running should increase HR
        assert state['condition'] == 'running'
    
    def test_emergency_scenarios(self):
        """Test emergency medical scenarios"""
        model = PhysiologicalModel()
        
        # Test heart attack scenario
        model.set_scenario('heart_attack')
        state = model.get_current_state()
        
        assert state['heart_rate_bpm'] < 60  # Bradycardia in heart attack
        assert state['spo2_percent'] < 90    # Low oxygen saturation
        assert state['pulse_quality'] == 'weak'
    
    def test_physiological_ranges(self):
        """Test that parameters stay within physiological ranges"""
        model = PhysiologicalModel()
        
        # Try to set extreme values
        model.update_parameters({
            'heart_rate_bpm': 500,  # Impossible value
            'spo2_percent': 200,    # Impossible value
            'respiratory_rate': 100 # Impossible value
        })
        
        state = model.get_current_state()
        
        # Should be clamped to reasonable ranges
        assert state['heart_rate_bpm'] <= 220
        assert state['spo2_percent'] <= 100
        assert state['respiratory_rate'] <= 60
    
    def test_stress_response(self):
        """Test stress response simulation"""
        model = PhysiologicalModel()
        
        initial_hr = model.state.heart_rate_bpm
        
        # Apply moderate stress
        model.simulate_stress_response(0.5)
        
        new_hr = model.state.heart_rate_bpm
        assert new_hr > initial_hr  # Stress should increase HR
    
    def test_reset_functionality(self):
        """Test reset to default values"""
        model = PhysiologicalModel()
        
        # Change some parameters
        model.update_parameters({
            'age': 45,
            'activity': 'running',
            'condition': 'heart_attack'
        })
        
        # Reset to defaults
        model.reset_to_defaults()
        
        state = model.get_current_state()
        assert state['age'] == 30
        assert state['activity'] == 'resting'
        assert state['condition'] == 'normal'

class TestScenarioManager:
    """Test cases for ScenarioManager class"""
    
    def test_scenario_loading(self):
        """Test that scenarios load correctly"""
        manager = ScenarioManager()
        scenarios = manager.get_all_scenarios()
        
        assert len(scenarios) > 0
        assert 'normal_resting' in scenarios
        assert 'heart_attack' in scenarios
        assert 'running' in scenarios
    
    def test_scenario_retrieval(self):
        """Test retrieving specific scenarios"""
        manager = ScenarioManager()
        
        scenario = manager.get_scenario('normal_resting')
        assert scenario is not None
        assert 'description' in scenario
        assert 'physiological' in scenario
        
        # Test non-existent scenario
        scenario = manager.get_scenario('non_existent')
        assert scenario is None
    
    def test_scenario_filtering(self):
        """Test filtering scenarios by type"""
        manager = ScenarioManager()
        
        emergency_scenarios = manager.get_scenarios_by_type('emergency')
        assert len(emergency_scenarios) >= 4  # heart_attack, anxiety, shock, fear
        
        activity_scenarios = manager.get_scenarios_by_type('activity')
        assert len(activity_scenarios) >= 4   # walking, running, sleeping, sex
    
    def test_custom_scenario_creation(self):
        """Test creating custom scenarios"""
        manager = ScenarioManager()
        
        success = manager.create_custom_scenario(
            name='test_scenario',
            description='Test scenario for unit testing',
            physiological_params={
                'heart_rate_bpm': 100,
                'spo2_percent': 97,
                'respiratory_rate': 20
            }
        )
        
        assert success == True
        assert 'test_scenario' in manager.get_scenario_names()
        
        # Clean up
        manager.delete_scenario('test_scenario')
    
    def test_scenario_validation(self):
        """Test scenario parameter validation"""
        manager = ScenarioManager()
        
        # Test valid parameters
        valid_params = {
            'heart_rate_bpm': 80,
            'spo2_percent': 98,
            'respiratory_rate': 16
        }
        
        errors = manager.validate_scenario_parameters(valid_params)
        assert len(errors) == 0
        
        # Test invalid parameters
        invalid_params = {
            'heart_rate_bpm': 300,  # Too high
            'spo2_percent': 50,     # Too low
            'respiratory_rate': 100 # Too high
        }
        
        errors = manager.validate_scenario_parameters(invalid_params)
        assert len(errors) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])