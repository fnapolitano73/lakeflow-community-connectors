import pytest
import os
from pathlib import Path

from tests import test_suite
from tests.test_suite import LakeflowConnectTester
from tests.test_utils import load_config
from sources.alphavantage.alphavantage import LakeflowConnect


def test_alphavantage_connector():
    """Test the Alpha Vantage connector using the shared LakeflowConnect test suite.
    
    Note: Due to Alpha Vantage API rate limits, this test uses a minimal subset of
    tables by default. Set ALPHAVANTAGE_TEST_ALL=1 to test all tables (requires
    premium tier API key with sufficient rate limits).
    """
    # Inject the Alpha Vantage LakeflowConnect class into the shared test_suite namespace
    # so that LakeflowConnectTester can instantiate it.
    test_suite.LakeflowConnect = LakeflowConnect

    # Load connection-level configuration (api_key)
    parent_dir = Path(__file__).parent.parent
    config_path = parent_dir / "configs" / "dev_config.json"
    
    # Use minimal table config by default to avoid rate limits
    # Set ALPHAVANTAGE_TEST_ALL=1 to test all tables
    if os.environ.get("ALPHAVANTAGE_TEST_ALL", "0") == "1":
        table_config_path = parent_dir / "configs" / "dev_table_config.json"
    else:
        table_config_path = parent_dir / "configs" / "dev_table_config_minimal.json"

    config = load_config(config_path)
    table_config = load_config(table_config_path)

    # Create tester with the config and per-table options
    tester = LakeflowConnectTester(config, table_config)

    # Run all standard LakeflowConnect tests for this connector
    report = tester.run_all_tests()
    tester.print_report(report, show_details=True)

    # Assert that all tests passed
    assert report.passed_tests == report.total_tests, (
        f"Test suite had failures: {report.failed_tests} failed, "
        f"{report.error_tests} errors"
    )


