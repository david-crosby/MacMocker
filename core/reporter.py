import json
import requests
import logging
from pathlib import Path
from typing import List
from datetime import datetime

from tests.base_test import TestResult


class Reporter:
    def __init__(self, results: List[TestResult], artifacts_dir: Path, config: dict):
        self.results = results
        self.artifacts_dir = artifacts_dir
        self.config = config
        self.logger = logging.getLogger("Reporter")

    def generate_all_reports(self):
        self.generate_text_report()
        self.generate_json_report()
        
        if self.config.get("teams_webhook"):
            self.send_teams_notification()
        
        if self.config.get("api_endpoint"):
            self.post_to_api()

    def generate_text_report(self):
        report_path = self.artifacts_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_path, 'w') as f:
            f.write("MacMocker Test Report\n")
            f.write("=" * 50 + "\n\n")
            
            summary = self._calculate_summary()
            f.write(f"Total Tests: {summary['total']}\n")
            f.write(f"Passed: {summary['passed']}\n")
            f.write(f"Failed: {summary['failed']}\n")
            f.write(f"Skipped: {summary['skipped']}\n")
            f.write(f"Success Rate: {summary['success_rate']:.1f}%\n\n")
            
            for result in self.results:
                f.write("-" * 50 + "\n")
                f.write(f"Test: {result.test_name}\n")
                f.write(f"Status: {result.status.upper()}\n")
                f.write(f"Duration: {result.duration:.2f}s\n")
                f.write(f"Message: {result.message}\n")
                
                if result.details:
                    f.write(f"Details: {result.details}\n")
                
                if result.screenshots:
                    f.write(f"Screenshots: {len(result.screenshots)}\n")
                
                f.write("\n")

        self.logger.info(f"Text report saved: {report_path}")

    def generate_json_report(self):
        report_path = self.artifacts_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            "generated_at": datetime.now().isoformat(),
            "summary": self._calculate_summary(),
            "tests": [
                {
                    "name": r.test_name,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details,
                    "duration": r.duration,
                    "screenshots": r.screenshots,
                    "logs": r.logs
                }
                for r in self.results
            ]
        }
        
        with open(report_path, 'w') as f:
            json.dump(data, f, indent=2)

        self.logger.info(f"JSON report saved: {report_path}")

    def send_teams_notification(self):
        webhook_url = self.config.get("teams_webhook")
        if not webhook_url:
            return

        summary = self._calculate_summary()
        
        colour = "00FF00" if summary['failed'] == 0 else "FF0000"
        
        message = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": "MacMocker Test Results",
            "themeColor": colour,
            "title": "MacMocker Test Results",
            "sections": [{
                "facts": [
                    {"name": "Total Tests", "value": str(summary['total'])},
                    {"name": "Passed", "value": str(summary['passed'])},
                    {"name": "Failed", "value": str(summary['failed'])},
                    {"name": "Success Rate", "value": f"{summary['success_rate']:.1f}%"}
                ]
            }]
        }

        try:
            response = requests.post(webhook_url, json=message, timeout=10)
            if response.status_code == 200:
                self.logger.info("Teams notification sent")
            else:
                self.logger.error(f"Teams notification failed: {response.status_code}")
        except Exception as e:
            self.logger.error(f"Failed to send Teams notification: {e}")

    def post_to_api(self):
        api_endpoint = self.config.get("api_endpoint")
        if not api_endpoint:
            return

        data = {
            "timestamp": datetime.now().isoformat(),
            "summary": self._calculate_summary(),
            "results": [
                {
                    "test": r.test_name,
                    "status": r.status,
                    "duration": r.duration,
                    "message": r.message
                }
                for r in self.results
            ]
        }

        try:
            headers = {}
            if api_key := self.config.get("api_key"):
                headers["Authorization"] = f"Bearer {api_key}"

            response = requests.post(
                api_endpoint,
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                self.logger.info("Results posted to API")
            else:
                self.logger.error(f"API post failed: {response.status_code}")
        except Exception as e:
            self.logger.error(f"Failed to post to API: {e}")

    def _calculate_summary(self) -> dict:
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "passed")
        failed = sum(1 for r in self.results if r.status == "failed")
        skipped = sum(1 for r in self.results if r.status == "skipped")
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "success_rate": (passed / total * 100) if total > 0 else 0
        }
