# MacMocker

A modular, interactive testing framework for macOS devices designed for CI/CD workflows. MacMocker simulates real user interactions to validate device configuration and application functionality.

## Overview

MacMocker provides:

- **Modular architecture** for easy test creation and management
- **Sequential test execution** simulating real user workflows
- **Flexible configuration** via YAML files
- **Comprehensive reporting** with screenshots and logs
- **Integration** with Teams webhooks and custom APIs
- **Jamf Pro deployment** support

## Features

- Network connectivity and performance testing
- Application launch and readiness verification
- Microsoft Office testing (Word, Excel, Outlook)
- UI interaction testing
- System log monitoring for errors
- Screenshot capture on failures
- Configurable timeouts and delays
- Human-readable reports
- CI/CD integration (GitHub Actions, Harness)

## Requirements

- macOS 12.0 or later
- Python 3.10 or later
- Accessibility permissions (via TCC profile)
- Screen recording permissions (for screenshots)

## Installation

### Via Jamf Pro

1. Build the package:
   ```bash
   cd deployment
   chmod +x build_pkg.sh
   ./build_pkg.sh
   ```

2. Upload `build/macmocker-0.1.0.pkg` to Jamf Pro

3. Deploy the TCC configuration profile:
   - Upload `deployment/tcc_profile.mobileconfig` to Jamf Pro
   - Assign to target devices
   - This grants necessary accessibility and screen recording permissions

4. Create a Jamf policy to install the package

### Manual Installation

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -e .

# Make main script executable
chmod +x main.py
```

## Configuration

### Quick Start

Copy the example configuration:

```bash
cp config/example_config.yaml config/my_tests.yaml
```

Edit `my_tests.yaml` to define your tests.

### Configuration Structure

```yaml
suite_name: "My Test Suite"
global_timeout: 3600
artifacts_retention_days: 7

reporting:
  teams_webhook: "https://your-webhook-url"
  api_url: "https://your-api.example.com/results"
  api_token: "your-token"

tests:
  - module: "tests.network.network_test.NetworkTest"
    enabled: true
    timeout: 120
    urls:
      - "https://www.example.com"
```

### Pre-configured Test Suites

- **Quick Tests** (`config/quick_tests.yaml`): 5-minute validation
- **Full Tests** (`config/full_tests.yaml`): Comprehensive test run including Office apps

## Usage

### Command Line

```bash
# Run quick tests
python3 main.py --config config/quick_tests.yaml

# Run with custom artifacts directory
python3 main.py \
  --config config/full_tests.yaml \
  --artifacts-dir /path/to/artifacts \
  --log-level DEBUG

# View help
python3 main.py --help
```

### Via Symlink (if installed system-wide)

```bash
macmocker --config config/quick_tests.yaml
```

## Available Test Modules

### Network Test
**Module:** `tests.network.network_test.NetworkTest`

Tests network connectivity, DNS resolution, and optionally measures connection speed.

**Configuration:**
```yaml
- module: "tests.network.network_test.NetworkTest"
  urls:
    - "https://www.example.com"
  test_dns: true
  test_speed: true
  max_response_time_ms: 5000
```

### Application Launch Test
**Module:** `tests.applications.application_launch_test.ApplicationLaunchTest`

Generic test for launching any application and verifying ready state.

**Configuration:**
```yaml
- module: "tests.applications.application_launch_test.ApplicationLaunchTest"
  app_name: "Safari"
  process_name: "Safari"
  monitor_logs: true
  ready_checks:
    window_visible: true
    menu_bar_loaded: true
    no_crash_dialogs: true
```

### Microsoft Word Test
**Module:** `tests.applications.word_test.MicrosoftWordTest`

Comprehensive Word testing: create, save, reopen, and edit documents.

**Configuration:**
```yaml
- module: "tests.applications.word_test.MicrosoftWordTest"
  test_content: "Test document content"
  cleanup: true
```

### Microsoft Excel Test
**Module:** `tests.applications.excel_test.MicrosoftExcelTest`

Complete Excel testing: create workbook, enter data, save, reopen, edit with formulas.

**Configuration:**
```yaml
- module: "tests.applications.excel_test.MicrosoftExcelTest"
  test_headers:
    - "Item"
    - "Quantity"
    - "Status"
  test_data:
    - ["Product A", "100", "Available"]
    - ["Product B", "50", "Available"]
  cleanup: true
```

### Microsoft Outlook Test
**Module:** `tests.applications.outlook_test.MicrosoftOutlookTest`

Email functionality testing: create, send, and verify receipt of test emails.

**Configuration:**
```yaml
- module: "tests.applications.outlook_test.MicrosoftOutlookTest"
  test_email_address: "test@yourcompany.com"
  email_body: "Test email from MacMocker"
  email_wait_time: 30
  receive_check_attempts: 3
  delete_test_email: true
```

**Note:** Requires Outlook to be configured with an email account. The test sends an email to the specified address and then checks for its receipt in the inbox.

## Creating Custom Tests

### 1. Create a new test module

```python
from tests.base_test import BaseTest, TestResult

class MyCustomTest(BaseTest):
    def get_name(self) -> str:
        return "my_custom_test"
    
    def get_description(self) -> str:
        return "Description of what this test does"
    
    def run(self) -> TestResult:
        self.result.mark_started()
        
        try:
            # Your test logic here
            
            if success:
                self.result.mark_passed("Test passed successfully")
            else:
                self.result.mark_failed("Test failed", "Error details")
                
        except Exception as e:
            self.result.mark_failed(f"Exception: {str(e)}", str(e))
        
        return self.result
```

### 2. Add to configuration

```yaml
tests:
  - module: "tests.my_module.my_custom_test.MyCustomTest"
    enabled: true
    timeout: 300
```

## CI/CD Integration

### GitHub Actions

The included workflow (`.github/workflows/test.yml`) runs tests automatically on:
- Push to main/develop branches
- Pull requests
- Daily schedule (2am)
- Manual trigger

Configure secrets in GitHub:
- `TEAMS_WEBHOOK_URL`: Microsoft Teams webhook for notifications

### Harness

Create a pipeline that:
1. Deploys the package via Jamf
2. Runs the test suite on target devices
3. Collects artifacts
4. Posts results to your monitoring system

## Reporting

### Report Formats

- **Text Report**: Human-readable summary with test results
- **JSON Report**: Machine-readable format for API integration
- **Logs**: Detailed execution logs for debugging

### Teams Integration

Configure a Teams webhook in your test configuration:

```yaml
reporting:
  teams_webhook: "https://outlook.office.com/webhook/..."
```

Results are automatically posted with:
- Test summary
- Pass/fail counts
- Success rate
- Duration

### API Integration

Post results to a custom API:

```yaml
reporting:
  api_url: "https://your-api.example.com/results"
  api_token: "your-bearer-token"
```

## Troubleshooting

### Permission Issues

If tests fail with permission errors:

1. Verify TCC profile is installed:
   ```bash
   profiles show
   ```

2. Check accessibility permissions:
   ```bash
   sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db \
     "SELECT * FROM access WHERE service='kTCCServiceAccessibility'"
   ```

### Application Not Launching

- Verify application is installed
- Check application path in configuration
- Increase `launch_wait_time` and `process_start_timeout`
- Review logs for specific errors

### Outlook Test Failing

- Ensure Outlook has an email account configured
- Verify the test email address is accessible
- Check that the account can send and receive emails
- Increase `email_wait_time` if emails are slow to arrive
- Ensure Outlook is not in offline mode

### Excel/Word Tests Failing

- Verify Microsoft Office is installed and licensed
- Check that applications can be controlled via AppleScript
- Ensure no Office updates are pending
- Grant Full Disk Access if saving to Desktop fails

## Development

### Project Structure

```
macmocker/
├── config/              # Test configurations
│   ├── quick_tests.yaml        # 5-minute test run
│   ├── full_tests.yaml         # Comprehensive tests
│   └── example_config.yaml     # Template
├── tests/               # Test modules
│   ├── network/        # Network tests
│   ├── applications/   # Application tests
│   │   ├── application_launch_test.py
│   │   ├── word_test.py
│   │   ├── excel_test.py
│   │   └── outlook_test.py
│   ├── system/         # System tests
│   └── performance/    # Performance tests
├── core/               # Framework core
│   ├── test_runner.py          # Main execution engine
│   ├── config_loader.py        # YAML parser
│   └── reporter.py             # Results & reporting
├── deployment/         # Deployment artifacts
│   ├── tcc_profile.mobileconfig
│   ├── install.sh
│   └── build_pkg.sh
├── main.py            # Entry point
├── pyproject.toml     # uv dependencies
└── README.md
```

### Running Tests in Development

```bash
# Install in development mode
uv pip install -e .

# Run with debug logging
python3 main.py \
  --config config/quick_tests.yaml \
  --log-level DEBUG
```

## Contributing

When creating new tests or features:

1. Follow the existing code structure
2. Use type hints
3. Keep comments focused on "why" not "how"
4. Write clean, readable code
5. Update documentation

## Git Commit Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new test module for disk space checking
fix: correct timeout handling in network test
docs: update README with Harness integration
```

## Contact

**David Crosby**  
LinkedIn: [https://www.linkedin.com/in/david-bing-crosby/](https://www.linkedin.com/in/david-bing-crosby/)  
GitHub: [https://github.com/david-crosby](https://github.com/david-crosby)

## Licence

Copyright © 2024 David Crosby. See LICENSE file for details.

## Version

Current version: 0.1.0
