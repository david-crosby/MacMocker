#!/usr/bin/env python3

import sys
import logging
import argparse
from pathlib import Path

from core.config_loader import ConfigLoader
from core.test_runner import TestRunner
from core.reporter import Reporter


def setup_logging(log_level: str):
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    parser = argparse.ArgumentParser(description='MacMocker - macOS Device Testing Suite')
    parser.add_argument(
        '--config',
        required=True,
        type=Path,
        help='Path to configuration file'
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )
    parser.add_argument(
        '--artifacts-dir',
        type=Path,
        help='Override artifacts directory'
    )

    args = parser.parse_args()

    setup_logging(args.log_level)
    logger = logging.getLogger("MacMocker")

    if not args.config.exists():
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(1)

    try:
        config = ConfigLoader(args.config)
        
        if args.artifacts_dir:
            config.config['artifacts_dir'] = str(args.artifacts_dir)

        logger.info(f"Starting {config.suite_name}")
        
        runner = TestRunner(config)
        results = runner.run_all_tests()
        
        reporter = Reporter(results, runner.artifacts_dir, config.reporting)
        reporter.generate_all_reports()
        
        summary = runner.summary
        logger.info(f"Tests completed: {summary['passed']}/{summary['total']} passed")
        
        if summary['failed'] > 0:
            sys.exit(1)
        
        sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
