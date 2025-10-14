# Scenario Guide

Complete guide to using and creating physiological scenarios in the MAX30102 Simulator.

## Overview

Scenarios are pre-defined sets of physiological parameters that simulate specific medical conditions, activities, or states. They provide a convenient way to quickly switch between different physiological profiles for testing and demonstration purposes.

## Available Scenarios

### Normal States

#### normal_resting

**Description**: Healthy adult at rest
**Typical Parameters**:

- Heart Rate: 60-80 bpm
- SpO2: 97-99%
- Respiratory Rate: 12-18 bpm
- Signal Quality: Clean, stable

**Use Cases**:

- Baseline health monitoring
- Algorithm validation
- System calibration

#### sleeping

**Description**: Deep sleep state
**Typical Parameters**:

- Heart Rate: 50-70 bpm
- SpO2: 95-98%
- Respiratory Rate: 10-14 bpm
- Signal Quality: Very stable, low noise

**Use Cases**:

- Sleep monitoring applications
- Low-activity scenarios
- Baseline variability studies

### Physical Activities

#### walking

**Description**: Light to moderate walking
**Typical Parameters**:

- Heart Rate: 90-110 bpm
- SpO2: 96-98%
- Respiratory Rate: 18-24 bpm
- Motion Artifacts: Moderate

**Use Cases**:

- Activity tracking
- Motion artifact handling
- Moderate exercise response

#### running

**Description**: Moderate to vigorous running
**Typical Parameters**:

- Heart Rate: 130-160 bpm
- SpO2: 95-97%
- Respiratory Rate: 24-35 bpm
- Motion Artifacts: High

**Use Cases**:

- Exercise physiology
- High heart rate scenarios
- Motion artifact testing

#### sex_intercourse

**Description**: Sexual activity simulation
**Typical Parameters**:

- Heart Rate: 120-140 bpm
- SpO2: 96-98%
- Respiratory Rate: 20-30 bpm
- Motion Artifacts: Moderate to high

**Use Cases**:

- Intimate activity monitoring
- Peak heart rate scenarios
- Private healthcare applications

### Medical Emergencies

#### heart_attack

**Description**: Myocardial infarction (heart attack)
**Typical Parameters**:

- Heart Rate: 40-60 bpm (bradycardia)
- SpO2: 80-90% (hypoxia)
- Respiratory Rate: 8-12 bpm (depressed)
- Pulse Quality: Weak, irregular
- Symptoms: Chest pain, sweating, shortness of breath

**Clinical Features**:

- ST elevation on ECG (simulated in waveform)
- Weak peripheral pulses
- Respiratory distress

**Use Cases**:

- Emergency detection systems
- Cardiac event simulation
- Medical training applications

#### extreme_anxiety

**Description**: Panic attack or extreme anxiety
**Typical Parameters**:

- Heart Rate: 110-130 bpm (tachycardia)
- SpO2: 94-96%
- Respiratory Rate: 22-28 bpm (tachypnea)
- Heart Rate Variability: Low
- Symptoms: Hyperventilation, palpitations

**Clinical Features**:

- Sinus tachycardia
- Respiratory alkalosis (from hyperventilation)
- Increased sympathetic tone

**Use Cases**:

- Mental health monitoring
- Stress response studies
- Anxiety detection algorithms

#### shock

**Description**: Medical shock (hypoperfusion)
**Typical Parameters**:

- Heart Rate: 130-150 bpm (compensatory tachycardia)
- SpO2: 80-85% (severe hypoxia)
- Respiratory Rate: 30-40 bpm (compensatory)
- Pulse Quality: Very weak, thready
- Symptoms: Pale skin, confusion, low blood pressure

**Clinical Features**:

- Poor peripheral perfusion
- Compensatory mechanisms failing
- Critical condition

**Use Cases**:

- Critical care monitoring
- Emergency response testing
- Vital sign threshold testing

#### fear

**Description**: Acute fear response
**Typical Parameters**:

- Heart Rate: 100-120 bpm
- SpO2: 95-97%
- Respiratory Rate: 20-25 bpm
- Heart Rate Variability: Very low
- Symptoms: Fight-or-flight response

**Clinical Features**:

- Sympathetic nervous system activation
- Increased cardiac output
- Preparedness for physical action

**Use Cases**:

- Emotional response studies
- Stress testing
- Biometric authentication research

## Using Scenarios

### Command Line Usage

```bash
# Using the example client
python examples/client_example.py --scenario heart_attack --duration 30

# Multiple scenario demonstration
python examples/scenario_demo.py
```

### Programmatic Usage

```python
from examples.client_example import MAX30102Client

client = MAX30102Client()
client.connect()

# Apply a scenario
client.set_scenario('running')

# Apply with verification
if client.set_scenario('heart_attack'):
    print("Scenario applied successfully")
else:
    print("Failed to apply scenario")

client.disconnect()
```

### TCP Protocol Usage

```json
{
  "command": "set_scenario",
  "scenario": "extreme_anxiety"
}
```

## Scenario Parameters

### Core Physiological Parameters

| Parameter             | Type  | Range      | Description                            |
| --------------------- | ----- | ---------- | -------------------------------------- |
| `heart_rate_bpm`      | float | 30-220     | Heart rate in beats per minute         |
| `spo2_percent`        | float | 70-100     | Blood oxygen saturation percentage     |
| `respiratory_rate`    | int   | 6-60       | Respiratory rate in breaths per minute |
| `pulse_amplitude_red` | int   | 1000-20000 | Red LED pulse waveform amplitude       |
| `pulse_amplitude_ir`  | int   | 1000-20000 | IR LED pulse waveform amplitude        |
| `noise_level`         | float | 0.01-1.0   | Signal noise level multiplier          |

### Advanced Parameters

| Parameter                     | Type   | Values                   | Description                |
| ----------------------------- | ------ | ------------------------ | -------------------------- |
| `heart_rate_variability`      | string | low/normal/high/very_low | HRV pattern                |
| `pulse_rhythm`                | string | regular/irregular        | Heart rhythm regularity    |
| `pulse_quality`               | string | normal/weak/strong       | Pulse signal strength      |
| `motion_artifact_probability` | float  | 0.0-1.0                  | Chance of motion artifacts |

### Symptom Descriptors

Some scenarios include symptom descriptions for educational purposes:

```json
"symptoms": [
  "chest_pain",
  "sweating",
  "shortness_of_breath",
  "palpitations",
  "dizziness"
]
```

## Creating Custom Scenarios

### Method 1: Configuration File

Add to `config/scenarios.json`:

```json
"my_custom_scenario": {
  "description": "Custom scenario for specific testing",
  "physiological": {
    "heart_rate_bpm": 100,
    "spo2_percent": 95,
    "respiratory_rate": 20,
    "pulse_amplitude_red": 12000,
    "pulse_amplitude_ir": 11500,
    "noise_level": 0.1,
    "heart_rate_variability": "low",
    "motion_artifact_probability": 0.3
  }
}
```

### Method 2: Programmatic Creation

```python
from models.scenarios import ScenarioManager

manager = ScenarioManager()

success = manager.create_custom_scenario(
    name='high_stress',
    description='High stress work environment',
    physiological_params={
        'heart_rate_bpm': 105,
        'spo2_percent': 96,
        'respiratory_rate': 22,
        'noise_level': 0.15,
        'heart_rate_variability': 'low'
    }
)
```

### Method 3: Runtime Creation via TCP

```json
{
  "command": "set_parameters",
  "parameters": {
    "heart_rate_bpm": 85,
    "spo2_percent": 97,
    "activity": "resting",
    "condition": "custom_scenario"
  }
}
```

## Scenario Validation

### Parameter Validation

The simulator validates all scenario parameters to ensure physiological plausibility:

```python
from models.scenarios import ScenarioManager

manager = ScenarioManager()

# Validate parameters before creating scenario
params = {
    'heart_rate_bpm': 300,  # Invalid - too high
    'spo2_percent': 95      # Valid
}

errors = manager.validate_scenario_parameters(params)
if errors:
    print("Validation errors:", errors)
else:
    manager.create_custom_scenario('test', 'Test scenario', params)
```

### Validation Rules

- Heart Rate: 30-220 bpm
- SpO2: 70-100%
- Respiratory Rate: 6-60 bpm
- Pulse Amplitudes: 1000-20000
- Noise Level: 0.01-1.0

## Scenario Transitions

### Smooth Transitions

The simulator provides smooth transitions between scenarios to avoid abrupt parameter changes:

```python
# Gradual transition example
client.set_scenario('normal_resting')
time.sleep(5)  # Observe baseline
client.set_scenario('running')  # Smooth transition to exercise
```

### Transition Effects

- Heart rate changes gradually over 10-30 seconds
- Respiratory rate adjusts progressively
- Waveform characteristics evolve smoothly
- Motion artifacts may increase during transition

## Medical Accuracy

### Clinical Basis

Scenarios are based on established medical knowledge:

1. **Heart Attack**: Based on ACS (Acute Coronary Syndrome) presentation
2. **Shock**: Reflects hypoperfusion and compensatory mechanisms
3. **Anxiety**: Models sympathetic nervous system activation
4. **Exercise**: Follows established exercise physiology principles

### Limitations

- Scenarios are simulations and not medical diagnoses
- Individual variations are not fully captured
- Complex pathophysiological interactions are simplified
- Always consult healthcare professionals for medical advice

## Use Case Examples

### Healthcare Application Testing

```python
# Test emergency detection
scenarios = ['normal_resting', 'heart_attack', 'shock']
for scenario in scenarios:
    client.set_scenario(scenario)
    # Run detection algorithm tests
    test_emergency_detection(scenario)
```

### Algorithm Development

```python
# Test motion artifact handling
client.set_scenario('running')
data = collect_data(60)  # Collect 60 seconds of data
test_motion_artifact_algorithm(data)
```

### Educational Demonstrations

```bash
# Run complete scenario demonstration
python examples/scenario_demo.py
```

### Research Applications

```python
# Study physiological responses
baseline = collect_data_scenario('normal_resting')
stress_response = collect_data_scenario('extreme_anxiety')
analyze_differences(baseline, stress_response)
```

## Best Practices

### Scenario Selection

1. **Start Simple**: Begin with `normal_resting` for baseline
2. **Progressive Complexity**: Move to activities before emergencies
3. **Context Appropriateness**: Choose scenarios relevant to your application
4. **Validation**: Always validate against known physiological ranges

### Testing Strategy

1. **Baseline Testing**: Always include normal scenarios
2. **Edge Cases**: Test with extreme scenarios
3. **Transition Testing**: Verify smooth scenario changes
4. **Performance Testing**: Ensure system handles all scenarios

### Medical Applications

1. **Clinical Validation**: Correlate with real clinical data when possible
2. **Professional Consultation**: Involve medical professionals for clinical scenarios
3. **Ethical Considerations**: Use appropriate disclaimers for medical simulations
4. **Accuracy Documentation**: Clearly document simulation limitations

## Troubleshooting

### Common Issues

**Scenario not found:**

- Check scenario name spelling
- Verify scenario exists in `config/scenarios.json`
- Check scenario manager initialization

**Unrealistic parameters:**

- Validate parameter ranges
- Check for conflicting parameter combinations
- Verify physiological model calculations

**Abrupt transitions:**

- Allow sufficient time for parameter stabilization
- Check for smooth transition implementation
- Monitor gradual parameter changes

### Debugging Tips

```python
# Get current scenario state
client.get_status()

# Monitor parameter changes
client.set_scenario('running')
time.sleep(2)
state = client.get_status()
print(f"Current HR: {state['heart_rate_bpm']}")
```

## Extending Scenarios

### Adding New Scenario Types

1. Define new parameter sets in `config/scenarios.json`
2. Update physiological model if new parameters are needed
3. Add validation rules for new parameters
4. Update documentation

### Custom Physiological Responses

For advanced users, you can modify the physiological model to create more complex scenario responses:

```python
class CustomPhysiologicalModel(PhysiologicalModel):
    def _apply_condition_effects(self):
        # Add custom condition handling
        if self.state.condition == 'my_custom_condition':
            # Custom physiological responses
            self.state.heart_rate_bpm = self._calculate_custom_hr()

        super()._apply_condition_effects()
```
