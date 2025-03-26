import logging
import time
import re
from collections import defaultdict
from typing import Dict, List

from models import Bond, AnalyticEquation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsEngine:
    def __init__(self, api_settings: Dict[str, float] = None):
        self.equations: Dict[str, AnalyticEquation] = {}
        self.computation_order: List[str] = []
        self.api_settings = api_settings or {
            'latency': 0.1,
            'yield_multiplier': 0.05,
            'risk_free_rate': 0.03,
            'volatility_multiplier': 0.02
        }
        
    def parse_equation(self, equation_str: str) -> AnalyticEquation:
        """Parse human-readable equation and extract dependencies and API calls"""
        if '=' not in equation_str:
            raise ValueError(f"Invalid equation format: {equation_str}")
            
        field, formula = [x.strip() for x in equation_str.split('=', 1)]
        
        # Extract API calls - format: API(name)
        api_calls = set(re.findall(r'API\((.*?)\)', formula))
        
        # Remove API calls from formula for dependency analysis
        formula_no_api = re.sub(r'API\(.*?\)', '', formula)
        
        # Extract variable dependencies (words not in quotes)
        dependencies = set()
        tokens = re.findall(r'\b\w+\b', formula_no_api)
        for token in tokens:
            if (not token.isdigit() and  # not a number
                token != field and       # not the field itself
                not token.upper() in ['AND', 'OR', 'NOT']):  # not an operator
                dependencies.add(token)
                
        return AnalyticEquation(field, formula, dependencies, api_calls)

    def validate_equations(self, equations: List[str]) -> None:
        """Validate equation syntax and check for circular dependencies"""
        # First pass: parse all equations
        for eq in equations:
            try:
                parsed = self.parse_equation(eq)
                self.equations[parsed.field] = parsed
            except Exception as e:
                raise ValueError(f"Failed to parse equation '{eq}': {str(e)}")

        # Second pass: validate dependencies
        all_fields = set(self.equations.keys())
        for field, eq in self.equations.items():
            undefined_deps = eq.dependencies - all_fields
            if undefined_deps:
                raise ValueError(f"Equation for {field} references undefined fields: {undefined_deps}")

        # Check for circular dependencies
        visited = set()
        temp_visited = set()

        def detect_cycle(field: str) -> bool:
            if field in temp_visited:
                return True
            if field in visited:
                return False
            
            temp_visited.add(field)
            for dep in self.equations[field].dependencies:
                if detect_cycle(dep):
                    return True
            temp_visited.remove(field)
            visited.add(field)
            return False

        for field in self.equations:
            if detect_cycle(field):
                raise ValueError(f"Circular dependency detected involving {field}")

    def topological_sort(self) -> None:
        """Determine computation order based on dependencies"""
        visited = set()
        temp = []

        def visit(field: str):
            if field in visited:
                return
            for dep in self.equations[field].dependencies:
                visit(dep)
            visited.add(field)
            temp.append(field)

        for field in self.equations:
            visit(field)
        
        self.computation_order = temp

    def mock_api_call(self, api_name: str, bonds: List[Bond]) -> Dict[str, float]:
        """Mock external API calls with simulated latency"""
        time.sleep(self.api_settings['latency'])  # Simulate API latency
        results = {}
        
        # Simulate different API behaviors based on API name
        for bond in bonds:
            if api_name == "YIELD":
                results[bond.identifier] = bond.price_quote * self.api_settings['yield_multiplier']
            elif api_name == "RISK_FREE_RATE":
                results[bond.identifier] = self.api_settings['risk_free_rate']
            elif api_name == "VOLATILITY":
                results[bond.identifier] = bond.price_quote * self.api_settings['volatility_multiplier']
            else:
                results[bond.identifier] = 0.0  # Default
                logger.warning(f"Unknown API call: {api_name}")
                
        return results

    def evaluate_formula(self, formula: str, bond: Bond, computed_values: Dict[str, float], 
                        api_results: Dict[str, Dict[str, float]]) -> float:
        """Evaluate formula with given values and API results"""
        # Create a copy of the formula for substitution
        eval_formula = formula
        
        # Replace API calls with their results
        for api_name in re.findall(r'API\((.*?)\)', formula):
            api_value = api_results[api_name][bond.identifier]
            eval_formula = re.sub(f"API\\({api_name}\\)", str(api_value), eval_formula)
        
        # Replace variables with their computed values
        # Sort variables by length (longest first) to avoid partial replacements
        variables = sorted(computed_values.keys(), key=len, reverse=True)
        for var in variables:
            # Use word boundaries to ensure we're replacing whole words only
            eval_formula = re.sub(r'\b' + var + r'\b', str(computed_values[var]), eval_formula)
        
        try:
            # Add basic math functions to evaluation context
            math_context = {
                'abs': abs,
                'max': max,
                'min': min,
                'pow': pow,
                '__builtins__': None  # Restrict built-ins for safety
            }
            # Safe eval of the formula
            return float(eval(eval_formula, math_context, {}))
        except Exception as e:
            logger.error(f"Failed to evaluate formula: '{formula}' -> '{eval_formula}'")
            raise ValueError(f"Failed to evaluate formula '{formula}': {str(e)}")

    def compute_analytics(self, bonds: List[Bond], requested_fields: List[str]) -> Dict[str, Dict[str, float]]:
        """Main computation method"""
        results = defaultdict(dict)
        
        # Validate inputs
        if not bonds or not requested_fields:
            raise ValueError("Must provide bonds and requested fields")

        try:
            # First, collect all required API calls
            required_apis = set()
            for field in self.computation_order:
                required_apis.update(self.equations[field].api_calls)

            # Execute all required API calls
            api_results = {}
            for api_name in required_apis:
                api_results[api_name] = self.mock_api_call(api_name, bonds)

            # Compute each field in order
            for bond in bonds:
                computed_values = {}  # Store intermediate results
                
                # Compute all fields in order, not just requested ones
                for field in self.computation_order:
                    equation = self.equations[field]
                    try:
                        # Check if all dependencies are available
                        missing_deps = [dep for dep in equation.dependencies if dep not in computed_values]
                        if missing_deps:
                            logger.error(f"Missing dependencies for {field}: {missing_deps}")
                            results[bond.identifier][field] = None
                            continue
                            
                        value = self.evaluate_formula(
                            equation.formula, 
                            bond,
                            computed_values,
                            api_results
                        )
                        computed_values[field] = value
                        # Only store in results if it's a requested field
                        if field in requested_fields:
                            results[bond.identifier][field] = value
                        
                    except Exception as e:
                        logger.error(f"Error computing {field} for bond {bond.identifier}: {str(e)}")
                        if field in requested_fields:
                            results[bond.identifier][field] = None
                        # Don't add failed computation to computed_values

        except Exception as e:
            logger.error(f"Error in compute_analytics: {str(e)}")
            raise

        return dict(results) 