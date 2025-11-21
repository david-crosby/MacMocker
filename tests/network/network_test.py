import time
import requests
from tests.base_test import BaseTest, TestResult


class NetworkTest(BaseTest):
    def get_name(self) -> str:
        return "network_connectivity_test"

    def get_description(self) -> str:
        return "Tests network connectivity and URL accessibility"

    def run(self) -> TestResult:
        self.result.mark_started()
        
        try:
            urls = self.config.get("urls", ["https://www.google.com"])
            timeout = self.config.get("request_timeout", 10)
            
            for url in urls:
                self._test_url(url, timeout)
            
            self.result.mark_passed(f"All {len(urls)} URLs accessible")
            
        except Exception as e:
            self.capture_screenshot("network_test_failure.png")
            self.result.mark_failed(str(e), str(e))
        
        return self.result

    def _test_url(self, url: str, timeout: int):
        self.logger.info(f"Testing {url}")
        
        start = time.time()
        
        try:
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            duration = time.time() - start
            
            if response.status_code == 200:
                self.result.add_log(f"{url}: OK ({duration:.2f}s)")
            else:
                raise Exception(f"{url}: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            raise Exception(f"{url}: Timed out after {timeout}s")
        except requests.exceptions.RequestException as e:
            raise Exception(f"{url}: {str(e)}")
