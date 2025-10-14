import json
import logging
import os
from typing import Dict, Any, Optional, List

class ScenarioManager:
    """
    Manages pre-defined physiological scenarios and medical conditions
    for the MAX30102 simulator.
    """
    
    def __init__(self, scenarios_file: Optional[str] = None):
        self.scenarios = {}
        self.setup_logging()
        
        if scenarios_file is None:
            # Default to package-relative path
            current_dir = os.path.dirname(__file__)
            scenarios_file = os.path.join(current_dir, '..', '..', 'config', 'scenarios.json')
        
        self.load_scenarios(scenarios_file)
    
    def setup_logging(self):
        """Setup logging for scenario manager"""
        self.logger = logging.getLogger('ScenarioManager')
    
    def load_scenarios(self, file_path: str) -> bool:
        """
        Load scenarios from a JSON file
        
        Args:
            file_path: Path to the scenarios JSON file
            
        Returns:
            bool: Success status
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.scenarios = data.get('scenarios', {})
            self.logger.info(f"Loaded {len(self.scenarios)} scenarios from {file_path}")
            return True
            
        except FileNotFoundError:
            self.logger.error(f"Scenarios file not found: {file_path}")
            return False
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in scenarios file: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error loading scenarios: {e}")
            return False
    
    def get_scenario(self, scenario_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific scenario by name
        
        Args:
            scenario_name: Name of the scenario to retrieve
            
        Returns:
            Scenario dictionary or None if not found
        """
        scenario = self.scenarios.get(scenario_name)
        if not scenario:
            self.logger.warning(f"Scenario not found: {scenario_name}")
        return scenario
    
    def get_all_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all available scenarios
        
        Returns:
            Dictionary of all scenarios
        """
        return self.scenarios.copy()
    
    def get_scenario_names(self) -> List[str]:
        """
        Get list of all available scenario names
        
        Returns:
            List of scenario names
        """
        return list(self.scenarios.keys())
    
    def get_scenarios_by_type(self, scenario_type: str) -> Dict[str, Dict[str, Any]]:
        """
        Get scenarios filtered by type (normal, emergency, activity, etc.)
        
        Args:
            scenario_type: Type of scenarios to filter by
            
        Returns:
            Dictionary of filtered scenarios
        """
        filtered = {}
        type_keywords = {
            'normal': ['normal', 'resting'],
            'emergency': ['heart_attack', 'anxiety', 'shock', 'fear'],
            'activity': ['walking', 'running', 'sleeping', 'sex'],
            'all': list(self.scenarios.keys())
        }
        
        keywords = type_keywords.get(scenario_type, [scenario_type])
        
        for name, scenario in self.scenarios.items():
            if any(keyword in name for keyword in keywords):
                filtered[name] = scenario
        
        return filtered
    
    def create_custom_scenario(self, name: str, description: str, 
                             physiological_params: Dict[str, Any]) -> bool:
        """
        Create a new custom scenario
        
        Args:
            name: Name of the new scenario
            description: Description of the scenario
            physiological_params: Physiological parameters for the scenario
            
        Returns:
            bool: Success status
        """
        if name in self.scenarios:
            self.logger.warning(f"Scenario already exists: {name}")
            return False
        
        self.scenarios[name] = {
            'description': description,
            'physiological': physiological_params
        }
        
        self.logger.info(f"Created custom scenario: {name}")
        return True
    
    def update_scenario(self, name: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing scenario
        
        Args:
            name: Name of the scenario to update
            updates: Dictionary of updates to apply
            
        Returns:
            bool: Success status
        """
        if name not in self.scenarios:
            self.logger.error(f"Scenario not found for update: {name}")
            return False
        
        # Merge updates with existing scenario
        if 'description' in updates:
            self.scenarios[name]['description'] = updates['description']
        
        if 'physiological' in updates:
            if 'physiological' not in self.scenarios[name]:
                self.scenarios[name]['physiological'] = {}
            
            # Merge physiological parameters
            for key, value in updates['physiological'].items():
                self.scenarios[name]['physiological'][key] = value
        
        self.logger.info(f"Updated scenario: {name}")
        return True
    
    def delete_scenario(self, name: str) -> bool:
        """
        Delete a scenario
        
        Args:
            name: Name of the scenario to delete
            
        Returns:
            bool: Success status
        """
        if name not in self.scenarios:
            self.logger.error(f"Scenario not found for deletion: {name}")
            return False
        
        del self.scenarios[name]
        self.logger.info(f"Deleted scenario: {name}")
        return True
    
    def export_scenarios(self, file_path: str) -> bool:
        """
        Export scenarios to a JSON file
        
        Args:
            file_path: Path where to save the scenarios
            
        Returns:
            bool: Success status
        """
        try:
            data = {'scenarios': self.scenarios}
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Exported {len(self.scenarios)} scenarios to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting scenarios: {e}")
            return False
    
    def validate_scenario_parameters(self, params: Dict[str, Any]) -> List[str]:
        """
        Validate physiological parameters for a scenario
        
        Args:
            params: Physiological parameters to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Valid parameter ranges
        valid_ranges = {
            'heart_rate_bpm': (30, 220),
            'spo2_percent': (70, 100),
            'respiratory_rate': (6, 60),
            'pulse_amplitude_red': (1000, 20000),
            'pulse_amplitude_ir': (1000, 20000),
            'noise_level': (0.01, 1.0)
        }
        
        for param, value in params.items():
            if param in valid_ranges:
                min_val, max_val = valid_ranges[param]
                if not (min_val <= value <= max_val):
                    errors.append(f"{param} value {value} outside valid range [{min_val}, {max_val}]")
        
        return errors
    
    def get_scenario_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about available scenarios
        
        Returns:
            Dictionary with scenario statistics
        """
        total = len(self.scenarios)
        
        # Count by type
        normal_count = len(self.get_scenarios_by_type('normal'))
        emergency_count = len(self.get_scenarios_by_type('emergency'))
        activity_count = len(self.get_scenarios_by_type('activity'))
        
        # Parameter ranges across all scenarios
        hr_values = []
        spo2_values = []
        
        for scenario in self.scenarios.values():
            physio = scenario.get('physiological', {})
            if 'heart_rate_bpm' in physio:
                hr_values.append(physio['heart_rate_bpm'])
            if 'spo2_percent' in physio:
                spo2_values.append(physio['spo2_percent'])
        
        return {
            'total_scenarios': total,
            'normal_scenarios': normal_count,
            'emergency_scenarios': emergency_count,
            'activity_scenarios': activity_count,
            'heart_rate_range': (min(hr_values), max(hr_values)) if hr_values else (0, 0),
            'spo2_range': (min(spo2_values), max(spo2_values)) if spo2_values else (0, 0)
        }