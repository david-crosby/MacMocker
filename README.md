# MacMocker

macOS device testing suite for CI/CD workflows.

## Overview

MacMocker runs automated tests on macOS devices to verify correct operation. Tests can check network connectivity, application functionality, and system behaviour.

## Quick Start

```bash
# Install dependencies
uv pip install -e .

# Run quick tests
python3 main.py --config config/quick_tests.yaml

# Run full test suite
python3 main.py --config config/full_tests.yaml
```

## Requirements

- macOS 12.0+
- Python 3.10+
- Accessibility permissions enabled
- Screen recording permissions enabled (for UI automation)

## Configuration

Tests are configured via YAML files in the `config/` directory.

Example:

```yaml
suite_name: "My Tests"
artifacts_dir: "~/macmocker_artifacts"

tests:
  - module: "tests.network.network_test.NetworkTest"
    enabled: true
    timeout: 60
    urls:
      - "https://www.google.com"
```

## Available Tests

### Network Tests
- URL accessibility and response times
- Proxy configuration verification

### Application Tests
- Microsoft Word document creation and editing
- Microsoft Excel spreadsheet manipulation
- Microsoft Outlook email sending and verification

## Writing Custom Tests

Create a new test by inheriting from `BaseTest`:

```python
from tests.base_test import BaseTest, TestResult

class MyTest(BaseTest):
    def get_name(self) -> str:
        return "my_test"

    def get_description(self) -> str:
        return "Description of what this test does"

    def run(self) -> TestResult:
        self.result.mark_started()
        
        try:
            # Your test logic here
            self.result.mark_passed("Test passed")
        except Exception as e:
            self.result.mark_failed(str(e))
        
        return self.result
```

Add your test to a configuration file:

```yaml
tests:
  - module: "tests.custom.my_test.MyTest"
    enabled: true
    timeout: 300
```

## Reporting

Results are saved to the artifacts directory in both text and JSON formats.

Optional integrations:
- Microsoft Teams webhooks
- Custom API endpoints

Configure in your YAML:

```yaml
reporting:
  teams_webhook: "https://your-webhook-url"
  api_endpoint: "https://your-api/results"
  api_key: "your-api-key"
```

**Future Additions** 

- Add reproting via Jamf Extension Attributes

## Deployment

### Manual Installation

```bash
git clone https://github.com/david-crosby/macmocker.git
cd macmocker
uv pip install -e .
```

### Jamf Pro

See `deployment/JAMF_DEPLOYMENT.md` for detailed instructions.

Quick steps:
1. Build package: `cd deployment && ./build_pkg.sh`
2. Upload package to Jamf Pro
3. Deploy TCC profile: `deployment/tcc_profile.mobileconfig`
4. Create policy to run tests

## Exit Codes

- `0`: All tests passed
- `1`: One or more tests failed
- `2`: Fatal error (configuration, missing dependencies, etc.)

## Contact

David Crosby - [LinkedIn](https://www.linkedin.com/in/david-bing-crosby/)

## Licence

MIT Licence - see LICENCE file for details
