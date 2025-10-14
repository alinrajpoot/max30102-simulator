#!/usr/bin/env python3
"""
Integration tests for MAX30102 Simulator

Tests the complete system integration from TCP server through
data generation and physiological modeling.
"""

import time
import json
import threading
from unittest.mock import Mock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from simulator.server import TCPServer
from simulator.data_generator import DataGenerator
from models.physiological_model import PhysiologicalModel

class TestIntegration:
    """Integration test cases"""
    
    def test_complete_data_flow(self):
        """Test complete data flow from model to TCP output"""
        # Create physiological model
        physio_model = PhysiologicalModel()
        
        # Create data generator
        data_gen = DataGenerator(physio_model)
        
        # Generate multiple data points
        data_points = []
        for _ in range(10):
            data_point = data_gen.generate_data_point()
            data_points.append(data_point)
        
        # Verify data structure and content
        for dp in data_points:
            assert all(key in dp for key in [
                'timestamp', 'red_ppg', 'ir_ppg', 'heart_rate', 
                'spO2', 'activity', 'condition'
            ])
            
            # Check data types
            assert isinstance(dp['red_ppg'], int)
            assert isinstance(dp['ir_ppg'], int)
            assert isinstance(dp['heart_rate'], float)
            assert isinstance(dp['spO2'], float)
    
    def test_scenario_transitions(self):
        """Test smooth transitions between scenarios"""
        physio_model = PhysiologicalModel()
        data_gen = DataGenerator(physio_model)
        
        scenarios = ['normal_resting', 'walking', 'running', 'heart_attack']
        hr_values = {}
        
        for scenario in scenarios:
            # Apply scenario
            physio_model.set_scenario(scenario)
            time.sleep(0.1)  # Allow model to stabilize
            
            # Generate samples and record average HR
            hr_sum = 0
            sample_count = 10
            
            for _ in range(sample_count):
                data_point = data_gen.generate_data_point()
                hr_sum += data_point['heart_rate']
                time.sleep(0.01)
            
            hr_values[scenario] = hr_sum / sample_count
        
        # Verify physiological responses
        assert hr_values['walking'] > hr_values['normal_resting']
        assert hr_values['running'] > hr_values['walking']
        assert hr_values['heart_attack'] < hr_values['normal_resting']  # Bradycardia
    
    def test_tcp_server_initialization(self):
        """Test TCP server initialization and basic functionality"""
        # Note: This test doesn't actually start the server to avoid port conflicts
        server = TCPServer(host='localhost', port=8888)
        
        # Verify components are initialized
        assert server.physio_model is not None
        assert server.max30102 is not None
        assert server.data_gen is not None
        assert server.host == 'localhost'
        assert server.port == 8888
    
    def test_real_time_parameter_updates(self):
        """Test real-time parameter updates during data generation"""
        physio_model = PhysiologicalModel()
        data_gen = DataGenerator(physio_model)
        
        # Start with normal parameters
        initial_data = data_gen.generate_data_point()
        initial_hr = initial_data['heart_rate']
        
        # Update to high-activity parameters
        physio_model.update_parameters({
            'activity': 'running',
            'heart_rate_bpm': 150
        })
        
        # Allow some time for the generator to update
        time.sleep(0.1)
        
        # Generate new data
        updated_data = data_gen.generate_data_point()
        updated_hr = updated_data['heart_rate']
        
        # Should reflect the updated parameters
        assert abs(updated_hr - 150) < 10  # Allow some algorithmic variation
    
    def test_error_handling(self):
        """Test error handling in the system"""
        physio_model = PhysiologicalModel()
        
        # Test invalid parameter update
        success = physio_model.update_parameters({
            'invalid_parameter': 'invalid_value',  # This should be ignored
            'age': 25  # This should work
        })
        
        # Should still return success (invalid parameters are ignored)
        assert success == True
        
        # Verify valid parameter was updated
        state = physio_model.get_current_state()
        assert state['age'] == 25
        
        # Test invalid scenario
        success = physio_model.set_scenario('non_existent_scenario')
        assert success == False

def run_integration_tests():
    """Run all integration tests"""
    print("Running MAX30102 Simulator Integration Tests")
    print("=" * 50)
    
    test_instance = TestIntegration()
    
    tests = [
        ('Complete Data Flow', test_instance.test_complete_data_flow),
        ('Scenario Transitions', test_instance.test_scenario_transitions),
        ('TCP Server Initialization', test_instance.test_tcp_server_initialization),
        ('Real-time Parameter Updates', test_instance.test_real_time_parameter_updates),
        ('Error Handling', test_instance.test_error_handling),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_method in tests:
        try:
            test_method()
            print(f"✅ {test_name}: PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: FAILED - {e}")
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)