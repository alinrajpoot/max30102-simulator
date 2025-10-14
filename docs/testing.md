# Testing Guide

Comprehensive guide to testing the MAX30102 Simulator, including unit tests, integration tests, and performance testing.

## Overview

The MAX30102 Simulator includes a comprehensive test suite to ensure reliability, accuracy, and performance. This guide covers running existing tests and writing new tests.

## Test Structure

### Test Directory Layout

```
max30102-simulator/
├── tests/
│   ├── __init__.py
│   ├── test_physiological_model.py
│   ├── test_max30102_device.py
│   ├── test_data_generator.py
│   ├── test_i2c_simulator.py
│   └── integration_test.py
```

### Test Categories

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing
3. **Performance Tests**: System performance validation
4. **Scenario Tests**: Medical scenario validation

## Running Tests

### Basic Test Execution

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_physiological_model.py -v

# Run tests with coverage report
python -m pytest --cov=src --cov-report=html
```

### Test Configuration

Create `pytest.ini` for custom test configuration:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
filterwarnings =
    ignore::DeprecationWarning
```

## Unit Testing

### Physiological Model Tests

```python
class TestPhysiologicalModel:
    def test_initial_state(self):
        """Test that model initializes with correct default state"""
        model = PhysiologicalModel()
        state = model.get_current_state()

        assert state['age'] == 30
        assert state['gender'] == 'male'
        assert state['activity'] == 'resting'
        assert state['condition'] == 'normal'
        assert 60 <= state['heart_rate_bpm'] <= 80  # Reasonable resting HR

    def test_parameter_update(self):
        """Test updating physiological parameters"""
        model = PhysiologicalModel()

        # Update parameters
        success = model.update_parameters({
            'age': 25,
            'gender': 'female',
            'activity': 'walking'
        })

        assert success == True

        state = model.get_current_state()
        assert state['age'] == 25
        assert state['gender'] == 'female'
        assert state['activity'] == 'walking'

    def test_scenario_application(self):
        """Test applying pre-defined scenarios"""
        model = PhysiologicalModel()

        # Apply running scenario
        success = model.set_scenario('running')
        assert success == True

        state = model.get_current_state()
        assert state['heart_rate_bpm'] > 100  # Running should increase HR
        assert state['condition'] == 'running'

    def test_emergency_scenarios(self):
        """Test emergency medical scenarios"""
        model = PhysiologicalModel()

        # Test heart attack scenario
        model.set_scenario('heart_attack')
        state = model.get_current_state()

        assert state['heart_rate_bpm'] < 60  # Bradycardia in heart attack
        assert state['spo2_percent'] < 90    # Low oxygen saturation
        assert state['pulse_quality'] == 'weak'

    def test_physiological_ranges(self):
        """Test that parameters stay within physiological ranges"""
        model = PhysiologicalModel()

        # Try to set extreme values
        model.update_parameters({
            'heart_rate_bpm': 500,  # Impossible value
            'spo2_percent': 200,    # Impossible value
            'respiratory_rate': 100 # Impossible value
        })

        state = model.get_current_state()

        # Should be clamped to reasonable ranges
        assert state['heart_rate_bpm'] <= 220
        assert state['spo2_percent'] <= 100
        assert state['respiratory_rate'] <= 60
```

### MAX30102 Device Tests

```python
class TestMAX30102Device:
    def test_device_initialization(self):
        """Test device initialization with default registers"""
        device = MAX30102Device()

        # Check some key registers
        assert device.registers[REG_MODE_CONFIG] == MODE_SPO2
        assert device.registers[REG_PART_ID] == 0x15  # MAX30102 part ID
        assert device.registers[REG_REV_ID] == 0x02   # Revision ID

    def test_register_write_read(self):
        """Test basic register write and read operations"""
        device = MAX30102Device()

        # Test valid register write/read
        success = device.write_register(REG_LED1_PA, 0x20)
        assert success == True

        value = device.read_register(REG_LED1_PA)
        assert value == 0x20

        # Test invalid register
        success = device.write_register(0xFF, 0x10)  # Invalid register
        assert success == False

        value = device.read_register(0xFF)  # Invalid register
        assert value is None

    def test_fifo_operations(self):
        """Test FIFO buffer operations"""
        device = MAX30102Device()

        # Push samples to FIFO
        device.push_sample_to_fifo(10000, 9500)
        device.push_sample_to_fifo(11000, 10500)

        # Check FIFO status
        status = device.get_status()
        assert status['fifo_samples'] == 2

        # Test FIFO overflow
        for i in range(40):  # More than FIFO size
            device.push_sample_to_fifo(10000 + i, 9500 + i)

        status = device.get_status()
        assert status['fifo_samples'] <= device.fifo_size
        assert device.registers[REG_OVF_COUNTER] > 0  # Should have overflows
```

### Data Generator Tests

```python
class TestDataGenerator:
    def test_data_generator_initialization(self):
        """Test data generator initialization"""
        physio_model = PhysiologicalModel()
        generator = DataGenerator(physio_model)

        assert generator.physio_model == physio_model
        assert generator.sample_rate == 1000
        assert generator.time_index == 0.0

    def test_data_point_generation(self):
        """Test generating individual data points"""
        physio_model = PhysiologicalModel()
        generator = DataGenerator(physio_model)

        data_point = generator.generate_data_point()

        # Check required fields
        assert 'timestamp' in data_point
        assert 'red_ppg' in data_point
        assert 'ir_ppg' in data_point
        assert 'heart_rate' in data_point
        assert 'spO2' in data_point
        assert 'activity' in data_point
        assert 'condition' in data_point

        # Check data types and reasonable ranges
        assert isinstance(data_point['red_ppg'], int)
        assert isinstance(data_point['ir_ppg'], int)
        assert isinstance(data_point['heart_rate'], float)
        assert isinstance(data_point['spO2'], float)

        # PPG values should be positive
        assert data_point['red_ppg'] > 0
        assert data_point['ir_ppg'] > 0

        # Heart rate should be in physiological range
        assert 30 <= data_point['heart_rate'] <= 220

        # SpO2 should be in reasonable range
        assert 70 <= data_point['spO2'] <= 100

    def test_ppg_waveform_generation(self):
        """Test PPG waveform generation"""
        physio_model = PhysiologicalModel()
        generator = DataGenerator(physio_model)

        # Generate multiple samples to check waveform pattern
        samples_red = []
        samples_ir = []

        for _ in range(100):  # Generate 100 samples
            data_point = generator.generate_data_point()
            samples_red.append(data_point['red_ppg'])
            samples_ir.append(data_point['ir_ppg'])

        # Should have some variation (not constant)
        assert len(set(samples_red)) > 1
        assert len(set(samples_ir)) > 1

        # Red and IR should be correlated but not identical
        assert samples_red != samples_ir
```

## Integration Testing

### Complete System Integration

```python
class TestIntegration:
    def test_complete_data_flow(self):
        """Test complete data flow from model to TCP output"""
        # Create physiological model
        physio_model = PhysiologicalModel()

        # Create data generator
        data_gen = DataGenerator(physio_model)

        # Generate multiple data points
        data_points = []
        for _ in range(10):
            data_point = data_gen.generate_data_point()
            data_points.append(data_point)

        # Verify data structure and content
        for dp in data_points:
            assert all(key in dp for key in [
                'timestamp', 'red_ppg', 'ir_ppg', 'heart_rate',
                'spO2', 'activity', 'condition'
            ])

            # Check data types
            assert isinstance(dp['red_ppg'], int)
            assert isinstance(dp['ir_ppg'], int)
            assert isinstance(dp['heart_rate'], float)
            assert isinstance(dp['spO2'], float)

    def test_scenario_transitions(self):
        """Test smooth transitions between scenarios"""
        physio_model = PhysiologicalModel()
        data_gen = DataGenerator(physio_model)

        scenarios = ['normal_resting', 'walking', 'running', 'heart_attack']
        hr_values = {}

        for scenario in scenarios:
            # Apply scenario
            physio_model.set_scenario(scenario)
            time.sleep(0.1)  # Allow model to stabilize

            # Generate samples and record average HR
            hr_sum = 0
            sample_count = 10

            for _ in range(sample_count):
                data_point = data_gen.generate_data_point()
                hr_sum += data_point['heart_rate']
                time.sleep(0.01)

            hr_values[scenario] = hr_sum / sample_count

        # Verify physiological responses
        assert hr_values['walking'] > hr_values['normal_resting']
        assert hr_values['running'] > hr_values['walking']
        assert hr_values['heart_attack'] < hr_values['normal_resting']  # Bradycardia
```

## Performance Testing

### Data Rate Testing

```python
def test_data_generation_performance():
    """Test that data generation meets performance requirements"""
    physio_model = PhysiologicalModel()
    generator = DataGenerator(physio_model)

    # Test different sample rates
    sample_rates = [100, 500, 1000]

    for sample_rate in sample_rates:
        generator.set_sample_rate(sample_rate)

        start_time = time.time()
        sample_count = 0

        # Generate data for 2 seconds
        while time.time() - start_time < 2.0:
            generator.generate_data_point()
            sample_count += 1

        actual_duration = time.time() - start_time
        actual_sample_rate = sample_count / actual_duration

        # Should achieve at least 90% of target sample rate
        assert actual_sample_rate >= sample_rate * 0.9, \
            f"Failed to achieve target sample rate: {sample_rate} Hz"
```

### Memory Usage Testing

```python
def test_memory_usage():
    """Test that memory usage remains within reasonable bounds"""
    import psutil
    import os

    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss

    # Create multiple components
    components = []
    for i in range(100):
        model = PhysiologicalModel()
        generator = DataGenerator(model)
        components.append((model, generator))

    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory

    # Memory increase should be reasonable (less than 10MB)
    assert memory_increase < 10 * 1024 * 1024, \
        f"Excessive memory usage: {memory_increase / 1024 / 1024:.2f} MB"
```

## Scenario Validation Testing

### Medical Scenario Validation

```python
def test_scenario_validation():
    """Test that all scenarios have valid physiological parameters"""
    scenario_manager = ScenarioManager()
    all_scenarios = scenario_manager.get_all_scenarios()

    for scenario_name, scenario in all_scenarios.items():
        physio_params = scenario.get('physiological', {})

        # Validate parameters
        errors = scenario_manager.validate_scenario_parameters(physio_params)

        assert len(errors) == 0, \
            f"Scenario '{scenario_name}' has invalid parameters: {errors}"

        # Verify scenario description exists
        assert 'description' in scenario, \
            f"Scenario '{scenario_name}' missing description"
```

## TCP Protocol Testing

### Client-Server Communication

```python
class TestTCPCommunication:
    def test_server_initialization(self):
        """Test TCP server initialization"""
        server = TCPServer(host='localhost', port=8888)

        # Verify components are initialized
        assert server.physio_model is not None
        assert server.max30102 is not None
        assert server.data_gen is not None
        assert server.host == 'localhost'
        assert server.port == 8888

    def test_command_processing(self):
        """Test command processing and responses"""
        # This would require mocking the TCP connection
        # or using a test client-server setup

        # Example of testing command validation
        model = PhysiologicalModel()

        # Test valid command
        success = model.update_parameters({'age': 35})
        assert success == True

        # Test invalid command
        success = model.update_parameters({'invalid_param': 'value'})
        # Should still return True (invalid params are ignored)
        assert success == True
```

## Mock Testing

### Using Mocks for Isolation

```python
from unittest.mock import Mock, patch

class TestWithMocks:
    def test_with_mocked_components(self):
        """Test using mocked dependencies"""
        # Create a mock physiological model
        mock_model = Mock(spec=PhysiologicalModel)
        mock_model.get_current_state.return_value = {
            'heart_rate_bpm': 75.0,
            'spo2_percent': 98.0,
            'activity': 'resting'
        }

        # Create data generator with mock model
        generator = DataGenerator(mock_model)

        # Generate data point
        data_point = generator.generate_data_point()

        # Verify data structure
        assert 'heart_rate' in data_point
        assert data_point['activity'] == 'resting'

        # Verify mock was called
        mock_model.get_current_state.assert_called()

    @patch('src.simulator.server.socket.socket')
    def test_server_with_mocked_socket(self, mock_socket):
        """Test server with mocked socket"""
        server = TCPServer()

        # Mock client connection
        mock_client = Mock()
        mock_socket.return_value.accept.return_value = (mock_client, ('127.0.0.1', 12345))

        # Start server (will use mocked socket)
        success = server.start_server()

        assert success == True
        mock_socket.assert_called()
```

## Continuous Integration

### GitHub Actions Configuration

Create `.github/workflows/test.yml`:

```yaml
name: Test MAX30102 Simulator

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10]

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          python -m pytest --cov=src --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v2
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
```

## Test Data Generation

### Creating Test Data Sets

```python
def generate_test_data():
    """Generate test data for validation"""
    scenarios = ['normal_resting', 'walking', 'running', 'heart_attack']
    test_data = {}

    for scenario in scenarios:
        model = PhysiologicalModel()
        model.set_scenario(scenario)

        generator = DataGenerator(model)
        samples = []

        # Generate 10 seconds of data
        for _ in range(10 * generator.sample_rate):
            sample = generator.generate_data_point()
            samples.append(sample)

        test_data[scenario] = samples

    # Save test data
    with open('test_data.json', 'w') as f:
        json.dump(test_data, f, indent=2)

    return test_data
```

## Writing New Tests

### Test Template

```python
def test_new_feature():
    """Test description explaining what is being tested"""
    # Setup
    component = ComponentUnderTest()

    # Exercise
    result = component.method_under_test()

    # Verify
    assert result == expected_value
    assert condition_is_met

    # Cleanup (if necessary)
    component.cleanup()
```

### Best Practices

1. **Test Naming**: Use descriptive test names
2. **Arrange-Act-Assert**: Follow the AAA pattern
3. **Isolation**: Each test should be independent
4. **Coverage**: Aim for high test coverage
5. **Edge Cases**: Test boundary conditions and error cases

### Example New Test

```python
def test_custom_scenario_creation():
    """Test creating and validating custom scenarios"""
    # Setup
    scenario_manager = ScenarioManager()

    # Exercise
    success = scenario_manager.create_custom_scenario(
        name='test_scenario',
        description='Test custom scenario',
        physiological_params={
            'heart_rate_bpm': 85,
            'spo2_percent': 97,
            'respiratory_rate': 18
        }
    )

    # Verify
    assert success == True

    # Retrieve and validate the scenario
    scenario = scenario_manager.get_scenario('test_scenario')
    assert scenario is not None
    assert scenario['description'] == 'Test custom scenario'

    # Cleanup
    scenario_manager.delete_scenario('test_scenario')
```

## Troubleshooting Tests

### Common Test Issues

**Test Dependencies:**

- Ensure all dependencies are installed
- Check Python version compatibility
- Verify test data files exist

**Timing Issues:**

- Use appropriate timeouts for performance tests
- Account for system load variations
- Consider using mock time for timing-sensitive tests

**Environment Issues:**

- Set up proper test environment variables
- Ensure sufficient system resources
- Check file permissions for test data

### Debugging Failed Tests

```python
# Add debug output to tests
def test_with_debugging():
    component = ComponentUnderTest()

    # Debug: print intermediate values
    print(f"Initial state: {component.get_state()}")

    result = component.method_under_test()

    print(f"Result: {result}")
    print(f"Expected: {expected_value}")

    assert result == expected_value
```

## Test Reports

### Generating Test Reports

```bash
# Generate HTML test report
python -m pytest --html=report.html --self-contained-html

# Generate JUnit XML for CI systems
python -m pytest --junitxml=report.xml

# Generate coverage report
python -m pytest --cov=src --cov-report=html
```

### Coverage Analysis

```bash
# Check coverage by module
python -m pytest --cov=src.models --cov-report=term-missing

# Check coverage for specific files
python -m pytest --cov=src/simulator/server.py --cov-report=term
```

## Next Steps

- Run the test suite regularly during development
- Add tests for new features and bug fixes
- Monitor test coverage and aim for improvement
- Integrate with CI/CD pipeline for automated testing
- Use test results to guide refactoring and optimization
