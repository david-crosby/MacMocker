import importlib
import logging
from pathlib import Path
from typing import List
from datetime import datetime

from core.config_loader import ConfigLoader
from tests.base_test import BaseTest, TestResult


class TestRunner:
    def __init__(self, config_loader: ConfigLoader):
        self.config = config_loader
        self.logger = logging.getLogger("TestRunner")
        self.results: List[TestResult] = []
        self.artifacts_dir = self._setup_artifacts_dir()

    def _setup_artifacts_dir(self) -> Path:
        base_dir = Path(self.config.artifacts_dir).expanduser()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = base_dir / f"run_{timestamp}"
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def _load_test_class(self, module_path: str):
        try:
            module_name, class_name = module_path.rsplit(".", 1)
            module = importlib.import_module(module_name)
            return getattr(module, class_name)
        except Exception as e:
            self.logger.error(f"Failed to load test {module_path}: {e}")
            return None

    def run_all_tests(self) -> List[TestResult]:
        tests = self.config.tests
        
        for test_config in tests:
            if not test_config.get("enabled", True):
                self.logger.info(f"Skipping disabled test: {test_config.get('module')}")
                continue

            result = self._run_single_test(test_config)
            self.results.append(result)

        return self.results

    def _run_single_test(self, test_config: dict) -> TestResult:
        module_path = test_config.get("module")
        test_class = self._load_test_class(module_path)

        if not test_class:
            result = TestResult(module_path)
            result.mark_failed("Failed to load test module")
            return result

        try:
            test_instance: BaseTest = test_class(test_config, self.artifacts_dir)
            self.logger.info(f"Running: {test_instance.get_description()}")
            return test_instance.run()
        except Exception as e:
            self.logger.error(f"Test crashed: {e}")
            result = TestResult(module_path)
            result.mark_failed("Test crashed", str(e))
            return result

    @property
    def summary(self) -> dict:
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "passed")
        failed = sum(1 for r in self.results if r.status == "failed")
        skipped = sum(1 for r in self.results if r.status == "skipped")
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "success_rate": (passed / total * 100) if total > 0 else 0
        }
