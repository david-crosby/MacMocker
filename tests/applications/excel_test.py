import time
from pathlib import Path
from tests.base_test import BaseTest, TestResult


class ExcelTest(BaseTest):
    def get_name(self) -> str:
        return "microsoft_excel_test"

    def get_description(self) -> str:
        return "Tests Microsoft Excel spreadsheet creation and editing"

    def run(self) -> TestResult:
        self.result.mark_started()
        
        try:
            if not self.check_application_exists("Microsoft Excel"):
                self.result.mark_skipped("Microsoft Excel not installed")
                return self.result

            self._launch_excel()
            self._create_workbook()
            self._add_data()
            self._save_workbook()
            self._verify_workbook()
            
            self.result.mark_passed("Excel test completed successfully")
            
        except Exception as e:
            self.capture_screenshot("excel_test_failure.png")
            self.result.mark_failed(str(e), str(e))
        finally:
            self._cleanup()
        
        return self.result

    def _launch_excel(self):
        if not self.launch_application("Microsoft Excel", timeout=30):
            raise Exception("Failed to launch Excel")
        
        time.sleep(3)
        self.result.add_log("Excel launched")

    def _create_workbook(self):
        script = '''
        tell application "Microsoft Excel"
            activate
            make new workbook
        end tell
        '''
        
        success, output = self.run_applescript(script, timeout=10)
        if not success:
            raise Exception(f"Failed to create workbook: {output}")
        
        time.sleep(2)
        self.result.add_log("Workbook created")

    def _add_data(self):
        script = '''
        tell application "Microsoft Excel"
            tell active sheet of active workbook
                set value of cell "A1" to "Test"
                set value of cell "B1" to "Data"
                set value of cell "A2" to "Row 1"
                set value of cell "B2" to 123
            end tell
        end tell
        '''
        
        success, output = self.run_applescript(script, timeout=10)
        if not success:
            raise Exception(f"Failed to add data: {output}")
        
        time.sleep(1)
        self.result.add_log("Data added to spreadsheet")

    def _save_workbook(self):
        test_file = Path.home() / "Desktop" / "macmocker_test.xlsx"
        
        if test_file.exists():
            test_file.unlink()

        script = f'''
        tell application "Microsoft Excel"
            save active workbook in "{test_file}"
        end tell
        '''
        
        success, output = self.run_applescript(script, timeout=10)
        if not success:
            raise Exception(f"Failed to save workbook: {output}")
        
        time.sleep(2)
        self.result.add_log(f"Workbook saved to {test_file}")

    def _verify_workbook(self):
        test_file = Path.home() / "Desktop" / "macmocker_test.xlsx"
        
        if not test_file.exists():
            raise Exception("Saved workbook not found")
        
        if test_file.stat().st_size < 5000:
            raise Exception("Workbook appears to be empty or corrupted")
        
        self.result.add_log("Workbook verified")

    def _cleanup(self):
        try:
            script = '''
            tell application "Microsoft Excel"
                close every workbook saving no
            end tell
            '''
            self.run_applescript(script, timeout=5)
            time.sleep(1)
        except:
            pass

        self.quit_application("Microsoft Excel")
        
        test_file = Path.home() / "Desktop" / "macmocker_test.xlsx"
        if test_file.exists():
            test_file.unlink()
