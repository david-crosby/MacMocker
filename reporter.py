import json
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class Reporter:
    """Handles test result reporting and external integrations"""
    
    def __init__(self, artifacts_dir: Path, config: Dict[str, Any]):
        self.artifacts_dir = artifacts_dir
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.results: List[Dict[str, Any]] = []
        self.start_time: datetime = datetime.now()
        self.end_time: Optional[datetime] = None
        
    def add_result(self, result: Dict[str, Any]):
        """Add a test result to the report"""
        self.results.append(result)
        
    def finalize(self):
        """Mark the test suite as complete"""
        self.end_time = datetime.now()
        
    def get_summary(self) -> Dict[str, Any]:
        """Generate a summary of test results"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "passed")
        failed = sum(1 for r in self.results if r["status"] == "failed")
        skipped = sum(1 for r in self.results if r["status"] == "skipped")
        
        duration = 0.0
        if self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "success_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
            "duration_seconds": duration,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }
        
    def generate_report(self) -> str:
        """Generate a human-readable report"""
        summary = self.get_summary()
        
        report_lines = [
            "=" * 80,
            "MacMocker Test Report",
            "=" * 80,
            "",
            f"Suite: {self.config.get('suite_name', 'Unknown')}",
            f"Started: {summary['start_time']}",
            f"Duration: {summary['duration_seconds']:.2f} seconds",
            "",
            "Summary:",
            f"  Total Tests: {summary['total_tests']}",
            f"  Passed: {summary['passed']}",
            f"  Failed: {summary['failed']}",
            f"  Skipped: {summary['skipped']}",
            f"  Success Rate: {summary['success_rate']}",
            "",
            "=" * 80,
            "Test Results:",
            "=" * 80,
            "",
        ]
        
        for result in self.results:
            status_symbol = {
                "passed": "✓",
                "failed": "✗",
                "skipped": "○",
            }.get(result["status"], "?")
            
            report_lines.append(
                f"{status_symbol} {result['test_name']} [{result['status'].upper()}]"
            )
            report_lines.append(f"  Duration: {result['duration_seconds']:.2f}s")
            
            if result.get("message"):
                report_lines.append(f"  Message: {result['message']}")
                
            if result.get("error_details"):
                report_lines.append(f"  Error: {result['error_details']}")
                
            if result.get("screenshots"):
                report_lines.append(f"  Screenshots: {len(result['screenshots'])}")
                
            report_lines.append("")
            
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
        
    def save_report(self):
        """Save report to artifacts directory"""
        report_path = self.artifacts_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_content = self.generate_report()
        
        with open(report_path, 'w') as f:
            f.write(report_content)
            
        self.logger.info(f"Report saved to {report_path}")
        
        json_path = self.artifacts_dir / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, 'w') as f:
            json.dump({
                "summary": self.get_summary(),
                "results": self.results,
            }, f, indent=2)
            
        self.logger.info(f"JSON results saved to {json_path}")
        
        return report_path
        
    def post_to_api(self, api_url: str, api_token: Optional[str] = None):
        """Post results to an API endpoint"""
        try:
            headers = {"Content-Type": "application/json"}
            if api_token:
                headers["Authorization"] = f"Bearer {api_token}"
                
            payload = {
                "summary": self.get_summary(),
                "results": self.results,
            }
            
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            self.logger.info(f"Results posted to API: {api_url}")
            return True
        except requests.RequestException as e:
            self.logger.error(f"Failed to post to API: {e}")
            return False
            
    def post_to_teams(self, webhook_url: str):
        """Post summary to Microsoft Teams"""
        try:
            summary = self.get_summary()
            
            status_colour = "00FF00" if summary["failed"] == 0 else "FF0000"
            
            card = {
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "summary": "MacMocker Test Results",
                "themeColor": status_colour,
                "title": f"Test Suite: {self.config.get('suite_name', 'Unknown')}",
                "sections": [{
                    "facts": [
                        {"name": "Total Tests", "value": str(summary["total_tests"])},
                        {"name": "Passed", "value": str(summary["passed"])},
                        {"name": "Failed", "value": str(summary["failed"])},
                        {"name": "Skipped", "value": str(summary["skipped"])},
                        {"name": "Success Rate", "value": summary["success_rate"]},
                        {"name": "Duration", "value": f"{summary['duration_seconds']:.2f}s"},
                    ]
                }]
            }
            
            response = requests.post(webhook_url, json=card, timeout=30)
            response.raise_for_status()
            
            self.logger.info("Results posted to Teams")
            return True
        except requests.RequestException as e:
            self.logger.error(f"Failed to post to Teams: {e}")
            return False
