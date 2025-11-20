from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import logging


class TestResult:
    """Represents the result of a test execution"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.status = "not_run"
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.duration_seconds: float = 0.0
        self.message: str = ""
        self.error_details: Optional[str] = None
        self.screenshots: list[Path] = []
        self.logs: list[str] = []
        
    def mark_started(self):
        self.start_time = datetime.now()
        self.status = "running"
        
    def mark_passed(self, message: str = ""):
        self.end_time = datetime.now()
        if self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        self.status = "passed"
        self.message = message
        
    def mark_failed(self, message: str, error_details: Optional[str] = None):
        self.end_time = datetime.now()
        if self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        self.status = "failed"
        self.message = message
        self.error_details = error_details
        
    def mark_skipped(self, reason: str):
        self.status = "skipped"
        self.message = reason
        
    def add_screenshot(self, screenshot_path: Path):
        self.screenshots.append(screenshot_path)
        
    def add_log(self, log_message: str):
        self.logs.append(log_message)
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "message": self.message,
            "error_details": self.error_details,
            "screenshots": [str(s) for s in self.screenshots],
            "logs": self.logs,
        }


class BaseTest(ABC):
    """Base class for all test modules"""
    
    def __init__(self, config: Dict[str, Any], artifacts_dir: Path):
        self.config = config
        self.artifacts_dir = artifacts_dir
        self.logger = logging.getLogger(self.__class__.__name__)
        self.result = TestResult(self.get_name())
        self.timeout = config.get("timeout", 300)
        
    @abstractmethod
    def get_name(self) -> str:
        """Return the test name"""
        pass
        
    @abstractmethod
    def get_description(self) -> str:
        """Return a human-readable description of what this test does"""
        pass
        
    @abstractmethod
    def run(self) -> TestResult:
        """Execute the test and return the result"""
        pass
        
    def capture_screenshot(self, filename: str) -> Optional[Path]:
        """Capture a screenshot and save to artifacts directory"""
        try:
            screenshot_path = self.artifacts_dir / filename
            subprocess.run(
                ["screencapture", "-x", str(screenshot_path)],
                check=True,
                capture_output=True,
            )
            self.result.add_screenshot(screenshot_path)
            self.logger.info(f"Screenshot captured: {screenshot_path}")
            return screenshot_path
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to capture screenshot: {e}")
            return None
            
    def run_command(self, command: list[str], timeout: Optional[int] = None) -> subprocess.CompletedProcess:
        """Execute a shell command with timeout"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout or self.timeout,
                check=False,
            )
            log_message = f"Command: {' '.join(command)}\nReturn code: {result.returncode}"
            if result.stdout:
                log_message += f"\nStdout: {result.stdout}"
            if result.stderr:
                log_message += f"\nStderr: {result.stderr}"
            self.result.add_log(log_message)
            return result
        except subprocess.TimeoutExpired as e:
            self.logger.error(f"Command timed out: {' '.join(command)}")
            raise
            
    def check_process_running(self, process_name: str) -> bool:
        """Check if a process is currently running"""
        result = self.run_command(["pgrep", "-x", process_name])
        return result.returncode == 0
        
    def wait_for_process(self, process_name: str, timeout: int = 30) -> bool:
        """Wait for a process to start running"""
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_process_running(process_name):
                return True
            time.sleep(1)
        return False
