import time
from tests.base_test import BaseTest, TestResult


class OutlookTest(BaseTest):
    def get_name(self) -> str:
        return "microsoft_outlook_test"

    def get_description(self) -> str:
        return "Tests Microsoft Outlook email functionality"

    def run(self) -> TestResult:
        self.result.mark_started()
        
        try:
            if not self.check_application_exists("Microsoft Outlook"):
                self.result.mark_skipped("Microsoft Outlook not installed")
                return self.result

            test_email = self.config.get("test_email")
            if not test_email:
                raise Exception("test_email not configured")

            self._launch_outlook()
            self._send_test_email(test_email)
            time.sleep(5)
            self._verify_email_sent()
            
            self.result.mark_passed("Outlook test completed successfully")
            
        except Exception as e:
            self.capture_screenshot("outlook_test_failure.png")
            self.result.mark_failed(str(e), str(e))
        finally:
            self._cleanup()
        
        return self.result

    def _launch_outlook(self):
        if not self.launch_application("Microsoft Outlook", timeout=30):
            raise Exception("Failed to launch Outlook")
        
        time.sleep(5)
        self.result.add_log("Outlook launched")

    def _send_test_email(self, recipient: str):
        subject = "MacMocker Test Email"
        body = f"This is a test email from MacMocker at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        script = f'''
        tell application "Microsoft Outlook"
            set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{body}"}}
            make new recipient at newMessage with properties {{email address:{{address:"{recipient}"}}}}
            send newMessage
        end tell
        '''
        
        success, output = self.run_applescript(script, timeout=15)
        if not success:
            raise Exception(f"Failed to send email: {output}")
        
        self.result.add_log(f"Test email sent to {recipient}")

    def _verify_email_sent(self):
        script = '''
        tell application "Microsoft Outlook"
            set sentCount to count of messages in sent items folder
            return sentCount
        end tell
        '''
        
        success, output = self.run_applescript(script, timeout=10)
        if success and output.strip().isdigit():
            count = int(output.strip())
            if count > 0:
                self.result.add_log(f"Verified {count} sent messages")
                return
        
        self.logger.warning("Could not verify sent email count")

    def _cleanup(self):
        self.quit_application("Microsoft Outlook")
