"""
Physiological Models Package

Contains models for simulating human physiological responses,
scenario management, and condition simulation.
"""

from .physiological_model import PhysiologicalModel
from .scenarios import ScenarioManager

__all__ = ['PhysiologicalModel', 'ScenarioManager']