#!/usr/bin/env python3
"""
Example TCP client for MAX30102 Simulator

This script demonstrates how to connect to the MAX30102 simulator
and receive real-time physiological data streams.
"""

import socket
import json
import time
import sys
import argparse
from typing import Dict, Any

class MAX30102Client:
    """
    Example client for connecting to MAX30102 Simulator TCP server
    """
    
    def __init__(self, host: str = 'localhost', port: int = 8888):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        
    def connect(self) -> bool:
        """Connect to the MAX30102 simulator server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"Connected to MAX30102 simulator at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.socket:
            self.socket.close()
        self.connected = False
        print("Disconnected from simulator")
    
    def receive_data(self, duration: int = 30):
        """
        Receive and display data from the simulator
        
        Args:
            duration: How long to receive data in seconds
        """
        if not self.connected:
            print("Not connected to server")
            return
        
        start_time = time.time()
        sample_count = 0
        
        print(f"Receiving data for {duration} seconds...")
        print("Press Ctrl+C to stop early")
        print("-" * 80)
        
        try:
            while time.time() - start_time < duration:
                # Receive data line
                data_line = self.socket.recv(1024).decode('utf-8').strip()
                if not data_line:
                    continue
                
                try:
                    data = json.loads(data_line)
                    sample_count += 1
                    
                    # Display data
                    if data.get('type') == 'welcome':
                        print(f"Welcome message: {data.get('message')}")
                        print(f"Current config: {json.dumps(data.get('config', {}), indent=2)}")
                    elif data.get('type') in ['error', 'command_response']:
                        print(f"Server response: {data}")
                    else:
                        # Regular data sample
                        self._display_sample(data, sample_count)
                        
                except json.JSONDecodeError:
                    print(f"Invalid JSON received: {data_line}")
                    
        except KeyboardInterrupt:
            print("\nStopped by user")
        except Exception as e:
            print(f"Error receiving data: {e}")
        
        print(f"\nReceived {sample_count} samples in {time.time() - start_time:.2f} seconds")
    
    def _display_sample(self, data: Dict[str, Any], sample_count: int):
        """Display a single data sample in a formatted way"""
        if sample_count % 50 == 1:  # Header every 50 samples
            print(f"{'Sample':>6} {'Timestamp':>12} {'Red PPG':>8} {'IR PPG':>8} {'HR':>6} {'SpO2':>5} {'Activity':>12} {'Condition':>12}")
            print("-" * 80)
        
        timestamp = data.get('timestamp', 0)
        red_ppg = data.get('red_ppg', 0)
        ir_ppg = data.get('ir_ppg', 0)
        heart_rate = data.get('heart_rate', 0)
        spo2 = data.get('spO2', 0)
        activity = data.get('activity', 'unknown')
        condition = data.get('condition', 'normal')
        
        print(f"{sample_count:6d} {timestamp:12.3f} {red_ppg:8d} {ir_ppg:8d} "
              f"{heart_rate:6.1f} {spo2:5.1f} {activity:>12} {condition:>12}")
    
    def send_command(self, command: Dict[str, Any]) -> bool:
        """
        Send a command to the simulator
        
        Args:
            command: Command dictionary to send
            
        Returns:
            bool: Success status
        """
        if not self.connected:
            print("Not connected to server")
            return False
        
        try:
            command_json = json.dumps(command) + '\n'
            self.socket.sendall(command_json.encode('utf-8'))
            print(f"Sent command: {command}")
            return True
        except Exception as e:
            print(f"Error sending command: {e}")
            return False
    
    def set_parameters(self, parameters: Dict[str, Any]):
        """Send parameter update command"""
        command = {
            "command": "set_parameters",
            "parameters": parameters
        }
        return self.send_command(command)
    
    def set_scenario(self, scenario: str):
        """Send scenario change command"""
        command = {
            "command": "set_scenario", 
            "scenario": scenario
        }
        return self.send_command(command)
    
    def get_status(self):
        """Request current status"""
        command = {"command": "get_status"}
        return self.send_command(command)
    
    def reset(self):
        """Reset to default parameters"""
        command = {"command": "reset"}
        return self.send_command(command)

def main():
    """Main function for the example client"""
    parser = argparse.ArgumentParser(description='MAX30102 Simulator Client Example')
    parser.add_argument('--host', default='localhost', help='Server hostname')
    parser.add_argument('--port', type=int, default=8888, help='Server port')
    parser.add_argument('--duration', type=int, default=30, help='Duration to receive data (seconds)')
    parser.add_argument('--scenario', help='Set scenario on startup')
    parser.add_argument('--age', type=int, help='Set age parameter')
    parser.add_argument('--gender', choices=['male', 'female'], help='Set gender parameter')
    parser.add_argument('--activity', choices=['resting', 'walking', 'running', 'sleeping', 'sex_time'], 
                       help='Set activity parameter')
    
    args = parser.parse_args()
    
    # Create and connect client
    client = MAX30102Client(args.host, args.port)
    
    if not client.connect():
        sys.exit(1)
    
    try:
        # Apply initial configuration if provided
        if args.scenario:
            print(f"Setting scenario to: {args.scenario}")
            client.set_scenario(args.scenario)
            time.sleep(1)  # Wait for scenario to apply
        
        if any([args.age, args.gender, args.activity]):
            parameters = {}
            if args.age:
                parameters['age'] = args.age
            if args.gender:
                parameters['gender'] = args.gender
            if args.activity:
                parameters['activity'] = args.activity
            
            if parameters:
                print(f"Setting parameters: {parameters}")
                client.set_parameters(parameters)
                time.sleep(1)
        
        # Start receiving data
        client.receive_data(args.duration)
        
    except KeyboardInterrupt:
        print("\nClient stopped by user")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()