# MAX30102 Physiological Simulator

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)

A high-fidelity TCP-based simulator for the MAX30102 pulse oximeter and heart-rate sensor. This tool generates realistic PPG waveform data and mimics actual register-based communication for testing AI platforms and medical device integrations.

## 🚀 Features

- **Realistic PPG Data Generation**: Raw red and infrared LED waveforms with medically accurate patterns
- **Register-Level Simulation**: Full MAX30102 register mapping and I2C communication emulation
- **Real-time TCP Streaming**: Live data streaming via TCP sockets for easy integration
- **Physiological Modeling**: Configurable parameters (age, gender, activity level) that influence data patterns
- **Medical Scenarios**: Pre-configured conditions:
  - Normal activities (resting, walking, running, sleeping, sex intercourse)
  - Emergency conditions (heart attack, extreme anxiety, shock, fear)
- **Real-time Configuration**: Dynamic parameter adjustment during simulation
- **Noise & Artifact Simulation**: Realistic motion artifacts and sensor noise

## 🛠️ Quick Start

### Prerequisites

- Python 3.8 or higher
- Required packages: `numpy`, `scipy`, `pyserial` (see requirements.txt)

### Installation

```bash
git clone https://github.com/alinrajpoot/max30102-simulator.git
cd max30102-simulator
pip install -r requirements.txt
```

### Basic Usage

```bash
# Start the simulator server
python src/simulator/server.py

# In another terminal, connect to the simulator
python examples/client_example.py
```

## 📡 TCP Protocol

The simulator communicates via TCP on port 8888 (configurable). Clients can send configuration commands and receive real-time data streams.

**Example Command Format:**

```json
{
  "command": "set_parameters",
  "age": 35,
  "gender": "male",
  "activity": "running",
  "condition": "normal"
}
```

**Data Output Format:**

```json
{
  "timestamp": 1635786300.123,
  "red_ppg": 12543,
  "ir_ppg": 11876,
  "heart_rate": 72.5,
  "spO2": 98.2,
  "status": "normal"
}
```

## 🏗️ Project Structure

```
max30102-simulator/
├── src/simulator/          # Core simulation engine
├── src/models/             # Physiological models
├── src/protocols/          # Communication protocols
├── config/                 # Configuration files
├── examples/               # Client examples
├── tests/                  # Unit tests
└── docs/                   # Documentation
```

## 🔧 Configuration

Modify `config/default.yaml` to adjust:

- Sensor parameters (sample rate, LED pulse width)
- TCP server settings (port, host)
- Default physiological parameters
- Scenario definitions

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the Apache-2.0 License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Based on MAX30102 specifications from Maxim Integrated
- Physiological models inspired by clinical research papers
- Waveform generation using signal processing best practices
