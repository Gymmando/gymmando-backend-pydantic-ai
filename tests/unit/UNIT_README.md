# Unit Tests

This directory contains unit tests for the Gymmando backend application.

## Running Tests

### Run all unit tests
```bash
pytest tests/unit/
```

### Run with verbose output
```bash
pytest tests/unit/ -v
```

### Run with coverage
```bash
pytest tests/unit/ --cov=gymmando_graph
```

### Run with verbose and coverage
```bash
pytest tests/unit/ -v --cov=gymmando_graph
```

### Run with coverage HTML report
```bash
pytest tests/unit/ --cov=gymmando_graph --cov-report=html
```

### Run a specific test file
```bash
pytest tests/unit/test_logger.py
```

### Run a specific test class
```bash
pytest tests/unit/test_logger.py::TestLogger
```

### Run a specific test method
```bash
pytest tests/unit/test_logger.py::TestLogger::TestInit::test_init_with_defaults
```

### Run tests matching a pattern
```bash
pytest tests/unit/ -k "test_init"
```

### Run tests and show print statements
```bash
pytest tests/unit/ -v -s
```

## Dependencies

Make sure you have the following packages installed:
```bash
pip install pytest pytest-cov pytest-mock
```

## Test Organization

Tests are organized using pytest's OOP style with test classes:
- Each test file corresponds to a module being tested
- Test classes group related tests (e.g., `TestInit`, `TestMethodName`)
- Tests follow the pattern: `test_<method_name>`

## Coverage Goals

- Target: 80%+ overall coverage
- Critical paths: 90%+ coverage
- All error paths should be tested

