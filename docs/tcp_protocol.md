# TCP Protocol Specification

Detailed specification of the TCP communication protocol used by the MAX30102 Simulator.

## Overview

The simulator uses a simple TCP-based protocol for real-time data streaming and command/control. All messages are JSON-formatted strings terminated with newline characters.

## Connection Details

- **Default Port**: 8888
- **Protocol**: TCP
- **Encoding**: UTF-8
- **Message Delimiter**: Newline (`\n`)

## Message Format

### General Structure

All messages are JSON objects with the following base structure:

```json
{
  "type": "message_type",
  "timestamp": 1635786300.123,
  ... type_specific_fields
}
```

### Message Types

| Type               | Direction       | Description                |
| ------------------ | --------------- | -------------------------- |
| `welcome`          | Server → Client | Initial connection message |
| `data`             | Server → Client | Physiological data sample  |
| `command`          | Client → Server | Control command            |
| `command_response` | Server → Client | Command execution result   |
| `error`            | Server → Client | Error notification         |

## Data Flow

### Connection Establishment

1. Client connects to server on specified port
2. Server sends `welcome` message
3. Client can begin sending commands or receiving data

### Welcome Message

Sent immediately after client connection:

```json
{
  "type": "welcome",
  "message": "Connected to MAX30102 Simulator",
  "timestamp": 1635786300.123,
  "config": {
    "age": 30,
    "gender": "male",
    "activity": "resting",
    "condition": "normal",
    "heart_rate_bpm": 72.0,
    "spo2_percent": 98.0
  }
}
```

### Data Streaming

Server continuously streams data samples:

```json
{
  "type": "data",
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

## Commands

### Command Structure

Client sends commands as JSON objects:

```json
{
  "command": "command_name",
  "parameters": {...},
  "id": "optional_request_id"
}
```

### Available Commands

#### set_parameters

Update physiological parameters.

**Request:**

```json
{
  "command": "set_parameters",
  "parameters": {
    "age": 35,
    "gender": "female",
    "activity": "walking",
    "heart_rate_bpm": 95.0
  }
}
```

**Response:**

```json
{
  "type": "command_response",
  "command": "set_parameters",
  "success": true,
  "new_state": {
    "age": 35,
    "gender": "female",
    "activity": "walking",
    "heart_rate_bpm": 95.0,
    "...": "..."
  }
}
```

#### set_scenario

Apply a pre-defined scenario.

**Request:**

```json
{
  "command": "set_scenario",
  "scenario": "heart_attack"
}
```

**Response:**

```json
{
  "type": "command_response",
  "command": "set_scenario",
  "success": true,
  "scenario": "heart_attack",
  "new_state": {
    "condition": "heart_attack",
    "heart_rate_bpm": 45.0,
    "spo2_percent": 85.0,
    "...": "..."
  }
}
```

#### get_status

Get current server status and configuration.

**Request:**

```json
{
  "command": "get_status"
}
```

**Response:**

```json
{
  "type": "command_response",
  "command": "get_status",
  "success": true,
  "status": {
    "clients_connected": 2,
    "model_state": {
      "age": 30,
      "gender": "male",
      "...": "..."
    },
    "sensor_status": {
      "power_on": true,
      "fifo_samples": 15,
      "sample_count": 12345
    }
  }
}
```

#### reset

Reset to default parameters.

**Request:**

```json
{
  "command": "reset"
}
```

**Response:**

```json
{
  "type": "command_response",
  "command": "reset",
  "success": true,
  "new_state": {
    "age": 30,
    "gender": "male",
    "activity": "resting",
    "...": "default_values"
  }
}
```

## Error Handling

### Error Responses

When a command fails or an error occurs:

```json
{
  "type": "error",
  "message": "Error description",
  "command": "failed_command_name",
  "timestamp": 1635786300.123
}
```

### Common Error Types

- `invalid_command`: Unknown command name
- `invalid_parameters`: Malformed or invalid parameters
- `scenario_not_found`: Requested scenario doesn't exist
- `connection_error`: Network communication issues

## Data Rates and Performance

### Sample Rates

The simulator supports various sample rates configured in `config/default.yaml`:

```yaml
sensor:
  sample_rate: 1000 # Samples per second
```

Common sample rates:

- 50 Hz - Low power, basic monitoring
- 100 Hz - Standard health monitoring
- 200-400 Hz - Clinical grade
- 1000 Hz - High-resolution research

### Bandwidth Requirements

Approximate data rates:

| Sample Rate | Bytes/Sec | MB/Hour |
| ----------- | --------- | ------- |
| 50 Hz       | ~4 KB/s   | ~14 MB  |
| 100 Hz      | ~8 KB/s   | ~28 MB  |
| 500 Hz      | ~40 KB/s  | ~140 MB |
| 1000 Hz     | ~80 KB/s  | ~280 MB |

### Client Implementation Tips

1. **Use Buffered Reading**: Read multiple messages at once when possible
2. **Handle Partial Messages**: Implement reassembly for split JSON
3. **Use Async I/O**: For high sample rates, use non-blocking I/O
4. **Monitor Performance**: Track message processing latency

## Example Client Implementation

### Python Example

```python
import socket
import json
import threading

class MAX30102TCPClient:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.buffer = ""

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def receive_messages(self):
        while True:
            data = self.socket.recv(4096).decode('utf-8')
            if not data:
                break

            self.buffer += data
            lines = self.buffer.split('\n')
            self.buffer = lines[-1]  # Keep incomplete line

            for line in lines[:-1]:
                if line.strip():
                    self.handle_message(json.loads(line))

    def handle_message(self, message):
        msg_type = message.get('type')

        if msg_type == 'welcome':
            print(f"Connected: {message['message']}")
        elif msg_type == 'data':
            self.handle_data_sample(message)
        elif msg_type == 'command_response':
            self.handle_command_response(message)
        elif msg_type == 'error':
            print(f"Error: {message['message']}")

    def handle_data_sample(self, sample):
        # Process physiological data
        hr = sample['heart_rate']
        spo2 = sample['spO2']
        print(f"HR: {hr}bpm, SpO2: {spo2}%")

    def send_command(self, command):
        command_json = json.dumps(command) + '\n'
        self.socket.sendall(command_json.encode('utf-8'))

    def disconnect(self):
        if self.socket:
            self.socket.close()

# Usage
client = MAX30102TCPClient()
client.connect()

# Start message receiving in background thread
thread = threading.Thread(target=client.receive_messages, daemon=True)
thread.start()

# Send commands
client.send_command({
    "command": "set_scenario",
    "scenario": "running"
})
```

## Protocol Versioning

Current protocol version: **1.0**

Future versions will maintain backward compatibility. Check the `version` field in welcome messages for protocol version information.

## Security Considerations

- The protocol is designed for local network or testing environments
- No encryption is implemented (use VPN or SSH tunneling for remote access)
- No authentication mechanism (firewall protection recommended)
- Consider rate limiting for production deployments
