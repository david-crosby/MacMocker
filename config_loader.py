import yaml
from pathlib import Path
from typing import Dict, Any, List
import logging


class ConfigLoader:
    """Loads and validates test configuration from YAML files"""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config: Dict[str, Any] = {}
        
    def load(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            self.logger.info(f"Loaded configuration from {self.config_path}")
            self._validate_config()
            return self.config
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            self.logger.error(f"Failed to parse YAML: {e}")
            raise
            
    def _validate_config(self):
        """Validate configuration structure"""
        required_fields = ["suite_name", "tests"]
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required field in config: {field}")
                
        if not isinstance(self.config["tests"], list):
            raise ValueError("'tests' must be a list")
            
        for idx, test in enumerate(self.config["tests"]):
            if "module" not in test:
                raise ValueError(f"Test at index {idx} missing 'module' field")
            if "enabled" not in test:
                test["enabled"] = True
                
    def get_enabled_tests(self) -> List[Dict[str, Any]]:
        """Return list of enabled tests"""
        return [test for test in self.config["tests"] if test.get("enabled", True)]
        
    def get_suite_name(self) -> str:
        """Return the suite name"""
        return self.config.get("suite_name", "Unnamed Test Suite")
        
    def get_global_timeout(self) -> int:
        """Return global timeout in seconds"""
        return self.config.get("global_timeout", 3600)
        
    def get_artifacts_retention(self) -> int:
        """Return number of days to retain artifacts"""
        return self.config.get("artifacts_retention_days", 7)
        
    def get_reporting_config(self) -> Dict[str, Any]:
        """Return reporting configuration"""
        return self.config.get("reporting", {})
