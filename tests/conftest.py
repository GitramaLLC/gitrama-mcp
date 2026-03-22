"""
Pytest configuration for Gitrama test suite.
"""
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests (requires gtr CLI installed)",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: marks tests requiring gtr CLI")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--integration"):
        skip_integration = pytest.mark.skip(reason="Need --integration flag to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
