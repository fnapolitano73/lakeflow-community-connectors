# Open-Meteo Connector Implementation Review

## Comparison with Other Connectors

### Connectors Reviewed
1. **GitHub** - REST API with session management, helper methods for nested schemas
2. **Stripe** - Centralized config pattern, schema cache, reusable nested schemas
3. **HubSpot** - Dynamic schema discovery, metadata cache, delete support (cdc_with_deletes)
4. **AlphaVantage** - Rate limiting, tier management, multi-symbol support, centralized config
5. **Zendesk** - Incremental API pattern, basic structure

---

## Key Pattern Differences

### 1. **Centralized Configuration Pattern**

#### Current Open-Meteo Implementation
```python
# Inline metadata dictionaries in read_table_metadata()
metadata = {
    "weather_forecast_hourly": {
        "primary_keys": ["latitude", "longitude", "time"],
        "cursor_field": "time",
        "ingestion_type": "append",
    },
    ...
}
```

#### Stripe/HubSpot/AlphaVantage Pattern
```python
def __init__(self, options):
    # Centralized configuration in __init__
    self._object_config = {
        "customers": {
            "primary_keys": ["id"],
            "cursor_field": "created",
            "ingestion_type": "cdc",
            "endpoint": "customers",
            "supports_deleted": True,
        },
        ...
    }
```

**Pros of Centralized Config:**
- ✅ Single source of truth - easier to maintain
- ✅ Configuration loaded once at initialization
- ✅ Can include endpoint URLs, API parameters, special behaviors
- ✅ Easier to extend with new metadata fields
- ✅ Better code organization and readability

**Cons:**
- ❌ Slightly more memory usage (negligible)
- ❌ Initial setup more verbose

**Recommendation:** ✅ **ADOPT** - Use centralized config pattern

---

### 2. **HTTP Session Management**

#### Current Open-Meteo Implementation
```python
# Creates new connection for each request
response = requests.get(url, params=params)
```

#### GitHub/AlphaVantage Pattern
```python
def __init__(self, options):
    # Reusable session with connection pooling
    self._session = requests.Session()
    self._session.headers.update({"Authorization": f"Bearer {token}"})

def _make_request(self):
    response = self._session.get(url, params=params)
```

**Pros of Session Management:**
- ✅ **Connection pooling** - reuses TCP connections (faster)
- ✅ **Automatic header management** - set headers once
- ✅ **Better performance** for multiple requests
- ✅ **Configurable retries** and timeouts

**Cons:**
- ❌ Slightly more complex initialization

**Recommendation:** ✅ **ADOPT** - Use session management for better performance

---

### 3. **Schema Organization**

#### Current Open-Meteo Implementation
```python
def get_table_schema(self, table_name, table_options):
    schemas = {
        "weather_forecast_hourly": StructType([
            StructField("latitude", DoubleType(), False),
            StructField("longitude", DoubleType(), False),
            # ... 46 more fields inline
        ]),
        ...
    }
    return schemas[table_name]
```

#### GitHub Pattern (Helper Methods)
```python
def _get_user_struct(self) -> StructType:
    """Return the nested user/assignee struct schema."""
    return StructType([...])

def _get_issues_schema(self) -> StructType:
    user_struct = self._get_user_struct()  # Reuse
    return StructType([
        StructField("user", user_struct, True),
        StructField("assignee", user_struct, True),
    ])
```

#### Stripe Pattern (Nested Schema Definitions)
```python
def __init__(self, options):
    # Define reusable nested schemas in __init__
    self._address_schema = StructType([...])
    self._shipping_schema = StructType([
        StructField("address", self._address_schema, True),  # Reuse
    ])
```

**Pros of Helper Methods (GitHub):**
- ✅ Reusable nested structures
- ✅ Better code organization
- ✅ Easier to maintain common schemas

**Pros of Initialized Nested Schemas (Stripe):**
- ✅ Schemas built once at init
- ✅ Very clean reuse pattern
- ✅ No repeated computation

**Cons of Current Inline Approach:**
- ❌ Difficult to reuse common structures
- ❌ Large inline dictionaries reduce readability
- ❌ Harder to maintain

**Recommendation:** ✅ **ADOPT** - Use helper methods for schema organization

---

### 4. **Schema Caching**

#### Current Open-Meteo Implementation
```python
# No caching - schemas recreated on each call
def get_table_schema(self, table_name, table_options):
    schemas = {...}  # Built every time
    return schemas[table_name]
```

#### Stripe/HubSpot Pattern
```python
def __init__(self, options):
    self._schema_cache = {}

def get_table_schema(self, table_name, table_options):
    if table_name in self._schema_cache:
        return self._schema_cache[table_name]

    schema = self._build_schema(table_name)
    self._schema_cache[table_name] = schema
    return schema
```

**Pros of Caching:**
- ✅ Avoids rebuilding StructType objects
- ✅ Better performance for repeated calls
- ✅ Minimal memory overhead

**Cons:**
- ❌ Slightly more code

**Recommendation:** ⚠️ **OPTIONAL** - Current approach acceptable for static schemas, but caching is best practice

---

### 5. **Rate Limiting**

#### Current Open-Meteo Implementation
```python
# No rate limiting implemented
```

#### AlphaVantage Pattern
```python
RATE_LIMIT_TIERS = {
    "free": {"requests_per_minute": 5, "requests_per_day": 25},
    "premium_30": {"requests_per_minute": 30, "requests_per_day": None},
}

def __init__(self, options):
    tier = options.get("tier", "free")
    tier_config = self.RATE_LIMIT_TIERS[tier]
    self.requests_per_minute = tier_config["requests_per_minute"]
    self._request_timestamps = []

def _enforce_rate_limit(self):
    # Enforce rate limiting logic
```

**Open-Meteo Rate Limits:**
- Free: 600/min, 5,000/hour, 10,000/day, 300,000/month
- Commercial: Unlimited per-minute/hour, 1M-50M+/month

**Pros of Rate Limiting:**
- ✅ **Critical** - Prevents API rejection/blocking
- ✅ Respects API provider limits
- ✅ Better error handling

**Cons:**
- ❌ Adds complexity

**Recommendation:** ✅ **ADOPT** - **CRITICAL** for production use

---

### 6. **Error Handling and Retries**

#### Current Open-Meteo Implementation
```python
response = requests.get(url, params=params)
response.raise_for_status()  # Simple error raising
```

#### AlphaVantage/HubSpot Pattern
```python
def _make_request_with_retry(self, url, params, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = self._session.get(url, params=params, timeout=30)

            if response.status_code == 429:  # Rate limit
                time.sleep(60)
                continue

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

**Pros of Retry Logic:**
- ✅ Handles transient failures
- ✅ Respects rate limit responses (429)
- ✅ Exponential backoff
- ✅ More robust in production

**Cons:**
- ❌ More complex code

**Recommendation:** ✅ **ADOPT** - Essential for production robustness

---

### 7. **Variable/Field Validation**

#### Current Open-Meteo Implementation
```python
# Uses table_options.get("variables", "default_vars")
# No validation of variable names
```

#### Best Practice Pattern
```python
# Define valid variables per table
VALID_HOURLY_VARS = {
    "temperature_2m", "relative_humidity_2m", "precipitation", ...
}

def _validate_variables(self, table_name, variables):
    var_list = variables.split(",")
    valid_vars = self._get_valid_variables(table_name)

    invalid = [v for v in var_list if v not in valid_vars]
    if invalid:
        raise ValueError(f"Invalid variables: {invalid}")
```

**Pros of Validation:**
- ✅ Early error detection
- ✅ Better user experience
- ✅ Prevents invalid API calls

**Cons:**
- ❌ Maintenance burden (keep variable list updated)

**Recommendation:** ⚠️ **OPTIONAL** - Good to have but not critical

---

### 8. **Helper Methods for Read Operations**

#### Current Open-Meteo Implementation
```python
def read_table(self, table_name, start_offset, table_options):
    if table_name.startswith("weather_forecast_"):
        return self._read_weather_forecast(...)
    elif table_name.startswith("historical_weather_"):
        return self._read_historical_weather(...)
```

**✅ Already using this pattern!** Good separation of concerns.

---

### 9. **Dynamic Schema Discovery**

#### Current Open-Meteo Implementation
```python
# Static schema definitions
```

#### HubSpot Pattern
```python
def list_tables(self):
    standard_tables = ["contacts", "companies", ...]
    try:
        custom_objects = self._discover_custom_objects()  # API call
        standard_tables.extend(custom_objects)
    except Exception as e:
        print(f"Warning: Could not discover custom objects: {e}")
    return standard_tables
```

**Applicability to Open-Meteo:**
- ❌ **NOT APPLICABLE** - Open-Meteo has static, well-defined API endpoints
- ✅ Current static approach is correct for Open-Meteo

**Recommendation:** ❌ **DO NOT ADOPT** - Not needed for Open-Meteo

---

### 10. **Multi-Location Support**

#### Current Open-Meteo Implementation
```python
# Single lat/long per query
latitude = table_options.get("latitude", self.default_latitude)
longitude = table_options.get("longitude", self.default_longitude)
```

#### AlphaVantage Multi-Symbol Pattern
```python
# Supports "MSFT,ORCL,AAPL" - splits and combines results
symbols = table_options.get("symbol", "").split(",")
all_records = []
for symbol in symbols:
    records = self._fetch_for_symbol(symbol)
    all_records.extend(records)
```

**Open-Meteo API Capability:**
```
?latitude=52.52,48.85&longitude=13.41,2.35
```
Open-Meteo **DOES support** multiple locations in a single API call!

**Pros of Multi-Location Support:**
- ✅ Efficient - one API call for multiple locations
- ✅ Saves rate limit quota
- ✅ Faster data collection

**Recommendation:** ✅ **ADOPT** - Open-Meteo supports this natively

---

## Summary: Pros & Cons

### Current Open-Meteo Implementation

**Strengths:**
- ✅ Correct interface implementation
- ✅ Good separation with helper methods (_read_weather_forecast, etc.)
- ✅ Handles both free and commercial tiers
- ✅ Clean offset management for incremental reads
- ✅ Proper ingestion type selection (append vs snapshot)

**Weaknesses:**
- ❌ No rate limiting (critical gap)
- ❌ No HTTP session management (performance issue)
- ❌ No retry/error handling (robustness issue)
- ❌ No centralized configuration (maintenance issue)
- ❌ Missing multi-location support (efficiency issue)
- ❌ No schema caching (minor performance issue)
- ❌ Inline schema definitions (readability issue)

---

## Enhancement Plan

### Priority 1: Critical (Required for Production)
1. ✅ **Add rate limiting** - Prevent API blocking
2. ✅ **Add HTTP session management** - Performance
3. ✅ **Add retry logic with exponential backoff** - Robustness
4. ✅ **Add centralized configuration** - Maintainability

### Priority 2: High (Significant Improvements)
5. ✅ **Add multi-location support** - API supports it natively
6. ✅ **Refactor schema organization** - Use helper methods
7. ✅ **Add schema caching** - Best practice

### Priority 3: Nice to Have
8. ⚠️ **Add variable validation** - Better UX
9. ⚠️ **Add logging** - Debugging support
10. ⚠️ **Add timeout configuration** - Control long requests

---

## Recommended Implementation Changes

### 1. Centralized Configuration
```python
def __init__(self, options):
    self._table_config = {
        "weather_forecast_hourly": {
            "primary_keys": ["latitude", "longitude", "time"],
            "cursor_field": "time",
            "ingestion_type": "append",
            "endpoint": "forecast",
            "data_key": "hourly",
            "forecast_days": 16,
            "variables": "temperature_2m,relative_humidity_2m,...",
        },
        ...
    }
```

### 2. HTTP Session
```python
def __init__(self, options):
    self._session = requests.Session()
    self._session.headers.update({"User-Agent": "LakeflowConnect-OpenMeteo/1.0"})
```

### 3. Rate Limiting
```python
RATE_LIMIT_TIERS = {
    "free": {"per_minute": 600, "per_hour": 5000, "per_day": 10000},
    "standard": {"per_minute": None, "per_hour": None, "per_day": None, "per_month": 1000000},
    ...
}

def _enforce_rate_limit(self):
    # Implement sliding window rate limiter
```

### 4. Retry Logic
```python
def _make_request(self, url, params, max_retries=3):
    for attempt in range(max_retries):
        try:
            self._enforce_rate_limit()
            response = self._session.get(url, params=params, timeout=30)

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                time.sleep(retry_after)
                continue

            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

### 5. Multi-Location Support
```python
def read_table(self, table_name, start_offset, table_options):
    # Support "52.52,48.85" format
    latitudes = table_options.get("latitude", self.default_latitude)
    longitudes = table_options.get("longitude", self.default_longitude)

    params = {
        "latitude": latitudes,  # Can be comma-separated
        "longitude": longitudes,
        ...
    }
```

### 6. Schema Helper Methods
```python
def _get_base_weather_fields(self) -> List[StructField]:
    return [
        StructField("latitude", DoubleType(), False),
        StructField("longitude", DoubleType(), False),
        StructField("time", StringType(), False),
    ]

def _get_hourly_weather_schema(self) -> StructType:
    fields = self._get_base_weather_fields()
    fields.extend([
        StructField("temperature_2m", DoubleType(), True),
        ...
    ])
    return StructType(fields)
```

---

## Conclusion

The current Open-Meteo implementation is **functionally correct** but lacks **production-ready features** found in mature connectors like AlphaVantage, Stripe, and HubSpot.

**Key Missing Features:**
1. Rate limiting (CRITICAL)
2. Session management (HIGH)
3. Retry logic (HIGH)
4. Centralized config (HIGH)
5. Multi-location support (HIGH)

**Next Steps:**
Implement enhancements in priority order to bring the connector to production quality.
