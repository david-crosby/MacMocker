import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load()

    def _load(self) -> Dict[str, Any]:
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    @property
    def suite_name(self) -> str:
        return self.config.get("suite_name", "MacMocker Test Suite")

    @property
    def tests(self) -> list:
        return self.config.get("tests", [])

    @property
    def artifacts_dir(self) -> str:
        return self.config.get("artifacts_dir", "~/macmocker_artifacts")

    @property
    def reporting(self) -> Dict[str, Any]:
        return self.config.get("reporting", {})

    @property
    def global_timeout(self) -> int:
        return self.config.get("global_timeout", 300)

    def get_test_config(self, index: int) -> Dict[str, Any]:
        tests = self.tests
        if 0 <= index < len(tests):
            return tests[index]
        return {}
