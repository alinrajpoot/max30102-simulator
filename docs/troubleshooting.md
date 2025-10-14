# Troubleshooting Guide

Comprehensive guide to diagnosing and resolving common issues with the MAX30102 Simulator.

## Quick Reference

### Common Issues and Solutions

| Issue                | Possible Cause      | Solution                       |
| -------------------- | ------------------- | ------------------------------ |
| Server won't start   | Port already in use | Change port in configuration   |
| Client can't connect | Wrong host/port     | Verify server address and port |
| No data received     | Network issues      | Check firewall and connection  |
| Unrealistic data     | Invalid parameters  | Validate physiological ranges  |
| High CPU usage       | High sample rate    | Reduce sample rate             |

## Installation Issues

### Python Environment Problems

**Issue**: Python not found or wrong version

```bash
# Check Python version
python --version
python3 --version

# If Python 3.8+ not found, install it:
# Windows: Download from python.org
# macOS: brew install python
# Linux: sudo apt install python3 python3-pip
```

**Issue**: Module not found errors

```bash
# Verify all dependencies are installed
pip list | grep -E "numpy|scipy|pyserial"

# Reinstall requirements
pip install -r requirements.txt

# For development, install extra dependencies
pip install -r requirements.txt
pip install black flake8 mypy pytest-cov
```

**Issue**: Permission errors on installation

```bash
# Use virtual environment to avoid permission issues
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## Server Issues

### Server Won't Start

**Issue**: Port already in use

```bash
# Check what's using the port
netstat -an | findstr 8888  # Windows
lsof -i :8888               # Linux/macOS

# Change port in config/default.yaml
tcp_server:
  port: 9999  # Use different port
```

**Issue**: Address already in use

```bash
# Check if another instance is running
ps aux | grep python        # Linux/macOS
tasklist | grep python      # Windows

# Kill existing processes if needed
pkill -f "python.*server.py"  # Linux/macOS
```

**Issue**: Permission denied

```bash
# On Linux/macOS, ports below 1024 require root
# Use port above 1024 or run with sudo (not recommended)
python src/simulator/server.py --port 8888
```

### Server Starts But Immediately Stops

**Issue**: Configuration errors

```bash
# Check for configuration file issues
python -c "import yaml; yaml.safe_load(open('config/default.yaml'))"

# Verify scenarios file
python -c "import json; json.load(open('config/scenarios.json'))"
```

**Issue**: Missing dependencies

```bash
# Check for import errors
python -c "from src.simulator.server import TCPServer"

# If errors, check missing packages
pip install -r requirements.txt --force-reinstall
```

## Client Connection Issues

### Client Can't Connect to Server

**Issue**: Wrong host or port

```python
# Verify server is running on expected address
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('localhost', 8888))
if result == 0:
    print("Port is open")
else:
    print("Port is not open")
sock.close()
```

**Issue**: Firewall blocking connection

```bash
# Check firewall settings
# Windows: Windows Defender Firewall
# Linux: sudo ufw status
# macOS: System Preferences > Security & Privacy > Firewall

# Temporarily disable firewall for testing (be cautious)
# Windows: netsh advfirewall set allprofiles state off
# Linux: sudo ufw disable
```

**Issue**: Server binding to wrong interface

```yaml
# In config/default.yaml, ensure correct host
tcp_server:
  host: "0.0.0.0" # Listen on all interfaces
  port: 8888
```

### Connection Drops Intermittently

**Issue**: Network instability

```python
# Implement reconnection logic in client
import time
import socket

def connect_with_retry(host, port, max_retries=5):
    for attempt in range(max_retries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            return sock
        except (ConnectionRefusedError, socket.timeout) as e:
            print(f"Connection attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
    raise ConnectionError("Failed to connect after multiple attempts")
```

**Issue**: Server overload

```bash
# Check server resource usage
top | grep python    # Linux/macOS
tasklist | grep python  # Windows

# Reduce sample rate if CPU usage is high
# In config/default.yaml:
sensor:
  sample_rate: 500  # Reduce from 1000 to 500 Hz
```

## Data Quality Issues

### Unrealistic Physiological Values

**Issue**: Parameters outside physiological ranges

```python
# Validate parameters before setting
from models.physiological_model import PhysiologicalModel

model = PhysiologicalModel()

# Check if parameters are valid
parameters = {'heart_rate_bpm': 300}  # Too high
state = model.get_current_state()
print(f"Current HR range: 30-220, attempted: {parameters['heart_rate_bpm']}")

# The model will clamp values, but better to validate first
```

**Issue**: Scenario configuration errors

```bash
# Validate scenarios file
python -c "
import json
with open('config/scenarios.json') as f:
    data = json.load(f)
print('Scenarios file is valid')
"

# Check individual scenario parameters
python -c "
from models.scenarios import ScenarioManager
manager = ScenarioManager()
for name, scenario in manager.get_all_scenarios().items():
    errors = manager.validate_scenario_parameters(scenario.get('physiological', {}))
    if errors:
        print(f'Scenario {name} errors: {errors}')
"
```

### No Data Received

**Issue**: Client not reading data properly

```python
# Ensure client is reading from socket continuously
import socket
import json

def receive_data_properly(sock):
    buffer = ""
    while True:
        data = sock.recv(4096).decode('utf-8')
        if not data:
            break
        buffer += data
        lines = buffer.split('\n')
        buffer = lines[-1]  # Keep incomplete line

        for line in lines[:-1]:
            if line.strip():
                try:
                    message = json.loads(line)
                    print(f"Received: {message}")
                except json.JSONDecodeError as e:
                    print(f"JSON error: {e}, data: {line}")
```

**Issue**: Server not sending data

```bash
# Check server logs for errors
python src/simulator/server.py

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Issues

### High CPU Usage

**Issue**: Sample rate too high

```yaml
# Reduce sample rate in config/default.yaml
sensor:
  sample_rate: 500 # Instead of 1000 Hz
```

**Issue**: Multiple clients connected

```python
# Monitor client connections
from src.simulator.server import TCPServer

server = TCPServer()
# Check server.clients list for connected clients
# Consider implementing client limits
```

**Issue**: Inefficient data processing

```python
# Optimize data generation
from src.simulator.data_generator import DataGenerator

# Use vectorized operations where possible
# Consider using numpy more efficiently
```

### Memory Leaks

**Issue**: Growing memory usage over time

```python
# Monitor memory usage
import psutil
import os

def check_memory_usage():
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.2f} MB")
    return memory_mb

# Call periodically to monitor
```

**Issue**: Unbounded buffer growth

```python
# Check for unbounded data structures
# In MAX30102Device, FIFO buffer should have fixed size
device = MAX30102Device()
print(f"FIFO size: {device.fifo_size}")
print(f"Current samples: {len(device.fifo_buffer)}")
```

## Configuration Issues

### Configuration File Errors

**Issue**: YAML syntax errors

```yaml
# Common YAML mistakes:
# - Using tabs instead of spaces
# - Incorrect indentation
# - Missing colons
# Example of correct format:
tcp_server:
  host: "localhost"
  port: 8888
  max_clients: 5
```

**Issue**: JSON syntax errors in scenarios

```json
// Common JSON mistakes:
// - Trailing commas
// - Missing quotes
// - Comments (not allowed in JSON)
// Example of correct format:
{
  "normal_resting": {
    "description": "Normal resting state",
    "physiological": {
      "heart_rate_bpm": 72,
      "spo2_percent": 98
    }
  }
}
```

### Invalid Parameter Values

**Issue**: Parameters outside valid ranges

```python
# Validate parameters before setting
from models.scenarios import ScenarioManager

manager = ScenarioManager()
parameters = {
    'heart_rate_bpm': 85,
    'spo2_percent': 97,
    'respiratory_rate': 16
}

errors = manager.validate_scenario_parameters(parameters)
if errors:
    print(f"Parameter errors: {errors}")
else:
    print("Parameters are valid")
```

## Network and Connectivity

### Cross-Platform Connectivity

**Issue**: Connecting between different machines

```bash
# On server machine, find IP address
ip addr show        # Linux
ipconfig           # Windows
ifconfig           # macOS

# Use actual IP address instead of localhost
python examples/client_example.py --host 192.168.1.100 --port 8888
```

**Issue**: Docker network issues

```dockerfile
# Ensure ports are properly exposed
EXPOSE 8888

# And mapped when running
docker run -p 8888:8888 max30102-simulator
```

**Issue**: VPN interference

```bash
# Temporary solution: disable VPN for testing
# Or configure VPN to allow local network traffic
```

## Debugging Techniques

### Enabling Debug Logging

```python
# Add to your application
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# For specific modules
logger = logging.getLogger('TCPServer')
logger.setLevel(logging.DEBUG)
```

### Using the Interactive Debugger

```python
# Insert breakpoints for debugging
import pdb

def problematic_function():
    pdb.set_trace()  # Execution will pause here
    # Use commands: n (next), s (step), c (continue), p (print)
    result = some_calculation()
    return result
```

### Data Validation Script

```python
#!/usr/bin/env python3
"""
Data validation script for troubleshooting
"""

import json
import yaml
from models.physiological_model import PhysiologicalModel
from models.scenarios import ScenarioManager

def validate_system():
    print("=== System Validation ===")

    # Check configuration files
    try:
        with open('config/default.yaml') as f:
            config = yaml.safe_load(f)
        print("✓ Configuration file is valid")
    except Exception as e:
        print(f"✗ Configuration error: {e}")

    try:
        with open('config/scenarios.json') as f:
            scenarios = json.load(f)
        print("✓ Scenarios file is valid")
    except Exception as e:
        print(f"✗ Scenarios error: {e}")

    # Check physiological model
    try:
        model = PhysiologicalModel()
        state = model.get_current_state()
        print("✓ Physiological model initialized")

        # Validate state
        if 60 <= state['heart_rate_bpm'] <= 80:
            print("✓ Heart rate in normal range")
        else:
            print(f"✗ Abnormal heart rate: {state['heart_rate_bpm']}")

    except Exception as e:
        print(f"✗ Physiological model error: {e}")

    # Check scenarios
    try:
        manager = ScenarioManager()
        scenarios = manager.get_all_scenarios()
        print(f"✓ Loaded {len(scenarios)} scenarios")

        for name in ['normal_resting', 'heart_attack', 'running']:
            if name in scenarios:
                print(f"✓ Scenario '{name}' exists")
            else:
                print(f"✗ Scenario '{name}' missing")

    except Exception as e:
        print(f"✗ Scenario manager error: {e}")

if __name__ == "__main__":
    validate_system()
```

## Common Error Messages

### Python Errors

**`ModuleNotFoundError: No module named 'src'`**

- Solution: Run from project root directory or set PYTHONPATH

**`Address already in use`**

- Solution: Change port or kill existing process

**`Connection refused`**

- Solution: Ensure server is running and accessible

**`JSONDecodeError`**

- Solution: Check data format and ensure newlines between messages

### Application-Specific Errors

**`Scenario not found`**

- Solution: Check scenario name spelling in scenarios.json

**`Invalid parameter`**

- Solution: Verify parameter names and ranges

**`FIFO overflow`**

- Solution: Client is reading data too slowly, increase buffer size

## Performance Optimization

### Reducing Resource Usage

```yaml
# In config/default.yaml
sensor:
  sample_rate: 250 # Lower sample rate for less CPU usage

tcp_server:
  max_clients: 3 # Limit concurrent connections
```

### Optimizing Client Code

```python
# Use buffered reads and efficient JSON parsing
import socket
import json

class EfficientClient:
    def __init__(self):
        self.buffer = ""

    def receive_data(self, sock):
        # Read larger chunks
        data = sock.recv(8192).decode('utf-8')
        self.buffer += data

        # Process complete messages
        messages = self.buffer.split('\n')
        self.buffer = messages[-1]  # Keep partial message

        for message in messages[:-1]:
            if message.strip():
                try:
                    data = json.loads(message)
                    self.process_message(data)
                except json.JSONDecodeError:
                    print(f"Invalid JSON: {message}")
```

## Getting Help

### Collecting Diagnostic Information

When asking for help, include:

1. **System Information**

```bash
python --version
pip list | grep -E "numpy|scipy|pyserial"
uname -a  # Linux/macOS
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"  # Windows
```

2. **Configuration Details**

```bash
# Share relevant configuration (remove sensitive info)
cat config/default.yaml | grep -E "(tcp_server|sensor):"
```

3. **Error Logs**

```bash
# Run with debug logging
python src/simulator/server.py 2>&1 | tee server.log
```

### Community Resources

- Check existing GitHub issues
- Review documentation
- Search for similar problems
- Create minimal reproduction case

## Prevention Best Practices

### Regular Maintenance

1. **Keep dependencies updated**

```bash
pip list --outdated
pip install -U -r requirements.txt
```

2. **Validate configurations after changes**

```bash
python -m py_compile config/default.yaml
python -c "import json; json.load(open('config/scenarios.json'))"
```

3. **Monitor system resources**

```bash
# Set up monitoring for long-running servers
watch "ps aux | grep python"  # Linux/macOS
```

### Development Practices

1. **Use version control**
2. **Write tests for new features**
3. **Validate inputs and parameters**
4. **Implement proper error handling**
5. **Use logging for debugging**

By following this troubleshooting guide, you should be able to resolve most issues with the MAX30102 Simulator. If problems persist, please collect the diagnostic information above and create an issue on the project repository.
