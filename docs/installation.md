# Installation Guide

This guide will help you install and set up the MAX30102 Simulator on your system.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

## Step 1: Clone the Repository

```bash
git clone https://github.com/alinrajpoot/max30102-simulator.git
cd max30102-simulator
```

## Step 2: Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Verify Installation

Run the basic test to verify everything is working:

```bash
python -m pytest tests/test_physiological_model.py -v
```

You should see all tests passing.

## Step 5: Start the Simulator

```bash
python src/simulator/server.py
```

The simulator should start and display:

```
INFO - TCPServer - MAX30102 Simulator TCP Server started on localhost:8888
```

## Alternative Installation Methods

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8888
CMD ["python", "src/simulator/server.py"]
```

Build and run:

```bash
docker build -t max30102-simulator .
docker run -p 8888:8888 max30102-simulator
```

### Development Installation

For development, install additional dependencies:

```bash
pip install -r requirements.txt
pip install black flake8 mypy pytest-cov
```

## Platform-Specific Notes

### Windows

- Ensure Python is added to your PATH
- Use Command Prompt or PowerShell with administrator privileges if encountering permission issues

### macOS

- Python 3.8+ can be installed via Homebrew: `brew install python`

### Linux

- On Ubuntu/Debian: `sudo apt update && sudo apt install python3 python3-pip python3-venv`
- On CentOS/RHEL: `sudo yum install python3 python3-pip`

## Verifying the Installation

1. Start the simulator: `python src/simulator/server.py`
2. In another terminal, run the example client: `python examples/client_example.py --duration 5`
3. You should see physiological data streaming in the client terminal

## Next Steps

- Read the [Quick Start Guide](quickstart.md) to begin using the simulator
- Check out the [User Manual](user_manual.md) for detailed usage instructions
- Explore the [Scenario Guide](scenario_guide.md) to learn about medical scenarios
