# Quick Start Guide

Get up and running with MacMocker in 5 minutes.

## Prerequisites

Ensure you have:
- macOS 12.0 or later
- Python 3.10 or later installed
- Administrator access

## Installation

### 1. Install uv Package Manager

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Add uv to your path (follow the installer instructions or add to `.zshrc`):

```bash
export PATH="$HOME/.cargo/bin:$PATH"
```

### 2. Clone or Download MacMocker

```bash
# If using git
git clone https://github.com/david-crosby/macmocker.git
cd macmocker

# Or download and extract the archive
```

### 3. Install Dependencies

```bash
uv pip install -e .
```

### 4. Make the Main Script Executable

```bash
chmod +x main.py
```

## Grant Permissions (Required)

MacMocker needs accessibility and screen recording permissions.

### Option A: Manual (for testing)

1. Open **System Settings** > **Privacy & Security**
2. Click **Accessibility**
3. Add Terminal (or your terminal application)
4. Enable the toggle
5. Go back and click **Screen Recording**
6. Add Terminal
7. Enable the toggle

### Option B: Configuration Profile (for production)

Deploy the TCC profile via Jamf Pro or manually:

```bash
sudo profiles install -path deployment/tcc_profile.mobileconfig
```

## Run Your First Test

### Quick Test (5 minutes)

```bash
python3 main.py --config config/quick_tests.yaml
```

This will:
- Test network connectivity to common URLs
- Launch Safari and verify ready state
- Launch Mail and verify ready state
- Generate a report in `~/macmocker_artifacts/`

### View Results

Results are printed to the console and saved to the artifacts directory:

```bash
# Find latest results
ls -lt ~/macmocker_artifacts/

# View text report
cat ~/macmocker_artifacts/macmocker_quick_tests_*/report_*.txt

# View JSON results
cat ~/macmocker_artifacts/macmocker_quick_tests_*/results_*.json
```

## Customise Your Tests

### 1. Copy the Example Configuration

```bash
cp config/example_config.yaml config/my_tests.yaml
```

### 2. Edit Configuration

Open `config/my_tests.yaml` in your favourite editor and customise:

```yaml
suite_name: "My Custom Tests"

tests:
  # Enable/disable tests
  - module: "tests.network.network_test.NetworkTest"
    enabled: true  # Set to false to skip
    
    # Add your URLs
    urls:
      - "https://your-internal-app.company.com"
      - "https://www.google.com"
  
  # Test your applications
  - module: "tests.applications.application_launch_test.ApplicationLaunchTest"
    enabled: true
    app_name: "Your App Name"
    process_name: "Your App"
```

### 3. Run Your Custom Tests

```bash
python3 main.py --config config/my_tests.yaml
```

## Test Microsoft Office

### Excel Test

```yaml
- module: "tests.applications.excel_test.MicrosoftExcelTest"
  enabled: true
  test_headers:
    - "Item"
    - "Quantity"
    - "Status"
  test_data:
    - ["Widget A", "100", "Available"]
    - ["Widget B", "50", "On Order"]
  cleanup: true
```

### Outlook Test

```yaml
- module: "tests.applications.outlook_test.MicrosoftOutlookTest"
  enabled: true
  test_email_address: "your-test-email@company.com"
  email_body: "Test email from MacMocker"
  email_wait_time: 30
```

**Note:** Outlook must have an email account configured.

## Common Use Cases

### Test After System Updates

```bash
python3 main.py \
  --config config/full_tests.yaml \
  --artifacts-dir /var/log/system-update-tests
```

### Quick Health Check

```bash
python3 main.py \
  --config config/quick_tests.yaml \
  --log-level INFO
```

### Test Specific Application

Create a minimal config:

```yaml
suite_name: "App-Specific Test"
tests:
  - module: "tests.applications.application_launch_test.ApplicationLaunchTest"
    enabled: true
    app_name: "Microsoft Excel"
    process_name: "Microsoft Excel"
    timeout: 120
```

## Enable Teams Notifications

Add your Teams webhook to any configuration:

```yaml
reporting:
  teams_webhook: "https://outlook.office.com/webhook/YOUR_WEBHOOK_URL"
```

Get a webhook URL:
1. In Teams, go to your channel
2. Click "..." > Connectors
3. Search for "Incoming Webhook"
4. Configure and copy the URL

## Troubleshooting

### "Permission denied" errors

Grant accessibility and screen recording permissions (see above).

### "Application not found" errors

Check the application name:
```bash
ls /Applications/
```

Use the exact name including `.app` extension in configuration if needed.

### Tests timing out

Increase timeout values in your configuration:

```yaml
tests:
  - module: "..."
    timeout: 300  # Increase from default
    launch_wait_time: 10  # Wait longer after launch
```

### Dependencies not installing

Ensure uv is in your PATH:
```bash
which uv
```

If not found, restart your terminal or run:
```bash
export PATH="$HOME/.cargo/bin:$PATH"
```

### Outlook test not receiving email

- Verify Outlook account is configured and connected
- Check the test email address is correct
- Ensure Outlook can send/receive normally
- Increase `email_wait_time` in configuration
- Check Outlook is not in offline mode

## Next Steps

- Read the full [README](README.md) for detailed documentation
- Explore [example configurations](config/)
- Learn about [creating custom tests](README.md#creating-custom-tests)
- Set up [CI/CD integration](.github/workflows/test.yml)
- Deploy via [Jamf Pro](deployment/JAMF_DEPLOYMENT.md)

## Getting Help

- Check the logs: `~/macmocker_artifacts/*/macmocker_*.log`
- Review test output for specific error messages
- Contact: [David Crosby](https://www.linkedin.com/in/david-bing-crosby/)

## Useful Commands

```bash
# View all available options
python3 main.py --help

# Run with debug logging
python3 main.py --config config/quick_tests.yaml --log-level DEBUG

# Specify custom artifacts location
python3 main.py \
  --config config/quick_tests.yaml \
  --artifacts-dir /path/to/artifacts

# Quick syntax check of config
python3 -c "import yaml; yaml.safe_load(open('config/my_tests.yaml'))"
```

## Development Workflow

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run linting
make lint

# Format code
make format

# Clean build artifacts
make clean
```

Happy testing with MacMocker!
