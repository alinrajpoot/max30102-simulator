# Quick Start Guide

Get up and running with the MAX30102 Simulator in 5 minutes or less.

## 🚀 5-Minute Quick Start

### Step 1: Start the Simulator Server

```bash
python src/simulator/server.py
```

You should see:

```
INFO - TCPServer - MAX30102 Simulator TCP Server started on localhost:8888
```

### Step 2: Connect with the Example Client

Open a new terminal and run:

```bash
python examples/client_example.py --duration 10
```

You'll see real-time physiological data streaming:

```
Sample   Timestamp          Red PPG     IR PPG      HR      SpO2        Activity    Condition
------------------------------------------------------------------------------------------------
     1   1635786300.123     12543       11876       72.5    98.2        resting     normal
     2   1635786300.124     12601       11921       72.5    98.2        resting     normal
```

### Step 3: Change Physiological Parameters

While the server is running, open another terminal and run:

```bash
python examples/client_example.py --activity running --duration 5
```

Watch the heart rate increase as the activity changes to running!

## 🎯 Basic Usage Examples

### Example 1: Monitor Normal Resting Data

```bash
# Terminal 1 - Start server
python src/simulator/server.py

# Terminal 2 - Monitor data
python examples/client_example.py --duration 30
```

### Example 2: Simulate Different Scenarios

```bash
# Terminal 2 - Run scenario demonstration
python examples/scenario_demo.py
```

This will automatically cycle through all available medical scenarios.

### Example 3: Custom Parameter Configuration

```bash
# Set specific parameters
python examples/client_example.py --age 45 --gender female --activity walking --duration 20
```

## 📊 Understanding the Data

The simulator generates the following data in real-time:

| Field        | Description                                 | Typical Range                       |
| ------------ | ------------------------------------------- | ----------------------------------- |
| `timestamp`  | Unix timestamp with milliseconds            | Current time                        |
| `red_ppg`    | Red LED photoplethysmography raw value      | 40,000-60,000                       |
| `ir_ppg`     | Infrared LED photoplethysmography raw value | 38,000-58,000                       |
| `heart_rate` | Calculated heart rate in BPM                | 40-180 BPM                          |
| `spO2`       | Blood oxygen saturation percentage          | 70-100%                             |
| `activity`   | Current activity level                      | resting, walking, running, etc.     |
| `condition`  | Medical condition                           | normal, heart_attack, anxiety, etc. |

## 🎮 Real-time Control

You can change parameters while the simulator is running:

### Using the Example Client

```python
from examples.client_example import MAX30102Client

client = MAX30102Client()
client.connect()

# Change to heart attack scenario
client.set_scenario('heart_attack')

# Set custom parameters
client.set_parameters({
    'age': 65,
    'activity': 'resting',
    'condition': 'heart_attack'
})

# Receive data for 30 seconds
client.receive_data(30)

client.disconnect()
```

## 🔧 Common Configuration Changes

### Change Sample Rate

Modify `config/default.yaml`:

```yaml
sensor:
  sample_rate: 500 # Change from 1000 to 500 Hz
```

### Change TCP Port

Modify `config/default.yaml`:

```yaml
tcp_server:
  port: 9999 # Change from 8888 to 9999
```

### Adjust Physiological Parameters

```bash
python examples/client_example.py --age 25 --gender male --activity running --duration 10
```

## 🆘 Getting Help

If you encounter issues:

1. Check that the server is running on the correct port
2. Verify all dependencies are installed (`pip list`)
3. Check the [Troubleshooting Guide](troubleshooting.md)
4. Review the [User Manual](user_manual.md) for detailed instructions

## Next Steps

- Read the [User Manual](user_manual.md) for comprehensive usage instructions
- Explore the [Scenario Guide](scenario_guide.md) for medical scenario details
- Check the [API Reference](api_reference.md) for programmatic usage
