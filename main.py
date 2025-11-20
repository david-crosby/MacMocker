#!/usr/bin/env python3
"""
MacMocker
Main entry point for running macOS device tests
"""

import sys
import logging
from pathlib import Path
import argparse
from datetime import datetime


def setup_logging(log_level: str, log_file: Path):
    """Configure logging for the test suite"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file)
    ]
    
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=handlers
    )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MacMocker - Interactive macOS device testing for CI/CD workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "-c", "--config",
        type=Path,
        required=True,
        help="Path to test configuration YAML file"
    )
    
    parser.add_argument(
        "-a", "--artifacts-dir",
        type=Path,
        default=Path.home() / "macmocker_artifacts",
        help="Base directory for test artifacts (default: ~/macmocker_artifacts)"
    )
    
    parser.add_argument(
        "-l", "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="MacMocker v0.1.0"
    )
    
    args = parser.parse_args()
    
    if not args.config.exists():
        print(f"Error: Configuration file not found: {args.config}")
        return 1
    
    args.artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = args.artifacts_dir / f"macmocker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    setup_logging(args.log_level, log_file)
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("MacMocker Starting")
    logger.info("=" * 80)
    logger.info(f"Configuration: {args.config}")
    logger.info(f"Artifacts directory: {args.artifacts_dir}")
    logger.info(f"Log level: {args.log_level}")
    
    try:
        from core.test_runner import TestRunner
        
        runner = TestRunner(args.config, args.artifacts_dir)
        exit_code = runner.run()
        
        logger.info("=" * 80)
        logger.info(f"Test suite completed with exit code: {exit_code}")
        logger.info("=" * 80)
        
        return exit_code
        
    except KeyboardInterrupt:
        logger.warning("Test suite interrupted by user")
        return 130
    except Exception as e:
        logger.exception("Fatal error running test suite")
        return 1


if __name__ == "__main__":
    sys.exit(main())
