import time
import subprocess
from pathlib import Path
from typing import Dict, Any

from tests.base_test import BaseTest, TestResult


class MicrosoftExcelTest(BaseTest):
    """Test Microsoft Excel application functionality"""
    
    def get_name(self) -> str:
        return "microsoft_excel_functionality"
        
    def get_description(self) -> str:
        return "Opens Excel, creates a workbook, enters data, saves to Desktop, reopens, edits, and saves"
        
    def run(self) -> TestResult:
        self.result.mark_started()
        
        desktop_path = Path.home() / "Desktop"
        test_file = desktop_path / "test_spreadsheet.xlsx"
        
        try:
            if not self._check_excel_installed():
                self.result.mark_failed("Microsoft Excel is not installed")
                return self.result
                
            if not self._launch_excel():
                self.result.mark_failed("Failed to launch Microsoft Excel")
                return self.result
                
            time.sleep(5)
            
            if not self._create_new_workbook():
                self.result.mark_failed("Failed to create new workbook")
                return self.result
                
            time.sleep(2)
            
            if not self._enter_data():
                self.result.mark_failed("Failed to enter data into workbook")
                return self.result
                
            time.sleep(1)
            
            if not self._save_workbook(test_file):
                self.result.mark_failed("Failed to save workbook")
                return self.result
                
            time.sleep(2)
            
            if not test_file.exists():
                self.result.mark_failed(f"Workbook not found at {test_file}")
                return self.result
                
            self._close_excel()
            time.sleep(2)
            
            if not self._open_workbook(test_file):
                self.result.mark_failed("Failed to reopen workbook")
                return self.result
                
            time.sleep(3)
            
            if not self._edit_workbook():
                self.result.mark_failed("Failed to edit reopened workbook")
                return self.result
                
            time.sleep(1)
            
            if not self._save_and_close():
                self.result.mark_failed("Failed to save and close workbook")
                return self.result
                
            if self.config.get("cleanup", True):
                if test_file.exists():
                    test_file.unlink()
                    self.logger.info(f"Cleaned up test file: {test_file}")
                    
            self.result.mark_passed("Microsoft Excel test completed successfully")
            
        except Exception as e:
            self.result.mark_failed(f"Excel test failed with exception: {str(e)}", str(e))
            
        finally:
            self._ensure_excel_closed()
            
        return self.result
        
    def _check_excel_installed(self) -> bool:
        """Check if Microsoft Excel is installed"""
        excel_path = Path("/Applications/Microsoft Excel.app")
        installed = excel_path.exists()
        
        if installed:
            self.logger.info("Microsoft Excel is installed")
        else:
            self.logger.error("Microsoft Excel is not installed")
            
        return installed
        
    def _launch_excel(self) -> bool:
        """Launch Microsoft Excel"""
        try:
            self.logger.info("Launching Microsoft Excel")
            result = self.run_command(["open", "-a", "Microsoft Excel"], timeout=10)
            
            if result.returncode != 0:
                return False
                
            return self.wait_for_process("Microsoft Excel", timeout=15)
            
        except Exception as e:
            self.logger.error(f"Failed to launch Excel: {e}")
            return False
            
    def _create_new_workbook(self) -> bool:
        """Create a new workbook"""
        try:
            self.logger.info("Creating new workbook")
            script = '''
            tell application "Microsoft Excel"
                activate
                make new workbook
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=10)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Failed to create workbook: {e}")
            return False
            
    def _enter_data(self) -> bool:
        """Enter data into the workbook"""
        try:
            self.logger.info("Entering data into workbook")
            
            headers = self.config.get("test_headers", ["Name", "Value", "Status"])
            data_rows = self.config.get("test_data", [
                ["Test Item 1", "100", "Active"],
                ["Test Item 2", "200", "Active"],
                ["Test Item 3", "300", "Complete"]
            ])
            
            script = f'''
            tell application "Microsoft Excel"
                tell active sheet of active workbook
                    -- Enter headers
                    set value of cell "A1" to "{headers[0]}"
                    set value of cell "B1" to "{headers[1]}"
                    set value of cell "C1" to "{headers[2]}"
                    
                    -- Enter data rows
                    set value of cell "A2" to "{data_rows[0][0]}"
                    set value of cell "B2" to "{data_rows[0][1]}"
                    set value of cell "C2" to "{data_rows[0][2]}"
                    
                    set value of cell "A3" to "{data_rows[1][0]}"
                    set value of cell "B3" to "{data_rows[1][1]}"
                    set value of cell "C3" to "{data_rows[1][2]}"
                    
                    set value of cell "A4" to "{data_rows[2][0]}"
                    set value of cell "B4" to "{data_rows[2][1]}"
                    set value of cell "C4" to "{data_rows[2][2]}"
                end tell
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=15)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Failed to enter data: {e}")
            return False
            
    def _save_workbook(self, file_path: Path) -> bool:
        """Save the workbook to specified path"""
        try:
            self.logger.info(f"Saving workbook to {file_path}")
            
            script = f'''
            tell application "Microsoft Excel"
                save active workbook in POSIX file "{file_path}"
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=10)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Failed to save workbook: {e}")
            return False
            
    def _open_workbook(self, file_path: Path) -> bool:
        """Open an existing workbook"""
        try:
            self.logger.info(f"Opening workbook: {file_path}")
            result = self.run_command(["open", str(file_path)], timeout=10)
            
            if result.returncode != 0:
                return False
                
            time.sleep(2)
            return self.check_process_running("Microsoft Excel")
            
        except Exception as e:
            self.logger.error(f"Failed to open workbook: {e}")
            return False
            
    def _edit_workbook(self) -> bool:
        """Edit the reopened workbook"""
        try:
            self.logger.info("Editing workbook")
            
            script = '''
            tell application "Microsoft Excel"
                tell active sheet of active workbook
                    set value of cell "A5" to "Test Item 4"
                    set value of cell "B5" to "400"
                    set value of cell "C5" to "New"
                    
                    -- Add a formula
                    set formula of cell "B6" to "=SUM(B2:B5)"
                end tell
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=10)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Failed to edit workbook: {e}")
            return False
            
    def _save_and_close(self) -> bool:
        """Save and close the workbook"""
        try:
            self.logger.info("Saving and closing workbook")
            script = '''
            tell application "Microsoft Excel"
                save active workbook
                close active workbook
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=10)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Failed to save and close: {e}")
            return False
            
    def _close_excel(self):
        """Close Microsoft Excel"""
        try:
            self.logger.info("Closing Microsoft Excel")
            script = '''
            tell application "Microsoft Excel"
                quit saving no
            end tell
            '''
            self.run_command(["osascript", "-e", script], timeout=5)
            time.sleep(2)
            
        except Exception as e:
            self.logger.warning(f"Error closing Excel gracefully: {e}")
            
    def _ensure_excel_closed(self):
        """Ensure Excel is fully closed"""
        try:
            if self.check_process_running("Microsoft Excel"):
                self.logger.warning("Force closing Microsoft Excel")
                self.run_command(["pkill", "-9", "Microsoft Excel"])
                
        except Exception as e:
            self.logger.warning(f"Error force closing Excel: {e}")
