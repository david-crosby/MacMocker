import time
import subprocess
from pathlib import Path
from typing import Dict, Any

from tests.base_test import BaseTest, TestResult


class MicrosoftOutlookTest(BaseTest):
    """Test Microsoft Outlook email functionality"""
    
    def get_name(self) -> str:
        return "microsoft_outlook_email_functionality"
        
    def get_description(self) -> str:
        return "Opens Outlook, creates and sends an email to test address, then verifies incoming email receipt"
        
    def run(self) -> TestResult:
        self.result.mark_started()
        
        try:
            if not self._check_outlook_installed():
                self.result.mark_failed("Microsoft Outlook is not installed")
                return self.result
                
            test_email = self.config.get("test_email_address")
            if not test_email:
                self.result.mark_failed("No test_email_address configured")
                return self.result
                
            if not self._launch_outlook():
                self.result.mark_failed("Failed to launch Microsoft Outlook")
                return self.result
                
            time.sleep(8)
            
            if not self._check_account_configured():
                self.result.mark_failed("No email account configured in Outlook")
                return self.result
                
            email_subject = f"MacMocker Test Email - {time.strftime('%Y%m%d_%H%M%S')}"
            
            if not self._create_and_send_email(test_email, email_subject):
                self.result.mark_failed("Failed to create and send email")
                return self.result
                
            self.logger.info("Email sent, waiting for delivery and receipt")
            wait_time = self.config.get("email_wait_time", 30)
            time.sleep(wait_time)
            
            if not self._sync_mailbox():
                self.logger.warning("Failed to trigger mailbox sync")
                
            time.sleep(5)
            
            if not self._verify_email_received(email_subject):
                self.result.mark_failed(
                    f"Failed to verify email receipt within {wait_time} seconds"
                )
                return self.result
                
            if self.config.get("delete_test_email", True):
                self._delete_test_email(email_subject)
                
            if self.config.get("close_after_test", True):
                self._close_outlook()
                
            self.result.mark_passed("Microsoft Outlook test completed successfully")
            
        except Exception as e:
            self.result.mark_failed(f"Outlook test failed with exception: {str(e)}", str(e))
            
        finally:
            if self.config.get("close_after_test", True):
                self._ensure_outlook_closed()
            
        return self.result
        
    def _check_outlook_installed(self) -> bool:
        """Check if Microsoft Outlook is installed"""
        outlook_path = Path("/Applications/Microsoft Outlook.app")
        installed = outlook_path.exists()
        
        if installed:
            self.logger.info("Microsoft Outlook is installed")
        else:
            self.logger.error("Microsoft Outlook is not installed")
            
        return installed
        
    def _launch_outlook(self) -> bool:
        """Launch Microsoft Outlook"""
        try:
            self.logger.info("Launching Microsoft Outlook")
            result = self.run_command(["open", "-a", "Microsoft Outlook"], timeout=10)
            
            if result.returncode != 0:
                return False
                
            return self.wait_for_process("Microsoft Outlook", timeout=20)
            
        except Exception as e:
            self.logger.error(f"Failed to launch Outlook: {e}")
            return False
            
    def _check_account_configured(self) -> bool:
        """Check if an email account is configured in Outlook"""
        try:
            self.logger.info("Checking for configured email account")
            script = '''
            tell application "Microsoft Outlook"
                try
                    set accountCount to count of accounts
                    if accountCount > 0 then
                        return "account_configured"
                    else
                        return "no_account"
                    end if
                on error
                    return "error"
                end try
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=10)
            
            if "account_configured" in result.stdout:
                self.logger.info("Email account is configured")
                return True
            else:
                self.logger.error("No email account configured in Outlook")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to check account configuration: {e}")
            return False
            
    def _create_and_send_email(self, recipient: str, subject: str) -> bool:
        """Create and send a test email"""
        try:
            self.logger.info(f"Creating and sending email to {recipient}")
            
            body = self.config.get("email_body", "This is a test email sent by MacMocker test suite.")
            
            script = f'''
            tell application "Microsoft Outlook"
                set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{body}"}}
                
                make new recipient at newMessage with properties {{email address:{{address:"{recipient}"}}}}
                
                send newMessage
                
                return "sent"
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=20)
            
            if result.returncode == 0 and "sent" in result.stdout:
                self.logger.info("Email sent successfully")
                return True
            else:
                self.logger.error(f"Failed to send email: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to create and send email: {e}")
            return False
            
    def _sync_mailbox(self) -> bool:
        """Trigger mailbox synchronisation"""
        try:
            self.logger.info("Triggering mailbox sync")
            script = '''
            tell application "Microsoft Outlook"
                try
                    synchronize
                    return "synced"
                on error
                    return "error"
                end try
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=30)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.warning(f"Error during mailbox sync: {e}")
            return False
            
    def _verify_email_received(self, subject: str) -> bool:
        """Verify that the test email was received"""
        try:
            self.logger.info(f"Checking for received email with subject: {subject}")
            
            max_attempts = self.config.get("receive_check_attempts", 3)
            check_interval = 10
            
            for attempt in range(max_attempts):
                self.logger.info(f"Attempt {attempt + 1}/{max_attempts} to find email")
                
                script = f'''
                tell application "Microsoft Outlook"
                    try
                        set inboxFolder to inbox
                        set foundMessages to (every message of inboxFolder whose subject contains "{subject}")
                        
                        if (count of foundMessages) > 0 then
                            return "found"
                        else
                            return "not_found"
                        end if
                    on error errMsg
                        return "error: " & errMsg
                    end try
                end tell
                '''
                result = self.run_command(["osascript", "-e", script], timeout=15)
                
                if "found" in result.stdout:
                    self.logger.info("Test email received successfully")
                    return True
                    
                if attempt < max_attempts - 1:
                    self.logger.info(f"Email not found yet, waiting {check_interval} seconds")
                    time.sleep(check_interval)
                    self._sync_mailbox()
                    time.sleep(3)
                    
            self.logger.error("Email was not received within the expected time")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to verify email receipt: {e}")
            return False
            
    def _delete_test_email(self, subject: str):
        """Delete the test email after verification"""
        try:
            self.logger.info("Deleting test email")
            script = f'''
            tell application "Microsoft Outlook"
                try
                    set inboxFolder to inbox
                    set foundMessages to (every message of inboxFolder whose subject contains "{subject}")
                    
                    repeat with aMessage in foundMessages
                        delete aMessage
                    end repeat
                    
                    -- Also check sent items
                    set sentFolder to sent items folder
                    set sentMessages to (every message of sentFolder whose subject contains "{subject}")
                    
                    repeat with aMessage in sentMessages
                        delete aMessage
                    end repeat
                    
                    return "deleted"
                on error errMsg
                    return "error: " & errMsg
                end try
            end tell
            '''
            result = self.run_command(["osascript", "-e", script], timeout=15)
            
            if "deleted" in result.stdout:
                self.logger.info("Test email deleted successfully")
            else:
                self.logger.warning("Could not delete test email")
                
        except Exception as e:
            self.logger.warning(f"Error deleting test email: {e}")
            
    def _close_outlook(self):
        """Close Microsoft Outlook"""
        try:
            self.logger.info("Closing Microsoft Outlook")
            script = '''
            tell application "Microsoft Outlook"
                quit
            end tell
            '''
            self.run_command(["osascript", "-e", script], timeout=10)
            time.sleep(3)
            
        except Exception as e:
            self.logger.warning(f"Error closing Outlook gracefully: {e}")
            
    def _ensure_outlook_closed(self):
        """Ensure Outlook is fully closed"""
        try:
            if self.check_process_running("Microsoft Outlook"):
                self.logger.warning("Force closing Microsoft Outlook")
                self.run_command(["pkill", "-9", "Microsoft Outlook"])
                
        except Exception as e:
            self.logger.warning(f"Error force closing Outlook: {e}")
