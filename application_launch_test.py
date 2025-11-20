import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import re

from tests.base_test import BaseTest, TestResult


class ApplicationLaunchTest(BaseTest):
    """Generic test for launching applications and verifying ready state"""
    
    def get_name(self) -> str:
        app_name = self.config.get("app_name", "unknown")
        return f"application_launch_{app_name.replace(' ', '_').lower()}"
        
    def get_description(self) -> str:
        app_name = self.config.get("app_name", "Application")
        return f"Launches {app_name}, verifies ready state, and checks logs for errors"
        
    def run(self) -> TestResult:
        self.result.mark_started()
        
        app_name = self.config.get("app_name")
        if not app_name:
            self.result.mark_failed("No app_name specified in configuration")
            return self.result
            
        try:
            if not self._check_app_installed():
                self.result.mark_failed(f"{app_name} is not installed")
                return self.result
                
            log_monitoring_started = False
            if self.config.get("monitor_logs", True):
                self._start_log_monitoring()
                log_monitoring_started = True
                
            if not self._launch_application():
                self.result.mark_failed(f"Failed to launch {app_name}")
                return self.result
                
            time.sleep(self.config.get("launch_wait_time", 5))
            
            if not self._verify_process_running():
                self.result.mark_failed(f"{app_name} process not found after launch")
                return self.result
                
            if not self._verify_ready_state():
                self.result.mark_failed(f"{app_name} did not reach ready state")
                return self.result
                
            if log_monitoring_started:
                log_errors = self._check_logs_for_errors()
                if log_errors:
                    self.result.mark_failed(
                        f"Errors found in logs: {len(log_errors)} error(s)",
                        error_details="\n".join(log_errors[:5])
                    )
                    return self.result
                    
            if self.config.get("close_after_test", True):
                self._close_application()
                
            self.result.mark_passed(f"{app_name} launched successfully and reached ready state")
            
        except Exception as e:
            self.result.mark_failed(f"Application test failed with exception: {str(e)}", str(e))
            
        return self.result
        
    def _check_app_installed(self) -> bool:
        """Check if application is installed"""
        app_name = self.config.get("app_name")
        app_path = self.config.get("app_path")
        
        if app_path:
            installed = Path(app_path).exists()
        else:
            installed = Path(f"/Applications/{app_name}.app").exists()
            
        if installed:
            self.logger.info(f"{app_name} is installed")
        else:
            self.logger.error(f"{app_name} is not installed")
            
        return installed
        
    def _launch_application(self) -> bool:
        """Launch the application"""
        try:
            app_name = self.config.get("app_name")
            app_path = self.config.get("app_path")
            
            self.logger.info(f"Launching {app_name}")
            
            if app_path:
                result = self.run_command(["open", app_path], timeout=10)
            else:
                result = self.run_command(["open", "-a", app_name], timeout=10)
                
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Failed to launch application: {e}")
            return False
            
    def _verify_process_running(self) -> bool:
        """Verify the application process is running"""
        process_name = self.config.get("process_name", self.config.get("app_name"))
        timeout = self.config.get("process_start_timeout", 30)
        
        self.logger.info(f"Waiting for process: {process_name}")
        
        if self.wait_for_process(process_name, timeout=timeout):
            self.logger.info(f"Process {process_name} is running")
            return True
        else:
            self.logger.error(f"Process {process_name} not found within {timeout} seconds")
            return False
            
    def _verify_ready_state(self) -> bool:
        """Verify application is in ready state"""
        ready_checks = self.config.get("ready_checks", {})
        
        if ready_checks.get("window_visible", True):
            if not self._check_window_visible():
                return False
                
        if ready_checks.get("menu_bar_loaded", True):
            if not self._check_menu_bar_loaded():
                return False
                
        if ready_checks.get("no_crash_dialogs", True):
            if not self._check_no_crash_dialogs():
                return False
                
        wait_time = ready_checks.get("additional_wait", 2)
        if wait_time > 0:
            self.logger.info(f"Additional wait time: {wait_time} seconds")
            time.sleep(wait_time)
            
        return True
        
    def _check_window_visible(self) -> bool:
        """Check if application window is visible"""
        try:
            app_name = self.config.get("app_name")
            script = f'''
            tell application "System Events"
                tell process "{app_name}"
                    return exists window 1
                end tell
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=5)
            
            window_exists = "true" in result.stdout.lower()
            if window_exists:
                self.logger.info("Application window is visible")
            else:
                self.logger.warning("Application window not visible")
                
            return window_exists
            
        except Exception as e:
            self.logger.warning(f"Could not check window visibility: {e}")
            return True
            
    def _check_menu_bar_loaded(self) -> bool:
        """Check if application menu bar is loaded"""
        try:
            app_name = self.config.get("app_name")
            script = f'''
            tell application "System Events"
                tell process "{app_name}"
                    return count of menu bars
                end tell
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=5)
            
            has_menu = result.returncode == 0 and int(result.stdout.strip() or "0") > 0
            if has_menu:
                self.logger.info("Application menu bar is loaded")
            else:
                self.logger.warning("Application menu bar not detected")
                
            return has_menu
            
        except Exception as e:
            self.logger.warning(f"Could not check menu bar: {e}")
            return True
            
    def _check_no_crash_dialogs(self) -> bool:
        """Check for crash or error dialogues"""
        try:
            script = '''
            tell application "System Events"
                set dialogList to {}
                repeat with proc in processes
                    try
                        set procName to name of proc
                        if procName contains "Crash Reporter" or procName contains "Problem Report" then
                            return "crash_dialog_found"
                        end if
                    end try
                end repeat
                return "no_crash_dialogs"
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=5)
            
            no_crashes = "no_crash_dialogs" in result.stdout
            if no_crashes:
                self.logger.info("No crash dialogues detected")
            else:
                self.logger.error("Crash dialogue detected")
                
            return no_crashes
            
        except Exception as e:
            self.logger.warning(f"Could not check for crash dialogues: {e}")
            return True
            
    def _start_log_monitoring(self):
        """Start monitoring system logs"""
        self._log_start_time = subprocess.check_output(["date", "+%Y-%m-%d %H:%M:%S"]).decode().strip()
        self.logger.info(f"Started log monitoring at {self._log_start_time}")
        
    def _check_logs_for_errors(self) -> list[str]:
        """Check logs for errors related to the application"""
        try:
            app_name = self.config.get("app_name")
            bundle_id = self.config.get("bundle_id")
            process_name = self.config.get("process_name", app_name)
            
            error_patterns = self.config.get("error_patterns", [
                "error", "crash", "exception", "failed", "fatal"
            ])
            
            log_filters = []
            if bundle_id:
                log_filters.append(f"process == '{bundle_id}'")
            if process_name:
                log_filters.append(f"process == '{process_name}'")
                
            filter_arg = " OR ".join(log_filters) if log_filters else "eventType == logEvent"
            
            cmd = [
                "log", "show",
                "--predicate", filter_arg,
                "--style", "syslog",
                "--start", self._log_start_time,
            ]
            
            result = self.run_command(cmd, timeout=10)
            
            errors = []
            for line in result.stdout.splitlines():
                line_lower = line.lower()
                if any(pattern in line_lower for pattern in error_patterns):
                    errors.append(line.strip())
                    
            if errors:
                self.logger.warning(f"Found {len(errors)} potential errors in logs")
            else:
                self.logger.info("No errors found in logs")
                
            return errors
            
        except Exception as e:
            self.logger.warning(f"Could not check logs: {e}")
            return []
            
    def _close_application(self):
        """Close the application"""
        try:
            app_name = self.config.get("app_name")
            self.logger.info(f"Closing {app_name}")
            
            script = f'''
            tell application "{app_name}"
                quit
            end tell
            '''
            self.run_command(["osascript", "-e", script], timeout=10)
            time.sleep(2)
            
        except Exception as e:
            self.logger.warning(f"Error closing application: {e}")
