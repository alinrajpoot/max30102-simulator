# User Manual

Complete guide to using the MAX30102 Physiological Simulator.

## Table of Contents

1. [Overview](#overview)
2. [Basic Operation](#basic-operation)
3. [TCP Client Integration](#tcp-client-integration)
4. [Physiological Parameters](#physiological-parameters)
5. [Medical Scenarios](#medical-scenarios)
6. [Real-time Control](#real-time-control)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)

## Overview

The MAX30102 Simulator is a high-fidelity simulator that generates realistic PPG (photoplethysmography) data and mimics the behavior of a real MAX30102 pulse oximeter sensor. It's designed for testing AI platforms, medical device software, and research applications.

## Basic Operation

### Starting the Server

```bash
python src/simulator/server.py
```

Optional command-line arguments:

```bash
python src/simulator/server.py --host 0.0.0.0 --port 9999
```

### Server Output

When the server starts successfully, you'll see:

```
INFO - TCPServer - MAX30102 Simulator TCP Server started on localhost:8888
INFO - TCPServer - New client connected: ('127.0.0.1', 54321)
```

## TCP Client Integration

### Basic Client Implementation

Here's a minimal Python client:

```python
import socket
import json

class MAX30102Client:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print("Connected to MAX30102 simulator")

    def receive_data(self):
        while True:
            data = self.socket.recv(1024).decode('utf-8').strip()
            if data:
                try:
                    sample = json.loads(data)
                    print(f"HR: {sample['heart_rate']} bpm, SpO2: {sample['spO2']}%")
                except json.JSONDecodeError:
                    print(f"Raw data: {data}")

    def send_command(self, command):
        command_json = json.dumps(command) + '\n'
        self.socket.sendall(command_json.encode('utf-8'))

    def disconnect(self):
        if self.socket:
            self.socket.close()
```

### Data Format

Each data sample has the following structure:

```json
{
  "timestamp": 1635786300.123,
  "red_ppg": 51234,
  "ir_ppg": 49876,
  "heart_rate": 72.5,
  "spO2": 98.2,
  "activity": "resting",
  "condition": "normal",
  "sample_rate": 1000
}
```

## Physiological Parameters

### Available Parameters

| Parameter       | Type    | Range                      | Description            |
| --------------- | ------- | -------------------------- | ---------------------- |
| `age`           | integer | 0-120                      | Subject age in years   |
| `gender`        | string  | male/female                | Biological sex         |
| `weight_kg`     | float   | 20-200                     | Weight in kilograms    |
| `height_cm`     | float   | 100-250                    | Height in centimeters  |
| `activity`      | string  | see below                  | Current activity level |
| `condition`     | string  | see below                  | Medical condition      |
| `fitness_level` | string  | athletic/average/sedentary | Physical fitness       |

### Activities

- `resting`: Normal resting state (HR: 60-80 bpm)
- `walking`: Light walking (HR: 90-110 bpm)
- `running`: Moderate running (HR: 130-160 bpm)
- `sleeping`: Deep sleep state (HR: 50-70 bpm)
- `sex_intercourse`: Sexual activity (HR: 120-140 bpm)

## Medical Scenarios

### Available Scenarios

| Scenario          | Description           | Key Characteristics                |
| ----------------- | --------------------- | ---------------------------------- |
| `normal_resting`  | Healthy resting state | HR: 72 bpm, SpO2: 98%              |
| `heart_attack`    | Myocardial infarction | HR: 45 bpm, SpO2: 85%, weak pulse  |
| `extreme_anxiety` | Panic attack          | HR: 120 bpm, high variability      |
| `shock`           | Medical shock         | HR: 140 bpm, SpO2: 82%, weak pulse |
| `fear`            | Acute fear response   | HR: 110 bpm, low variability       |
| `running`         | Exercise simulation   | HR: 140 bpm, motion artifacts      |
| `sleeping`        | Sleep state           | HR: 55 bpm, stable signal          |

### Using Scenarios

```python
# Through TCP client
client.send_command({
    "command": "set_scenario",
    "scenario": "heart_attack"
})

# Using example client
from examples.client_example import MAX30102Client
client = MAX30102Client()
client.connect()
client.set_scenario('running')
```

## Real-time Control

### Changing Parameters During Operation

```python
# Update multiple parameters
client.set_parameters({
    'age': 45,
    'gender': 'female',
    'activity': 'walking',
    'condition': 'normal'
})

# Update single parameter
client.set_parameters({
    'heart_rate_bpm': 150
})
```

### Command Reference

| Command          | Parameters          | Description                         |
| ---------------- | ------------------- | ----------------------------------- |
| `set_parameters` | `parameters` object | Update physiological parameters     |
| `set_scenario`   | `scenario` string   | Apply pre-defined scenario          |
| `get_status`     | none                | Get server status and current state |
| `reset`          | none                | Reset to default parameters         |

Example commands:

```json
{"command": "set_parameters", "parameters": {"age": 35, "activity": "running"}}
{"command": "set_scenario", "scenario": "heart_attack"}
{"command": "get_status"}
{"command": "reset"}
```

## Configuration

### Configuration Files

The simulator uses two main configuration files:

1. **`config/default.yaml`** - Main configuration (sensor parameters, TCP settings)
2. **`config/scenarios.json`** - Pre-defined medical scenarios

### Modifying Default Parameters

Edit `config/default.yaml`:

```yaml
# Change sample rate
sensor:
  sample_rate: 500 # From 1000 Hz to 500 Hz

# Change TCP settings
tcp_server:
  port: 9999
  host: "0.0.0.0" # Listen on all interfaces

# Change default physiological parameters
physiological:
  age: 40
  gender: "female"
  activity: "walking"
```

### Adding Custom Scenarios

Add to `config/scenarios.json`:

```json
"my_custom_scenario": {
  "description": "My custom medical scenario",
  "physiological": {
    "heart_rate_bpm": 100,
    "spo2_percent": 95,
    "respiratory_rate": 20,
    "pulse_amplitude_red": 12000,
    "pulse_amplitude_ir": 11500
  }
}
```

## Troubleshooting

### Common Issues

**Server won't start:**

- Check if port is already in use: `netstat -an | findstr 8888`
- Try a different port in configuration

**Client can't connect:**

- Verify server is running
- Check host/port match server configuration
- Ensure firewall allows the connection

**No data received:**

- Check client is sending newline characters after commands
- Verify JSON format is correct
- Check server logs for errors

**Unrealistic data values:**

- Verify physiological parameters are in valid ranges
- Check scenario definitions for errors
- Review configuration files for mistakes

### Logging

The simulator uses Python's logging module. To increase log verbosity, modify the server:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Issues

For high sample rates (1000+ Hz):

- Ensure adequate CPU resources
- Consider reducing sample rate if needed
- Use appropriate buffer sizes in client applications

## Next Steps

- Read the [API Reference](api_reference.md) for detailed technical information
- Explore the [Scenario Guide](scenario_guide.md) for medical scenario details
- Check the [Architecture Overview](architecture.md) to understand the system design
- Review [Testing Guide](testing.md) for verification procedures
