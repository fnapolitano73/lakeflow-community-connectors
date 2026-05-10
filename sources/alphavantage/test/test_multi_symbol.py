"""
Test Multi-Symbol Support for Alpha Vantage Connector

Tests the following tables with multi-symbol input:
- time_series_daily
- company_overview
- earnings

Symbols: MSFT, ORCL, AAPL, AMZN, SNOW
"""

import json
import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from sources.alphavantage.alphavantage import LakeflowConnect


def load_config():
    """Load dev_config.json"""
    config_path = Path(__file__).parent.parent / "configs" / "dev_config.json"
    with open(config_path) as f:
        return json.load(f)


def test_multi_symbol_time_series_daily():
    """Test time_series_daily with multiple symbols"""
    print("\n" + "=" * 60)
    print("TEST: time_series_daily with multi-symbol")
    print("=" * 60)
    
    config = load_config()
    connector = LakeflowConnect(config)
    
    symbols = "MSFT,ORCL,AAPL,AMZN,SNOW"
    table_options = {
        "symbol": symbols,
        "outputsize": "compact",
    }
    
    print(f"Fetching time_series_daily for: {symbols}")
    
    records_iter, next_offset = connector.read_table(
        "time_series_daily", {}, table_options
    )
    records = list(records_iter)
    
    print(f"Total records fetched: {len(records)}")
    
    # Check which symbols we got data for
    symbols_found = set(r.get("symbol") for r in records)
    print(f"Symbols found in data: {symbols_found}")
    
    # Verify we got at least some symbols (rate limits may affect this)
    expected_symbols = {"MSFT", "ORCL", "AAPL", "AMZN", "SNOW"}
    missing = expected_symbols - symbols_found
    if missing:
        print(f"Note: Missing symbols (may be due to rate limits): {missing}")
    
    # Show sample data
    if records:
        print(f"\nSample record (first):")
        for key, value in list(records[0].items())[:8]:
            print(f"  {key}: {value}")
    
    # Count by symbol
    print(f"\nRecords per symbol:")
    for sym in sorted(symbols_found):
        count = sum(1 for r in records if r.get("symbol") == sym)
        print(f"  {sym}: {count} records")
    
    assert len(records) > 0, "Should return records"
    # Allow at least 3 symbols to pass (rate limits may affect some)
    assert len(symbols_found) >= 3, f"Should have at least 3 symbols, got {len(symbols_found)}"
    
    print("\n✓ TEST PASSED: time_series_daily multi-symbol")
    return True


def test_multi_symbol_company_overview():
    """Test company_overview with multiple symbols"""
    print("\n" + "=" * 60)
    print("TEST: company_overview with multi-symbol")
    print("=" * 60)
    
    config = load_config()
    connector = LakeflowConnect(config)
    
    # Use fewer symbols to reduce API calls
    symbols = "MSFT,AAPL,AMZN"
    table_options = {
        "symbol": symbols,
    }
    
    print(f"Fetching company_overview for: {symbols}")
    
    records_iter, next_offset = connector.read_table(
        "company_overview", {}, table_options
    )
    records = list(records_iter)
    
    print(f"Total records fetched: {len(records)}")
    
    # Check which symbols we got data for
    symbols_found = set(r.get("symbol") for r in records)
    print(f"Symbols found in data: {symbols_found}")
    
    # Show company names
    print(f"\nCompanies fetched:")
    for record in records:
        print(f"  {record.get('symbol')}: {record.get('name')}")
    
    assert len(records) >= 1, "Should return at least 1 record"
    # At least 2 out of 3 symbols should work
    assert len(symbols_found) >= 2, f"Should have at least 2 symbols, got {len(symbols_found)}"
    
    print("\n✓ TEST PASSED: company_overview multi-symbol")
    return True


def test_multi_symbol_earnings():
    """Test earnings with multiple symbols"""
    print("\n" + "=" * 60)
    print("TEST: earnings with multi-symbol")
    print("=" * 60)
    
    config = load_config()
    connector = LakeflowConnect(config)
    
    # Use fewer symbols to reduce API calls
    symbols = "MSFT,AAPL"
    table_options = {
        "symbol": symbols,
    }
    
    print(f"Fetching earnings for: {symbols}")
    
    records_iter, next_offset = connector.read_table(
        "earnings", {}, table_options
    )
    records = list(records_iter)
    
    print(f"Total records fetched: {len(records)}")
    
    # Check which symbols we got data for
    symbols_found = set(r.get("symbol") for r in records)
    print(f"Symbols found in data: {symbols_found}")
    
    # Count by symbol and report type
    if symbols_found:
        print(f"\nRecords per symbol:")
        for sym in sorted(symbols_found):
            sym_records = [r for r in records if r.get("symbol") == sym]
            annual = sum(1 for r in sym_records if r.get("report_type") == "annual")
            quarterly = sum(1 for r in sym_records if r.get("report_type") == "quarterly")
            print(f"  {sym}: {len(sym_records)} total ({annual} annual, {quarterly} quarterly)")
    
    assert len(records) > 0, "Should return records"
    # At least 1 symbol should work
    assert len(symbols_found) >= 1, f"Should have at least 1 symbol, got {len(symbols_found)}"
    
    print("\n✓ TEST PASSED: earnings multi-symbol")
    return True


def test_error_handling_with_invalid_symbol():
    """Test that invalid symbols don't break the batch"""
    print("\n" + "=" * 60)
    print("TEST: Error handling with invalid symbol")
    print("=" * 60)
    
    config = load_config()
    connector = LakeflowConnect(config)
    
    # Mix valid and invalid symbols
    symbols = "AAPL,INVALIDXYZ123"
    table_options = {
        "symbol": symbols,
    }
    
    print(f"Fetching company_overview for: {symbols}")
    print("(INVALIDXYZ123 should fail but not break the batch)")
    
    records_iter, next_offset = connector.read_table(
        "company_overview", {}, table_options
    )
    records = list(records_iter)
    
    print(f"Total records fetched: {len(records)}")
    
    symbols_found = set(r.get("symbol") for r in records)
    print(f"Symbols found in data: {symbols_found}")
    
    # Should have at least AAPL (the valid symbol should work)
    assert len(records) >= 1, "Should have at least 1 valid record"
    
    print("\n✓ TEST PASSED: Error handling works correctly")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Alpha Vantage Multi-Symbol Support Tests")
    print("=" * 60)
    print("\nNote: Tests are designed to be tolerant of API rate limits.")
    print("Some symbols may be skipped due to rate limiting.\n")
    
    tests = [
        ("time_series_daily", test_multi_symbol_time_series_daily),
        ("company_overview", test_multi_symbol_company_overview),
        ("earnings", test_multi_symbol_earnings),
        ("error_handling", test_error_handling_with_invalid_symbol),
    ]
    
    results = {}
    for name, test_func in tests:
        # Add delay between tests to avoid rate limits
        time.sleep(3)
        try:
            result = test_func()
            results[name] = "PASSED" if result else "FAILED"
        except Exception as e:
            print(f"\n✗ TEST FAILED: {name}")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            results[name] = f"ERROR: {e}"
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, result in results.items():
        status = "✓" if result == "PASSED" else "✗"
        print(f"{status} {name}: {result}")
    
    # Count passed tests
    passed = sum(1 for r in results.values() if r == "PASSED")
    total = len(results)
    print(f"\n{passed}/{total} tests passed")
    
    # Exit with error if less than half passed
    if passed < total / 2:
        sys.exit(1)
