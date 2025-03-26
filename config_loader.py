import json
import logging
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigLoader:
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        
    def load(self) -> None:
        """Load and validate the configuration file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            
            # Validate required sections
            required_sections = ['equations', 'default_requested_fields', 'api_settings']
            for section in required_sections:
                if section not in self.config:
                    raise ValueError(f"Missing required section '{section}' in config file")
            
            # Validate equations
            if not isinstance(self.config['equations'], list):
                raise ValueError("'equations' must be a list")
            if not all(isinstance(eq, str) for eq in self.config['equations']):
                raise ValueError("All equations must be strings")
            
            # Validate requested fields
            if not isinstance(self.config['default_requested_fields'], list):
                raise ValueError("'default_requested_fields' must be a list")
            if not all(isinstance(field, str) for field in self.config['default_requested_fields']):
                raise ValueError("All requested fields must be strings")
            
            # Validate API settings
            required_api_settings = ['latency', 'yield_multiplier', 'risk_free_rate', 'volatility_multiplier']
            for setting in required_api_settings:
                if setting not in self.config['api_settings']:
                    raise ValueError(f"Missing required API setting '{setting}'")
                if not isinstance(self.config['api_settings'][setting], (int, float)):
                    raise ValueError(f"API setting '{setting}' must be a number")
            
            logger.info(f"Successfully loaded configuration from {self.config_path}")
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in configuration file: {self.config_path}")
        except Exception as e:
            raise RuntimeError(f"Error loading configuration: {str(e)}")
    
    @property
    def equations(self) -> List[str]:
        """Get the list of equations from the config"""
        return self.config['equations']
    
    @property
    def default_requested_fields(self) -> List[str]:
        """Get the list of default requested fields"""
        return self.config['default_requested_fields']
    
    @property
    def api_settings(self) -> Dict[str, float]:
        """Get the API settings"""
        return self.config['api_settings'] 