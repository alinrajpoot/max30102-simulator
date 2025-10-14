"""
Communication Protocols Package

Contains protocol implementations for MAX30102 communication simulation,
including I2C protocol simulation and data formatting.
"""

from .i2c_simulator import I2CProtocolSimulator

__all__ = ['I2CProtocolSimulator']