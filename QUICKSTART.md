# MacMocker Quick Start

Get running in 5 minutes.

## Installation

```bash
# Clone the repository
git clone https://github.com/david-crosby/macmocker.git
cd macmocker

# Install dependencies
uv pip install -e .
```

## Run Your First Test

```bash
python3 main.py --config config/quick_tests.yaml
```

This runs basic network and Word tests. Results are saved to `~/macmocker_artifacts/`.

## View Results

```bash
cat ~/macmocker_artifacts/run_*/report_*.txt
```

## Run Full Test Suite

```bash
python3 main.py --config config/full_tests.yaml
```

This includes Word, Excel, and Outlook tests.

## Create Custom Configuration

```bash
cp config/quick_tests.yaml config/my_tests.yaml
```

Edit `my_tests.yaml` to enable/disable tests or change settings.

```yaml
tests:
  - module: "tests.network.network_test.NetworkTest"
    enabled: true
    timeout: 60
    urls:
      - "https://www.google.com"
```

Run your custom tests:

```bash
python3 main.py --config config/my_tests.yaml
```

## Common Options

```bash
# Debug mode
python3 main.py --config config/quick_tests.yaml --log-level DEBUG

# Custom artifacts location
python3 main.py --config config/quick_tests.yaml --artifacts-dir /tmp/results
```

## What Next?

- Read the full README for detailed documentation
- Check `deployment/JAMF_DEPLOYMENT.md` for Jamf Pro integration
- Look at test examples in `tests/applications/` to write your own tests

## Troubleshooting

### Permission Errors

Grant accessibility and screen recording permissions:
- System Preferences > Security & Privacy > Privacy
- Add Terminal to Accessibility and Screen Recording

### Module Not Found

Ensure you're in the macmocker directory and dependencies are installed:

```bash
cd macmocker
uv pip install -e .
```

### Tests Failing

Check logs with debug mode:

```bash
python3 main.py --config config/quick_tests.yaml --log-level DEBUG
```

## Support

David Crosby - [LinkedIn](https://www.linkedin.com/in/david-bing-crosby/)
