# Changelog

All notable changes to MacMocker will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-11-20

### Added

- Initial release of MacMocker
- Core test framework with base test class
- Modular test architecture supporting custom test modules
- YAML-based configuration system
- Network connectivity and performance testing module
- Application launch and readiness verification module
- Microsoft Word comprehensive testing module
- Microsoft Excel comprehensive testing module
  - Create workbooks with data
  - Save and reopen files
  - Edit cells and add formulas
  - Full validation workflow
- Microsoft Outlook email testing module
  - Create and send test emails
  - Verify email receipt
  - Inbox synchronisation
  - Automatic cleanup of test emails
- Automated screenshot capture on test failures
- System log monitoring for application errors
- Comprehensive reporting in text and JSON formats
- Microsoft Teams webhook integration
- Custom API result posting
- Jamf Pro deployment support with TCC configuration profile
- GitHub Actions workflow for CI/CD
- Sequential test execution with configurable delays
- Graceful interrupt handling
- Artifacts directory management
- Quick test configuration (5 minutes)
- Full test configuration (1 day) including Office apps
- Extensive documentation including:
  - README with usage examples
  - Jamf Pro deployment guide
  - Configuration examples
  - Development guidelines

### Configuration

- Support for test-level timeout configuration
- Support for global suite timeout
- Configurable artifacts retention
- Flexible test enabling/disabling
- Custom error pattern matching
- Ready state verification options
- Excel test data and header configuration
- Outlook email parameters and receipt verification settings

### Testing

- Network URL accessibility testing
- DNS resolution testing
- Connection speed testing
- Application window visibility verification
- Menu bar loading verification
- Crash dialogue detection
- Process monitoring and verification
- Log-based error detection
- Microsoft Office AppleScript automation
- Email send and receive verification

### Deployment

- Package builder script for .pkg creation
- TCC configuration profile for permissions
- Installation script with dependency management
- Support for uv package manager
- Bundle ID: uk.co.bing-bong.macmocker

### Infrastructure

- Logging to both console and file
- Exit codes for CI/CD integration
- Artifact cleanup and retention policies
- Python type hints throughout codebase
- Conventional Commits for version control
- British English spelling

## [Unreleased]

### Planned

- Additional test modules for system preferences
- Login window automation
- FileVault status verification
- Disk space monitoring test
- Memory usage test
- CPU performance benchmarking
- Harness CI/CD workflow examples
- Video recording of test sessions
- Parallel test execution option
- Test retry logic for flaky tests
- Enhanced Teams notifications with detailed results
- Slack webhook integration
- Email notification support
- PowerPoint testing module
- Teams desktop application testing
- OneDrive synchronisation testing
