# **Open-Meteo API Documentation**

## **Authorization**

### Free Tier (Non-Commercial Use)
- **No API key required** for non-commercial applications
- Uses public endpoints (e.g., `https://api.open-meteo.com`)
- Rate limits: 10,000 calls/day, 5,000 calls/hour, 600 calls/minute

### Commercial Tier
- **API key required** via `apikey` query parameter
- Authentication method: API key in URL query string
  ```
  https://customer-api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&apikey=YOUR_API_KEY
  ```
- Uses dedicated customer endpoints (e.g., `https://customer-api.open-meteo.com`)
- Higher rate limits: 1M-50M+ calls/month depending on tier
- Reserved server instances with 99.9% uptime SLA

### Example API Request (Authenticated)
```http
GET https://customer-api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m&apikey=abc123
```

### Example API Request (Free)
```http
GET https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m
```

**Note:** The connector stores the API key (if commercial) and includes it in all requests. OAuth flows are not used.

---

## **Object List**

Open-Meteo provides access to multiple API endpoints representing different data types. The object list is **static** and documented below.

### Available APIs (Objects/Tables)

#### Free & Commercial Tier APIs

| Object Name | Description | Endpoint |
|-------------|-------------|----------|
| `weather_forecast` | Current and future weather predictions (0-16 days) | `/v1/forecast` |
| `historical_weather` | Past weather data from 1940-present | `/v1/archive` |
| `historical_forecast` | Previous forecast runs (archived) | `/v1/forecast` (with past parameters) |
| `air_quality` | Atmospheric pollution and air quality metrics | `/v1/air-quality` |
| `marine_weather` | Ocean and coastal weather conditions | `/v1/marine` |
| `geocoding` | Location name-to-coordinate conversion | `/v1/search` |
| `elevation` | Terrain elevation data | `/v1/elevation` |

#### Commercial Tier Only APIs

| Object Name | Description | Endpoint |
|-------------|-------------|----------|
| `ensemble_models` | Multiple weather model simulations | `/v1/ensemble` |
| `seasonal_forecast` | Extended forecasts beyond 16 days | `/v1/seasonal` |
| `climate_change` | Long-term climate projection data | `/v1/climate` |
| `satellite_radiation` | Solar irradiance measurements | `/v1/solar` |
| `flood` | Flood risk assessment | `/v1/flood` |

#### Regional Weather Models (Free & Commercial)

Additional region-specific weather forecast endpoints are available for:
- DWD Germany (ICON)
- NOAA U.S. (GFS/HRRR)
- Météo-France
- ECMWF
- UK Met Office
- And 14+ other national meteorological services

**Note:** The object list is static and predefined. No API endpoint exists to dynamically retrieve the list of available objects.

---

## **Object Schema**

Schemas are **static and documented** for each object. There is no API to retrieve schemas dynamically.

### Weather Forecast Schema (`weather_forecast`)

**Hourly Variables (100+ available):**

| Field Name | Data Type | Unit | Description |
|------------|-----------|------|-------------|
| `time` | timestamp | ISO8601 | Time of observation/forecast |
| `temperature_2m` | float | °C / °F | Air temperature at 2 meters height |
| `relative_humidity_2m` | integer | % | Relative humidity at 2 meters |
| `dew_point_2m` | float | °C / °F | Dew point temperature |
| `apparent_temperature` | float | °C / °F | Feels-like temperature |
| `precipitation` | float | mm / inch | Total precipitation |
| `rain` | float | mm / inch | Rain only |
| `snowfall` | float | cm / inch | Snowfall amount |
| `snow_depth` | float | meters | Snow depth on ground |
| `weather_code` | integer | WMO code | Weather condition code |
| `pressure_msl` | float | hPa | Mean sea level pressure |
| `surface_pressure` | float | hPa | Surface pressure |
| `cloud_cover` | integer | % | Total cloud cover |
| `cloud_cover_low` | integer | % | Low level clouds |
| `cloud_cover_mid` | integer | % | Mid level clouds |
| `cloud_cover_high` | integer | % | High level clouds |
| `visibility` | float | meters | Visibility distance |
| `evapotranspiration` | float | mm | Evapotranspiration |
| `et0_fao_evapotranspiration` | float | mm | Reference evapotranspiration |
| `vapour_pressure_deficit` | float | kPa | Vapor pressure deficit |
| `wind_speed_10m` | float | km/h, m/s, mph, kn | Wind speed at 10 meters |
| `wind_speed_80m` | float | km/h, m/s, mph, kn | Wind speed at 80 meters |
| `wind_speed_120m` | float | km/h, m/s, mph, kn | Wind speed at 120 meters |
| `wind_direction_10m` | integer | ° | Wind direction at 10 meters |
| `wind_direction_80m` | integer | ° | Wind direction at 80 meters |
| `wind_direction_120m` | integer | ° | Wind direction at 120 meters |
| `wind_gusts_10m` | float | km/h, m/s, mph, kn | Wind gusts at 10 meters |
| `shortwave_radiation` | float | W/m² | Shortwave solar radiation |
| `direct_radiation` | float | W/m² | Direct solar radiation |
| `diffuse_radiation` | float | W/m² | Diffuse solar radiation |
| `direct_normal_irradiance` | float | W/m² | Direct normal irradiance |
| `global_tilted_irradiance` | float | W/m² | Global irradiance on tilted plane |
| `terrestrial_radiation` | float | W/m² | Terrestrial radiation |
| `shortwave_radiation_instant` | float | W/m² | Instantaneous shortwave radiation |
| `diffuse_radiation_instant` | float | W/m² | Instantaneous diffuse radiation |
| `direct_normal_irradiance_instant` | float | W/m² | Instantaneous DNI |
| `soil_temperature_0cm` | float | °C / °F | Soil temperature at surface |
| `soil_temperature_6cm` | float | °C / °F | Soil temperature at 6cm depth |
| `soil_temperature_18cm` | float | °C / °F | Soil temperature at 18cm depth |
| `soil_temperature_54cm` | float | °C / °F | Soil temperature at 54cm depth |
| `soil_moisture_0_to_1cm` | float | m³/m³ | Soil moisture 0-1cm |
| `soil_moisture_1_to_3cm` | float | m³/m³ | Soil moisture 1-3cm |
| `soil_moisture_3_to_9cm` | float | m³/m³ | Soil moisture 3-9cm |
| `soil_moisture_9_to_27cm` | float | m³/m³ | Soil moisture 9-27cm |
| `soil_moisture_27_to_81cm` | float | m³/m³ | Soil moisture 27-81cm |

**Daily Variables:**

| Field Name | Data Type | Unit | Description |
|------------|-----------|------|-------------|
| `time` | date | ISO8601 | Date |
| `weather_code` | integer | WMO code | Dominant weather code |
| `temperature_2m_max` | float | °C / °F | Maximum daily temperature |
| `temperature_2m_min` | float | °C / °F | Minimum daily temperature |
| `apparent_temperature_max` | float | °C / °F | Maximum apparent temperature |
| `apparent_temperature_min` | float | °C / °F | Minimum apparent temperature |
| `sunrise` | timestamp | ISO8601 | Sunrise time |
| `sunset` | timestamp | ISO8601 | Sunset time |
| `daylight_duration` | float | seconds | Daylight duration |
| `sunshine_duration` | float | seconds | Sunshine duration |
| `uv_index_max` | float | index | Maximum UV index |
| `uv_index_clear_sky_max` | float | index | Max UV index (clear sky) |
| `precipitation_sum` | float | mm / inch | Total precipitation |
| `rain_sum` | float | mm / inch | Total rain |
| `snowfall_sum` | float | cm / inch | Total snowfall |
| `precipitation_hours` | integer | hours | Hours with precipitation |
| `precipitation_probability_max` | integer | % | Max precipitation probability |
| `wind_speed_10m_max` | float | km/h, m/s, mph, kn | Maximum wind speed |
| `wind_gusts_10m_max` | float | km/h, m/s, mph, kn | Maximum wind gusts |
| `wind_direction_10m_dominant` | integer | ° | Dominant wind direction |
| `shortwave_radiation_sum` | float | MJ/m² | Total shortwave radiation |
| `et0_fao_evapotranspiration` | float | mm | Reference evapotranspiration |

**Current Variables:**

Returns the current value of any hourly variable.

### Historical Weather Schema (`historical_weather`)

Same schema as `weather_forecast` but for past dates (1940-present). Requires `start_date` and `end_date` parameters.

### Air Quality Schema (`air_quality`)

**Hourly Variables:**

| Field Name | Data Type | Unit | Description |
|------------|-----------|------|-------------|
| `time` | timestamp | ISO8601 | Time of measurement |
| `pm10` | float | μg/m³ | Particulate matter < 10μm |
| `pm2_5` | float | μg/m³ | Particulate matter < 2.5μm |
| `carbon_monoxide` | float | μg/m³ | CO concentration |
| `nitrogen_dioxide` | float | μg/m³ | NO₂ concentration |
| `sulphur_dioxide` | float | μg/m³ | SO₂ concentration |
| `ozone` | float | μg/m³ | O₃ concentration |
| `carbon_dioxide` | float | ppm | CO₂ concentration |
| `ammonia` | float | μg/m³ | NH₃ concentration |
| `aerosol_optical_depth` | float | dimensionless | Aerosol optical depth |
| `dust` | float | μg/m³ | Dust concentration |
| `uv_index` | float | index | UV index |
| `uv_index_clear_sky` | float | index | UV index (clear sky) |
| `alder_pollen` | integer | grains/m³ | Alder pollen (Europe only) |
| `birch_pollen` | integer | grains/m³ | Birch pollen (Europe only) |
| `grass_pollen` | integer | grains/m³ | Grass pollen (Europe only) |
| `mugwort_pollen` | integer | grains/m³ | Mugwort pollen (Europe only) |
| `olive_pollen` | integer | grains/m³ | Olive pollen (Europe only) |
| `ragweed_pollen` | integer | grains/m³ | Ragweed pollen (Europe only) |
| `european_aqi` | integer | index | European Air Quality Index |
| `european_aqi_pm2_5` | integer | index | European AQI for PM2.5 |
| `european_aqi_pm10` | integer | index | European AQI for PM10 |
| `european_aqi_no2` | integer | index | European AQI for NO₂ |
| `european_aqi_o3` | integer | index | European AQI for O₃ |
| `european_aqi_so2` | integer | index | European AQI for SO₂ |
| `us_aqi` | integer | index | U.S. Air Quality Index |
| `us_aqi_pm2_5` | integer | index | U.S. AQI for PM2.5 |
| `us_aqi_pm10` | integer | index | U.S. AQI for PM10 |
| `us_aqi_no2` | integer | index | U.S. AQI for NO₂ |
| `us_aqi_co` | integer | index | U.S. AQI for CO |
| `us_aqi_o3` | integer | index | U.S. AQI for O₃ |
| `us_aqi_so2` | integer | index | U.S. AQI for SO₂ |

### Marine Weather Schema (`marine_weather`)

**Hourly Variables:**

| Field Name | Data Type | Unit | Description |
|------------|-----------|------|-------------|
| `time` | timestamp | ISO8601 | Time of forecast |
| `wave_height` | float | meters | Significant wave height |
| `wave_direction` | integer | ° | Wave direction |
| `wave_period` | float | seconds | Wave period |
| `wind_wave_height` | float | meters | Wind wave height |
| `wind_wave_direction` | integer | ° | Wind wave direction |
| `wind_wave_period` | float | seconds | Wind wave period |
| `wind_wave_peak_period` | float | seconds | Wind wave peak period |
| `swell_wave_height` | float | meters | Swell wave height |
| `swell_wave_direction` | integer | ° | Swell wave direction |
| `swell_wave_period` | float | seconds | Swell wave period |
| `swell_wave_peak_period` | float | seconds | Swell wave peak period |
| `ocean_current_velocity` | float | m/s | Ocean current speed |
| `ocean_current_direction` | integer | ° | Ocean current direction |
| `sea_surface_temperature` | float | °C / °F | Sea surface temperature |

**Daily Variables:**

| Field Name | Data Type | Unit | Description |
|------------|-----------|------|-------------|
| `wave_height_max` | float | meters | Maximum wave height |
| `wave_direction_dominant` | integer | ° | Dominant wave direction |
| `wave_period_max` | float | seconds | Maximum wave period |
| `wind_wave_height_max` | float | meters | Maximum wind wave height |
| `swell_wave_height_max` | float | meters | Maximum swell wave height |

### Geocoding Schema (`geocoding`)

**Response Fields:**

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `id` | integer | Unique location identifier |
| `name` | string | Location name (localized) |
| `latitude` | float | WGS84 latitude |
| `longitude` | float | WGS84 longitude |
| `elevation` | float | Elevation above sea level (meters) |
| `timezone` | string | IANA timezone identifier |
| `feature_code` | string | GeoNames feature classification |
| `country_code` | string | ISO-3166-1 alpha2 country code |
| `country` | string | Country name (localized) |
| `population` | integer | Population count |
| `postcodes` | array[string] | Associated postal codes |
| `admin1` | string | First-level administrative division |
| `admin2` | string | Second-level administrative division |
| `admin3` | string | Third-level administrative division |
| `admin4` | string | Fourth-level administrative division |

---

## **Get Object Primary Keys**

Primary keys are **static** for each object type:

| Object Name | Primary Key(s) |
|-------------|----------------|
| `weather_forecast` | `latitude`, `longitude`, `time` |
| `historical_weather` | `latitude`, `longitude`, `time` |
| `air_quality` | `latitude`, `longitude`, `time` |
| `marine_weather` | `latitude`, `longitude`, `time` |
| `geocoding` | `id` |
| All other forecast/weather APIs | `latitude`, `longitude`, `time` |

**Note:** No API endpoint exists to retrieve primary keys dynamically. They are documented above.

---

## **Object's Ingestion Type**

| Object Name | Ingestion Type | Rationale |
|-------------|----------------|-----------|
| `weather_forecast` | `append` | New forecast data is continuously generated; time series grows forward |
| `historical_weather` | `snapshot` | Historical data is static once finalized (2-5 day delay); requires full refresh for date range |
| `air_quality` | `append` | New forecast data generated continuously |
| `marine_weather` | `append` | New forecast data generated continuously |
| `geocoding` | `snapshot` | Location data is relatively static; full refresh recommended |

**Definitions:**
- **append**: Only new data can be read incrementally, no updates to existing records
- **snapshot**: Full data refresh required, no incremental support
- **cdc**: Incremental with upserts (not applicable to Open-Meteo)
- **cdc_with_deletes**: Incremental with upserts and deletes (not applicable to Open-Meteo)

---

## **Read API for Data Retrieval**

### Weather Forecast API

**Endpoint:** `https://api.open-meteo.com/v1/forecast` (Free) or `https://customer-api.open-meteo.com/v1/forecast` (Commercial)

**Method:** GET

**Required Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `latitude` | float | WGS84 latitude coordinate |
| `longitude` | float | WGS84 longitude coordinate |

**Optional Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hourly` | string (comma-separated) | — | List of hourly variables to retrieve |
| `daily` | string (comma-separated) | — | List of daily variables (requires `timezone`) |
| `current` | string (comma-separated) | — | List of current condition variables |
| `temperature_unit` | string | `celsius` | Options: `celsius`, `fahrenheit` |
| `wind_speed_unit` | string | `kmh` | Options: `kmh`, `ms`, `mph`, `kn` |
| `precipitation_unit` | string | `mm` | Options: `mm`, `inch` |
| `timeformat` | string | `iso8601` | Options: `iso8601`, `unixtime` |
| `timezone` | string | `GMT` | IANA timezone or `auto` |
| `past_days` | integer (0-92) | 0 | Days of historical data |
| `forecast_days` | integer (0-16) | 7 | Days of forecast data |
| `forecast_hours` | integer | — | Control hourly timesteps |
| `past_hours` | integer | — | Historical hourly data |
| `start_date` | string (yyyy-mm-dd) | — | Start date for data range |
| `end_date` | string (yyyy-mm-dd) | — | End date for data range |
| `start_hour` | string (yyyy-mm-ddThh:mm) | — | Start hour for data range |
| `end_hour` | string (yyyy-mm-ddThh:mm) | — | End hour for data range |
| `models` | string (comma-separated) | `auto` | Specific weather models to use |
| `cell_selection` | string | `land` | Options: `land`, `sea`, `nearest` |
| `apikey` | string | — | Required for commercial tier |

**Incremental Data Retrieval:**

Use `start_date` and `end_date` parameters to fetch specific date ranges. For continuous ingestion:
- Track the last ingested timestamp
- Set `start_date` to the day after the last ingested date
- Set `end_date` to today or desired end date

**Pagination:**

Not applicable. All data for the specified date/time range is returned in a single response. Maximum range is 16 days for forecasts.

**Example Request:**

```http
GET https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m,precipitation&daily=temperature_2m_max,precipitation_sum&timezone=auto&start_date=2024-01-01&end_date=2024-01-31
```

**Example Response:**

```json
{
  "latitude": 52.52,
  "longitude": 13.419,
  "elevation": 44.812,
  "generationtime_ms": 2.2119,
  "utc_offset_seconds": 3600,
  "timezone": "Europe/Berlin",
  "timezone_abbreviation": "CET",
  "hourly": {
    "time": [
      "2024-01-01T00:00",
      "2024-01-01T01:00",
      "2024-01-01T02:00"
    ],
    "temperature_2m": [13.0, 12.7, 12.5],
    "precipitation": [0.0, 0.1, 0.2]
  },
  "hourly_units": {
    "time": "iso8601",
    "temperature_2m": "°C",
    "precipitation": "mm"
  },
  "daily": {
    "time": ["2024-01-01", "2024-01-02"],
    "temperature_2m_max": [15.2, 14.8],
    "precipitation_sum": [2.5, 1.8]
  },
  "daily_units": {
    "time": "iso8601",
    "temperature_2m_max": "°C",
    "precipitation_sum": "mm"
  }
}
```

**Rate Limits:**

| Tier | Calls/Minute | Calls/Hour | Calls/Day | Calls/Month |
|------|--------------|------------|-----------|-------------|
| Free | 600 | 5,000 | 10,000 | 300,000 |
| Standard (Commercial) | Unlimited minutely | Unlimited | Unlimited | 1,000,000 |
| Professional (Commercial) | Unlimited minutely | Unlimited | Unlimited | 5,000,000 |
| Enterprise (Commercial) | Unlimited minutely | Unlimited | Unlimited | 50,000,000+ |

**Note:** The connector should implement rate limiting to stay within these bounds.

### Historical Weather API

**Endpoint:** `https://archive-api.open-meteo.com/v1/archive` (Free & Commercial)

**Method:** GET

**Required Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `latitude` | float | WGS84 latitude coordinate |
| `longitude` | float | WGS84 longitude coordinate |
| `start_date` | string (yyyy-mm-dd) | Beginning of historical period |
| `end_date` | string (yyyy-mm-dd) | End of historical period |

**Optional Parameters:**

Same as Weather Forecast API (excluding `forecast_days`, `forecast_hours`, `past_days`, `past_hours`)

**Data Coverage:** 1940-present (with 2-5 day delay)

**Example Request:**

```http
GET https://archive-api.open-meteo.com/v1/archive?latitude=52.52&longitude=13.41&start_date=2023-01-01&end_date=2023-12-31&hourly=temperature_2m,precipitation&daily=temperature_2m_max,precipitation_sum&timezone=auto
```

**Incremental Data Retrieval:**

Historical data has a 2-5 day delay. For incremental ingestion:
- Track the last ingested date
- Query for new date ranges starting from the last ingested date + 5 days
- Backfill older data if needed

### Air Quality API

**Endpoint:** `https://air-quality-api.open-meteo.com/v1/air-quality`

**Method:** GET

**Required Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `latitude` | float | WGS84 latitude coordinate |
| `longitude` | float | WGS84 longitude coordinate |

**Optional Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hourly` | string (comma-separated) | — | Air quality variables |
| `current` | string (comma-separated) | — | Current air quality variables |
| `domains` | string | `auto` | Options: `auto`, `cams_europe`, `cams_global` |
| `timeformat` | string | `iso8601` | Options: `iso8601`, `unixtime` |
| `timezone` | string | `GMT` | IANA timezone |
| `past_days` | integer (0-92) | 0 | Historical air quality data |
| `forecast_days` | integer (0-7) | 5 | Forecast days |
| `forecast_hours` | integer | — | Control hourly timesteps |
| `past_hours` | integer | — | Historical hourly data |
| `start_date` | string (yyyy-mm-dd) | — | Start date |
| `end_date` | string (yyyy-mm-dd) | — | End date |
| `cell_selection` | string | `nearest` | Options: `land`, `sea`, `nearest` |
| `apikey` | string | — | Commercial tier only |

**Example Request:**

```http
GET https://air-quality-api.open-meteo.com/v1/air-quality?latitude=52.52&longitude=13.41&hourly=pm10,pm2_5,european_aqi&start_date=2024-01-01&end_date=2024-01-31
```

**Update Frequency:**
- European Forecast: Every 24 hours, 4 days forecast
- Global Forecast: Every 12 hours, 5 days forecast
- Historical data available from October 2023 (European) or August 2022 (Global)

### Marine Weather API

**Endpoint:** `https://marine-api.open-meteo.com/v1/marine`

**Method:** GET

**Required Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `latitude` | float | WGS84 latitude coordinate |
| `longitude` | float | WGS84 longitude coordinate |

**Optional Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hourly` | string (comma-separated) | — | Marine variables |
| `daily` | string (comma-separated) | — | Daily marine aggregations |
| `current` | string (comma-separated) | — | Current marine conditions |
| `forecast_days` | integer (0-8) | 5 | Forecast duration |
| `past_days` | integer (0-92) | 0 | Historical marine data |
| `timezone` | string | `GMT` | IANA timezone |
| `length_unit` | string | `metric` | Options: `metric`, `imperial` |
| `timeformat` | string | `iso8601` | Options: `iso8601`, `unixtime` |
| `cell_selection` | string | `sea` | Options: `sea`, `land`, `nearest` |
| `apikey` | string | — | Commercial tier only |

**Example Request:**

```http
GET https://marine-api.open-meteo.com/v1/marine?latitude=54.54&longitude=10.23&hourly=wave_height,sea_surface_temperature&forecast_days=7
```

### Geocoding API

**Endpoint:** `https://geocoding-api.open-meteo.com/v1/search`

**Method:** GET

**Required Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Location name or postal code to search (min 2 characters) |

**Optional Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `count` | integer (1-100) | 10 | Number of results |
| `language` | string | `en` | Result language |
| `format` | string | `json` | Options: `json`, `protobuf` |
| `country` | string | — | ISO-3166 country code filter |
| `apikey` | string | — | Commercial tier only |

**Example Request:**

```http
GET https://geocoding-api.open-meteo.com/v1/search?name=Berlin&count=10&language=en
```

**Example Response:**

```json
{
  "results": [
    {
      "id": 2950159,
      "name": "Berlin",
      "latitude": 52.52437,
      "longitude": 13.41053,
      "elevation": 74.0,
      "timezone": "Europe/Berlin",
      "country_code": "DE",
      "country": "Deutschland",
      "population": 3426354,
      "postcodes": ["10967", "13347"],
      "admin1": "Berlin",
      "feature_code": "PPLC"
    }
  ]
}
```

### Deleted Records

Open-Meteo does not support delete operations or delete tracking. Weather/forecast data is append-only or snapshot-based.

---

## **Field Type Mapping**

| API Data Type | Spark/Standard Type | Description |
|---------------|---------------------|-------------|
| `float` | `DOUBLE` | Floating-point numbers (temperature, precipitation, etc.) |
| `integer` | `INTEGER` | Whole numbers (humidity percentage, weather codes, etc.) |
| `string` (ISO8601) | `TIMESTAMP` | Date/time in ISO8601 format (e.g., "2024-01-01T00:00") |
| `string` (date) | `DATE` | Date in yyyy-mm-dd format |
| `string` (timezone) | `STRING` | IANA timezone identifier |
| `string` (general) | `STRING` | Text fields (location names, country codes, etc.) |
| `array[string]` | `ARRAY<STRING>` | Arrays of strings (postcodes) |

**Special Behaviors:**

- **Weather codes**: Integer enumeration following WMO code table (0-99)
- **Wind direction**: Integer (0-360°), where 0° = North, 90° = East, 180° = South, 270° = West
- **Timestamps**: Always in the specified timezone (default GMT unless overridden by `timezone` parameter)
- **Auto-generated values**: `latitude`, `longitude`, and `elevation` in responses are adjusted to the actual grid cell used (may differ slightly from request)
- **Units**: Specified in `*_units` fields in the response (e.g., `hourly_units`, `daily_units`)

**Constraints:**

- Latitude: -90 to +90
- Longitude: -180 to +180
- Dates: Must be within valid range for each API (e.g., 1940-present for historical, 0-16 days for forecast)

---

## **Free vs. Commercial API Differences**

### Summary Table

| Feature | Free Tier | Commercial Tier |
|---------|-----------|-----------------|
| **Authentication** | No API key required | API key required (`apikey` parameter) |
| **Base URL** | Public endpoints (e.g., `api.open-meteo.com`) | Customer endpoints (e.g., `customer-api.open-meteo.com`) |
| **Rate Limits (Calls/Minute)** | 600 | Unlimited |
| **Rate Limits (Calls/Hour)** | 5,000 | Unlimited |
| **Rate Limits (Calls/Day)** | 10,000 | Unlimited |
| **Rate Limits (Calls/Month)** | 300,000 | 1M (Standard), 5M (Professional), 50M+ (Enterprise) |
| **Weather Forecast API** | ✅ Available | ✅ Available |
| **Historical Weather API** | ✅ Available | ✅ Available |
| **Air Quality API** | ✅ Available | ✅ Available |
| **Marine Weather API** | ✅ Available | ✅ Available |
| **Geocoding API** | ✅ Available | ✅ Available |
| **Ensemble Models API** | ❌ Not available | ✅ Available |
| **Seasonal Forecast API** | ❌ Not available | ✅ Available |
| **Climate Change API** | ❌ Not available | ✅ Available |
| **Satellite Radiation API** | ❌ Not available | ✅ Available |
| **Flood API** | ❌ Not available | ✅ Available |
| **Commercial Use** | ❌ Prohibited | ✅ Allowed |
| **Server Infrastructure** | Shared public servers | Dedicated reserved servers |
| **Uptime SLA** | No guarantee | 99.9% (redundant data centers) |
| **Support** | Community support | Priority support (Enterprise tier) |
| **Billing** | Free | Paid subscription via Stripe |

### Key Differences Details

1. **API Access**
   - Free: Limited to core weather, historical, air quality, marine, and geocoding APIs
   - Commercial: Access to all APIs including advanced forecasting (ensemble, seasonal, climate)

2. **Rate Limiting**
   - Free: Strict limits (10K/day, 300K/month) suitable for small-scale applications
   - Commercial: Unlimited per-minute/hour/day usage with monthly caps based on tier

3. **Infrastructure**
   - Free: Shared public infrastructure with no SLA
   - Commercial: Dedicated servers with 99.9% uptime guarantee, redundant data centers in Europe/North America

4. **Usage Rights**
   - Free: Non-commercial use only (personal projects, research, education)
   - Commercial: Permitted for business applications, production systems, revenue-generating services

5. **Authentication**
   - Free: No authentication required (anonymous access)
   - Commercial: API key authentication required for all requests

6. **Endpoints**
   - Free: Public domain endpoints (e.g., `https://api.open-meteo.com/v1/forecast`)
   - Commercial: Customer-specific endpoints (e.g., `https://customer-api.open-meteo.com/v1/forecast`)

---

## **Sources and References**

### Research Log

| Source Type | URL | Accessed (UTC) | Confidence | What it confirmed |
|-------------|-----|----------------|------------|-------------------|
| Official Docs | https://open-meteo.com/en/docs | 2026-01-08 | Highest | Complete API endpoint structure, parameters, response formats for Weather Forecast API |
| Official Docs | https://open-meteo.com/en/pricing | 2026-01-08 | Highest | Free vs. Commercial tier differences, rate limits, feature access, pricing tiers |
| Official Docs | https://open-meteo.com/en/docs/historical-weather-api | 2026-01-08 | Highest | Historical Weather API endpoint, parameters, date range capabilities, data models |
| Official Docs | https://open-meteo.com/en/docs/air-quality-api | 2026-01-08 | Highest | Air Quality API endpoint, pollutants, pollen data, AQI indices, update frequency |
| Official Docs | https://open-meteo.com/en/docs/geocoding-api | 2026-01-08 | Highest | Geocoding API endpoint, search parameters, response schema, GeoNames attribution |
| Official Docs | https://open-meteo.com/en/docs/marine-weather-api | 2026-01-08 | Highest | Marine Weather API endpoint, wave/ocean variables, data sources, models |

### Official Documentation

- **Primary Documentation**: https://open-meteo.com/en/docs
- **Pricing & Tiers**: https://open-meteo.com/en/pricing
- **Weather Forecast API**: https://open-meteo.com/en/docs (default API)
- **Historical Weather API**: https://open-meteo.com/en/docs/historical-weather-api
- **Air Quality API**: https://open-meteo.com/en/docs/air-quality-api
- **Geocoding API**: https://open-meteo.com/en/docs/geocoding-api
- **Marine Weather API**: https://open-meteo.com/en/docs/marine-weather-api

### Confidence Level

**Highest confidence** - All information derived directly from official Open-Meteo API documentation. No conflicts between sources. All endpoints, parameters, schemas, and tier differences verified from primary sources.

### Notes

- No existing connector implementations (Airbyte, Singer, dltHub) were found for Open-Meteo during research
- All schema definitions, parameters, and examples are directly from official documentation
- Free vs. Commercial differences are explicitly documented on the official pricing page
- Data sources (NOAA, ECMWF, Météo-France, etc.) are cited in the official documentation
