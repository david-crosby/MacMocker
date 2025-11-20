import importlib
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import signal
import time

from core.config_loader import ConfigLoader
from core.reporter import Reporter
from tests.base_test import BaseTest


class TestRunner:
    """Main orchestration engine for running tests"""
    
    def __init__(self, config_path: Path, artifacts_base_dir: Path):
        self.config_path = config_path
        self.artifacts_base_dir = artifacts_base_dir
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config_loader = ConfigLoader(config_path)
        self.config: Dict[str, Any] = {}
        self.reporter: Optional[Reporter] = None
        self.interrupted = False
        
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)
        
    def _handle_interrupt(self, signum, frame):
        """Handle graceful shutdown on interrupt"""
        self.logger.warning("Interrupt received, finishing current test and shutting down")
        self.interrupted = True
        
    def _setup_artifacts_dir(self) -> Path:
        """Create artifacts directory for this test run"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suite_name = self.config.get("suite_name", "unknown").replace(" ", "_").lower()
        artifacts_dir = self.artifacts_base_dir / f"{suite_name}_{timestamp}"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Artifacts directory: {artifacts_dir}")
        return artifacts_dir
        
    def _load_test_module(self, module_path: str, test_config: Dict[str, Any], artifacts_dir: Path) -> BaseTest:
        """Dynamically load a test module"""
        try:
            module_name, class_name = module_path.rsplit(".", 1)
            module = importlib.import_module(module_name)
            test_class = getattr(module, class_name)
            
            return test_class(test_config, artifacts_dir)
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to load test module {module_path}: {e}")
            raise
            
    def _run_test(self, test: BaseTest) -> Dict[str, Any]:
        """Run a single test with timeout handling"""
        self.logger.info(f"Starting test: {test.get_name()}")
        self.logger.info(f"Description: {test.get_description()}")
        
        try:
            result = test.run()
            
            if result.status == "passed":
                self.logger.info(f"Test PASSED: {test.get_name()}")
            elif result.status == "failed":
                self.logger.error(f"Test FAILED: {test.get_name()} - {result.message}")
                if test.config.get("screenshot_on_failure", True):
                    test.capture_screenshot(f"{test.get_name()}_failure.png")
            else:
                self.logger.warning(f"Test {result.status.upper()}: {test.get_name()}")
                
            return result.to_dict()
            
        except Exception as e:
            self.logger.exception(f"Test raised exception: {test.get_name()}")
            test.result.mark_failed(f"Exception raised: {str(e)}", error_details=str(e))
            test.capture_screenshot(f"{test.get_name()}_exception.png")
            return test.result.to_dict()
            
    def run(self) -> int:
        """Execute the test suite and return exit code"""
        try:
            self.config = self.config_loader.load()
            artifacts_dir = self._setup_artifacts_dir()
            self.reporter = Reporter(artifacts_dir, self.config)
            
            self.logger.info(f"Starting test suite: {self.config_loader.get_suite_name()}")
            
            enabled_tests = self.config_loader.get_enabled_tests()
            self.logger.info(f"Found {len(enabled_tests)} enabled tests")
            
            for idx, test_config in enumerate(enabled_tests):
                if self.interrupted:
                    self.logger.warning("Test suite interrupted by user")
                    break
                    
                self.logger.info(f"Running test {idx + 1}/{len(enabled_tests)}")
                
                try:
                    test = self._load_test_module(
                        test_config["module"],
                        test_config,
                        artifacts_dir
                    )
                    
                    result = self._run_test(test)
                    self.reporter.add_result(result)
                    
                    if test_config.get("delay_after", 0) > 0:
                        delay = test_config["delay_after"]
                        self.logger.info(f"Waiting {delay} seconds before next test")
                        time.sleep(delay)
                        
                except Exception as e:
                    self.logger.exception(f"Failed to run test {test_config.get('module')}")
                    self.reporter.add_result({
                        "test_name": test_config.get("module", "unknown"),
                        "status": "failed",
                        "message": f"Failed to initialise test: {str(e)}",
                        "error_details": str(e),
                        "duration_seconds": 0,
                    })
                    
            self.reporter.finalize()
            report_path = self.reporter.save_report()
            
            print("\n" + self.reporter.generate_report())
            
            reporting_config = self.config_loader.get_reporting_config()
            
            if reporting_config.get("teams_webhook"):
                self.reporter.post_to_teams(reporting_config["teams_webhook"])
                
            if reporting_config.get("api_url"):
                self.reporter.post_to_api(
                    reporting_config["api_url"],
                    reporting_config.get("api_token")
                )
                
            summary = self.reporter.get_summary()
            
            if summary["failed"] > 0:
                self.logger.error("Test suite completed with failures")
                return 1
            elif summary["total_tests"] == 0:
                self.logger.warning("No tests were run")
                return 2
            else:
                self.logger.info("Test suite completed successfully")
                return 0
                
        except Exception as e:
            self.logger.exception("Fatal error running test suite")
            return 3
