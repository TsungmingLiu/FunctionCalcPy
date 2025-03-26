import json
import logging
from pathlib import Path
from models import Bond
from engine import AnalyticsEngine
from config_loader import ConfigLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Load configuration
    config_path = Path(__file__).parent / 'config.json'
    config = ConfigLoader(str(config_path))
    config.load()
    
    # Create bonds
    bonds = [
        Bond("BOND1", "20230601", 100.0),
        Bond("BOND2", "20230601", 101.5),
        Bond("BOND3", "20230601", 99.75)
    ]
    
    try:
        # Initialize engine with API settings from config
        engine = AnalyticsEngine(api_settings=config.api_settings)
        
        # Validate and sort equations from config
        engine.validate_equations(config.equations)
        engine.topological_sort()
        
        # Compute analytics using requested fields from config
        results = engine.compute_analytics(bonds, config.default_requested_fields)
        
        # Output results
        print(json.dumps(results, indent=2))
        
    except Exception as e:
        logger.error(f"Failed to process analytics: {str(e)}")
        raise

if __name__ == "__main__":
    main() 