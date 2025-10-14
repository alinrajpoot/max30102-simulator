"""
MAX30102 Simulator Package

A high-fidelity TCP-based simulator for MAX30102 pulse oximeter and heart-rate sensor.
Provides realistic PPG waveform data and register-level communication simulation.
"""

__version__ = "1.0.0"
__author__ = "MAX30102 Simulator Team"

from .server import TCPServer
from .max30102_device import MAX30102Device
from .data_generator import DataGenerator

__all__ = ['TCPServer', 'MAX30102Device', 'DataGenerator']