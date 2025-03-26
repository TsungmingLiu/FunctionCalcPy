# Bond Analytics Engine

A flexible and extensible analytics engine for evaluating financial equations with support for external API calls and dependency management.

## Features

- Dynamic equation parsing and validation
- Support for external API calls
- Automatic dependency resolution
- Circular dependency detection
- Safe formula evaluation
- Configurable API settings
- JSON-based configuration

## Project Structure

```
.
├── README.md
├── requirements.txt
├── config.json           # Configuration file for equations and settings
├── models.py            # Data classes and models
├── engine.py            # Core analytics engine
├── config_loader.py     # Configuration management
└── main.py             # Main entry point
```

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The `config.json` file contains all the equations and settings:

```json
{
    "equations": [
        "yield = API(YIELD)",
        "risk_free = API(RISK_FREE_RATE)",
        "volatility = API(VOLATILITY)",
        "spread = yield - risk_free",
        "risk = volatility * 2"
    ],
    "default_requested_fields": ["yield", "spread", "risk"],
    "api_settings": {
        "latency": 0.1,
        "yield_multiplier": 0.05,
        "risk_free_rate": 0.03,
        "volatility_multiplier": 0.02
    }
}
```

### Configuration Options

- `equations`: List of equations in the format `field = formula`
- `default_requested_fields`: List of fields to compute by default
- `api_settings`: Configuration for API behavior
  - `latency`: Simulated API call delay in seconds
  - `yield_multiplier`: Multiplier for yield calculation
  - `risk_free_rate`: Constant risk-free rate
  - `volatility_multiplier`: Multiplier for volatility calculation

## Usage

1. Basic usage:
```python
from models import Bond
from engine import AnalyticsEngine
from config_loader import ConfigLoader

# Load configuration
config = ConfigLoader('config.json')
config.load()

# Create bonds
bonds = [
    Bond("BOND1", "20230601", 100.0),
    Bond("BOND2", "20230601", 101.5)
]

# Initialize engine
engine = AnalyticsEngine(api_settings=config.api_settings)

# Validate and process equations
engine.validate_equations(config.equations)
engine.topological_sort()

# Compute analytics
results = engine.compute_analytics(bonds, config.default_requested_fields)
```

2. Run the example:
```bash
python main.py
```

## Equation Syntax

- Basic arithmetic: `field = value1 + value2`
- API calls: `field = API(API_NAME)`
- Variables: `field = other_field * 2`
- Functions: `field = max(value1, value2)`

Supported functions:
- `abs()`: Absolute value
- `max()`: Maximum value
- `min()`: Minimum value
- `pow()`: Power function

## Error Handling

The engine provides detailed error messages for:
- Invalid equation syntax
- Missing dependencies
- Circular dependencies
- API call failures
- Formula evaluation errors

## Development

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest
```

3. Format code:
```bash
black .
```

4. Type checking:
```bash
mypy .
```

5. Lint code:
```bash
pylint .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
