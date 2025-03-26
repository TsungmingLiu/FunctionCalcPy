# Bond Analytics Engine

A flexible and extensible analytics engine for computing bond-related metrics using a declarative equation system.

## Features

- Declarative equation system for defining bond analytics
- Support for external API calls with simulated latency
- Automatic dependency resolution and computation ordering
- Circular dependency detection
- Safe formula evaluation with restricted context
- Support for basic mathematical operations
- Comprehensive error handling and logging

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Example

```python
from analytics_engine import AnalyticsEngine, Bond

# Define equations
equations = [
    "yield = API(YIELD)",
    "risk_free = API(RISK_FREE_RATE)",
    "volatility = API(VOLATILITY)",
    "spread = yield - risk_free",
    "risk = volatility * 2"
]

# Create bond instances
bonds = [
    Bond("BOND1", "20230601", 100.0),
    Bond("BOND2", "20230601", 101.5),
    Bond("BOND3", "20230601", 99.75)
]

# Initialize engine and compute analytics
engine = AnalyticsEngine()
engine.validate_equations(equations)
engine.topological_sort()
results = engine.compute_analytics(bonds, ["yield", "spread", "risk"])
```

### Equation Syntax

Equations follow a simple format:
```
field_name = formula
```

Where:
- `field_name`: The name of the computed field
- `formula`: A mathematical expression that can include:
  - Numbers (e.g., `2.5`)
  - Variables (e.g., `yield`, `spread`)
  - API calls (e.g., `API(YIELD)`)
  - Basic operators (`+`, `-`, `*`, `/`)
  - Parentheses for grouping

### Available API Calls

The engine includes mock implementations for the following API calls:
- `API(YIELD)`: Returns yield based on bond price
- `API(RISK_FREE_RATE)`: Returns a constant risk-free rate
- `API(VOLATILITY)`: Returns volatility based on bond price

## Error Handling

The engine provides detailed error messages for:
- Invalid equation syntax
- Missing dependencies
- Circular dependencies
- API call failures
- Formula evaluation errors

## Logging

The engine uses Python's logging module to provide detailed information about:
- Equation parsing
- Dependency resolution
- Computation progress
- Error conditions

## Dependencies

- Python 3.7+
- dataclasses
- typing
- logging
- json
- enum
- time
- collections
- re

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 