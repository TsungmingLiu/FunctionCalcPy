from typing import Dict, List, Set
from collections import defaultdict
import re

class EquationResolver:
    def __init__(self):
        self.variables = {}  # Stores variable values
        self.dependencies = defaultdict(set)  # Graph of dependencies
        self.equations = {}  # Stores equations/computations for each variable

    def parse_equation(self, var_name: str, equation: str) -> callable:
        """
        Parse a string equation into a lambda function
        Example: "x + y * 2" becomes lambda x, y: x + y * 2
        """
        # Find all variable names used in equation
        vars = set(re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', equation))
        
        # Add to dependencies
        self.dependencies[var_name].update(vars)
        
        # Create lambda function that accepts **kwargs to handle any variable
        # Replace variables with kwargs access using regex to avoid partial matches
        for var in vars:
            equation = re.sub(rf'\b{var}\b', f"kwargs['{var}']", equation)
        return eval(f"lambda **kwargs: {equation}")

    def add_equation(self, var_name: str, equation):
        """
        Add an equation for a variable. Equation can be:
        - A string containing arithmetic expression
        - A constant value
        - An async function for external API calls
        """
        if isinstance(equation, str):
            # Parse string equation and find dependencies
            vars = set(re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', equation))
            vars.discard(var_name)  # Remove self-reference
            self.dependencies[var_name].update(vars)
            self.equations[var_name] = self.parse_equation(var_name, equation)
        else:
            self.equations[var_name] = equation

    def _topological_sort(self) -> List[str]:
        """
        Perform topological sort on variable dependencies
        """
        visited = set()
        temp_mark = set()
        order = []
        
        def visit(var: str):
            if var in temp_mark:
                raise ValueError(f"Circular dependency detected involving {var}")
            if var in visited:
                return
                
            temp_mark.add(var)
            
            for dep in self.dependencies[var]:
                visit(dep)
                
            temp_mark.remove(var)
            visited.add(var)
            order.append(var)
            
        for var in self.equations:
            if var not in visited:
                visit(var)
                
        return order

    async def resolve(self) -> Dict[str, any]:
        """
        Resolve all variables in dependency order
        """
        order = self._topological_sort()
        
        for var in order:
            equation = self.equations[var]
            
            if callable(equation):
                if asyncio.iscoroutinefunction(equation):
                    # Handle async API calls
                    self.variables[var] = await equation()
                else:
                    # Handle arithmetic computations
                    try:
                        self.variables[var] = equation(**self.variables)
                    except Exception as e:
                        raise ValueError(f"Error resolving {var}: {str(e)}")
            else:
                # Handle constant values
                self.variables[var] = equation
                
        return self.variables

    async def resolve_variable(self, var_name: str) -> any:
        """
        Resolve a single variable and its dependencies
        """
        if var_name not in self.equations:
            raise ValueError(f"Variable {var_name} not found")
            
        # Get all dependencies for this variable
        deps = set()
        def collect_deps(var: str):
            deps.add(var)
            for dep in self.dependencies[var]:
                collect_deps(dep)
        collect_deps(var_name)
        
        # Sort dependencies topologically
        order = self._topological_sort()
        order = [var for var in order if var in deps]
        
        # Resolve only required variables
        for var in order:
            equation = self.equations[var]
            
            if callable(equation):
                if asyncio.iscoroutinefunction(equation):
                    self.variables[var] = await equation()
                else:
                    try:
                        self.variables[var] = equation(**self.variables)
                    except Exception as e:
                        raise ValueError(f"Error resolving {var}: {str(e)}")
            else:
                self.variables[var] = equation
                
        return self.variables[var_name]

    async def resolve_variables(self, var_names: List[str]) -> Dict[str, any]:
        """
        Resolve multiple variables and their shared dependencies
        """
        # Validate all variables exist
        for var_name in var_names:
            if var_name not in self.equations:
                raise ValueError(f"Variable {var_name} not found")
            
        # Get all dependencies for all requested variables
        deps = set()
        def collect_deps(var: str):
            deps.add(var)
            for dep in self.dependencies[var]:
                collect_deps(dep)
        
        for var_name in var_names:
            collect_deps(var_name)
        
        # Sort dependencies topologically
        order = self._topological_sort()
        order = [var for var in order if var in deps]
        
        # Resolve only required variables
        for var in order:
            equation = self.equations[var]
            
            if callable(equation):
                if asyncio.iscoroutinefunction(equation):
                    self.variables[var] = await equation()
                else:
                    try:
                        self.variables[var] = equation(**self.variables)
                    except Exception as e:
                        raise ValueError(f"Error resolving {var}: {str(e)}")
            else:
                self.variables[var] = equation
                
        # Return only the requested variables
        return {var: self.variables[var] for var in var_names}

# Example usage with human-readable equations:
async def example():
    resolver = EquationResolver()
    
    # Basic arithmetic equations
    resolver.add_equation('base_price', 100)  # Constant
    resolver.add_equation('tax_rate', 0.2)    # Constant
    resolver.add_equation('tax_amount', 'base_price * tax_rate')
    resolver.add_equation('shipping', 15)      # Constant
    resolver.add_equation('total', 'base_price + tax_amount + shipping')
    
    # More complex equations
    resolver.add_equation('x', 5)
    resolver.add_equation('y', 3)
    resolver.add_equation('z', 'x * y + (x + y) / 2')
    
    # Equation with multiple dependencies
    resolver.add_equation('a', 10)
    resolver.add_equation('b', 'a * 2')
    resolver.add_equation('c', 'a + b')
    resolver.add_equation('final', 'c * (z + total)')
    
    # Add async API call example
    async def get_exchange_rate():
        # Simulate API call
        await asyncio.sleep(1)
        return 1.2
    resolver.add_equation('exchange_rate', get_exchange_rate)
    
    # Use API result in equation
    resolver.add_equation('foreign_price', 'total * exchange_rate')
    
    # Resolve multiple variables at once
    results = await resolver.resolve_variables(['foreign_price', 'final'])
    print("\nResolved Variables:")
    for var, value in results.items():
        print(f"{var} = {value}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example())

