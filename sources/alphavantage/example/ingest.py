"""
Alpha Vantage Ingestion Pipeline Example

This example demonstrates how to ingest financial data from Alpha Vantage
using multi-symbol support. All symbols for each table type are loaded into
a single destination table.

Tables included:
1. time_series_daily - Daily OHLCV stock price data
2. company_overview - Fundamental company information
3. earnings - Quarterly and annual earnings data
4. sma - Simple Moving Average (50-day) technical indicator
5. global_quote - Real-time stock quotes

Multi-Symbol Feature:
    The connector supports comma-separated symbols (e.g., "MSFT,ORCL,AAPL").
    All data is combined into ONE destination table per source table type,
    with the 'symbol' column identifying each record.

Note: Alpha Vantage has rate limits. Free tier allows 5 requests/minute, 25/day.
      Consider using a premium tier for production workloads.

API Key:
    The API key is read from Databricks secrets using:
    dbutils.secrets.get("alpha_vantage_secrets", "api_key")
    
    Set up your secret scope before running:
    - Create a secret scope named "alpha_vantage_secrets"
    - Add a secret named "api_key" with your Alpha Vantage API key
"""

from pipeline.ingestion_pipeline import ingest
from libs.source_loader import get_register_function

# =============================================================================
# CONFIGURATION VARIABLES
# =============================================================================
# Connector source name
SOURCE_NAME = "alphavantage"

# Destination catalog and schema (update these for your environment)
DESTINATION_CATALOG = "fna_demo"
DESTINATION_SCHEMA = "bronze_alphavantage"

# Unity Catalog connection name (update with your connection name)
CONNECTION_NAME = "alphavantage_connection"

# Symbols to ingest - comma-separated string for multi-symbol support
# All symbols will be fetched and loaded into ONE table per source table type
SYMBOLS = "MSFT,ORCL,AAPL,AMZN,SNOW"

# API Key from Databricks secrets (set up your secret scope first)
# To set up: databricks secrets create-scope --scope alpha_vantage_secrets
# Then: databricks secrets put --scope alpha_vantage_secrets --key api_key

# Rate limit tier (optional) - determines requests per minute
# Options: "free", "premium_30", "premium_75", "premium_150", "premium_300", "premium_600", "premium_1200"
TIER = "premium_30"


# =============================================================================
# PIPELINE SPECIFICATION
# =============================================================================
# Each table uses the multi-symbol feature:
# - symbol="MSFT,ORCL,AAPL,AMZN,SNOW" fetches data for all 5 symbols
# - All data goes into ONE destination table (e.g., "time_series_daily")
# - The "symbol" column identifies which company each record belongs to
# =============================================================================

pipeline_spec = {
    "connection_name": CONNECTION_NAME,
    "objects": [
        # 1. Stock Time Series - Daily OHLCV prices for all symbols
        {
            "table": {
                "source_table": "time_series_daily",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "time_series_daily",
                "table_configuration": {
                    "tier": TIER,
                    "symbol": SYMBOLS,  # Multi-symbol: fetches all 5 stocks
                    "outputsize": "compact",  # "compact" = 100 days, "full" = 20+ years
                },
            }
        },
        # 2. Company Overview - Fundamental company data for all symbols
        {
            "table": {
                "source_table": "company_overview",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "company_overview",
                "table_configuration": {
                    "tier": TIER,
                    "symbol": SYMBOLS,  # Multi-symbol: fetches all 5 companies
                },
            }
        },
        # 3. Earnings - Quarterly and annual earnings for all symbols
        {
            "table": {
                "source_table": "earnings",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "earnings",
                "table_configuration": {
                    "tier": TIER,
                    "symbol": SYMBOLS,  # Multi-symbol: fetches all 5 companies
                },
            }
        },
        # 4. SMA (Simple Moving Average) - 50-day SMA for all symbols
        {
            "table": {
                "source_table": "sma",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "sma",
                "table_configuration": {
                    "tier": TIER,
                    "symbol": SYMBOLS,  # Multi-symbol: fetches all 5 stocks
                    "interval": "daily",
                    "time_period": "50",
                    "series_type": "close",
                },
            }
        },
        # 5. Global Quote - Real-time quotes for all symbols
        {
            "table": {
                "source_table": "global_quote",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "global_quote",
                "table_configuration": {
                    "tier": TIER,
                    "symbol": SYMBOLS,  # Multi-symbol: fetches all 5 stocks
                },
            }
        },
    ],
}


# =============================================================================
# EXECUTE INGESTION
# =============================================================================
# Dynamically import and register the LakeFlow source
register_lakeflow_source = get_register_function(SOURCE_NAME)
register_lakeflow_source(spark)

# Ingest the tables specified in the pipeline spec
ingest(spark, pipeline_spec)
