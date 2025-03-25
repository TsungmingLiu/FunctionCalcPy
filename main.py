import asyncio
from equation_resolver import EquationResolver
from api_functions import get_exchange_rate

async def example():
    resolver = EquationResolver()
    
    # Import equations from XML file
    resolver.import_from_xml('equations.xml')
    
    # Add async API call
    resolver.add_equation('exchange_rate', get_exchange_rate)
    
    # Use API result in equation
    resolver.add_equation('foreign_price', 'total * exchange_rate')
    
    # Resolve multiple variables at once
    results = await resolver.resolve_variables(['foreign_price', 'final'])
    print("\nResolved Variables:")
    for var, value in results.items():
        print(f"{var} = {value}")

if __name__ == "__main__":
    asyncio.run(example())