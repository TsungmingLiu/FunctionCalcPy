# Equation Resolver

A Python-based equation resolver that handles complex dependencies between variables, supports asynchronous API calls, and allows importing equations from XML files.

## Features

- **Dynamic Equation Resolution**: Resolves equations with complex dependencies in the correct order
- **Multiple Variable Types**:
  - Constant values
  - Arithmetic expressions
  - Asynchronous API calls
- **XML Import**: Load equations from external XML configuration files
- **Dependency Management**: Automatically detects and validates dependencies between variables
- **Selective Resolution**: Resolve only specific variables and their dependencies
- **Circular Dependency Detection**: Prevents infinite loops by detecting circular dependencies

## Installation

1. Clone the repository
2. Ensure you have Python 3.7+ installed
3. No additional dependencies required (uses standard library only)

## Usage

### Basic Usage

```python
import asyncio
from equation_resolver import EquationResolver

async def main():
    resolver = EquationResolver()
    
    # Add some equations
    resolver.add_equation('x', 5)  # Constant
    resolver.add_equation('y', 'x * 2')  # Expression
    
    # Resolve and print result
    result = await resolver.resolve_variable('y')
    print(f"y = {result}")  # Output: y = 10

asyncio.run(main())
```

### XML Configuration

Create an XML file with your equations:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<equations>
    <equation>
        <name>base_price</name>
        <value>100</value>
    </equation>
    <equation>
        <name>tax_rate</name>
        <value>0.2</value>
    </equation>
    <equation>
        <name>total</name>
        <expression>base_price * (1 + tax_rate)</expression>
    </equation>
</equations>
```

Load and use the XML configuration:

```python
resolver = EquationResolver()
resolver.import_from_xml('equations.xml')
result = await resolver.resolve_variable('total')
```

### Async API Integration

```python
# In api_functions.py
async def get_exchange_rate():
    # Make API call here
    return 1.2

# In your main code
from api_functions import get_exchange_rate

resolver.add_equation('exchange_rate', get_exchange_rate)
resolver.add_equation('foreign_price', 'total * exchange_rate')
```

## Project Structure

- `equation_resolver.py`: Core equation resolver implementation
- `xml_importer.py`: XML parsing functionality
- `api_functions.py`: Async API call implementations
- `main.py`: Example usage
- `equations.xml`: Example equation configuration

## Features in Detail

### Variable Resolution

The resolver handles three types of variables:
1. **Constants**: Simple numeric or string values
2. **Expressions**: Mathematical expressions using other variables
3. **API Calls**: Asynchronous functions that fetch external data

### Dependency Management

- Automatically detects dependencies in expressions
- Creates a dependency graph
- Performs topological sorting to determine resolution order
- Detects circular dependencies

### Error Handling

- Validates variable existence
- Detects circular dependencies
- Handles expression evaluation errors
- Provides meaningful error messages

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open-source and available under the MIT License. 
