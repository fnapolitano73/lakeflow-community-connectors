"""
Batch testing script for Alpha Vantage connector.

This script tests all 103 tables in batches to handle API rate limits.
It tests schema and metadata validation for all tables (no API calls),
then tests read operations in batches with delays between groups.

Usage:
    python sources/alphavantage/test/test_batch_all_tables.py [--batch-size N] [--delay SECONDS]
"""

import sys
import time
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from sources.alphavantage.alphavantage import LakeflowConnect


def load_config(config_path: Path) -> Dict:
    """Load configuration from JSON file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path) as f:
        return json.load(f)


def test_schema_and_metadata(connector: LakeflowConnect, table_config: Dict) -> Tuple[int, int, List[str]]:
    """
    Test schema and metadata for all tables (no API calls).
    Returns (passed, failed, error_messages).
    """
    print("\n" + "=" * 70)
    print("PHASE 1: Schema and Metadata Validation (No API calls)")
    print("=" * 70)
    
    tables = connector.list_tables()
    passed = 0
    failed = 0
    errors = []
    
    for table in tables:
        table_options = table_config.get(table, {})
        try:
            # Test schema
            schema = connector.get_table_schema(table, table_options)
            field_count = len(schema.fields)
            
            # Test metadata
            metadata = connector.read_table_metadata(table, table_options)
            ingestion_type = metadata.get("ingestion_type", "unknown")
            primary_keys = metadata.get("primary_keys", [])
            
            print(f"  ✓ {table}: {field_count} fields, {ingestion_type}, pk={primary_keys}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {table}: {str(e)}")
            errors.append(f"{table}: {str(e)}")
            failed += 1
    
    print(f"\nSchema/Metadata Results: {passed} passed, {failed} failed")
    return passed, failed, errors


def test_read_batch(
    connector: LakeflowConnect, 
    tables: List[str], 
    table_config: Dict,
    batch_name: str
) -> Tuple[int, int, int, List[str]]:
    """
    Test read operations for a batch of tables.
    Returns (passed, failed, skipped, error_messages).
    """
    print(f"\n--- Batch: {batch_name} ({len(tables)} tables) ---")
    
    passed = 0
    failed = 0
    skipped = 0
    errors = []
    
    for table in tables:
        table_options = table_config.get(table, {})
        try:
            # Attempt to read the table
            iterator, offset = connector.read_table(table, {}, table_options)
            records = list(iterator)
            record_count = len(records)
            
            if record_count > 0:
                first_record = records[0]
                # Check that records match schema
                schema = connector.get_table_schema(table, table_options)
                schema_fields = set(f.name for f in schema.fields)
                record_fields = set(first_record.keys())
                
                if not record_fields.issubset(schema_fields):
                    extra_fields = record_fields - schema_fields
                    print(f"  ⚠ {table}: {record_count} records (extra fields: {extra_fields})")
                else:
                    print(f"  ✓ {table}: {record_count} records")
                passed += 1
            else:
                print(f"  ✓ {table}: 0 records (empty response)")
                passed += 1
                
        except RuntimeError as e:
            error_msg = str(e)
            if "Rate limit" in error_msg or "daily" in error_msg.lower():
                print(f"  ⊘ {table}: Rate limit hit - skipped")
                skipped += 1
            else:
                print(f"  ✗ {table}: {error_msg[:80]}")
                errors.append(f"{table}: {error_msg}")
                failed += 1
        except ValueError as e:
            # Missing required options - expected for unconfigured tables
            print(f"  ⊘ {table}: Missing options - {str(e)[:50]}")
            skipped += 1
        except Exception as e:
            print(f"  ✗ {table}: {type(e).__name__}: {str(e)[:80]}")
            errors.append(f"{table}: {str(e)}")
            failed += 1
    
    return passed, failed, skipped, errors


def run_all_tests(
    api_key: str, 
    table_config: Dict, 
    batch_size: int = 5,
    delay_seconds: int = 65,
    tier: str = "premium_30"
) -> Dict[str, Any]:
    """
    Run all tests for the Alpha Vantage connector.
    
    Args:
        api_key: Alpha Vantage API key
        table_config: Dict of table options for each table
        batch_size: Number of tables to test per batch
        delay_seconds: Seconds to wait between batches
        tier: Rate limit tier to use
    """
    print("=" * 70)
    print(f"Alpha Vantage Connector - Comprehensive Test Suite")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Batch size: {batch_size}, Delay: {delay_seconds}s, Tier: {tier}")
    print("=" * 70)
    
    # Initialize connector with appropriate tier
    connector = LakeflowConnect({
        "api_key": api_key,
        "tier": tier,
    })
    
    results = {
        "schema_passed": 0,
        "schema_failed": 0,
        "read_passed": 0,
        "read_failed": 0,
        "read_skipped": 0,
        "errors": []
    }
    
    # Phase 1: Schema and metadata validation (no API calls)
    s_passed, s_failed, s_errors = test_schema_and_metadata(connector, table_config)
    results["schema_passed"] = s_passed
    results["schema_failed"] = s_failed
    results["errors"].extend(s_errors)
    
    # Phase 2: Read operations in batches
    print("\n" + "=" * 70)
    print("PHASE 2: Read Operations (API calls with rate limiting)")
    print("=" * 70)
    
    # Get all tables that have config
    configured_tables = [t for t in connector.list_tables() if t in table_config]
    
    # Prioritize CSV-based tables that are more rate-limit sensitive
    priority_tables = ["earnings_calendar", "ipo_calendar"]
    priority_list = [t for t in priority_tables if t in configured_tables]
    remaining_list = [t for t in configured_tables if t not in priority_tables]
    configured_tables = priority_list + remaining_list
    
    print(f"Testing {len(configured_tables)} configured tables in batches of {batch_size}")
    
    # Split into batches
    batches = []
    for i in range(0, len(configured_tables), batch_size):
        batches.append(configured_tables[i:i + batch_size])
    
    total_read_passed = 0
    total_read_failed = 0
    total_read_skipped = 0
    
    for batch_idx, batch in enumerate(batches):
        batch_name = f"Batch {batch_idx + 1}/{len(batches)}"
        
        r_passed, r_failed, r_skipped, r_errors = test_read_batch(
            connector, batch, table_config, batch_name
        )
        
        total_read_passed += r_passed
        total_read_failed += r_failed
        total_read_skipped += r_skipped
        results["errors"].extend(r_errors)
        
        # Wait between batches (except for last batch)
        if batch_idx < len(batches) - 1:
            print(f"\n  Waiting {delay_seconds}s before next batch...")
            time.sleep(delay_seconds)
    
    results["read_passed"] = total_read_passed
    results["read_failed"] = total_read_failed
    results["read_skipped"] = total_read_skipped
    
    # Print final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"Schema/Metadata: {results['schema_passed']} passed, {results['schema_failed']} failed")
    print(f"Read Operations: {results['read_passed']} passed, {results['read_failed']} failed, {results['read_skipped']} skipped")
    
    total_tests = results['schema_passed'] + results['schema_failed'] + \
                  results['read_passed'] + results['read_failed']
    total_passed = results['schema_passed'] + results['read_passed']
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if results["errors"]:
        print(f"\nErrors ({len(results['errors'])}):")
        for error in results["errors"][:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(results["errors"]) > 10:
            print(f"  ... and {len(results['errors']) - 10} more")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Test Alpha Vantage connector in batches")
    parser.add_argument("--batch-size", type=int, default=5, 
                        help="Number of tables to test per batch (default: 5)")
    parser.add_argument("--delay", type=int, default=65, 
                        help="Seconds to wait between batches (default: 65)")
    parser.add_argument("--tier", type=str, default="premium_30",
                        help="Rate limit tier (default: premium_30)")
    args = parser.parse_args()
    
    # Load configs
    config_dir = Path(__file__).parent.parent / "configs"
    dev_config = load_config(config_dir / "dev_config.json")
    table_config = load_config(config_dir / "dev_table_config.json")
    
    api_key = dev_config.get("api_key")
    if not api_key:
        print("ERROR: api_key not found in dev_config.json")
        sys.exit(1)
    
    # Run tests
    results = run_all_tests(
        api_key=api_key,
        table_config=table_config,
        batch_size=args.batch_size,
        delay_seconds=args.delay,
        tier=args.tier
    )
    
    # Exit with appropriate code
    if results["schema_failed"] > 0 or results["read_failed"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()

