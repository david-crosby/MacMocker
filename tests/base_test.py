import subprocess
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class TestResult:
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.status = "pending"
        self.message = ""
        self.details = ""
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.logs = []
        self.screenshots = []

    def mark_started(self):
        self.start_time = datetime.now()
        self.status = "running"

    def mark_passed(self, message: str = "Test passed"):
        self.status = "passed"
        self.message = message
        self.end_time = datetime.now()

    def mark_failed(self, message: str, details: str = ""):
        self.status = "failed"
        self.message = message
        self.details = details
        self.end_time = datetime.now()

    def mark_skipped(self, reason: str):
        self.status = "skipped"
        self.message = reason
        self.end_time = datetime.now()

    def add_log(self, message: str):
        self.logs.append(f"{datetime.now().isoformat()}: {message}")

    def add_screenshot(self, path: str):
        self.screenshots.append(path)

    @property
    def duration(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


class BaseTest(ABC):
    def __init__(self, config: Dict[str, Any], artifacts_dir: Path):
        self.config = config
        self.artifacts_dir = artifacts_dir
        self.result = TestResult(self.get_name())
        self.logger = logging.getLogger(self.get_name())
        self.timeout = config.get("timeout", 300)

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

    @abstractmethod
    def run(self) -> TestResult:
        pass

    def run_command(self, cmd: list, timeout: int = 30) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out: {' '.join(cmd)}")
            raise

    def run_applescript(self, script: str, timeout: int = 30) -> tuple[bool, str]:
        try:
            result = self.run_command(
                ["osascript", "-e", script],
                timeout=timeout
            )
            return result.returncode == 0, result.stdout.strip()
        except Exception as e:
            self.logger.error(f"AppleScript failed: {e}")
            return False, str(e)

    def check_process_running(self, process_name: str) -> bool:
        result = self.run_command(["pgrep", "-x", process_name])
        return result.returncode == 0

    def wait_for_process(self, process_name: str, timeout: int = 30) -> bool:
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self.check_process_running(process_name):
                return True
            time.sleep(1)
        return False

    def kill_process(self, process_name: str, force: bool = False):
        signal = "-9" if force else "-15"
        self.run_command(["pkill", signal, process_name])

    def capture_screenshot(self, filename: str):
        screenshot_path = self.artifacts_dir / filename
        self.run_command(["screencapture", "-x", str(screenshot_path)])
        if screenshot_path.exists():
            self.result.add_screenshot(str(screenshot_path))
            self.logger.info(f"Screenshot saved: {filename}")

    def check_application_exists(self, app_name: str) -> bool:
        return Path(f"/Applications/{app_name}.app").exists()

    def launch_application(self, app_name: str, timeout: int = 30) -> bool:
        if not self.check_application_exists(app_name):
            self.logger.error(f"Application not found: {app_name}")
            return False

        result = self.run_command(["open", "-a", app_name])
        if result.returncode != 0:
            return False

        return self.wait_for_process(app_name, timeout)

    def quit_application(self, app_name: str, timeout: int = 10):
        script = f'tell application "{app_name}" to quit'
        success, _ = self.run_applescript(script, timeout)
        
        if not success:
            self.kill_process(app_name)

        time.sleep(2)
