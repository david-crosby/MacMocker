import time
import subprocess
from pathlib import Path
from typing import Dict, Any
import requests

from tests.base_test import BaseTest, TestResult


class NetworkTest(BaseTest):
    """Test network connectivity, speed, and proxy access to specified URLs"""
    
    def get_name(self) -> str:
        return "network_connectivity_and_performance"
        
    def get_description(self) -> str:
        return "Tests network connectivity, measures speed, and validates proxy access to configured URLs"
        
    def run(self) -> TestResult:
        self.result.mark_started()
        
        try:
            urls = self.config.get("urls", [])
            if not urls:
                self.result.mark_failed("No URLs configured for testing")
                return self.result
                
            test_results = {
                "urls_tested": len(urls),
                "successful": 0,
                "failed": 0,
                "details": []
            }
            
            for url in urls:
                url_result = self._test_url(url)
                test_results["details"].append(url_result)
                
                if url_result["success"]:
                    test_results["successful"] += 1
                else:
                    test_results["failed"] += 1
                    
            if self.config.get("test_dns", True):
                dns_result = self._test_dns()
                test_results["dns"] = dns_result
                
            if self.config.get("test_speed", False):
                speed_result = self._test_connection_speed()
                test_results["speed"] = speed_result
                
            if test_results["failed"] > 0:
                self.result.mark_failed(
                    f"Network test completed with {test_results['failed']} failures out of {test_results['urls_tested']} URLs",
                    error_details=str(test_results)
                )
            else:
                self.result.mark_passed(
                    f"All {test_results['urls_tested']} URLs accessible, network performing correctly"
                )
                
            self.result.add_log(f"Network test results: {test_results}")
            
        except Exception as e:
            self.result.mark_failed(f"Network test failed with exception: {str(e)}", str(e))
            
        return self.result
        
    def _test_url(self, url: str) -> Dict[str, Any]:
        """Test a single URL for accessibility and response time"""
        result = {
            "url": url,
            "success": False,
            "response_time_ms": 0,
            "status_code": None,
            "error": None
        }
        
        try:
            start_time = time.time()
            
            timeout = self.config.get("url_timeout", 10)
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            
            response_time = (time.time() - start_time) * 1000
            
            result["response_time_ms"] = round(response_time, 2)
            result["status_code"] = response.status_code
            result["success"] = 200 <= response.status_code < 400
            
            self.logger.info(f"URL {url}: {response.status_code} in {response_time:.2f}ms")
            
            max_response_time = self.config.get("max_response_time_ms", 5000)
            if response_time > max_response_time:
                result["warning"] = f"Response time exceeded {max_response_time}ms threshold"
                
        except requests.Timeout:
            result["error"] = "Request timed out"
            self.logger.error(f"URL {url}: Timeout")
        except requests.RequestException as e:
            result["error"] = str(e)
            self.logger.error(f"URL {url}: {e}")
            
        return result
        
    def _test_dns(self) -> Dict[str, Any]:
        """Test DNS resolution"""
        test_domains = self.config.get("dns_test_domains", ["www.apple.com", "www.google.com"])
        
        dns_result = {
            "tested": len(test_domains),
            "successful": 0,
            "failed": 0,
            "details": []
        }
        
        for domain in test_domains:
            try:
                result = self.run_command(["nslookup", domain], timeout=5)
                success = result.returncode == 0
                
                dns_result["details"].append({
                    "domain": domain,
                    "success": success
                })
                
                if success:
                    dns_result["successful"] += 1
                else:
                    dns_result["failed"] += 1
                    
            except subprocess.TimeoutExpired:
                dns_result["failed"] += 1
                dns_result["details"].append({
                    "domain": domain,
                    "success": False,
                    "error": "timeout"
                })
                
        return dns_result
        
    def _test_connection_speed(self) -> Dict[str, Any]:
        """Test network connection speed by downloading a test file"""
        test_url = self.config.get("speed_test_url", "http://speedtest.tele2.net/1MB.zip")
        
        try:
            start_time = time.time()
            response = requests.get(test_url, timeout=30, stream=True)
            
            total_bytes = 0
            for chunk in response.iter_content(chunk_size=8192):
                total_bytes += len(chunk)
                
            elapsed_time = time.time() - start_time
            speed_mbps = (total_bytes * 8) / (elapsed_time * 1_000_000)
            
            return {
                "success": True,
                "bytes_downloaded": total_bytes,
                "elapsed_seconds": round(elapsed_time, 2),
                "speed_mbps": round(speed_mbps, 2)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
