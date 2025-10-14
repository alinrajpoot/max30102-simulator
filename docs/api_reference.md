# API Reference

Complete API documentation for the MAX30102 Simulator.

## Table of Contents

1. [Core Classes](#core-classes)
2. [TCP Server API](#tcp-server-api)
3. [Physiological Model API](#physiological-model-api)
4. [Data Generator API](#data-generator-api)
5. [MAX30102 Device API](#max30102-device-api)
6. [I2C Protocol API](#i2c-protocol-api)
7. [Scenario Manager API](#scenario-manager-api)

## Core Classes

### TCPServer

Main TCP server class that handles client connections and data streaming.

**Location**: `src/simulator/server.py`

```python
class TCPServer:
    def __init__(self, host: str = 'localhost', port: int = 8888)
    def start_server(self) -> bool
    def stop_server(self)
    def handle_client_message(self, client_socket: socket.socket, message: str)
```

### PhysiologicalModel

Models human physiological responses and manages parameter state.

**Location**: `src/models/physiological_model.py`

```python
class PhysiologicalModel:
    def __init__(self)
    def update_parameters(self, parameters: Dict[str, Any]) -> bool
    def set_scenario(self, scenario_name: str) -> bool
    def get_current_state(self) -> Dict[str, Any]
    def reset_to_defaults(self)
    def simulate_stress_response(self, stress_level: float)
    def get_physiological_summary(self) -> Dict[str, Any]
```

### DataGenerator

Generates realistic PPG waveform data.

**Location**: `src/simulator/data_generator.py`

```python
class DataGenerator:
    def __init__(self, physio_model: PhysiologicalModel)
    def generate_data_point(self) -> Dict[str, any]
    def set_sample_rate(self, sample_rate: int)
```

## TCP Server API

### TCPServer Constructor

```python
def __init__(self, host: str = 'localhost', port: int = 8888)
```

**Parameters:**

- `host` (str): Hostname or IP address to bind to
- `port` (int): TCP port number

**Example:**

```python
server = TCPServer(host='0.0.0.0', port=9999)
```

### start_server

```python
def start_server(self) -> bool
```

Starts the TCP server and begins accepting connections.

**Returns:**

- `bool`: True if server started successfully, False otherwise

**Example:**

```python
if server.start_server():
    print("Server started successfully")
else:
    print("Failed to start server")
```

### stop_server

```python
def stop_server(self)
```

Stops the server and cleans up resources.

**Example:**

```python
server.stop_server()
```

### handle_client_message

```python
def handle_client_message(self, client_socket: socket.socket, message: str)
```

Process incoming messages from clients.

**Parameters:**

- `client_socket` (socket.socket): Client socket object
- `message` (str): Raw message string from client

## Physiological Model API

### PhysiologicalModel Constructor

```python
def __init__(self)
```

Creates a new physiological model with default parameters.

**Example:**

```python
model = PhysiologicalModel()
```

### update_parameters

```python
def update_parameters(self, parameters: Dict[str, Any]) -> bool
```

Updates physiological parameters and recalculates dependent values.

**Parameters:**

- `parameters` (Dict[str, Any]): Dictionary of parameters to update

**Returns:**

- `bool`: True if update successful, False otherwise

**Example:**

```python
success = model.update_parameters({
    'age': 35,
    'gender': 'female',
    'activity': 'walking'
})
```

### set_scenario

```python
def set_scenario(self, scenario_name: str) -> bool
```

Applies a pre-defined physiological scenario.

**Parameters:**

- `scenario_name` (str): Name of the scenario to apply

**Returns:**

- `bool`: True if scenario applied successfully, False otherwise

**Example:**

```python
success = model.set_scenario('heart_attack')
```

### get_current_state

```python
def get_current_state(self) -> Dict[str, Any]
```

Returns the current physiological state as a dictionary.

**Returns:**

- `Dict[str, Any]`: Current physiological parameters

**Example:**

```python
state = model.get_current_state()
print(f"Heart rate: {state['heart_rate_bpm']} bpm")
```

### reset_to_defaults

```python
def reset_to_defaults(self)
```

Resets the model to default parameter values.

**Example:**

```python
model.reset_to_defaults()
```

### simulate_stress_response

```python
def simulate_stress_response(self, stress_level: float)
```

Simulates a stress response with adjustable intensity.

**Parameters:**

- `stress_level` (float): Stress level from 0.0 (none) to 1.0 (extreme)

**Example:**

```python
model.simulate_stress_response(0.7)  # Moderate stress
```

### get_physiological_summary

```python
def get_physiological_summary(self) -> Dict[str, Any]
```

Returns a summary of key physiological metrics.

**Returns:**

- `Dict[str, Any]`: Summary of physiological state

**Example:**

```python
summary = model.get_physiological_summary()
print(f"Age: {summary['age']}, HR: {summary['heart_rate']}bpm")
```

## Data Generator API

### DataGenerator Constructor

```python
def __init__(self, physio_model: PhysiologicalModel)
```

Creates a new data generator linked to a physiological model.

**Parameters:**

- `physio_model` (PhysiologicalModel): Physiological model instance

**Example:**

```python
data_gen = DataGenerator(physio_model)
```

### generate_data_point

```python
def generate_data_point(self) -> Dict[str, any]
```

Generates a single data point with PPG waveforms and vital signs.

**Returns:**

- `Dict[str, any]`: Data point with timestamp, PPG data, and vital signs

**Example:**

```python
data_point = data_gen.generate_data_point()
red_ppg = data_point['red_ppg']
heart_rate = data_point['heart_rate']
```

### set_sample_rate

```python
def set_sample_rate(self, sample_rate: int)
```

Sets the sample rate for data generation.

**Parameters:**

- `sample_rate` (int): Samples per second

**Example:**

```python
data_gen.set_sample_rate(500)  # 500 Hz
```

## MAX30102 Device API

### MAX30102Device Constructor

```python
def __init__(self)
```

Creates a new MAX30102 device simulator.

**Example:**

```python
device = MAX30102Device()
```

### write_register

```python
def write_register(self, register: int, value: int) -> bool
```

Writes a value to a device register.

**Parameters:**

- `register` (int): Register address
- `value` (int): Value to write (0-255)

**Returns:**

- `bool`: True if write successful, False otherwise

**Example:**

```python
device.write_register(0x0C, 0x24)  # Set LED1 pulse amplitude
```

### read_register

```python
def read_register(self, register: int) -> Optional[int]
```

Reads a value from a device register.

**Parameters:**

- `register` (int): Register address

**Returns:**

- `Optional[int]`: Register value or None if error

**Example:**

```python
value = device.read_register(0x00)  # Read interrupt status
```

### push_sample_to_fifo

```python
def push_sample_to_fifo(self, red_sample: int, ir_sample: int)
```

Pushes a new PPG sample to the FIFO buffer.

**Parameters:**

- `red_sample` (int): Red LED sample value (18-bit)
- `ir_sample` (int): IR LED sample value (18-bit)

**Example:**

```python
device.push_sample_to_fifo(15000, 14500)
```

### get_status

```python
def get_status(self) -> Dict[str, any]
```

Returns current device status.

**Returns:**

- `Dict[str, any]`: Device status information

**Example:**

```python
status = device.get_status()
print(f"FIFO samples: {status['fifo_samples']}")
```

### get_sample_rate

```python
def get_sample_rate(self) -> int
```

Calculates current sample rate from configuration.

**Returns:**

- `int`: Current sample rate in Hz

**Example:**

```python
sample_rate = device.get_sample_rate()
```

## I2C Protocol API

### I2CProtocolSimulator Constructor

```python
def __init__(self, device_address: int = 0x57)
```

Creates a new I2C protocol simulator.

**Parameters:**

- `device_address` (int): I2C device address (default 0x57 for MAX30102)

**Example:**

```python
i2c = I2CProtocolSimulator(device_address=0x57)
```

### write_register

```python
def write_register(self, register: int, value: int) -> bool
```

Simulates writing to a MAX30102 register over I2C.

**Parameters:**

- `register` (int): Register address
- `value` (int): Value to write

**Returns:**

- `bool`: Success status

**Example:**

```python
i2c.write_register(0x09, 0x03)  # Set to SpO2 mode
```

### read_register

```python
def read_register(self, register: int) -> Optional[int]
```

Simulates reading from a MAX30102 register over I2C.

**Parameters:**

- `register` (int): Register address

**Returns:**

- `Optional[int]`: Register value or None if error

**Example:**

```python
value = i2c.read_register(0xFF)  # Read part ID
```

### read_registers_burst

```python
def read_registers_burst(self, start_register: int, count: int) -> Optional[List[int]]
```

Simulates burst read of multiple registers.

**Parameters:**

- `start_register` (int): Starting register address
- `count` (int): Number of registers to read

**Returns:**

- `Optional[List[int]]`: List of register values or None if error

**Example:**

```python
values = i2c.read_registers_burst(0x07, 6)  # Read FIFO data
```

### push_sample_to_fifo

```python
def push_sample_to_fifo(self, red_sample: int, ir_sample: int)
```

Pushes a new PPG sample to the FIFO buffer.

**Parameters:**

- `red_sample` (int): Red LED sample (18-bit)
- `ir_sample` (int): IR LED sample (18-bit)

**Example:**

```python
i2c.push_sample_to_fifo(12000, 11500)
```

### read_fifo_samples

```python
def read_fifo_samples(self, sample_count: int) -> List[Tuple[int, int]]
```

Reads samples from FIFO and converts back to 18-bit values.

**Parameters:**

- `sample_count` (int): Number of samples to read

**Returns:**

- `List[Tuple[int, int]]`: List of (red_sample, ir_sample) tuples

**Example:**

```python
samples = i2c.read_fifo_samples(4)
for red, ir in samples:
    print(f"Red: {red}, IR: {ir}")
```

### get_device_status

```python
def get_device_status(self) -> Dict[str, Any]
```

Returns current device status and statistics.

**Returns:**

- `Dict[str, Any]`: Device status information

**Example:**

```python
status = i2c.get_device_status()
print(f"Sample rate: {status['sample_rate']} Hz")
```

## Scenario Manager API

### ScenarioManager Constructor

```python
def __init__(self, scenarios_file: Optional[str] = None)
```

Creates a new scenario manager.

**Parameters:**

- `scenarios_file` (Optional[str]): Path to scenarios JSON file

**Example:**

```python
scenario_mgr = ScenarioManager()
```

### get_scenario

```python
def get_scenario(self, scenario_name: str) -> Optional[Dict[str, Any]]
```

Retrieves a specific scenario by name.

**Parameters:**

- `scenario_name` (str): Name of the scenario

**Returns:**

- `Optional[Dict[str, Any]]`: Scenario dictionary or None if not found

**Example:**

```python
scenario = scenario_mgr.get_scenario('heart_attack')
```

### get_all_scenarios

```python
def get_all_scenarios(self) -> Dict[str, Dict[str, Any]]
```

Returns all available scenarios.

**Returns:**

- `Dict[str, Dict[str, Any]]`: Dictionary of all scenarios

**Example:**

```python
all_scenarios = scenario_mgr.get_all_scenarios()
```

### create_custom_scenario

```python
def create_custom_scenario(self, name: str, description: str,
                         physiological_params: Dict[str, Any]) -> bool
```

Creates a new custom scenario.

**Parameters:**

- `name` (str): Scenario name
- `description` (str): Scenario description
- `physiological_params` (Dict[str, Any]): Physiological parameters

**Returns:**

- `bool`: Success status

**Example:**

```python
success = scenario_mgr.create_custom_scenario(
    'my_scenario',
    'Custom test scenario',
    {'heart_rate_bpm': 100, 'spo2_percent': 97}
)
```

### validate_scenario_parameters

```python
def validate_scenario_parameters(self, params: Dict[str, Any]) -> List[str]
```

Validates physiological parameters for a scenario.

**Parameters:**

- `params` (Dict[str, Any]): Parameters to validate

**Returns:**

- `List[str]`: List of validation errors (empty if valid)

**Example:**

```python
errors = scenario_mgr.validate_scenario_parameters({
    'heart_rate_bpm': 300,  # Invalid - too high
    'spo2_percent': 95      # Valid
})
```

## Data Structures

### PhysiologicalState

Dataclass representing physiological state.

**Location**: `src/models/physiological_model.py`

```python
@dataclass
class PhysiologicalState:
    age: int = 30
    gender: str = "male"
    weight_kg: float = 70.0
    height_cm: float = 175.0
    activity: str = "resting"
    condition: str = "normal"
    fitness_level: str = "average"
    heart_rate_bpm: float = 72.0
    spo2_percent: float = 98.0
    respiratory_rate: int = 16
    pulse_amplitude_red: int = 10000
    pulse_amplitude_ir: int = 9500
    baseline_red: int = 50000
    baseline_ir: int = 48000
    noise_level: float = 0.05
    motion_artifact_probability: float = 0.1
    motion_artifact_duration: float = 0.5
    heart_rate_variability: str = "normal"
    pulse_rhythm: str = "regular"
    pulse_quality: str = "normal"
```

## Error Handling

All API methods that can fail return boolean success status or raise appropriate exceptions. Check return values and handle errors appropriately in client code.

**Example:**

```python
if not model.set_scenario('invalid_scenario'):
    print("Failed to set scenario")
```

## Thread Safety

- **TCPServer**: Thread-safe for multiple client connections
- **PhysiologicalModel**: Not thread-safe (use locks if accessing from multiple threads)
- **DataGenerator**: Not thread-safe
- **MAX30102Device**: Basic thread safety for register access
- **I2CProtocolSimulator**: Basic thread safety

For multi-threaded applications, use appropriate synchronization mechanisms when accessing shared resources.
