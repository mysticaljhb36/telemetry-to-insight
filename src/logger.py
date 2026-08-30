# =============================================================================
# Logging Configuration
# =============================================================================
"""
Central logging configuration for the telemetry-to-insight pipeline.

This module provides a consistent logging setup across the application.

It:
    1. Defines the project-level logs directory.
    2. Creates the logs directory when it does not already exist.
    3. Configures application-wide logging at INFO level.
    4. Appends pipeline activity to ``logs/pipeline.log``.
    5. Records timestamps, module names, severity levels and messages.
    6. Allows individual modules to create their own named loggers using
       ``logging.getLogger(__name__)``.

The configuration is applied when this module is imported, allowing the
pipeline entry point and supporting modules to share the same logging
configuration.
"""

import logging

from pathlib import Path


# Resolve the project root from the location of this module.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Define and create the directory used to persist application logs.
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


# Configure the root logger so that application modules share a consistent
# logging format and destination.
logging.basicConfig(

    # Persist pipeline activity to a central log file.
    filename=LOG_DIR / "pipeline.log",

    # Preserve previous pipeline runs by appending new log records.
    filemode="a",

    # Capture normal pipeline activity as well as warnings and errors.
    level=logging.INFO,

    # Include sufficient context to identify when, where and at what
    # severity each event occurred.
    format=(
        "%(asctime)s - "
        "%(name)s - "
        "%(levelname)s - "
        "%(message)s"
    ),

    # Ensure this configuration is applied consistently when development
    # environments such as Jupyter or Spyder have configured logging already.
    force=True
)


# Module-specific logger used when this file is executed directly.
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    # Simple standalone check that the logging configuration is operational.
    logger.info(
        "Logging configuration initialised successfully."
    )