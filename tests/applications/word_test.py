import time
from pathlib import Path
from tests.base_test import BaseTest, TestResult


class WordTest(BaseTest):
    def get_name(self) -> str:
        return "microsoft_word_test"

    def get_description(self) -> str:
        return "Tests Microsoft Word document creation and editing"

    def run(self) -> TestResult:
        self.result.mark_started()
        
        try:
            if not self.check_application_exists("Microsoft Word"):
                self.result.mark_skipped("Microsoft Word not installed")
                return self.result

            self._launch_word()
            self._create_document()
            self._save_document()
            self._verify_document()
            
            self.result.mark_passed("Word test completed successfully")
            
        except Exception as e:
            self.capture_screenshot("word_test_failure.png")
            self.result.mark_failed(str(e), str(e))
        finally:
            self._cleanup()
        
        return self.result

    def _launch_word(self):
        if not self.launch_application("Microsoft Word", timeout=30):
            raise Exception("Failed to launch Word")
        
        time.sleep(3)
        self.result.add_log("Word launched")

    def _create_document(self):
        script = '''
        tell application "Microsoft Word"
            activate
            make new document
            tell active document
                insert text "MacMocker Test Document" at text object
            end tell
        end tell
        '''
        
        success, output = self.run_applescript(script, timeout=10)
        if not success:
            raise Exception(f"Failed to create document: {output}")
        
        time.sleep(2)
        self.result.add_log("Document created")

    def _save_document(self):
        test_file = Path.home() / "Desktop" / "macmocker_test.docx"
        
        if test_file.exists():
            test_file.unlink()

        script = f'''
        tell application "Microsoft Word"
            save active document in "{test_file}" as save as file format format document
        end tell
        '''
        
        success, output = self.run_applescript(script, timeout=10)
        if not success:
            raise Exception(f"Failed to save document: {output}")
        
        time.sleep(2)
        self.result.add_log(f"Document saved to {test_file}")

    def _verify_document(self):
        test_file = Path.home() / "Desktop" / "macmocker_test.docx"
        
        if not test_file.exists():
            raise Exception("Saved document not found")
        
        if test_file.stat().st_size < 1000:
            raise Exception("Document appears to be empty or corrupted")
        
        self.result.add_log("Document verified")

    def _cleanup(self):
        try:
            script = '''
            tell application "Microsoft Word"
                close every document saving no
            end tell
            '''
            self.run_applescript(script, timeout=5)
            time.sleep(1)
        except:
            pass

        self.quit_application("Microsoft Word")
        
        test_file = Path.home() / "Desktop" / "macmocker_test.docx"
        if test_file.exists():
            test_file.unlink()
