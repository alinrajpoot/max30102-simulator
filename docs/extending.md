# Extending the Simulator

Comprehensive guide for developers who want to extend and customize the MAX30102 Simulator.

## Overview

The MAX30102 Simulator is designed to be extensible. This guide covers how to add new features, modify existing components, and integrate custom functionality.

## Architecture Overview

### Core Components

The simulator follows a modular architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   TCP Server    │    │ Physiological    │    │  Data Generator │
│                 │    │     Model        │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌──────────────────┐
                    │  Configuration   │
                    │     Files        │
                    └──────────────────┘
```

## Adding New Physiological Parameters

### Step 1: Extend PhysiologicalState

```python
from dataclasses import dataclass
from .physiological_model import PhysiologicalState

@dataclass
class ExtendedPhysiologicalState(PhysiologicalState):
    # Add new parameters
    blood_pressure_systolic: int = 120
    blood_pressure_diastolic: int = 80
    temperature_c: float = 37.0
    blood_glucose: float = 5.0  # mmol/L
    stress_level: float = 0.0   # 0.0 to 1.0

    # Custom waveform parameters
    waveform_shape: str = "normal"
    cardiac_output: float = 5.0  # L/min
```

### Step 2: Create Extended Physiological Model

```python
from src.models.physiological_model import PhysiologicalModel

class ExtendedPhysiologicalModel(PhysiologicalModel):
    def __init__(self):
        # Use extended state
        self.state = ExtendedPhysiologicalState()
        super().__init__()

    def _recalculate_physiology(self):
        # Call parent calculations first
        super()._recalculate_physiology()

        # Add custom calculations
        self._calculate_blood_pressure()
        self._calculate_temperature()
        self._calculate_cardiac_output()

    def _calculate_blood_pressure(self):
        # Custom blood pressure calculation based on other parameters
        base_systolic = 120
        base_diastolic = 80

        # Adjust based on heart rate and activity
        hr_factor = (self.state.heart_rate_bpm - 72) / 50  # Normalize
        activity_factor = self.activity_effects[self.state.activity].get('bp_factor', 1.0)

        self.state.blood_pressure_systolic = int(base_systolic * (1 + hr_factor * 0.3) * activity_factor)
        self.state.blood_pressure_diastolic = int(base_diastolic * (1 + hr_factor * 0.2) * activity_factor)

    def _calculate_temperature(self):
        # Temperature variations based on condition and activity
        base_temp = 37.0

        if self.state.condition == 'fever':
            base_temp = 38.5
        elif self.state.condition == 'hypothermia':
            base_temp = 35.0

        # Small variations based on activity
        activity_temp_effect = {
            'resting': 0.0,
            'walking': 0.2,
            'running': 0.8,
            'sleeping': -0.3
        }

        temp_adjustment = activity_temp_effect.get(self.state.activity, 0.0)
        self.state.temperature_c = base_temp + temp_adjustment

    def _calculate_cardiac_output(self):
        # Simplified cardiac output calculation
        # CO = HR × SV (simplified)
        stroke_volume = 70  # mL, approximate
        self.state.cardiac_output = (self.state.heart_rate_bpm * stroke_volume) / 1000  # L/min

    def set_custom_parameter(self, parameter: str, value: any):
        """Set custom parameters with validation"""
        if hasattr(self.state, parameter):
            # Add custom validation if needed
            if parameter == 'blood_glucose' and not (2.0 <= value <= 20.0):
                raise ValueError("Blood glucose must be between 2.0 and 20.0 mmol/L")

            setattr(self.state, parameter, value)
            self._recalculate_physiology()
        else:
            raise AttributeError(f"Unknown parameter: {parameter}")
```

## Creating Custom Medical Scenarios

### Method 1: Configuration-Based Scenarios

Add to `config/scenarios.json`:

```json
"diabetic_emergency": {
  "description": "Diabetic ketoacidosis simulation",
  "physiological": {
    "heart_rate_bpm": 110,
    "spo2_percent": 95,
    "respiratory_rate": 28,
    "respiratory_depth": "deep",  // Kussmaul breathing
    "blood_glucose": 22.5,        // Severe hyperglycemia
    "pulse_quality": "bounding",
    "temperature_c": 37.8
  },
  "symptoms": [
    "fruity_breath_odor",
    "frequent_urination",
    "extreme_thirst",
    "confusion",
    "abdominal_pain"
  ]
},

"sepsis": {
  "description": "Systemic inflammatory response syndrome",
  "physiological": {
    "heart_rate_bpm": 125,
    "spo2_percent": 88,
    "respiratory_rate": 32,
    "temperature_c": 39.2,
    "blood_pressure_systolic": 85,
    "blood_pressure_diastolic": 45,
    "pulse_quality": "thready"
  },
  "symptoms": [
    "fever",
    "chills",
    "low_blood_pressure",
    "tachypnea",
    "tachycardia"
  ]
}
```

### Method 2: Programmatic Scenario Creation

```python
from src.models.scenarios import ScenarioManager

class CustomScenarioManager(ScenarioManager):
    def __init__(self, scenarios_file=None):
        super().__init__(scenarios_file)
        self._add_custom_scenarios()

    def _add_custom_scenarios(self):
        """Add custom scenarios programmatically"""
        custom_scenarios = {
            'my_custom_emergency': {
                'description': 'Custom emergency condition',
                'physiological': {
                    'heart_rate_bpm': 140,
                    'spo2_percent': 82,
                    'respiratory_rate': 35,
                    'blood_glucose': 3.0,  # Hypoglycemia
                    'waveform_shape': 'irregular'
                }
            }
        }

        for name, scenario in custom_scenarios.items():
            if name not in self.scenarios:
                self.scenarios[name] = scenario

    def create_dynamic_scenario(self, base_scenario: str, modifications: dict):
        """Create a scenario by modifying an existing one"""
        base = self.get_scenario(base_scenario)
        if not base:
            raise ValueError(f"Base scenario not found: {base_scenario}")

        # Create modified scenario
        modified = base.copy()
        if 'physiological' in modifications:
            modified['physiological'] = {
                **base.get('physiological', {}),
                **modifications['physiological']
            }

        scenario_name = f"{base_scenario}_modified"
        self.scenarios[scenario_name] = modified
        return scenario_name
```

## Custom Data Generation

### Extended Data Generator

```python
from src.simulator.data_generator import DataGenerator

class ExtendedDataGenerator(DataGenerator):
    def __init__(self, physio_model):
        super().__init__(physio_model)
        # Initialize custom state
        self.custom_waveform_phase = 0.0

    def generate_data_point(self) -> Dict[str, any]:
        # Get base data point
        data_point = super().generate_data_point()

        # Add custom parameters
        data_point.update({
            'blood_pressure_systolic': self.physio_model.state.blood_pressure_systolic,
            'blood_pressure_diastolic': self.physio_model.state.blood_pressure_diastolic,
            'temperature_c': self.physio_model.state.temperature_c,
            'blood_glucose': self.physio_model.state.blood_glucose,
            'cardiac_output': self.physio_model.state.cardiac_output,
            'signal_quality': self._calculate_signal_quality()
        })

        return data_point

    def _generate_ppg_waveforms(self) -> Tuple[float, float]:
        # Custom waveform generation based on extended parameters
        if self.physio_model.state.waveform_shape == "pulsus_alternans":
            return self._generate_alternans_waveform()
        elif self.physio_model.state.waveform_shape == "pulsus_paradoxus":
            return self._generate_paradoxus_waveform()
        else:
            return super()._generate_ppg_waveforms()

    def _generate_alternans_waveform(self):
        """Generate pulsus alternans pattern (alternating strong/weak beats)"""
        t = self.time_index * (self.heart_rate / 60.0) * 2 * np.pi

        # Alternating amplitude
        alternans_factor = 0.3  # 30% variation
        beat_variation = 1.0 + (alternans_factor if int(t / (2 * np.pi)) % 2 == 0 else -alternans_factor)

        cardiac_signal = (np.sin(t) ** 3 + 0.3 * np.sin(2 * t - np.pi/4) ** 2) * beat_variation

        red_signal = self.baseline_red + self.pulse_amplitude_red * cardiac_signal
        ir_signal = self.baseline_ir + self.pulse_amplitude_ir * cardiac_signal * 0.95

        return red_signal, ir_signal

    def _generate_paradoxus_waveform(self):
        """Generate pulsus paradoxus pattern (respiratory variation in pulse amplitude)"""
        t = self.time_index * (self.heart_rate / 60.0) * 2 * np.pi

        # Strong respiratory modulation
        respiratory_modulation = 0.3 * np.sin(self.respiratory_phase)

        cardiac_signal = np.sin(t) ** 3 + 0.3 * np.sin(2 * t - np.pi/4) ** 2
        modulated_signal = cardiac_signal * (1 + respiratory_modulation)

        red_signal = self.baseline_red + self.pulse_amplitude_red * modulated_signal
        ir_signal = self.baseline_ir + self.pulse_amplitude_ir * modulated_signal * 0.95

        return red_signal, ir_signal

    def _calculate_signal_quality(self) -> float:
        """Calculate overall signal quality metric (0.0 to 1.0)"""
        quality_factors = []

        # Signal strength factor
        strength_factor = min(1.0, (self.pulse_amplitude_red / 10000))
        quality_factors.append(strength_factor)

        # Noise factor (inverse)
        noise_factor = max(0.0, 1.0 - (self.noise_level / 0.1))
        quality_factors.append(noise_factor)

        # Motion artifact factor
        motion_factor = 1.0 - (self.physio_model.state.motion_artifact_probability / 0.5)
        quality_factors.append(motion_factor)

        return sum(quality_factors) / len(quality_factors)
```

## Custom TCP Protocol Extensions

### Extended TCP Server

```python
from src.simulator.server import TCPServer

class ExtendedTCPServer(TCPServer):
    def __init__(self, host='localhost', port=8888):
        # Use extended models
        self.physio_model = ExtendedPhysiologicalModel()
        self.data_gen = ExtendedDataGenerator(self.physio_model)
        super().__init__(host, port)

    def handle_client_message(self, client_socket, message: str):
        try:
            data = json.loads(message.strip())
            command = data.get('command', '')

            # Handle custom commands first
            if command == 'set_custom_parameter':
                self._handle_custom_parameter(client_socket, data)
            elif command == 'get_extended_status':
                self._handle_extended_status(client_socket, data)
            else:
                # Fall back to parent implementation
                super().handle_client_message(client_socket, message)

        except json.JSONDecodeError as e:
            self._send_error(client_socket, f"Invalid JSON: {e}")

    def _handle_custom_parameter(self, client_socket, data):
        """Handle custom parameter setting"""
        parameter = data.get('parameter')
        value = data.get('value')

        try:
            if hasattr(self.physio_model.state, parameter):
                setattr(self.physio_model.state, parameter, value)
                self.physio_model._recalculate_physiology()

                response = {
                    "type": "command_response",
                    "command": "set_custom_parameter",
                    "success": True,
                    "parameter": parameter,
                    "value": value,
                    "new_state": self.physio_model.get_current_state()
                }
            else:
                response = {
                    "type": "command_response",
                    "command": "set_custom_parameter",
                    "success": False,
                    "error": f"Unknown parameter: {parameter}"
                }

            self._send_to_client(client_socket, response)

        except Exception as e:
            self._send_error(client_socket, f"Error setting parameter: {e}")

    def _handle_extended_status(self, client_socket, data):
        """Provide extended status information"""
        status = {
            "type": "command_response",
            "command": "get_extended_status",
            "success": True,
            "status": {
                "clients_connected": len(self.clients),
                "model_state": self.physio_model.get_current_state(),
                "sensor_status": self.max30102.get_status(),
                "data_generation_stats": self._get_generation_stats(),
                "system_metrics": self._get_system_metrics()
            }
        }

        self._send_to_client(client_socket, status)

    def _get_generation_stats(self):
        """Get data generation statistics"""
        return {
            "samples_generated": self.data_gen.sample_count,
            "current_sample_rate": self.data_gen.sample_rate,
            "data_points_sent": getattr(self, 'data_points_sent', 0),
            "average_generation_time": getattr(self, 'avg_generation_time', 0)
        }

    def _get_system_metrics(self):
        """Get system performance metrics"""
        import psutil
        import os

        process = psutil.Process(os.getpid())

        return {
            "memory_usage_mb": process.memory_info().rss / 1024 / 1024,
            "cpu_percent": process.cpu_percent(),
            "threads_count": process.num_threads(),
            "uptime_seconds": time.time() - getattr(self, 'start_time', time.time())
        }
```

## Adding New Communication Protocols

### WebSocket Protocol Support

```python
import asyncio
import websockets
import json

class WebSocketServer:
    def __init__(self, physio_model, data_generator, host='localhost', port=8765):
        self.physio_model = physio_model
        self.data_generator = data_generator
        self.host = host
        self.port = port
        self.clients = set()
        self.running = False

    async def start_server(self):
        """Start WebSocket server"""
        self.running = True
        start_server = websockets.serve(self.handle_client, self.host, self.port)

        print(f"WebSocket server started on ws://{self.host}:{self.port}")
        await start_server

    async def handle_client(self, websocket, path):
        """Handle new WebSocket client connection"""
        self.clients.add(websocket)
        print(f"New WebSocket client connected. Total clients: {len(self.clients)}")

        try:
            # Send welcome message
            welcome_msg = {
                "type": "welcome",
                "message": "Connected to MAX30102 WebSocket Simulator",
                "config": self.physio_model.get_current_state()
            }
            await websocket.send(json.dumps(welcome_msg))

            # Handle incoming messages
            async for message in websocket:
                await self.handle_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            print("WebSocket client disconnected")
        finally:
            self.clients.remove(websocket)

    async def handle_message(self, websocket, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            command = data.get('command')

            if command == 'set_parameters':
                success = self.physio_model.update_parameters(data.get('parameters', {}))
                response = {
                    "type": "command_response",
                    "command": "set_parameters",
                    "success": success,
                    "new_state": self.physio_model.get_current_state()
                }
                await websocket.send(json.dumps(response))

            elif command == 'set_scenario':
                success = self.physio_model.set_scenario(data.get('scenario'))
                response = {
                    "type": "command_response",
                    "command": "set_scenario",
                    "success": success,
                    "scenario": data.get('scenario'),
                    "new_state": self.physio_model.get_current_state()
                }
                await websocket.send(json.dumps(response))

            else:
                response = {
                    "type": "error",
                    "message": f"Unknown command: {command}"
                }
                await websocket.send(json.dumps(response))

        except json.JSONDecodeError as e:
            error_msg = {"type": "error", "message": f"Invalid JSON: {e}"}
            await websocket.send(json.dumps(error_msg))

    async def broadcast_data(self):
        """Broadcast data to all connected WebSocket clients"""
        while self.running:
            if self.clients:
                data_point = self.data_generator.generate_data_point()
                data_json = json.dumps(data_point)

                # Send to all connected clients
                if self.clients:
                    await asyncio.gather(
                        *[client.send(data_json) for client in self.clients],
                        return_exceptions=True
                    )

            await asyncio.sleep(0.001)  # ~1000 Hz

    async def stop_server(self):
        """Stop WebSocket server"""
        self.running = False
        # Close all client connections
        for client in self.clients:
            await client.close()
        self.clients.clear()
```

## Custom Data Export Formats

### CSV Data Exporter

```python
import csv
import time
from datetime import datetime

class CSVDataExporter:
    def __init__(self, filename_prefix="ppg_data"):
        self.filename_prefix = filename_prefix
        self.current_file = None
        self.csv_writer = None
        self.sample_count = 0

    def start_recording(self, additional_fields=None):
        """Start recording data to CSV file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.filename_prefix}_{timestamp}.csv"

        self.current_file = open(filename, 'w', newline='')

        # Define CSV fields
        base_fields = [
            'timestamp', 'red_ppg', 'ir_ppg', 'heart_rate', 'spO2',
            'activity', 'condition', 'sample_rate'
        ]

        if additional_fields:
            base_fields.extend(additional_fields)

        self.csv_writer = csv.DictWriter(self.current_file, fieldnames=base_fields)
        self.csv_writer.writeheader()
        self.sample_count = 0

        print(f"Started recording to {filename}")
        return filename

    def record_data_point(self, data_point):
        """Record a single data point to CSV"""
        if self.csv_writer and self.current_file:
            self.csv_writer.writerow(data_point)
            self.sample_count += 1

            # Flush periodically to ensure data is written
            if self.sample_count % 100 == 0:
                self.current_file.flush()

    def stop_recording(self):
        """Stop recording and close CSV file"""
        if self.current_file:
            self.current_file.close()
            self.current_file = None
            self.csv_writer = None

            print(f"Stopped recording. Total samples: {self.sample_count}")
            return self.sample_count
        return 0

# Usage example
exporter = CSVDataExporter()
exporter.start_recording(['blood_pressure_systolic', 'blood_pressure_diastolic'])

# In data generation loop
for i in range(1000):
    data_point = data_generator.generate_data_point()
    exporter.record_data_point(data_point)

exporter.stop_recording()
```

### Real-time Data Visualization

```python
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

class RealTimeVisualizer:
    def __init__(self, max_points=1000):
        self.max_points = max_points
        self.red_data = deque(maxlen=max_points)
        self.ir_data = deque(maxlen=max_points)
        self.timestamps = deque(maxlen=max_points)

        # Setup plot
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 8))
        self.setup_plots()

    def setup_plots(self):
        """Initialize plot configuration"""
        # Red PPG plot
        self.ax1.set_title('Red PPG Signal')
        self.ax1.set_ylabel('Amplitude')
        self.ax1.grid(True)
        self.red_line, = self.ax1.plot([], [], 'r-', linewidth=1)

        # IR PPG plot
        self.ax2.set_title('IR PPG Signal')
        self.ax2.set_ylabel('Amplitude')
        self.ax2.set_xlabel('Time (s)')
        self.ax2.grid(True)
        self.ir_line, = self.ax2.plot([], [], 'b-', linewidth=1)

        plt.tight_layout()

    def update_data(self, data_point):
        """Update with new data point"""
        current_time = time.time()

        self.timestamps.append(current_time)
        self.red_data.append(data_point['red_ppg'])
        self.ir_data.append(data_point['ir_ppg'])

        # Convert to relative time
        if len(self.timestamps) > 1:
            relative_times = [t - self.timestamps[0] for t in self.timestamps]

            # Update plots
            self.red_line.set_data(relative_times, self.red_data)
            self.ir_line.set_data(relative_times, self.ir_data)

            # Adjust axes
            for ax in [self.ax1, self.ax2]:
                ax.relim()
                ax.autoscale_view()

    def start_animation(self, data_callback, interval=10):
        """Start real-time animation"""
        def animate(frame):
            data_point = data_callback()
            self.update_data(data_point)
            return self.red_line, self.ir_line

        self.ani = animation.FuncAnimation(
            self.fig, animate, interval=interval, blit=False
        )
        plt.show()

# Usage example
visualizer = RealTimeVisualizer()

def get_data_callback():
    return data_generator.generate_data_point()

visualizer.start_animation(get_data_callback)
```

## Integration with External Systems

### MQTT Integration

```python
import paho.mqtt.client as mqtt
import json

class MQTTIntegration:
    def __init__(self, broker_host='localhost', broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client()
        self.connected = False

        # Setup callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.connected = True
            print("Connected to MQTT broker")
            # Subscribe to command topics
            client.subscribe("max30102/commands/#")
        else:
            print(f"Failed to connect to MQTT broker, return code {rc}")

    def _on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            payload = json.loads(msg.payload.decode())
            topic = msg.topic

            if topic == "max30102/commands/set_parameters":
                # Handle parameter setting command
                self._handle_set_parameters(payload)
            elif topic == "max30102/commands/set_scenario":
                # Handle scenario setting command
                self._handle_set_scenario(payload)

        except json.JSONDecodeError as e:
            print(f"Invalid JSON in MQTT message: {e}")

    def connect(self):
        """Connect to MQTT broker"""
        self.client.connect(self.broker_host, self.broker_port, 60)
        self.client.loop_start()

    def publish_data(self, data_point):
        """Publish data point to MQTT topics"""
        if self.connected:
            # Publish to data topic
            self.client.publish("max30102/data/ppg", json.dumps(data_point))

            # Also publish individual vital signs
            self.client.publish("max30102/vitals/heart_rate", data_point['heart_rate'])
            self.client.publish("max30102/vitals/spo2", data_point['spO2'])
            self.client.publish("max30102/vitals/activity", data_point['activity'])

    def _handle_set_parameters(self, payload):
        """Handle parameter setting via MQTT"""
        # This would interface with your physiological model
        parameters = payload.get('parameters', {})
        print(f"Setting parameters via MQTT: {parameters}")
        # Implement parameter setting logic here

    def _handle_set_scenario(self, payload):
        """Handle scenario setting via MQTT"""
        scenario = payload.get('scenario')
        print(f"Setting scenario via MQTT: {scenario}")
        # Implement scenario setting logic here

    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False

# Usage example
mqtt_integration = MQTTIntegration('mqtt.broker.com')
mqtt_integration.connect()

# In data generation loop
data_point = data_generator.generate_data_point()
mqtt_integration.publish_data(data_point)
```

## Best Practices for Extension

### 1. Maintain Backward Compatibility

```python
class BackwardCompatibleExtendedModel(PhysiologicalModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure existing API still works
        self._setup_backward_compatibility()

    def _setup_backward_compatibility(self):
        """Ensure existing code continues to work"""
        # Map new parameters to old names if needed
        if not hasattr(self.state, 'heart_rate_bpm'):
            self.state.heart_rate_bpm = getattr(self.state, 'new_hr_param', 72.0)
```

### 2. Use Configuration-Driven Extensions

```yaml
# config/extensions.yaml
custom_parameters:
  blood_pressure:
    enabled: true
    systolic_range: [60, 200]
    diastolic_range: [40, 120]

  temperature:
    enabled: true
    range: [35.0, 41.0]
    unit: "celsius"

  custom_waveforms:
    enabled: true
    types: ["alternans", "paradoxus", "bigeminy"]
```

### 3. Implement Proper Error Handling

```python
class RobustExtendedGenerator(ExtendedDataGenerator):
    def generate_data_point(self) -> Dict[str, any]:
        try:
            return super().generate_data_point()
        except Exception as e:
            logger.error(f"Error generating data point: {e}")
            # Return safe fallback data
            return self._get_fallback_data_point()

    def _get_fallback_data_point(self) -> Dict[str, any]:
        """Provide fallback data when generation fails"""
        return {
            'timestamp': time.time(),
            'red_ppg': 50000,
            'ir_ppg': 48000,
            'heart_rate': 72.0,
            'spO2': 98.0,
            'activity': 'resting',
            'condition': 'normal',
            'sample_rate': self.sample_rate,
            'error': True
        }
```

### 4. Add Comprehensive Testing

```python
class TestExtendedFeatures:
    def test_custom_parameters(self):
        """Test that custom parameters work correctly"""
        model = ExtendedPhysiologicalModel()

        # Test parameter setting
        model.set_custom_parameter('blood_glucose', 5.5)
        assert model.state.blood_glucose == 5.5

        # Test validation
        with pytest.raises(ValueError):
            model.set_custom_parameter('blood_glucose', 25.0)  # Too high

    def test_custom_waveforms(self):
        """Test custom waveform generation"""
        model = ExtendedPhysiologicalModel()
        model.state.waveform_shape = "pulsus_alternans"

        generator = ExtendedDataGenerator(model)
        data_point = generator.generate_data_point()

        assert 'signal_quality' in data_point
        assert 0.0 <= data_point['signal_quality'] <= 1.0
```

## Conclusion

The MAX30102 Simulator is designed to be highly extensible. By following the patterns in this guide, you can:

- Add new physiological parameters and calculations
- Create custom medical scenarios
- Implement alternative communication protocols
- Integrate with external systems
- Add real-time visualization and data export
- Maintain backward compatibility

Remember to test your extensions thoroughly and consider contributing valuable extensions back to the main project.
