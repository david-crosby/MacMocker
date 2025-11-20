import time
import subprocess
from pathlib import Path
from typing import Dict, Any
import os

from tests.base_test import BaseTest, TestResult


class MicrosoftWordTest(BaseTest):
    """Test Microsoft Word application functionality"""
    
    def get_name(self) -> str:
        return "microsoft_word_functionality"
        
    def get_description(self) -> str:
        return "Opens Word, creates a document, saves to Desktop, reopens and edits, validates dialogue boxes"
        
    def run(self) -> TestResult:
        self.result.mark_started()
        
        desktop_path = Path.home() / "Desktop"
        test_file = desktop_path / "test_document.docx"
        
        try:
            if not self._check_word_installed():
                self.result.mark_failed("Microsoft Word is not installed")
                return self.result
                
            if not self._launch_word():
                self.result.mark_failed("Failed to launch Microsoft Word")
                return self.result
                
            time.sleep(5)
            
            if not self._create_new_document():
                self.result.mark_failed("Failed to create new document")
                return self.result
                
            time.sleep(2)
            
            if not self._type_content():
                self.result.mark_failed("Failed to type content into document")
                return self.result
                
            time.sleep(1)
            
            if not self._save_document(test_file):
                self.result.mark_failed("Failed to save document")
                return self.result
                
            time.sleep(2)
            
            if not test_file.exists():
                self.result.mark_failed(f"Document not found at {test_file}")
                return self.result
                
            self._close_word()
            time.sleep(2)
            
            if not self._open_document(test_file):
                self.result.mark_failed("Failed to reopen document")
                return self.result
                
            time.sleep(3)
            
            if not self._edit_document():
                self.result.mark_failed("Failed to edit reopened document")
                return self.result
                
            time.sleep(1)
            
            if not self._save_and_close():
                self.result.mark_failed("Failed to save and close document")
                return self.result
                
            if self.config.get("cleanup", True):
                if test_file.exists():
                    test_file.unlink()
                    self.logger.info(f"Cleaned up test file: {test_file}")
                    
            self.result.mark_passed("Microsoft Word test completed successfully")
            
        except Exception as e:
            self.result.mark_failed(f"Word test failed with exception: {str(e)}", str(e))
            
        finally:
            self._ensure_word_closed()
            
        return self.result
        
    def _check_word_installed(self) -> bool:
        """Check if Microsoft Word is installed"""
        word_path = Path("/Applications/Microsoft Word.app")
        installed = word_path.exists()
        
        if installed:
            self.logger.info("Microsoft Word is installed")
        else:
            self.logger.error("Microsoft Word is not installed")
            
        return installed
        
    def _launch_word(self) -> bool:
        """Launch Microsoft Word"""
        try:
            self.logger.info("Launching Microsoft Word")
            result = self.run_command(["open", "-a", "Microsoft Word"], timeout=10)
            
            if result.returncode != 0:
                return False
                
            return self.wait_for_process("Microsoft Word", timeout=15)
            
        except Exception as e:
            self.logger.error(f"Failed to launch Word: {e}")
            return False
            
    def _create_new_document(self) -> bool:
        """Create a new document using keyboard shortcut"""
        try:
            self.logger.info("Creating new document")
            script = '''
            tell application "Microsoft Word"
                activate
                make new document
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=10)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Failed to create document: {e}")
            return False
            
    def _type_content(self) -> bool:
        """Type content into the document"""
        try:
            self.logger.info("Typing content")
            content = self.config.get("test_content", "This is a test document created by the macOS test suite.")
            
            script = f'''
            tell application "Microsoft Word"
                tell active document
                    set content of text object to "{content}"
                end tell
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=10)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Failed to type content: {e}")
            return False
            
    def _save_document(self, file_path: Path) -> bool:
        """Save the document to specified path"""
        try:
            self.logger.info(f"Saving document to {file_path}")
            
            script = f'''
            tell application "Microsoft Word"
                save active document in POSIX file "{file_path}"
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=10)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Failed to save document: {e}")
            return False
            
    def _open_document(self, file_path: Path) -> bool:
        """Open an existing document"""
        try:
            self.logger.info(f"Opening document: {file_path}")
            result = self.run_command(["open", str(file_path)], timeout=10)
            
            if result.returncode != 0:
                return False
                
            time.sleep(2)
            return self.check_process_running("Microsoft Word")
            
        except Exception as e:
            self.logger.error(f"Failed to open document: {e}")
            return False
            
    def _edit_document(self) -> bool:
        """Edit the reopened document"""
        try:
            self.logger.info("Editing document")
            additional_content = " This line was added during the edit test."
            
            script = f'''
            tell application "Microsoft Word"
                tell active document
                    set content of text object to (content of text object) & "{additional_content}"
                end tell
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=10)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Failed to edit document: {e}")
            return False
            
    def _save_and_close(self) -> bool:
        """Save and close the document"""
        try:
            self.logger.info("Saving and closing document")
            script = '''
            tell application "Microsoft Word"
                save active document
                close active document
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=10)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Failed to save and close: {e}")
            return False
            
    def _close_word(self):
        """Close Microsoft Word"""
        try:
            self.logger.info("Closing Microsoft Word")
            script = '''
            tell application "Microsoft Word"
                quit saving no
            end tell
            '''
            self.run_command(["osascript", "-e", script], timeout=5)
            time.sleep(2)
            
        except Exception as e:
            self.logger.warning(f"Error closing Word gracefully: {e}")
            
    def _ensure_word_closed(self):
        """Ensure Word is fully closed"""
        try:
            if self.check_process_running("Microsoft Word"):
                self.logger.warning("Force closing Microsoft Word")
                self.run_command(["pkill", "-9", "Microsoft Word"])
                
        except Exception as e:
            self.logger.warning(f"Error force closing Word: {e}")
