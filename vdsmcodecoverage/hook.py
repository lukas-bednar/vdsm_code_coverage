"""
This module is meant to be imported by vdsm in order to enable code coverage
"""
import os


def instrument(config=None):
    """
    enables code coverage, you can specify config file for coverage module
    """
    if config:
        os.environ['COVERAGE_PROCESS_START'] = config
    from coverage.control import process_startup
    process_startup()
