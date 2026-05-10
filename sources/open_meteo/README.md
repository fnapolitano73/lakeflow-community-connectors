# Lakeflow Open-Meteo Community Connector

This documentation provides setup instructions and reference information for the Open-Meteo source connector.

The Lakeflow Open-Meteo Connector allows you to extract weather forecasts, historical weather data, air quality information, marine weather data, and location/geocoding data from Open-Meteo APIs and load it into your data lake or warehouse. This connector supports both free and commercial API tiers with automatic rate limiting and efficient data synchronization.

## Prerequisites

- **Open-Meteo API Access**:
  - Free tier available without registration for basic weather data
  - Commercial API key required for higher rate limits, enterprise features, and guaranteed availability
- **Location Coordinates**: Latitude and longitude values for the locations you want to monitor
- **Network Access**: The environment running the connector must be able to reach Open-Meteo API endpoints
- **Lakeflow / Databricks Environment**: A workspace where you can register a Lakeflow community connector and run ingestion pipelines

## Setup

### Required Connection Parameters

Provide the following **connection-level** options when configuring the connector:

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `latitude` | string | No* | Default latitude for weather queries (can be overridden per table) | `52.52` (Berlin) |
| `longitude` | string | No* | Default longitude for weather queries (can be overridden per table) | `13.41` (Berlin) |
| `api_key` | string | No | Commercial API key for paid tiers. Omit for free tier. | `your-api-key-here` |
| `tier` | string | No | Rate limit tier: `free`, `standard`, `professional`, or `enterprise`. Auto-detected based on `api_key` presence. | `standard` |
| `requests_per_minute` | integer | No | Override default per-minute rate limit for custom configurations | `1000` |
| `requests_per_day` | integer | No | Override default daily rate limit for custom configurations | `50000` |
| `timeout` | integer | No | Request timeout in seconds (default: 30) | `60` |
| `externalOptionsAllowList` | string | Yes | Comma-separated list of table-specific option names that can be passed through | `latitude,longitude,variables,start_date,end_date,timezone,name,count,language` |

**Note**:
- Either `latitude` and `longitude` must be specified at connection level OR provided per table via table options.
- The `geocoding` table does NOT require `latitude`/`longitude` - it uses `name`, `count`, and `language` instead.

### Multi-Location Support

The connector supports querying multiple locations in a single request by providing comma-separated values:

```
latitude: "52.52,48.85,40.71"
longitude: "13.41,2.35,-74.01"
```

This will return data for Berlin, Paris, and New York City in a single API call, which is more efficient than multiple separate requests.

### Rate Limit Tiers

Open-Meteo offers different rate limit tiers:

| Tier | Per Minute | Per Day | Per Month | Cost |
|------|------------|---------|-----------|------|
| **Free** | 600 | 10,000 | 300,000 | Free |
| **Standard** | Unlimited* | Unlimited* | 1,000,000 | Paid |
| **Professional** | Unlimited* | Unlimited* | 5,000,000 | Paid |
| **Enterprise** | Unlimited* | Unlimited* | 50,000,000 | Paid |

*Note: Unlimited means no per-minute/per-day limits, but monthly caps still apply.

The connector automatically enforces rate limits with a sliding window algorithm and exponential backoff retry logic.

### Obtaining API Access

**For Free Tier:**
- No registration required
- Simply omit the `api_key` parameter when configuring the connector
- Subject to free tier rate limits and availability

**For Commercial Tiers:**
1. Visit [open-meteo.com](https://open-meteo.com/en/pricing)
2. Choose a subscription plan (Standard, Professional, or Enterprise)
3. Register and obtain your API key
4. Use the API key in the `api_key` connection parameter
5. Access commercial API endpoints with higher rate limits and guaranteed uptime

### Create a Unity Catalog Connection

The API key and other connection parameters are configured **once** when creating the Unity Catalog connection. They are NOT specified per table.

#### Via Databricks UI

1. Navigate to **Catalog → Connections** in Databricks workspace
2. Click **Create Connection**
3. Select **Lakeflow Community Connector** as connection type
4. Enter connection properties:
   - **Name**: `open_meteo_connection` (or your choice)
   - **api_key**: Your commercial API key (optional - omit for free tier)
   - **latitude**: Default latitude (optional)
   - **longitude**: Default longitude (optional)
   - **tier**: `standard`, `professional`, or `enterprise` (optional)
   - **externalOptionsAllowList**: `latitude,longitude,variables,start_date,end_date`

Alternatively, follow the **Lakeflow Community Connector** UI flow from the **Add Data** page.

#### Via SQL

**Free Tier Connection (no API key):**

```sql
CREATE CONNECTION open_meteo_free
TYPE lakeflow_community_connector
OPTIONS (
  latitude '52.52',
  longitude '13.41',
  externalOptionsAllowList 'latitude,longitude,variables,start_date,end_date'
);
```

**Commercial Tier Connection (with API key):**

```sql
CREATE CONNECTION open_meteo_commercial
TYPE lakeflow_community_connector
OPTIONS (
  api_key '<your-commercial-api-key-here>',
  tier 'standard',
  latitude '52.52',
  longitude '13.41',
  externalOptionsAllowList 'latitude,longitude,variables,start_date,end_date'
);
```

#### Securing Your API Key

**Never hardcode API keys in SQL or configuration files.**

**Use Databricks Secrets:**

```sql
-- First, create a secret scope (via Databricks CLI or UI)
-- databricks secrets create-scope --scope open_meteo_secrets
-- databricks secrets put --scope open_meteo_secrets --key api_key

-- Then reference the secret in your connection
CREATE CONNECTION open_meteo_commercial
TYPE lakeflow_community_connector
OPTIONS (
  api_key secret('open_meteo_secrets', 'api_key'),
  tier 'standard',
  externalOptionsAllowList 'latitude,longitude,variables,start_date,end_date'
);
```

The connection can also be created using the standard Unity Catalog API.

## Supported Objects

The Open-Meteo connector exposes the following tables:

- `weather_forecast_hourly` - Hourly weather forecasts (up to 16 days)
- `weather_forecast_daily` - Daily weather forecasts (up to 16 days)
- `historical_weather_hourly` - Historical hourly weather data (from 1940 onwards)
- `historical_weather_daily` - Historical daily weather data (from 1940 onwards)
- `air_quality_hourly` - Hourly air quality forecasts (up to 7 days)
- `marine_weather_hourly` - Hourly marine/ocean forecasts (up to 8 days)
- `marine_weather_daily` - Daily marine/ocean forecasts (up to 8 days)
- `geocoding` - Location search and coordinate lookup

### Object Summary, Primary Keys, and Ingestion Mode

| Table | Description | Ingestion Type | Primary Key | Incremental Cursor |
|-------|-------------|----------------|-------------|-------------------|
| `weather_forecast_hourly` | Hourly weather forecasts (16 days) | `append` | `["latitude", "longitude", "time"]` | `time` |
| `weather_forecast_daily` | Daily weather forecasts (16 days) | `append` | `["latitude", "longitude", "time"]` | `time` |
| `historical_weather_hourly` | Historical hourly weather | `snapshot` | `["latitude", "longitude", "time"]` | n/a (full refresh) |
| `historical_weather_daily` | Historical daily weather | `snapshot` | `["latitude", "longitude", "time"]` | n/a (full refresh) |
| `air_quality_hourly` | Hourly air quality forecasts (7 days) | `append` | `["latitude", "longitude", "time"]` | `time` |
| `marine_weather_hourly` | Hourly marine forecasts (8 days) | `append` | `["latitude", "longitude", "time"]` | `time` |
| `marine_weather_daily` | Daily marine forecasts (8 days) | `append` | `["latitude", "longitude", "time"]` | `time` |
| `geocoding` | Location search by name | `snapshot` | `["id"]` | n/a (full refresh) |

**Note**:
- **Forecast tables** (weather_forecast, air_quality, marine_weather) use `append` ingestion and always fetch the latest forecast. The offset is managed automatically.
- **Historical tables** require explicit `start_date` and `end_date` in table options and use `snapshot` ingestion for full refresh of the specified date range.

### Required and Optional Table Options

Table-specific options are passed via the pipeline spec under `table` in `objects`:

**Common Options for All Tables:**

| Option | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| `latitude` | string | Yes* | Latitude(s) for weather data (comma-separated for multiple locations) | `52.52` or `52.52,48.85` |
| `longitude` | string | Yes* | Longitude(s) for weather data (comma-separated for multiple locations) | `13.41` or `13.41,2.35` |
| `variables` | string | No | Comma-separated list of weather variables to retrieve. Uses sensible defaults if omitted. | `temperature_2m,precipitation,wind_speed_10m` |

**Options for Historical Tables Only:**

| Option | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| `start_date` | string | Yes | Start date for historical data (ISO 8601 format: YYYY-MM-DD) | `2024-01-01` |
| `end_date` | string | Yes | End date for historical data (ISO 8601 format: YYYY-MM-DD) | `2024-12-31` |

*Note: `latitude` and `longitude` are required either at connection level or per table.

### Default Variables by Table

If you don't specify custom variables, each table uses these defaults:

**Weather Forecast Hourly:**
- `temperature_2m`, `relative_humidity_2m`, `precipitation`, `rain`, `snowfall`
- `weather_code`, `pressure_msl`, `cloud_cover`, `wind_speed_10m`, `wind_direction_10m`

**Weather Forecast Daily:**
- `weather_code`, `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`
- `rain_sum`, `snowfall_sum`, `wind_speed_10m_max`, `wind_direction_10m_dominant`

**Historical Weather Hourly:**
- Same as Weather Forecast Hourly

**Historical Weather Daily:**
- Same as Weather Forecast Daily

**Air Quality Hourly:**
- `pm10`, `pm2_5`, `carbon_monoxide`, `nitrogen_dioxide`, `sulphur_dioxide`
- `ozone`, `european_aqi`, `us_aqi`

**Marine Weather Hourly:**
- `wave_height`, `wave_direction`, `wave_period`, `sea_surface_temperature`
- `ocean_current_velocity`, `ocean_current_direction`

**Marine Weather Daily:**
- `wave_height_max`, `wave_direction_dominant`, `wave_period_max`

### Schema Highlights

All tables share a common structure with location and time fields, plus variable-specific data:

**Common Fields (All Tables):**
- `latitude` (DOUBLE) - Location latitude
- `longitude` (DOUBLE) - Location longitude
- `time` (STRING) - Timestamp in ISO 8601 format (hourly: `2024-01-15T14:00`, daily: `2024-01-15`)
- `elevation` (DOUBLE) - Elevation above sea level in meters
- `timezone` (STRING) - Timezone identifier (e.g., `Europe/Berlin`)
- `timezone_abbreviation` (STRING) - Timezone abbreviation (e.g., `CET`)
- `utc_offset_seconds` (LONG) - UTC offset in seconds

**Weather-Specific Fields:**
- Temperature fields: `DOUBLE` (Celsius)
- Precipitation fields: `DOUBLE` (mm)
- Wind fields: speed in `DOUBLE` (km/h), direction in `LONG` (degrees)
- Pressure: `DOUBLE` (hPa)
- Humidity: `DOUBLE` (%)
- Cloud cover: `DOUBLE` (%)
- Weather code: `LONG` (WMO code)

**Air Quality Fields:**
- Particulate matter: `DOUBLE` (μg/m³)
- Gas concentrations: `DOUBLE` (μg/m³)
- Air quality indices: `LONG` (scale values)

**Marine Weather Fields:**
- Wave height: `DOUBLE` (meters)
- Wave direction: `LONG` (degrees)
- Wave period: `DOUBLE` (seconds)
- Sea temperature: `DOUBLE` (Celsius)
- Ocean current velocity: `DOUBLE` (m/s)
- Ocean current direction: `LONG` (degrees)

**Geocoding Fields:**
- Location identification: `id` (LONG), `name` (STRING)
- Coordinates: `latitude` (DOUBLE), `longitude` (DOUBLE), `elevation` (DOUBLE)
- Administrative boundaries: `country` (STRING), `admin1-4` (STRING, hierarchical regions)
- Metadata: `feature_code` (STRING), `timezone` (STRING), `population` (LONG), `postcodes` (ARRAY<STRING>)

Full schemas are defined by the connector and documented in [open_meteo_api_doc.md](open_meteo_api_doc.md).

## Data Type Mapping

Open-Meteo JSON fields are mapped to Spark types as follows:

| Open-Meteo Type | Databricks Type | Notes |
|-----------------|-----------------|-------|
| Float (temperatures, precipitation) | DOUBLE | All numeric measurements |
| Integer (codes, directions) | LONG | Weather codes, wind direction, timestamps |
| String (timestamps) | STRING | ISO 8601 datetime strings |
| String (timezone) | STRING | Timezone identifiers and abbreviations |

## How to Run

### Step 1: Clone/Copy the Source Connector Code

Use the Lakeflow Community Connector UI to copy or reference the Open-Meteo connector source in your workspace. This will place the connector code (`open_meteo.py`) in a project path that Lakeflow can load.

### Step 2: Configure Your Pipeline

In your pipeline code (e.g., `ingestion_pipeline.py`), configure a `pipeline_spec` that references:

- A **Unity Catalog connection** that uses this Open-Meteo connector
- One or more **tables** to ingest, each with required table options

**Example 1: Weather Forecasts for a Single Location**

```json
{
  "pipeline_spec": {
    "connection_name": "open_meteo_connection",
    "object": [
      {
        "table": {
          "source_table": "weather_forecast_hourly",
          "latitude": "52.52",
          "longitude": "13.41",
          "variables": "temperature_2m,precipitation,wind_speed_10m"
        }
      },
      {
        "table": {
          "source_table": "weather_forecast_daily",
          "latitude": "52.52",
          "longitude": "13.41"
        }
      }
    ]
  }
}
```

**Example 2: Multiple Locations (Berlin, Paris, New York)**

```json
{
  "pipeline_spec": {
    "connection_name": "open_meteo_connection",
    "object": [
      {
        "table": {
          "source_table": "weather_forecast_hourly",
          "latitude": "52.52,48.85,40.71",
          "longitude": "13.41,2.35,-74.01"
        }
      }
    ]
  }
}
```

**Example 3: Historical Weather Data**

```json
{
  "pipeline_spec": {
    "connection_name": "open_meteo_connection",
    "object": [
      {
        "table": {
          "source_table": "historical_weather_daily",
          "latitude": "52.52",
          "longitude": "13.41",
          "start_date": "2024-01-01",
          "end_date": "2024-12-31"
        }
      }
    ]
  }
}
```

**Example 4: Air Quality Monitoring**

```json
{
  "pipeline_spec": {
    "connection_name": "open_meteo_connection",
    "object": [
      {
        "table": {
          "source_table": "air_quality_hourly",
          "latitude": "52.52",
          "longitude": "13.41",
          "variables": "pm10,pm2_5,ozone,european_aqi"
        }
      }
    ]
  }
}
```

**Example 5: Marine/Ocean Weather**

```json
{
  "pipeline_spec": {
    "connection_name": "open_meteo_connection",
    "object": [
      {
        "table": {
          "source_table": "marine_weather_hourly",
          "latitude": "59.91",
          "longitude": "10.75",
          "variables": "wave_height,sea_surface_temperature"
        }
      }
    ]
  }
}
```

**Example 6: Location Search (Geocoding)**

```json
{
  "pipeline_spec": {
    "connection_name": "open_meteo_connection",
    "object": [
      {
        "table": {
          "source_table": "geocoding",
          "name": "Berlin",
          "count": "10",
          "language": "en"
        }
      }
    ]
  }
}
```

**Note**: The geocoding table searches for locations by name and returns coordinates and metadata. This is useful for discovering coordinates for subsequent weather queries. Unlike other tables, it does not require `latitude` or `longitude` parameters.

### Step 3: Run and Schedule the Pipeline

Run the pipeline using your standard Lakeflow / Databricks orchestration (e.g., a scheduled job or workflow).

**For Forecast Tables:**
- Each run fetches the latest forecast data automatically
- The connector manages offsets internally based on the forecast horizon
- Schedule runs based on your data freshness requirements (e.g., hourly, every 6 hours, daily)

**For Historical Tables:**
- Specify the date range via `start_date` and `end_date` table options
- Each run performs a full refresh for the specified period
- Use for backfilling or analyzing specific historical periods

#### Best Practices

**Start Small:**
- Begin with a single location and one table to validate configuration
- Test with default variables before customizing
- Verify data quality before scaling to multiple locations

**Optimize API Usage:**
- Use multi-location queries (comma-separated lat/lon) instead of separate tables for each location
- For free tier, stay well under the 10,000 requests/day limit
- For commercial tiers, monitor monthly usage against your subscription limit
- Schedule forecast syncs at intervals that match your data freshness needs (e.g., every 6 hours rather than every hour)

**Choose Appropriate Variables:**
- Only request the variables you need to minimize data transfer and processing
- Weather forecast tables support 50+ variables - see [Open-Meteo API documentation](https://open-meteo.com/en/docs) for complete list
- Use default variable sets if you need comprehensive weather data

**Rate Limiting:**
- The connector automatically enforces rate limits with sliding window algorithm
- Includes exponential backoff retry logic for transient failures
- Handles HTTP 429 (rate limit) responses gracefully with automatic delays

**Historical Data:**
- Historical data is available from 1940 onwards
- Large date ranges can result in many API calls - consider breaking into smaller batches
- Historical tables use snapshot ingestion (full refresh) for the specified date range

#### Troubleshooting

**Common Issues:**

- **Missing latitude/longitude**:
  - Error: Configuration requires latitude and longitude
  - Solution: Provide `latitude` and `longitude` either at connection level or in table options

- **Invalid coordinates**:
  - Error: HTTP 400 Bad Request
  - Solution: Verify latitude is between -90 and 90, longitude between -180 and 180

- **Rate limit exceeded**:
  - Error: Daily rate limit exceeded (10000 requests/day)
  - Solution:
    - For free tier: reduce sync frequency or upgrade to commercial tier
    - For commercial tier: check your monthly usage against subscription limits
    - Use multi-location queries to reduce API calls

- **Historical data errors**:
  - Error: HTTP 400 Bad Request for historical tables
  - Solution: Ensure `start_date` and `end_date` are provided in YYYY-MM-DD format and within valid range (1940-present)

- **Invalid variables**:
  - Error: API returns error about unknown variables
  - Solution: Verify variable names against [Open-Meteo API documentation](https://open-meteo.com/en/docs). Variable names are case-sensitive and table-specific.

- **Connection timeouts**:
  - Error: Request timeout
  - Solution: Increase the `timeout` parameter in connection options (default: 30 seconds) or check network connectivity

- **Authentication errors (commercial tier)**:
  - Error: HTTP 401 Unauthorized
  - Solution: Verify your `api_key` is correct and active. Check your subscription status at open-meteo.com

**Error Handling:**

The connector includes built-in error handling:
- **Automatic retries** with exponential backoff for transient network issues
- **Rate limit management** with automatic throttling and delays
- **Detailed error messages** in pipeline logs for troubleshooting
- **HTTP session reuse** for improved performance and reliability

Check the pipeline logs for detailed error information and stack traces.

## Free vs Commercial Tier Comparison

| Feature | Free Tier | Commercial Tier |
|---------|-----------|-----------------|
| **API Endpoints** | Standard public endpoints | Dedicated commercial endpoints |
| **Rate Limits** | 600/min, 10K/day, 300K/month | Unlimited per-minute/day, up to 50M/month depending on plan |
| **Uptime SLA** | Best-effort | Guaranteed availability |
| **Historical Data** | From 1940 onwards | From 1940 onwards |
| **Forecast Horizon** | Up to 16 days (weather) | Up to 16 days (weather) |
| **Data Freshness** | Hourly updates | Hourly updates |
| **Support** | Community support | Priority email support |
| **Cost** | Free | Starting at ~$15/month |

**When to Use Commercial Tier:**
- Production applications requiring guaranteed uptime
- High-frequency data ingestion (more than 10K requests/day)
- Applications with strict SLA requirements
- Need for priority technical support

**When Free Tier is Sufficient:**
- Development and testing
- Personal projects
- Low-frequency data collection (daily or weekly syncs)
- Proof-of-concept implementations

## Frequently Asked Questions

### Q: Where do I configure my API key?

**A**: The API key is configured **at the connection level** when creating the Unity Catalog connection, NOT in the pipeline or table configuration.

**Correct:**
```sql
CREATE CONNECTION open_meteo_connection
TYPE lakeflow_community_connector
OPTIONS (
  api_key '<your-key>',  -- ← Configure here
  externalOptionsAllowList 'latitude,longitude,variables,start_date,end_date'
);
```

**Incorrect:**
```python
# DO NOT do this - api_key is not a table option
"table_configuration": {
    "api_key": "...",  # ← WRONG - will be ignored
}
```

### Q: Can I use different API keys for different tables?

**A**: No. All tables using the same connection share the same API key. If you need different API keys (e.g., different accounts or tiers), create separate connections:

```python
# Connection 1: Free tier
pipeline_spec_free = {
    "connection_name": "open_meteo_free",  # Uses free tier connection
    "objects": [
        {"table": {"source_table": "weather_forecast_hourly", ...}}
    ]
}

# Connection 2: Commercial tier
pipeline_spec_commercial = {
    "connection_name": "open_meteo_commercial",  # Uses commercial connection
    "objects": [
        {"table": {"source_table": "air_quality_hourly", ...}}
    ]
}
```

### Q: How do I know if my commercial API key is being used?

**A**: Check the connection configuration or monitor API requests:

1. **Verify connection**: Query connection metadata in Unity Catalog
2. **Check logs**: API requests should go to `customer-api.open-meteo.com` (not `api.open-meteo.com`)
3. **Test rate limits**: Commercial tiers have unlimited per-minute requests (free tier is limited to 600/min)

### Q: Can I override the connection's latitude/longitude per table?

**A**: Yes! Latitude and longitude can be specified at both connection level (default) and table level (override):

```python
# Connection has default: latitude="52.52", longitude="13.41" (Berlin)

pipeline_spec = {
    "connection_name": "open_meteo_connection",
    "objects": [
        {
            "table": {
                "source_table": "weather_forecast_hourly",
                # Uses connection default: Berlin (52.52, 13.41)
            }
        },
        {
            "table": {
                "source_table": "air_quality_hourly",
                "latitude": "48.85",  # ← Override: Paris
                "longitude": "2.35",
            }
        }
    ]
}
```

## References

- Connector implementation: [open_meteo.py](open_meteo.py)
- Connector API documentation: [open_meteo_api_doc.md](open_meteo_api_doc.md)
- Official Open-Meteo API documentation:
  - [Weather Forecast API](https://open-meteo.com/en/docs)
  - [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)
  - [Air Quality API](https://open-meteo.com/en/docs/air-quality-api)
  - [Marine Weather API](https://open-meteo.com/en/docs/marine-weather-api)
  - [API Pricing](https://open-meteo.com/en/pricing)
  - [Terms of Service](https://open-meteo.com/en/terms)
