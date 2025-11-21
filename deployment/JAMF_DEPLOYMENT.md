# Jamf Pro Deployment Guide

## Prerequisites

- Jamf Pro 10.40+
- macOS 12.0+ on target devices
- Admin access to Jamf Pro

## Step 1: Build Package

```bash
cd deployment
chmod +x build_pkg.sh
./build_pkg.sh
```

This creates `MacMocker-1.0.0.pkg`

## Step 2: Upload Package

1. Log in to Jamf Pro
2. Navigate to Settings > Computer Management > Packages
3. Click New
4. Upload `MacMocker-1.0.0.pkg`
5. Set display name to "MacMocker"
6. Save

## Step 3: Deploy TCC Profile

1. Navigate to Configuration Profiles
2. Click New
3. Upload `tcc_profile.mobileconfig`
4. Scope to computers that will run tests
5. Save

## Step 4: Create Policy

### Install Policy

1. Navigate to Policies
2. Click New
3. Configure:
   - Name: "Install MacMocker"
   - Trigger: Recurring check-in, enrollment
   - Execution frequency: Once per computer
4. Add package: MacMocker-1.0.0.pkg
5. Scope to test computers
6. Save

### Test Execution Policy

1. Create new policy
2. Configure:
   - Name: "Run MacMocker Tests"
   - Trigger: Recurring check-in (or custom)
   - Execution frequency: As needed
3. Add script:

```bash
#!/bin/bash
cd /usr/local/macmocker
python3 main.py --config config/quick_tests.yaml
exit $?
```

4. Set script parameters as needed
5. Scope appropriately
6. Save

## Configuration Management

Store custom configurations in Jamf as scripts or extension attributes.

Example script to deploy custom config:

```bash
#!/bin/bash

cat > /usr/local/macmocker/config/custom.yaml << 'EOF'
suite_name: "Production Tests"
tests:
  - module: "tests.network.network_test.NetworkTest"
    enabled: true
    timeout: 60
    urls:
      - "https://internal.company.com"
EOF
```

## Reporting Integration

### Teams Webhook

Add webhook URL to configuration:

```yaml
reporting:
  teams_webhook: "https://company.webhook.office.com/..."
```

### API Endpoint

Configure API posting:

```yaml
reporting:
  api_endpoint: "https://api.company.com/test-results"
  api_key: "your-api-key"
```

## Troubleshooting

### Permissions Issues

Verify TCC profile is installed:

```bash
sudo profiles show
```

### Python Issues

Check Python version:

```bash
python3 --version
```

### Test Failures

Check logs:

```bash
cat ~/macmocker_artifacts/run_*/report_*.txt
```

## Maintenance

### Updating MacMocker

1. Build new package with updated version
2. Upload to Jamf Pro
3. Update install policy
4. Flush policy on test devices

### Log Rotation

Add script to clean old results:

```bash
find ~/macmocker_artifacts -type d -mtime +30 -exec rm -rf {} \;
```

## Contact

For support, contact David Crosby via [LinkedIn](https://www.linkedin.com/in/david-bing-crosby/)
