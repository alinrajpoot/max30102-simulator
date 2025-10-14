# Architecture Overview

Comprehensive architecture documentation for the MAX30102 Simulator.

## System Architecture

The simulator follows a modular, layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    TCP Client Applications                  │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│                     TCP Server Layer                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  TCPServer Class                      │  │
│  │  - Client connection management                       │  │
│  │  - Message routing                                    │  │
│  │  - Data broadcasting                                  │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│                   Simulation Engine Layer                   │
│  ┌───────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │ DataGenerator │  │ Physiological   │  │ MAX30102Device│  │
│  │               │  │ Model           │  │               │  │
│  │ - PPG waveform│  │ - Parameter     │  │ - Register    │  │
│  │   generation  │  │   management    │  │   simulation  │  │
│  │ - Noise       │  │ - Scenario      │  │ - FIFO buffer │  │
│  │   simulation  │  │   application   │  │   management  │  │
│  │ - Motion      │  │ - Physiological │  │ - I2C protocol│  │
│  │   artifacts   │  │   calculations  │  │   emulation   │  │
│  └───────────────┘  └─────────────────┘  └───────────────┘  │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│                    Protocol Layer                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │               I2CProtocolSimulator                    │  │
│  │  - Register read/write simulation                     │  │
│  │  - Burst operation handling                           │  │
│  │  - Communication timing simulation                    │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│                    Configuration Layer                      │
│  ┌───────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │   default.yaml│  │  scenarios.json │  │register_map.py│  │
│  │ - Server      │  │ - Pre-defined   │  │ - MAX30102    │  │
│  │   settings    │  │   scenarios     │  │   register    │  │
│  │ - Sensor      │  │ - Medical       │  │   definitions │  │
│  │   parameters  │  │   conditions    │  │ - Constants   │  │
│  │ - Default     │  │ - Physiological │  │   and masks   │  │
│  │   physiology  │  │   parameters    │  │               │  │
│  └───────────────┘  └─────────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. TCPServer (`src/simulator/server.py`)

**Responsibilities:**

- Manage TCP client connections
- Route incoming commands to appropriate handlers
- Broadcast physiological data to connected clients
- Handle client disconnections and errors

**Key Features:**

- Multi-client support with thread-safe operations
- Real-time data streaming at configurable rates
- JSON-based command/response protocol
- Comprehensive logging and error handling

### 2. PhysiologicalModel (`src/models/physiological_model.py`)

**Responsibilities:**

- Manage physiological parameter state
- Apply physiological relationships and constraints
- Handle scenario transitions and parameter validation
- Calculate dependent physiological values

**Key Algorithms:**

- Age-based parameter adjustments
- Gender-specific physiological differences
- Activity-level effects on vital signs
- Medical condition simulations

### 3. DataGenerator (`src/simulator/data_generator.py`)

**Responsibilities:**

- Generate realistic PPG waveform data
- Simulate sensor noise and motion artifacts
- Calculate derived vital signs (HR, SpO2)
- Maintain waveform timing and synchronization

**Signal Generation:**

- Cardiac pulse waveform with systolic/diastolic components
- Respiratory modulation (baseline wander)
- Motion artifact simulation
- Multi-frequency noise injection

### 4. MAX30102Device (`src/simulator/max30102_device.py`)

**Responsibilities:**

- Simulate MAX30102 register-based interface
- Manage FIFO buffer operations
- Handle device configuration and modes
- Provide device status and diagnostics

**Hardware Emulation:**

- Complete register map simulation
- FIFO overflow and rollover handling
- Sample rate and averaging configuration
- Power management simulation

### 5. I2CProtocolSimulator (`src/protocols/i2c_simulator.py`)

**Responsibilities:**

- Simulate I2C communication protocol
- Handle burst read/write operations
- Manage communication timing and delays
- Provide protocol statistics

**Protocol Features:**

- Register address validation
- Burst operation simulation
- Communication delay modeling
- Error condition simulation

## Data Flow

### 1. Client Connection Sequence

```
Client Connect → Welcome Message → Command Processing → Data Streaming
      │               │                  │                  │
      ▼               ▼                  ▼                  ▼
TCP Handshake   Send current    Update parameters   Continuous data
               configuration    or apply scenario      generation
```

### 2. Data Generation Pipeline

```
Physiological Model → Waveform Generation → Noise Addition → FIFO Buffer
        │                   │                  │               │
        ▼                   ▼                  ▼               ▼
Parameter state    PPG signal creation   Realistic noise   Sample storage
```

### 3. Command Processing

```
Client Command → JSON Parsing → Parameter Validation → Model Update
       │               │                 │                 │
       ▼               ▼                 ▼                 ▼
  TCP Receive     Deserialize       Check ranges      Update state &
                                   and constraints      recalculate
```

## Configuration Management

### Configuration Files

1. **`config/default.yaml`**

   - TCP server settings (host, port, buffer sizes)
   - Sensor parameters (sample rate, ADC range, LED currents)
   - Default physiological parameters
   - Simulation control settings

2. **`config/scenarios.json`**

   - Pre-defined medical scenarios
   - Emergency condition parameters
   - Activity-specific configurations
   - Scenario descriptions and metadata

3. **`config/register_map.py`**
   - MAX30102 register addresses and definitions
   - Operating mode constants
   - Default register values
   - Bit masks and configuration values

### Configuration Hierarchy

```
Hard-coded defaults ← YAML configuration ← Runtime parameters ← Scenarios
```

## Physiological Modeling

### Parameter Relationships

The simulator implements realistic physiological relationships:

**Age Effects:**

- Maximum heart rate decreases with age
- Resting heart rate shows slight age-related changes
- Respiratory rate has minor age adjustments

**Gender Differences:**

- Different baseline heart rates
- Variation in pulse waveform amplitudes
- Gender-specific response patterns

**Activity Levels:**

- Heart rate increases with activity intensity
- Respiratory rate scales with metabolic demand
- Motion artifact probability increases

**Medical Conditions:**

- Pathological vital sign patterns
- Condition-specific waveform characteristics
- Emergency scenario parameter sets

### Waveform Generation

The PPG waveform generation uses:

1. **Cardiac Component**

   - Fundamental pulse shape based on heart rate
   - Systolic peak and diastolic notch
   - Heart rate variability simulation

2. **Respiratory Component**

   - Baseline wander at respiratory frequency
   - Respiratory sinus arrhythmia
   - Modulation of pulse amplitude

3. **Noise Components**
   - White noise (sensor noise)
   - 1/f noise (flicker noise)
   - Power line interference (50/60 Hz)
   - Motion artifacts (transient disturbances)

## Protocol Simulation

### I2C Protocol Emulation

The I2C simulation provides:

1. **Register Access**

   - Read/write operations with address validation
   - Special register behavior simulation
   - Configuration bit manipulation

2. **FIFO Operations**

   - Sample storage in 18-bit format
   - Overflow detection and handling
   - Read pointer management

3. **Timing Simulation**
   - Communication delay modeling
   - Sample rate timing accuracy
   - Burst operation timing

### TCP Protocol

The TCP protocol features:

1. **Message Format**

   - JSON-based message structure
   - Type-based message routing
   - Timestamp inclusion

2. **Command Set**

   - Parameter updates
   - Scenario selection
   - Status queries
   - System reset

3. **Error Handling**
   - Comprehensive error reporting
   - Connection management
   - Message validation

## Performance Considerations

### Real-time Requirements

- **Data Generation**: Must keep up with configured sample rate
- **TCP Streaming**: Efficient data serialization and transmission
- **Client Handling**: Non-blocking I/O for multiple clients

### Memory Management

- **FIFO Buffer**: Fixed-size circular buffer for samples
- **Client Connections**: Dynamic management with connection pooling
- **Data Structures**: Efficient data structures for real-time operation

### Scalability

- **Multiple Clients**: Support for concurrent client connections
- **Configurable Rates**: Adaptable to different performance requirements
- **Resource Monitoring**: Built-in performance tracking

## Extension Points

### Adding New Scenarios

1. Add scenario definition to `config/scenarios.json`
2. Implement any special handling in `PhysiologicalModel`
3. Update documentation

### Custom Physiological Models

1. Extend `PhysiologicalModel` class
2. Override calculation methods
3. Add new parameter types

### Alternative Protocols

1. Implement new protocol class following I2C interface
2. Update configuration for protocol selection
3. Add protocol-specific parameters

## Testing Architecture

### Unit Testing

- Individual component testing
- Mock dependencies for isolation
- Parameter validation tests

### Integration Testing

- Component interaction testing
- End-to-end data flow validation
- Scenario transition testing

### Performance Testing

- Data rate validation
- Memory usage monitoring
- Multi-client load testing
