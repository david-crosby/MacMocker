# MacMocker - Project Summary

## Overview

MacMocker is a comprehensive, modular testing framework for macOS devices designed specifically for CI/CD workflows and Jamf Pro integration. The suite simulates real user interactions to validate device configuration and application functionality.

## What's New

✨ **Project renamed from "macOS Test Suite" to "MacMocker"**  
✨ **Microsoft Excel test module** - Complete spreadsheet workflow testing  
✨ **Microsoft Outlook test module** - Email send and receive verification  
✨ **Updated configurations** - Full test suite includes Office apps  
✨ **Enhanced documentation** - All guides updated with new features

## Test Modules

### 1. Network Test
- URL accessibility testing
- DNS resolution verification
- Connection speed testing
- Response time monitoring

### 2. Application Launch Test
- Generic, configurable for any application
- Process monitoring
- Window visibility verification
- Menu bar loading checks
- Crash dialogue detection
- System log monitoring

### 3. Microsoft Word Test
- Document creation
- Save and reopen
- Edit operations
- AppleScript integration

### 4. Microsoft Excel Test ✨ NEW
- Create workbook with headers and data
- Enter cell data programmatically
- Save to Desktop
- Reopen and verify
- Edit cells and add formulas (SUM)
- Full validation workflow

### 5. Microsoft Outlook Test ✨ NEW
- Verify email account configured
- Create and send test email
- Trigger mailbox synchronisation
- Check inbox for received email
- Configurable retry attempts
- Automatic cleanup of test emails

## Key Features

- **Modular architecture** for easy extension
- **Sequential execution** simulating real users
- **YAML configuration** for flexibility
- **Screenshot capture** on failures
- **Log monitoring** for errors
- **Teams integration** for notifications
- **API posting** for custom workflows
- **Jamf Pro deployment** ready

## Configuration Examples

### Excel Test

```yaml
- module: "tests.applications.excel_test.MicrosoftExcelTest"
  enabled: true
  timeout: 300
  test_headers:
    - "Product"
    - "Quantity"  
    - "Status"
  test_data:
    - ["Widget A", "150", "In Stock"]
    - ["Widget B", "75", "In Stock"]
  cleanup: true
```

### Outlook Test

```yaml
- module: "tests.applications.outlook_test.MicrosoftOutlookTest"
  enabled: true
  timeout: 600
  test_email_address: "test@company.com"
  email_body: "Automated test from MacMocker"
  email_wait_time: 30
  receive_check_attempts: 3
  delete_test_email: true
```

## File Structure

```
macmocker/
├── main.py
├── config/
│   ├── quick_tests.yaml
│   ├── full_tests.yaml
│   └── example_config.yaml
├── tests/
│   ├── base_test.py
│   ├── network/
│   │   └── network_test.py
│   └── applications/
│       ├── application_launch_test.py
│       ├── word_test.py
│       ├── excel_test.py          ✨ NEW
│       └── outlook_test.py        ✨ NEW
├── core/
│   ├── test_runner.py
│   ├── config_loader.py
│   └── reporter.py
└── deployment/
    ├── tcc_profile.mobileconfig
    ├── install.sh
    └── build_pkg.sh
```

## Quick Start

### Installation

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
cd macmocker
uv pip install -e .
```

### Run Tests

```bash
# Quick 5-minute test
python3 main.py --config config/quick_tests.yaml

# Full test suite (includes Office apps)
python3 main.py --config config/full_tests.yaml
```

### View Results

```bash
# Results saved to:
~/macmocker_artifacts/

# View latest report
ls -lt ~/macmocker_artifacts/
cat ~/macmocker_artifacts/*/report_*.txt
```

## Deployment

### Via Jamf Pro

1. Build package:
   ```bash
   cd deployment
   ./build_pkg.sh
   ```

2. Upload `macmocker-0.1.0.pkg` to Jamf Pro

3. Deploy TCC profile (`tcc_profile.mobileconfig`)

4. Create installation policy

## Technical Details

- **Bundle ID**: `uk.co.bing-bong.macmocker`
- **Requirements**: macOS 12.0+, Python 3.10+
- **Permissions**: Accessibility, Screen Recording
- **Dependencies**: PyYAML, requests, Pillow, pyobjc, atomacos

## Documentation

- **README.md** - Comprehensive guide
- **QUICKSTART.md** - 5-minute setup
- **CHANGELOG.md** - Version history
- **JAMF_DEPLOYMENT.md** - Jamf integration
- **example_config.yaml** - Configuration template

## What Makes MacMocker Special

1. **Office App Testing** - Comprehensive Microsoft Office validation
2. **Email Verification** - Outlook send/receive testing
3. **Spreadsheet Testing** - Excel data entry and formula validation
4. **Sequential Execution** - Mimics real user behaviour
5. **Production Ready** - Jamf deployment, CI/CD integration
6. **Fully Modular** - Easy to extend with new tests

## Notes for Outlook Testing

The Outlook test requires:
- Outlook configured with an email account
- Test email address accessible by the account
- Account can send and receive emails
- Recommended: use a dedicated test account

The test is **disabled by default** in `full_tests.yaml`. Enable it by setting `enabled: true` and configuring your test email address.

## Contact

**David Crosby**  
LinkedIn: https://www.linkedin.com/in/david-bing-crosby/  
GitHub: https://github.com/david-crosby  
Email: bing@bing-bong.co.uk

## Access Your Project

[View MacMocker](computer:///mnt/user-data/outputs/macmocker)

## Version

**MacMocker v0.1.0**  
Released: 2024-11-20

All code follows your preferences:
- ✅ British English spelling
- ✅ Clean Python with type hints
- ✅ uv for dependency management
- ✅ Conventional Commits ready
- ✅ Minimal, meaningful comments
