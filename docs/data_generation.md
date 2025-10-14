# Data Generation Algorithms

Detailed documentation of the PPG waveform generation and signal processing algorithms in the MAX30102 Simulator.

## Overview

The data generation system creates realistic photoplethysmography (PPG) waveforms that mimic real MAX30102 sensor data, including both red and infrared LED signals with appropriate physiological characteristics.

## Core Waveform Generation

### PPG Signal Components

The PPG waveform is composed of multiple physiological components:

```python
def _generate_ppg_waveforms(self) -> Tuple[float, float]:
    # Calculate fundamental frequencies
    heart_rate_hz = self.heart_rate / 60.0  # Convert BPM to Hz
    respiratory_hz = self.respiratory_rate / 60.0

    # Update respiratory phase
    self.respiratory_phase += 2 * np.pi * respiratory_hz / self.sample_rate
    self.respiratory_phase %= 2 * np.pi

    # Generate cardiac pulse waveform
    t = self.time_index * heart_rate_hz * 2 * np.pi

    # Fundamental pulse shape (systolic peak)
    pulse_waveform = np.sin(t) ** 3

    # Add diastolic notch for more realistic waveform
    diastolic_notch = 0.3 * np.sin(2 * t - np.pi/4) ** 2

    # Combine components
    cardiac_signal = pulse_waveform + diastolic_notch

    # Add respiratory modulation (baseline wander)
    respiratory_modulation = 0.1 * np.sin(self.respiratory_phase)

    # Generate red and IR signals with different characteristics
    red_signal = (self.baseline_red +
                 self.pulse_amplitude_red * cardiac_signal * (1 + 0.05 * respiratory_modulation))

    ir_signal = (self.baseline_ir +
                self.pulse_amplitude_ir * cardiac_signal * (1 + 0.05 * respiratory_modulation) *
                (1.0 + 0.02 * np.sin(t * 0.5)))  # Slight different modulation for IR

    return red_signal, ir_signal
```

## Cardiac Component

### Systolic Peak

The main systolic component uses a modified sine wave:

```python
# Fundamental cardiac pulse
pulse_waveform = np.sin(t) ** 3
```

This creates a sharp systolic upstroke and more gradual diastolic decay, mimicking real arterial pressure waves.

### Diastolic Notch

The dicrotic notch is added for arterial compliance:

```python
# Diastolic notch simulation
diastolic_notch = 0.3 * np.sin(2 * t - np.pi/4) ** 2
```

This creates the characteristic notch seen in arterial pressure waveforms during valve closure.

### Combined Cardiac Signal

```python
cardiac_signal = pulse_waveform + diastolic_notch
```

## Respiratory Component

### Baseline Wander

Respiratory activity causes low-frequency baseline variations:

```python
# Respiratory modulation
respiratory_modulation = 0.1 * np.sin(self.respiratory_phase)
```

### Respiratory Sinus Arrhythmia

Heart rate varies with respiration:

```python
# RSA component for heart rate calculation
rsa_component = 2.0 * np.sin(2 * np.pi * self.respiratory_rate/60 * self.time_index)
heart_rate = self.heart_rate + rsa_component
```

## Noise Simulation

### Multi-frequency Noise Model

The simulator adds several types of realistic noise:

```python
def _add_sensor_noise(self, signal: float) -> float:
    # White noise (thermal and shot noise)
    white_noise = np.random.normal(0, self.noise_level * self.pulse_amplitude_red)

    # 1/f noise (flicker noise) - more realistic for sensors
    flicker_noise = np.random.normal(0, self.noise_level * self.pulse_amplitude_red * 0.3)

    # Power line interference (50/60 Hz)
    power_line_noise = (0.05 * self.pulse_amplitude_red *
                      np.sin(2 * np.pi * 50 * self.time_index))

    return signal + white_noise + flicker_noise + power_line_noise
```

### Noise Characteristics

| Noise Type  | Frequency      | Source             | Characteristics             |
| ----------- | -------------- | ------------------ | --------------------------- |
| White Noise | Broad spectrum | Thermal/Shot noise | Random, uncorrelated        |
| 1/f Noise   | Low frequency  | Flicker noise      | "Pink noise" spectrum       |
| Power Line  | 50/60 Hz       | AC interference    | Sinusoidal, fixed frequency |

## Motion Artifact Simulation

### Motion Artifact Generation

Motion artifacts are simulated as transient disturbances:

```python
def _add_motion_artifacts(self, red_ppg: float, ir_ppg: float) -> Tuple[float, float]:
    current_time = time.time()

    # Check if we should start a new motion artifact
    if (not self.motion_artifact_active and
        np.random.random() < self.physio_model.motion_artifact_probability):
        self.motion_artifact_active = True
        self.motion_start_time = current_time
        self.motion_duration = np.random.uniform(0.1, 2.0)

    # Apply motion artifact if active
    if self.motion_artifact_active:
        artifact_time = current_time - self.motion_start_time

        if artifact_time < self.motion_duration:
            # Create motion artifact (combination of low and high frequency components)
            motion_freq1 = 2.0  # Hz - gross movement
            motion_freq2 = 8.0  # Hz - tremor/vibration

            motion_artifact = (
                0.7 * np.sin(2 * np.pi * motion_freq1 * artifact_time) +
                0.3 * np.sin(2 * np.pi * motion_freq2 * artifact_time)
            ) * self.pulse_amplitude_red * 0.5

            red_ppg += motion_artifact
            ir_ppg += motion_artifact * 1.1  # Slightly different for IR
        else:
            self.motion_artifact_active = False

    return red_ppg, ir_ppg
```

### Motion Artifact Types

The simulator models different types of motion:

1. **Gross Movement** (2 Hz): Large-scale body movements
2. **Tremor/Vibration** (8 Hz): Fine motor movements, shivering
3. **Combined Artifacts**: Realistic superposition of multiple motion types

## Vital Sign Calculation

### Heart Rate Calculation

Heart rate is derived from the PPG waveform characteristics:

```python
def _calculate_vital_signs(self, red_ppg: float, ir_ppg: float) -> Tuple[float, float]:
    # For simulation purposes, we use the model values with some noise
    heart_rate = (self.heart_rate +
                 np.random.normal(0, 1.0) +  # Small random variation
                 2.0 * np.sin(2 * np.pi * self.respiratory_rate/60 * self.time_index))  # RSA

    return round(heart_rate, 1), round(spo2, 1)
```

### SpO2 Calculation

Blood oxygen saturation is calculated using the ratio-of-ratios method:

```python
# SpO2 calculation based on ratio of ratios
ac_red = self.pulse_amplitude_red
ac_ir = self.pulse_amplitude_ir
dc_red = self.baseline_red
dc_ir = self.baseline_ir

# Ratio of ratios (simplified)
R = (ac_red / dc_red) / (ac_ir / dc_ir)

# Empirical SpO2 calculation (simplified)
spo2 = 110.0 - 25.0 * R
spo2 = max(70.0, min(100.0, spo2))  # Clamp to realistic range

# Add small random variation
spo2 += np.random.normal(0, 0.5)
```

## Signal Characteristics by Scenario

### Normal Resting

```python
normal_characteristics = {
    'signal_stability': 'high',
    'noise_level': 'low',
    'motion_artifacts': 'rare',
    'waveform_consistency': 'excellent',
    'signal_to_noise': 'high'
}
```

### Exercise Scenarios

```python
exercise_characteristics = {
    'signal_stability': 'moderate',
    'noise_level': 'high',
    'motion_artifacts': 'frequent',
    'waveform_consistency': 'variable',
    'signal_to_noise': 'moderate'
}
```

### Medical Emergencies

```python
emergency_characteristics = {
    'signal_stability': 'low',
    'noise_level': 'variable',
    'motion_artifacts': 'common',
    'waveform_consistency': 'poor',
    'signal_to_noise': 'low'
}
```

## Sample Rate Management

### Timing Control

The generator maintains precise timing for consistent data rates:

```python
def generate_data_point(self) -> Dict[str, any]:
    current_time = time.time()
    dt = current_time - self.last_update_time
    self.last_update_time = current_time

    # Update time index for waveform generation
    self.time_index += dt

    # Generate data point...
    return data_point
```

### Sample Rate Configuration

```python
def set_sample_rate(self, sample_rate: int):
    self.sample_rate = sample_rate
    self.logger.info(f"Sample rate set to {sample_rate} Hz")
```

## Red vs Infrared Signal Differences

### Physiological Basis

The simulator models key differences between red and IR PPG signals:

1. **Different Absorption**: Hemoglobin has different absorption spectra for red vs IR light
2. **Pulse Amplitude**: IR typically has slightly lower pulse amplitude
3. **Signal Quality**: IR often has better signal-to-noise ratio
4. **Motion Artifacts**: Different susceptibility to motion artifacts

### Implementation

```python
# Red signal - higher absorption, more sensitive to oxygen saturation
red_signal = (self.baseline_red +
             self.pulse_amplitude_red * cardiac_signal * (1 + 0.05 * respiratory_modulation))

# IR signal - lower absorption, better baseline stability
ir_signal = (self.baseline_ir +
            self.pulse_amplitude_ir * cardiac_signal * (1 + 0.05 * respiratory_modulation) *
            (1.0 + 0.02 * np.sin(t * 0.5)))  # Slight different modulation
```

## Signal Quality Metrics

### Quality Assessment

The generator can provide signal quality metrics:

```python
def calculate_signal_quality(self, red_ppg: float, ir_ppg: float) -> Dict[str, float]:
    # Calculate various quality metrics
    quality_metrics = {
        'signal_strength': self._calculate_signal_strength(red_ppg, ir_ppg),
        'noise_level': self._estimate_noise_level(red_ppg, ir_ppg),
        'pulse_consistency': self._assess_pulse_consistency(),
        'motion_artifact_level': self._detect_motion_artifacts(),
        'overall_quality': self._compute_overall_quality()
    }

    return quality_metrics
```

### Quality Indicators

| Metric                | Range | Interpretation       |
| --------------------- | ----- | -------------------- |
| Signal Strength       | 0-1   | Higher is better     |
| Noise Level           | 0-1   | Lower is better      |
| Pulse Consistency     | 0-1   | Regularity of pulses |
| Motion Artifact Level | 0-1   | Lower is better      |
| Overall Quality       | 0-100 | Composite score      |

## Advanced Signal Features

### Pathological Waveforms

For medical scenarios, the generator creates characteristic pathological patterns:

```python
def _generate_pathological_waveforms(self, condition: str) -> Tuple[float, float]:
    if condition == 'heart_attack':
        # Weak, irregular pulses with possible arrhythmias
        pulse_amplitude = self.pulse_amplitude_red * 0.5
        irregularity = np.random.normal(0, 0.2)  # Added irregularity
        cardiac_signal = cardiac_signal * (1 + irregularity) * 0.7

    elif condition == 'shock':
        # Very weak, thready pulses
        pulse_amplitude = self.pulse_amplitude_red * 0.3
        cardiac_signal = cardiac_signal * 0.5

    return self._apply_waveform_characteristics(cardiac_signal, pulse_amplitude)
```

### Arrhythmia Simulation

Basic arrhythmia patterns can be simulated:

```python
def _simulate_arrhythmia(self, base_signal: float, arrhythmia_type: str) -> float:
    if arrhythmia_type == 'premature_ventricular_contraction':
        # Occasional early, large-amplitude beats
        if np.random.random() < 0.1:  # 10% chance of PVC
            return base_signal * 1.5  # Larger amplitude
    elif arrhythmia_type == 'atrial_fibrillation':
        # Irregularly irregular rhythm
        irregularity = np.random.normal(0, 0.3)
        return base_signal * (1 + irregularity)

    return base_signal
```

## Custom Waveform Generation

### Extending with Custom Patterns

Users can extend the waveform generation with custom patterns:

```python
class CustomDataGenerator(DataGenerator):
    def _generate_custom_waveform(self, waveform_type: str) -> float:
        if waveform_type == 'custom_pattern':
            # Implement custom waveform pattern
            custom_signal = self._create_custom_pattern()
            return custom_signal
        else:
            return super()._generate_waveform(waveform_type)

    def _create_custom_pattern(self) -> float:
        # Custom waveform generation logic
        t = self.time_index * 2 * np.pi
        custom_wave = (np.sin(t) + 0.5 * np.sin(3*t) + 0.25 * np.sin(5*t)) / 1.75
        return custom_wave
```

### Adding New Noise Types

```python
def _add_custom_noise(self, signal: float, noise_type: str) -> float:
    if noise_type == 'electromagnetic_interference':
        emi_noise = 0.1 * np.sin(2 * np.pi * 120 * self.time_index)  # 120 Hz EMI
        return signal + emi_noise
    elif noise_type == 'baseline_drift':
        drift = 0.01 * self.time_index  # Slow baseline drift
        return signal + drift
    else:
        return signal
```

## Performance Optimization

### Efficient Signal Generation

The generator uses several optimization techniques:

1. **Vectorized Operations**: Using NumPy for efficient array operations
2. **Cached Calculations**: Reusing calculated values when possible
3. **Lazy Evaluation**: Only recalculating when parameters change
4. **Memory Management**: Efficient buffer management for real-time operation

### Real-time Considerations

```python
def optimize_for_realtime(self, target_latency_ms: float):
    # Adjust parameters for real-time performance
    sample_rate = min(self.sample_rate, 1000)  # Cap sample rate if needed
    buffer_size = int(target_latency_ms * sample_rate / 1000)

    self.set_sample_rate(sample_rate)
    self.buffer_size = buffer_size
```

## Validation and Testing

### Signal Validation

```python
def validate_signal_characteristics(self, signal: np.array) -> bool:
    # Check for physiologically plausible signals
    checks = [
        self._check_signal_range(signal),
        self._check_heart_rate_consistency(signal),
        self._check_respiratory_modulation(signal),
        self._check_noise_levels(signal)
    ]

    return all(checks)

def _check_signal_range(self, signal: np.array) -> bool:
    # Signal should stay within reasonable bounds
    signal_range = np.max(signal) - np.min(signal)
    return 1000 < signal_range < 50000
```

### Performance Testing

```python
def test_generation_performance(self, duration_seconds: int) -> Dict[str, Any]:
    start_time = time.time()
    sample_count = 0

    while time.time() - start_time < duration_seconds:
        self.generate_data_point()
        sample_count += 1

    actual_duration = time.time() - start_time
    actual_sample_rate = sample_count / actual_duration

    return {
        'target_sample_rate': self.sample_rate,
        'actual_sample_rate': actual_sample_rate,
        'samples_generated': sample_count,
        'duration': actual_duration,
        'performance_ratio': actual_sample_rate / self.sample_rate
    }
```

## Research and Development Applications

The data generation algorithms can be used for:

1. **Algorithm Development**: Testing PPG processing algorithms
2. **Machine Learning**: Generating training data for ML models
3. **Device Testing**: Validating pulse oximeter performance
4. **Clinical Research**: Simulating various physiological conditions
5. **Education**: Demonstrating PPG signal characteristics

### Example Research Setup

```python
# Generate data for algorithm testing
generator = DataGenerator(physio_model)
test_scenarios = ['normal_resting', 'running', 'heart_attack']

for scenario in test_scenarios:
    physio_model.set_scenario(scenario)

    # Generate 5 minutes of data
    data = []
    for _ in range(5 * 60 * generator.sample_rate):
        data_point = generator.generate_data_point()
        data.append(data_point)

    # Save for algorithm testing
    save_test_data(data, f'{scenario}_ppg_data.csv')
```
