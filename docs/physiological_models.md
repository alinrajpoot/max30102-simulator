# Physiological Models

Detailed documentation of the physiological modeling system in the MAX30102 Simulator.

## Overview

The physiological models simulate realistic human physiological responses based on parameters like age, gender, activity level, and medical conditions. These models drive the generation of realistic PPG waveforms and vital signs.

## Core Physiological Model

### PhysiologicalState Dataclass

The foundation of the modeling system is the `PhysiologicalState` dataclass:

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

    # Vital signs
    heart_rate_bpm: float = 72.0
    spo2_percent: float = 98.0
    respiratory_rate: int = 16

    # Waveform parameters
    pulse_amplitude_red: int = 10000
    pulse_amplitude_ir: int = 9500
    baseline_red: int = 50000
    baseline_ir: int = 48000
    noise_level: float = 0.05

    # Motion artifacts
    motion_artifact_probability: float = 0.1
    motion_artifact_duration: float = 0.5

    # Heart rate variability
    heart_rate_variability: str = "normal"
    pulse_rhythm: str = "regular"
    pulse_quality: str = "normal"
```

## Parameter Relationships

### Age-Based Adjustments

The model implements several age-dependent physiological relationships:

**Maximum Heart Rate (Tanaka formula):**

```python
max_hr = 208 - (0.7 * age)
```

**Resting Heart Rate:**

```python
resting_hr = 72 - (age - 30) * 0.1  # Slight decrease with age
```

**Respiratory Rate:**

```python
respiratory_rate = 16 - (age - 30) * 0.02
```

### Gender Differences

The model accounts for physiological differences between genders:

```python
gender_factors = {
    'male': {
        'hr_offset': 0,           # No heart rate offset
        'amplitude_factor': 1.0   # Normal pulse amplitude
    },
    'female': {
        'hr_offset': 5,           # Slightly higher heart rate
        'amplitude_factor': 0.9   # Slightly lower pulse amplitude
    }
}
```

### Activity Level Effects

Different activities significantly impact physiological parameters:

```python
activity_effects = {
    'resting': {
        'heart_rate_factor': 1.0,
        'respiratory_factor': 1.0,
        'amplitude_factor': 1.0,
        'noise_factor': 0.2
    },
    'walking': {
        'heart_rate_factor': 1.3,
        'respiratory_factor': 1.5,
        'amplitude_factor': 1.2,
        'noise_factor': 0.5
    },
    'running': {
        'heart_rate_factor': 1.9,
        'respiratory_factor': 2.0,
        'amplitude_factor': 1.5,
        'noise_factor': 0.8
    },
    'sleeping': {
        'heart_rate_factor': 0.8,
        'respiratory_factor': 0.6,
        'amplitude_factor': 0.7,
        'noise_factor': 0.1
    },
    'sex_time': {
        'heart_rate_factor': 1.8,
        'respiratory_factor': 1.8,
        'amplitude_factor': 1.4,
        'noise_factor': 0.6
    }
}
```

### Fitness Level Adjustments

Physical fitness level influences cardiovascular parameters:

```python
fitness_effects = {
    'athletic': {
        'hr_factor': 0.8,   # Lower resting heart rate
        'hrv': 'high'       # Higher heart rate variability
    },
    'average': {
        'hr_factor': 1.0,   # Standard heart rate
        'hrv': 'normal'     # Normal variability
    },
    'sedentary': {
        'hr_factor': 1.1,   # Higher resting heart rate
        'hrv': 'low'        # Lower variability
    }
}
```

## Medical Condition Modeling

### Heart Attack (Myocardial Infarction)

**Pathophysiology:**

- Reduced cardiac output due to myocardial damage
- Compensatory mechanisms failing
- Poor peripheral perfusion

**Parameter Changes:**

```python
heart_attack_params = {
    'heart_rate_bpm': 45,        # Bradycardia
    'spo2_percent': 85,          # Hypoxia
    'respiratory_rate': 8,       # Depressed breathing
    'pulse_amplitude_red': 5000, # Weak pulse
    'pulse_amplitude_ir': 4500,
    'noise_level': 0.1,
    'pulse_rhythm': 'irregular', # Arrhythmias
    'pulse_quality': 'weak'
}
```

### Extreme Anxiety (Panic Attack)

**Pathophysiology:**

- Sympathetic nervous system activation
- Increased catecholamine release
- Hyperventilation syndrome

**Parameter Changes:**

```python
anxiety_params = {
    'heart_rate_bpm': 120,       # Tachycardia
    'spo2_percent': 95,          # Mild desaturation
    'respiratory_rate': 25,      # Tachypnea
    'pulse_amplitude_red': 12000,# Strong, bounding pulse
    'pulse_amplitude_ir': 11500,
    'noise_level': 0.15,
    'heart_rate_variability': 'low'
}
```

### Medical Shock

**Pathophysiology:**

- Inadequate tissue perfusion
- Compensatory tachycardia
- Progressive organ dysfunction

**Parameter Changes:**

```python
shock_params = {
    'heart_rate_bpm': 140,       # Compensatory tachycardia
    'spo2_percent': 82,          # Severe hypoxia
    'respiratory_rate': 35,      # Compensatory hyperventilation
    'pulse_amplitude_red': 3000, # Very weak, thready pulse
    'pulse_amplitude_ir': 2800,
    'noise_level': 0.25,
    'pulse_quality': 'weak'
}
```

## Calculation Pipeline

### Parameter Recalculation

When parameters change, the model recalculates dependent values:

```python
def _recalculate_physiology(self):
    # Base calculations from age
    base_hr = self.age_factors['baseline_hr'](self.state.age)
    base_rr = self.age_factors['respiratory_rate'](self.state.age)

    # Apply gender adjustments
    gender_adj = self.gender_factors.get(self.state.gender,
                                       self.gender_factors['male'])
    base_hr += gender_adj['hr_offset']

    # Apply activity effects
    activity_eff = self.activity_effects.get(self.state.activity,
                                           self.activity_effects['resting'])
    self.state.heart_rate_bpm = base_hr * activity_eff['heart_rate_factor']
    self.state.respiratory_rate = int(base_rr * activity_eff['respiratory_factor'])

    # Apply fitness level
    fitness_eff = self.fitness_effects.get(self.state.fitness_level,
                                         self.fitness_effects['average'])
    self.state.heart_rate_bpm *= fitness_eff['hr_factor']
    self.state.heart_rate_variability = fitness_eff['hrv']

    # Apply condition-specific overrides
    self._apply_condition_effects()

    # Ensure realistic ranges
    self._clamp_to_physiological_ranges()
```

### Physiological Range Validation

The model ensures all parameters stay within physiologically possible ranges:

```python
def _clamp_to_physiological_ranges(self):
    # Heart rate limits
    self.state.heart_rate_bpm = max(30, min(220, self.state.heart_rate_bpm))

    # SpO2 limits
    self.state.spo2_percent = max(70, min(100, self.state.spo2_percent))

    # Respiratory rate limits
    self.state.respiratory_rate = max(6, min(60, self.state.respiratory_rate))

    # Amplitude limits
    self.state.pulse_amplitude_red = max(1000, min(20000, self.state.pulse_amplitude_red))
    self.state.pulse_amplitude_ir = max(1000, min(20000, self.state.pulse_amplitude_ir))

    # Noise level limits
    self.state.noise_level = max(0.01, min(1.0, self.state.noise_level))
```

## Stress Response Simulation

The model includes a configurable stress response:

```python
def simulate_stress_response(self, stress_level: float):
    stress_level = max(0.0, min(1.0, stress_level))

    # Linear interpolation between normal and extreme stress
    normal_hr = 72
    stress_hr = 120

    self.state.heart_rate_bpm = normal_hr + (stress_hr - normal_hr) * stress_level
    self.state.respiratory_rate = int(16 + (25 - 16) * stress_level)
    self.state.noise_level = 0.05 + (0.15 - 0.05) * stress_level
```

## Heart Rate Variability (HRV)

The model simulates different HRV patterns:

### HRV Patterns

```python
hrv_patterns = {
    'very_low': {
        'variation_range': 0.5,   # Very little variation
        'respiratory_modulation': 0.1
    },
    'low': {
        'variation_range': 1.0,   # Minimal variation
        'respiratory_modulation': 0.2
    },
    'normal': {
        'variation_range': 2.0,   # Healthy variation
        'respiratory_modulation': 0.5
    },
    'high': {
        'variation_range': 3.0,   # High variation (athletic)
        'respiratory_modulation': 0.8
    }
}
```

### Respiratory Sinus Arrhythmia

The model includes respiratory modulation of heart rate:

```python
# Calculate respiratory sinus arrhythmia component
respiratory_phase = 2 * np.pi * (self.respiratory_rate / 60.0) * time
rsa_component = np.sin(respiratory_phase) * hrv_pattern['respiratory_modulation']

# Apply to heart rate
instantaneous_hr = base_hr + rsa_component * hrv_pattern['variation_range']
```

## Custom Model Extensions

### Adding New Parameters

To add new physiological parameters:

1. **Extend PhysiologicalState:**

```python
@dataclass
class ExtendedPhysiologicalState(PhysiologicalState):
    blood_pressure_systolic: int = 120
    blood_pressure_diastolic: int = 80
    temperature_c: float = 37.0
    blood_glucose: float = 5.0  # mmol/L
```

2. **Update Calculation Methods:**

```python
def _recalculate_physiology(self):
    super()._recalculate_physiology()

    # Add custom parameter calculations
    self._calculate_blood_pressure()
    self._calculate_temperature()
```

### Custom Condition Handling

Add new medical conditions:

```python
def _apply_condition_effects(self):
    # Call parent method first
    super()._apply_condition_effects()

    # Add custom conditions
    if self.state.condition == 'fever':
        self.state.temperature_c = 39.0
        self.state.heart_rate_bpm *= 1.2

    elif self.state.condition == 'hypoglycemia':
        self.state.blood_glucose = 3.0
        self.state.heart_rate_bpm *= 1.3
        self.state.respiratory_rate += 5
```

## Validation and Testing

### Parameter Validation

```python
def validate_parameters(self, parameters: Dict[str, Any]) -> List[str]:
    errors = []

    valid_ranges = {
        'heart_rate_bpm': (30, 220),
        'spo2_percent': (70, 100),
        'respiratory_rate': (6, 60),
        'pulse_amplitude_red': (1000, 20000),
        'pulse_amplitude_ir': (1000, 20000),
        'noise_level': (0.01, 1.0)
    }

    for param, value in parameters.items():
        if param in valid_ranges:
            min_val, max_val = valid_ranges[param]
            if not (min_val <= value <= max_val):
                errors.append(f"{param} value {value} outside valid range")

    return errors
```

### Model Consistency Checks

```python
def check_model_consistency(self) -> Dict[str, Any]:
    issues = {}

    # Check heart rate vs activity consistency
    if self.state.activity == 'resting' and self.state.heart_rate_bpm > 100:
        issues['high_resting_hr'] = "Resting heart rate appears elevated"

    # Check SpO2 consistency with condition
    if self.state.condition == 'normal' and self.state.spo2_percent < 90:
        issues['low_normal_spo2'] = "Normal condition with low SpO2"

    # Check respiratory rate vs heart rate ratio
    rr_hr_ratio = self.state.respiratory_rate / self.state.heart_rate_bpm
    if rr_hr_ratio > 0.5:
        issues['high_rr_hr_ratio'] = "Respiratory rate high relative to heart rate"

    return issues
```

## Performance Considerations

### Real-time Calculations

The model is optimized for real-time operation:

- **Cached Calculations**: Frequently used values are cached
- **Lazy Evaluation**: Parameters are only recalculated when changed
- **Efficient Algorithms**: Use of vectorized operations where possible

### Memory Usage

- **Fixed State Size**: PhysiologicalState has fixed memory footprint
- **No Deep Copies**: State modifications are in-place when possible
- **Efficient Data Structures**: Use of native Python types

## Clinical Accuracy

### Reference Ranges

The model uses established clinical reference ranges:

| Parameter        | Normal Range | Critical Values |
| ---------------- | ------------ | --------------- |
| Heart Rate       | 60-100 bpm   | <40 or >180 bpm |
| SpO2             | 95-100%      | <90%            |
| Respiratory Rate | 12-20 bpm    | <8 or >30 bpm   |
| Pulse Amplitude  | 8,000-12,000 | <3,000          |

### Limitations and Assumptions

1. **Population Averages**: Models represent population averages, not individuals
2. **Simplified Physiology**: Complex interactions are simplified for simulation
3. **Static Parameters**: Some parameters that change slowly are treated as static
4. **Limited Comorbidities**: Complex multi-condition scenarios are simplified

## Research Applications

The physiological model can be used for:

1. **Algorithm Development**: Testing signal processing algorithms
2. **Clinical Training**: Simulating patient scenarios for education
3. **Device Testing**: Validating medical device performance
4. **Research Studies**: Investigating physiological relationships

### Example Research Use Case

```python
# Study age-related heart rate changes
ages = range(20, 81, 10)
hr_values = []

for age in ages:
    model = PhysiologicalModel()
    model.update_parameters({'age': age})
    state = model.get_current_state()
    hr_values.append(state['heart_rate_bpm'])

# Plot results
import matplotlib.pyplot as plt
plt.plot(ages, hr_values)
plt.xlabel('Age (years)')
plt.ylabel('Resting Heart Rate (bpm)')
plt.title('Age vs Resting Heart Rate')
plt.show()
```
