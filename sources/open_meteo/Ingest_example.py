"""
Open-Meteo Ingestion Pipeline Example

This example demonstrates how to ingest weather data from Open-Meteo API
using the Lakeflow Community Connector. It showcases different table types
and SCD (Slowly Changing Dimension) patterns.

Tables included:
1. weather_forecast_hourly - Hourly weather forecasts (APPEND_ONLY for time-series data)
2. weather_forecast_daily - Daily weather forecasts (APPEND_ONLY for time-series data)
3. air_quality_hourly - Hourly air quality data (APPEND_ONLY for monitoring trends)
4. marine_weather_hourly - Hourly marine/ocean forecasts (SCD_TYPE_1 for latest conditions)
5. marine_weather_daily - Daily marine/ocean forecasts (SCD_TYPE_1 for latest conditions)
6. historical_weather_daily - Historical daily weather (SCD_TYPE_2 for historical analysis)
7. geocoding - Location search and coordinate lookup (SCD_TYPE_1 for location reference data)

Multi-Location Support:
    The connector supports comma-separated latitude/longitude pairs
    (e.g., "52.52,48.85,40.71" for Berlin, Paris, NYC).
    All data is combined into ONE destination table per source table type,
    with latitude/longitude columns identifying each location.

API Tiers:
    - Free tier: 600 req/min, 10K req/day (no API key needed)
    - Commercial tiers: Higher limits with API key (optional)

    For production workloads with frequent updates, consider a commercial tier
    from https://open-meteo.com/en/pricing

Note:
    - Forecast tables (weather, air quality, marine) use APPEND_ONLY to track
      forecast changes over time
    - Historical tables use date ranges (start_date, end_date) for backfilling
    - Coordinates must be provided either at connection or table level
"""

from pipeline.ingestion_pipeline import ingest
from libs.source_loader import get_register_function

# =============================================================================
# CONFIGURATION VARIABLES
# =============================================================================
# Connector source name
SOURCE_NAME = "open_meteo"

# Destination catalog and schema (update these for your environment)
DESTINATION_CATALOG = "weather_analytics"
DESTINATION_SCHEMA = "bronze_open_meteo"

# Unity Catalog connection name (update with your connection name)
#
# IMPORTANT: The connection must be created BEFORE running this pipeline.
#
# The connection stores authentication and configuration parameters:
#   - api_key (optional): Your commercial API key for paid tiers
#   - tier (optional): "free", "standard", "professional", or "enterprise"
#   - latitude (optional): Default latitude if not specified per table
#   - longitude (optional): Default longitude if not specified per table
#   - timeout (optional): Request timeout in seconds
#
# Create the connection via:
#   1. Databricks UI:
#      Catalog → Connections → Create Connection → Lakeflow Community Connector
#
#   2. SQL:
#      CREATE CONNECTION open_meteo_connection
#      TYPE lakeflow_community_connector
#      OPTIONS (
#        api_key '<your-key>',
#        tier 'standard',
#        externalOptionsAllowList 'latitude,longitude,variables,start_date,end_date,timezone,name,count,language'
#      );
#
#   3. Databricks CLI:
#      databricks connections create --name open_meteo_connection \
#        --connection-type lakeflow_community_connector \
#        --options '{"api_key":"<your-key>","tier":"standard"}'
#
# See README.md "Create a Unity Catalog Connection" section for detailed examples.
CONNECTION_NAME = "open_meteo_connection"

# Location coordinates - Multi-location example
# Berlin, Germany
BERLIN_LAT = "52.52"
BERLIN_LON = "13.41"

# Paris, France
PARIS_LAT = "48.85"
PARIS_LON = "2.35"

# New York City, USA
NYC_LAT = "40.71"
NYC_LON = "-74.01"

# Multi-location coordinates (comma-separated)
# All locations will be fetched in a single API call and loaded into ONE table
MULTI_LOCATIONS_LAT = f"{BERLIN_LAT},{PARIS_LAT},{NYC_LAT}"
MULTI_LOCATIONS_LON = f"{BERLIN_LON},{PARIS_LON},{NYC_LON}"

# API Configuration (optional - omit for free tier)
# Set tier to "standard", "professional", or "enterprise" if using commercial API
# API_KEY = dbutils.secrets.get("open_meteo_secrets", "api_key")  # Uncomment if using commercial tier
TIER = "free"  # Options: "free", "standard", "professional", "enterprise"

# Date range for historical data backfill
HISTORICAL_START_DATE = "2024-01-01"
HISTORICAL_END_DATE = "2024-12-31"


# =============================================================================
# PIPELINE SPECIFICATION
# =============================================================================
# This example demonstrates different SCD types and use cases:
#
# APPEND_ONLY:
#   - Used for time-series forecast data where you want to track how forecasts
#     change over time
#   - New records are always appended; old forecasts are preserved
#   - Useful for forecast accuracy analysis
#
# SCD_TYPE_1:
#   - Used for "current state" tables where you only care about latest values
#   - Updates overwrite existing records based on primary keys
#   - Useful for dashboards showing current conditions
#
# SCD_TYPE_2:
#   - Used for historical tracking with full audit trail
#   - Maintains version history with start/end timestamps
#   - Useful for compliance and historical analysis
# =============================================================================

pipeline_spec = {
    "connection_name": CONNECTION_NAME,
    "objects": [
        # 1. Hourly Weather Forecasts - APPEND_ONLY
        # Captures forecast evolution over time for accuracy analysis
        # Each pipeline run appends new forecast data
        {
            "table": {
                "source_table": "weather_forecast_hourly",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "weather_forecast_hourly",
                "table_configuration": {
                    "scd_type": "APPEND_ONLY",
                    "latitude": MULTI_LOCATIONS_LAT,  # Multi-location: Berlin, Paris, NYC
                    "longitude": MULTI_LOCATIONS_LON,
                    "variables": "temperature_2m,precipitation,wind_speed_10m,relative_humidity_2m,pressure_msl",
                },
            }
        },

        # 2. Daily Weather Forecasts - APPEND_ONLY
        # Tracks daily forecast trends across multiple cities
        {
            "table": {
                "source_table": "weather_forecast_daily",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "weather_forecast_daily",
                "table_configuration": {
                    "scd_type": "APPEND_ONLY",
                    "latitude": MULTI_LOCATIONS_LAT,
                    "longitude": MULTI_LOCATIONS_LON,
                    "variables": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
                },
            }
        },

        # 3. Air Quality Hourly - APPEND_ONLY
        # Environmental monitoring with historical tracking
        # Tracks air quality changes over time for pollution analysis
        {
            "table": {
                "source_table": "air_quality_hourly",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "air_quality_hourly",
                "table_configuration": {
                    "scd_type": "APPEND_ONLY",
                    "latitude": MULTI_LOCATIONS_LAT,
                    "longitude": MULTI_LOCATIONS_LON,
                    "variables": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone,european_aqi,us_aqi",
                },
            }
        },

        # 4. Marine Weather Hourly - SCD_TYPE_1
        # Current ocean conditions for marine operations
        # Always overwrites with latest forecast for operational dashboards
        {
            "table": {
                "source_table": "marine_weather_hourly",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "marine_weather_hourly",
                "table_configuration": {
                    "scd_type": "SCD_TYPE_1",
                    "latitude": "59.91",  # Oslo, Norway (coastal city)
                    "longitude": "10.75",
                    "variables": "wave_height,wave_direction,sea_surface_temperature,ocean_current_velocity",
                },
            }
        },

        # 5. Marine Weather Daily - SCD_TYPE_1
        # Daily marine conditions summary
        {
            "table": {
                "source_table": "marine_weather_daily",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "marine_weather_daily",
                "table_configuration": {
                    "scd_type": "SCD_TYPE_1",
                    "latitude": "59.91",  # Oslo, Norway
                    "longitude": "10.75",
                    "variables": "wave_height_max,wave_direction_dominant,wave_period_max",
                },
            }
        },

        # 6. Historical Weather Daily - SCD_TYPE_2
        # Historical backfill with full version tracking
        # Maintains audit trail if historical data is ever corrected/updated
        {
            "table": {
                "source_table": "historical_weather_daily",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "historical_weather_daily",
                "table_configuration": {
                    "scd_type": "SCD_TYPE_2",
                    "latitude": BERLIN_LAT,  # Single location for historical analysis
                    "longitude": BERLIN_LON,
                    "start_date": HISTORICAL_START_DATE,
                    "end_date": HISTORICAL_END_DATE,
                    "variables": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
                },
            }
        },

        # 7. Geocoding - SCD_TYPE_1
        # Location search for discovering coordinates of cities/places
        # Useful for building location reference tables or discovering coordinates
        # Note: Does NOT require latitude/longitude - uses location name instead
        {
            "table": {
                "source_table": "geocoding",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "locations_geocoding",
                "table_configuration": {
                    "scd_type": "SCD_TYPE_1",
                    "name": "Berlin",  # Location name to search
                    "count": "10",  # Number of results to return
                    "language": "en",  # Result language
                },
            }
        },

        # 8. Historical Weather Hourly - SCD_TYPE_2 (Optional - commented out by default)
        # Uncomment for detailed hourly historical backfill
        # WARNING: Large date ranges generate many API calls
        # {
        #     "table": {
        #         "source_table": "historical_weather_hourly",
        #         "destination_catalog": DESTINATION_CATALOG,
        #         "destination_schema": DESTINATION_SCHEMA,
        #         "destination_table": "historical_weather_hourly",
        #         "table_configuration": {
        #             "scd_type": "SCD_TYPE_2",
        #             "latitude": BERLIN_LAT,
        #             "longitude": BERLIN_LON,
        #             "start_date": "2024-11-01",  # Use shorter date range for hourly data
        #             "end_date": "2024-11-30",
        #             "variables": "temperature_2m,precipitation,wind_speed_10m,pressure_msl",
        #         },
        #     }
        # },
    ],
}


# =============================================================================
# SCD TYPE USAGE GUIDE
# =============================================================================
#
# When to use each SCD type:
#
# APPEND_ONLY:
#   ✓ Time-series forecast data (track forecast accuracy over time)
#   ✓ Event logs and audit trails
#   ✓ Sensor readings and measurements
#   ✓ Any data where you need complete historical record
#   ✗ Current state dashboards (creates duplicates)
#   ✗ Reference data that changes infrequently
#
# SCD_TYPE_1:
#   ✓ Current state/snapshot tables (latest conditions only)
#   ✓ Operational dashboards (real-time views)
#   ✓ Reference data with infrequent updates (e.g., geocoding/location lookups)
#   ✓ When storage optimization is critical
#   ✗ Historical analysis (loses previous values)
#   ✗ Audit requirements (no change tracking)
#   ✗ Forecast accuracy studies (need historical forecasts)
#
# Example: Geocoding table uses SCD_TYPE_1 because location coordinates rarely change,
#          and you typically only need the current/latest coordinates for each location.
#
# SCD_TYPE_2:
#   ✓ Compliance and audit requirements
#   ✓ Historical analysis with version tracking
#   ✓ Data quality monitoring (track corrections)
#   ✓ Dimensional modeling for analytics
#   ✗ High-velocity streaming data (overhead cost)
#   ✗ When only current state matters
#   ✗ Storage-constrained environments
#
# =============================================================================


# =============================================================================
# RATE LIMITING CONSIDERATIONS
# =============================================================================
#
# Free Tier Limits:
#   - 600 requests per minute
#   - 10,000 requests per day
#   - 300,000 requests per month
#
# This pipeline makes 7 API requests per run (one per active table):
#   - 3 multi-location tables (Berlin, Paris, NYC combined in one request each)
#   - 2 single-location marine tables (Oslo)
#   - 1 historical table (Berlin with date range)
#   - 1 geocoding table (location search)
#
# Recommended Schedule for Free Tier:
#   - Hourly runs: ~168 requests/day (7 tables × 24 hours) ✓ Within limits
#   - Every 6 hours: ~28 requests/day ✓ Conservative approach
#   - Every 12 hours: ~12 requests/day ✓ Most conservative
#
# For Commercial Tier:
#   - Can run every 15 minutes or more frequently
#   - See https://open-meteo.com/en/pricing for tier details
#
# =============================================================================


# =============================================================================
# EXECUTE INGESTION
# =============================================================================
# Dynamically import and register the LakeFlow source
register_lakeflow_source = get_register_function(SOURCE_NAME)
register_lakeflow_source(spark)

# Ingest the tables specified in the pipeline spec
ingest(spark, pipeline_spec)
