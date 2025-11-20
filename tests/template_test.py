"""
Test Template for MacMocker

This is a template for creating new test modules. Copy this file and customise it for your needs.

Usage:
1. Copy this file to the appropriate directory (e.g., tests/applications/, tests/system/)
2. Rename to describe your test (e.g., test_my_application.py)
3. Update the class name (e.g., TestMyApplication)
4. Implement get_name(), get_description(), and run() methods
5. Add your test logic, python or shell script or OSA script for user interaction
6. Update configuration files to include your test

Example:
  tests/applications/test_slack.py
  class TestSlackApplication(BaseTest):
      ...
"""

import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

from tests.base_test import BaseTest, TestResult


class TestTemplate(BaseTest):
    """
    Brief description of what this test validates
    
    This test verifies that [APPLICATION/FEATURE] can:
    - Action 1
    - Action 2
    - Action 3
    """
    
    def get_name(self) -> str:
        """
        Return the test name (used in reports and logs)
        
        Use lowercase with underscores, should be unique and descriptive
        """
        return "test_template_example"
        
    def get_description(self) -> str:
        """
        Return a human-readable description of what this test does
        
        This appears in reports and helps users understand the test purpose
        """
        return "Template test demonstrating how to create new test modules"
        
    def run(self) -> TestResult:
        """
        Main test execution method
        
        This is where your test logic goes. Follow this pattern:
        1. Mark test as started
        2. Perform setup/verification
        3. Execute test steps
        4. Validate results
        5. Mark as passed/failed
        6. Clean up (in finally block if needed)
        7. Return result
        """
        self.result.mark_started()
        
        try:
            # Step 1: Verify prerequisites
            if not self._check_prerequisites():
                self.result.mark_failed("Prerequisites not met")
                return self.result
            
            # Step 2: Perform setup
            if not self._setup():
                self.result.mark_failed("Setup failed")
                return self.result
            
            # Step 3: Execute main test logic
            if not self._execute_test():
                self.result.mark_failed("Test execution failed")
                return self.result
            
            # Step 4: Validate results
            if not self._validate_results():
                self.result.mark_failed("Validation failed")
                return self.result
            
            # Step 5: Mark as passed
            self.result.mark_passed("Test completed successfully")
            
        except Exception as e:
            # Handle unexpected errors
            self.result.mark_failed(f"Test failed with exception: {str(e)}", str(e))
            
        finally:
            # Always clean up, even if test failed
            self._cleanup()
            
        return self.result
    
    # Helper Methods
    # Add private methods to break down your test logic into manageable pieces
    
    def _check_prerequisites(self) -> bool:
        """
        Verify that prerequisites for the test are met
        
        Examples:
        - Application is installed
        - Required files exist
        - System is in correct state
        """
        self.logger.info("Checking prerequisites")
        
        # Example: Check if an application is installed
        app_name = self.config.get("app_name", "MyApplication")
        app_path = Path(f"/Applications/{app_name}.app")
        
        if not app_path.exists():
            self.logger.error(f"{app_name} is not installed")
            return False
        
        self.logger.info("Prerequisites met")
        return True
    
    def _setup(self) -> bool:
        """
        Perform any setup needed before the test runs
        
        Examples:
        - Launch applications
        - Create temporary files
        - Configure environment
        """
        self.logger.info("Setting up test environment")
        
        # Example: Launch an application
        app_name = self.config.get("app_name", "MyApplication")
        
        try:
            result = self.run_command(["open", "-a", app_name], timeout=10)
            if result.returncode != 0:
                self.logger.error(f"Failed to launch {app_name}")
                return False
            
            # Wait for application to start
            wait_time = self.config.get("launch_wait_time", 5)
            time.sleep(wait_time)
            
            # Verify process is running
            if not self.wait_for_process(app_name, timeout=30):
                self.logger.error(f"{app_name} process not found")
                return False
            
            self.logger.info("Setup complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False
    
    def _execute_test(self) -> bool:
        """
        Execute the main test logic
        
        This is where you implement your actual test steps
        """
        self.logger.info("Executing test")
        
        # Example: Interact with application using AppleScript
        app_name = self.config.get("app_name", "MyApplication")
        
        try:
            script = f'''
            tell application "{app_name}"
                activate
                -- Add your AppleScript commands here
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=30)
            
            if result.returncode != 0:
                self.logger.error(f"AppleScript execution failed: {result.stderr}")
                return False
            
            # Example: Wait for operation to complete
            time.sleep(2)
            
            # Example: Take screenshot for documentation
            if self.config.get("capture_screenshots", True):
                self.capture_screenshot(f"{self.get_name()}_during_test.png")
            
            self.logger.info("Test execution complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Test execution failed: {e}")
            return False
    
    def _validate_results(self) -> bool:
        """
        Validate that the test produced expected results
        
        Examples:
        - Check that files were created
        - Verify data is correct
        - Confirm application state
        """
        self.logger.info("Validating results")
        
        # Example: Check if a file was created
        expected_file = Path.home() / "Desktop" / "test_output.txt"
        
        if self.config.get("expect_file_creation", False):
            if not expected_file.exists():
                self.logger.error(f"Expected file not found: {expected_file}")
                return False
            
            self.logger.info(f"File created successfully: {expected_file}")
        
        # Example: Verify process is still running
        app_name = self.config.get("app_name", "MyApplication")
        if not self.check_process_running(app_name):
            self.logger.warning(f"{app_name} is not running")
        
        self.logger.info("Validation complete")
        return True
    
    def _cleanup(self):
        """
        Clean up after the test
        
        Examples:
        - Close applications
        - Delete temporary files
        - Reset state
        
        This method should not raise exceptions
        """
        self.logger.info("Cleaning up")
        
        try:
            # Example: Close application
            if self.config.get("close_after_test", True):
                app_name = self.config.get("app_name", "MyApplication")
                self._close_application(app_name)
            
            # Example: Delete temporary files
            if self.config.get("cleanup_files", True):
                temp_file = Path.home() / "Desktop" / "test_output.txt"
                if temp_file.exists():
                    temp_file.unlink()
                    self.logger.info(f"Deleted temporary file: {temp_file}")
            
        except Exception as e:
            self.logger.warning(f"Cleanup encountered error: {e}")
    
    # Additional Helper Methods
    
    def _close_application(self, app_name: str):
        """Close an application gracefully"""
        try:
            self.logger.info(f"Closing {app_name}")
            script = f'''
            tell application "{app_name}"
                quit
            end tell
            '''
            self.run_command(["osascript", "-e", script], timeout=10)
            time.sleep(2)
            
        except Exception as e:
            self.logger.warning(f"Error closing {app_name} gracefully: {e}")
            
            # Force close if graceful close failed
            if self.check_process_running(app_name):
                self.logger.warning(f"Force closing {app_name}")
                self.run_command(["pkill", "-9", app_name])
    
    def _verify_window_visible(self, app_name: str) -> bool:
        """Verify application window is visible"""
        try:
            script = f'''
            tell application "System Events"
                tell process "{app_name}"
                    return exists window 1
                end tell
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=5)
            return "true" in result.stdout.lower()
            
        except Exception as e:
            self.logger.warning(f"Could not verify window visibility: {e}")
            return True
    
    def _check_for_error_dialogs(self) -> bool:
        """Check if error dialogues are present"""
        try:
            script = '''
            tell application "System Events"
                set dialogList to {}
                repeat with proc in processes
                    try
                        set procName to name of proc
                        if procName contains "Error" or procName contains "Warning" then
                            return "error_dialog_found"
                        end if
                    end try
                end repeat
                return "no_error_dialogs"
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=5)
            return "no_error_dialogs" in result.stdout
            
        except Exception as e:
            self.logger.warning(f"Could not check for error dialogues: {e}")
            return True


# Configuration Example for this test
"""
Add this to your YAML configuration file:

tests:
  - module: "tests.applications.test_template.TestTemplate"
    enabled: true
    timeout: 300
    screenshot_on_failure: true
    
    # Application to test
    app_name: "MyApplication"
    
    # Timing configuration
    launch_wait_time: 5
    
    # Behaviour configuration
    close_after_test: true
    cleanup_files: true
    capture_screenshots: true
    expect_file_creation: false
    
    # Wait time after test completes
    delay_after: 2

Usage:
1. Copy this template
2. Rename the file and class
3. Update get_name() and get_description()
4. Implement your test logic in the helper methods
5. Add to configuration file
6. Run: python3 main.py --config config/my_tests.yaml
"""