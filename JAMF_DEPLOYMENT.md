# Jamf Pro Deployment Guide

This guide covers deploying the macOS Test Suite via Jamf Pro.

## Prerequisites

- Jamf Pro account with appropriate permissions
- Target devices enrolled in Jamf Pro
- Network access to required URLs (for downloading dependencies)

## Deployment Steps

### 1. Build the Package

On a macOS machine with the test suite:

```bash
cd deployment
chmod +x build_pkg.sh
./build_pkg.sh
```

This creates `build/macos-test-suite-0.1.0.pkg`

### 2. Upload to Jamf Pro

1. Log into Jamf Pro
2. Navigate to **Settings** > **Computer Management** > **Packages**
3. Click **New**
4. Upload `macos-test-suite-0.1.0.pkg`
5. Configure:
   - Display Name: "macOS Test Suite"
   - Category: "Testing" or "Utilities"
   - Priority: 10 (default)
6. Save

### 3. Deploy TCC Configuration Profile

The test suite requires accessibility and screen recording permissions.

1. Navigate to **Configuration Profiles**
2. Click **New**
3. Under **General**:
   - Name: "macOS Test Suite TCC Permissions"
   - Level: Computer Level
4. Click **Upload**
5. Upload `deployment/tcc_profile.mobileconfig`
6. Configure scope (assign to test devices)
7. Save

### 4. Create Installation Policy

1. Navigate to **Policies**
2. Click **New**
3. Configure **General**:
   - Display Name: "Install macOS Test Suite"
   - Enabled: Yes
   - Trigger: Check-in, Recurring
   - Execution Frequency: Once per computer
4. Configure **Packages**:
   - Add "macOS Test Suite" package
   - Action: Install
5. Configure **Scope**:
   - Add target devices/groups
6. Save

### 5. Create Test Execution Policy

#### Quick Test Policy

1. Create new policy: "Run macOS Quick Tests"
2. **Scripts** section:
   - Add script (see below)
   - Priority: After
3. **Scope**: Your test devices
4. **Trigger**: 
   - Recurring check-in (for scheduled tests)
   - Or Self Service (for on-demand)

**Script:**
```bash
#!/bin/bash

# Run quick tests
/usr/local/bin/macos-test-suite \
  --config /usr/local/macos-test-suite/config/quick_tests.yaml \
  --artifacts-dir /var/log/macos-test-suite/artifacts \
  --log-level INFO

exit $?
```

#### Full Test Policy

Similar to above, but use `full_tests.yaml` configuration.

### 6. Create Teams Integration (Optional)

To post results to Microsoft Teams:

1. Get Teams webhook URL:
   - In Teams, go to channel
   - Click "..." > Connectors > Incoming Webhook
   - Configure and copy URL

2. Create extension attribute for webhook:
   - Navigate to **Computer Management** > **Extension Attributes**
   - Create new attribute: "test_suite_teams_webhook"
   - Set value to your webhook URL

3. Update test configurations to use webhook:

Edit `/usr/local/macos-test-suite/config/quick_tests.yaml` on devices:

```yaml
reporting:
  teams_webhook: "YOUR_WEBHOOK_URL"
```

Or use a configuration profile to deploy the config.

### 7. Monitoring and Results

#### View Logs

SSH into test device or use Jamf Remote:

```bash
# View latest run log
ls -lt /var/log/macos-test-suite/artifacts/
tail -f /var/log/macos-test-suite/artifacts/latest.log

# View specific test results
cat /var/log/macos-test-suite/artifacts/quick_tests_*/report_*.txt
```

#### Collect Artifacts

Create a policy to upload test artifacts:

**Script:**
```bash
#!/bin/bash

# Zip latest artifacts
LATEST_DIR=$(ls -td /var/log/macos-test-suite/artifacts/* | head -1)
zip -r /tmp/test-artifacts.zip "$LATEST_DIR"

# Upload to Jamf (adjust path as needed)
curl -X POST \
  -F "file=@/tmp/test-artifacts.zip" \
  "https://your-jamf-server/api/artifacts" \
  -H "Authorization: Bearer $API_TOKEN"

# Clean up
rm /tmp/test-artifacts.zip
```

## Smart Groups

Create smart groups for test result tracking:

### Failed Tests Group

**Criteria:**
```
Last Check-in: Less than 1 day ago
AND
Extension Attribute: test_suite_last_run IS "failed"
```

### Successful Tests Group

**Criteria:**
```
Last Check-in: Less than 1 day ago
AND
Extension Attribute: test_suite_last_run IS "passed"
```

## Automation with Jamf

### Daily Automated Testing

1. Create policy with **Recurring Check-in** trigger
2. Set frequency to "Once every day"
3. Set preferred time (e.g., 2:00 AM)

### Post-Imaging Testing

1. Create policy triggered by **Enrollment Complete**
2. Add test suite execution script
3. This validates device configuration after imaging

### CI/CD Integration

Use Jamf API to trigger tests after configuration changes:

```bash
# Trigger test policy via API
curl -X POST \
  "https://your-jamf-server/JSSResource/computercommands/command/PolicyById/id/YOUR_POLICY_ID" \
  -H "Authorization: Bearer $API_TOKEN"
```

## Troubleshooting

### Package Installation Fails

Check installation logs:
```bash
tail -f /var/log/macos-test-suite-install.log
```

Common issues:
- Python not installed (deploy Python package first)
- Network restrictions preventing uv download
- Insufficient permissions

### Tests Not Running

1. Verify package is installed:
   ```bash
   ls -la /usr/local/macos-test-suite/
   ```

2. Check TCC profile is deployed:
   ```bash
   profiles show | grep "macos-test-suite"
   ```

3. Manually run test:
   ```bash
   sudo -u testuser /usr/local/bin/macos-test-suite \
     --config /usr/local/macos-test-suite/config/quick_tests.yaml
   ```

### Permission Denied Errors

The TCC profile may not have taken effect:

1. Remove and reinstall profile
2. Restart device
3. Verify in System Settings > Privacy & Security

## Best Practices

1. **Test in Development First**: Deploy to a test group before production
2. **Monitor Results**: Set up Teams/Slack notifications for failures
3. **Regular Updates**: Keep test suite updated with new tests
4. **Artifact Retention**: Regularly clean old artifacts to save disk space
5. **Scheduled Testing**: Run comprehensive tests during off-hours

## Support

For issues or questions:
- Check the main [README.md](../README.md)
- Review logs in `/var/log/macos-test-suite/`
- Contact: [David Crosby](https://www.linkedin.com/in/david-bing-crosby/)
