# actiTIME Connector Implementation Plan

## Overview

This document outlines the implementation plan for the actiTIME Lakeflow Community Connector. The connector will enable data ingestion from actiTIME (time tracking software) into Databricks.

---

## 1. Rate Limiting & Retry Logic

### actiTIME Rate Limits (from API Documentation)

| Limit Type | Value | Notes |
|------------|-------|-------|
| **Per Second** | 100 requests | Per user account |
| **Per Minute** | 1000 requests | Per user account |
| **Auth Ban** | 3 failed attempts in 10s | IP banned for 1 minute |

### Response Headers for Rate Limiting

| Header | Description |
|--------|-------------|
| `X-Ratelimit-Remaining` | Requests left in current window |
| `X-Ratelimit-Reset` | Seconds until window reset |
| `Retry-After` | Seconds to wait (when 429 returned) |

### Implementation Strategy

Following the **Alpha Vantage pattern** (strict rate limiting):

```python
class RateLimiter:
    """Rate limiter with exponential backoff for actiTIME API."""
    
    def __init__(self, requests_per_second: int = 100, requests_per_minute: int = 1000):
        self.requests_per_second = requests_per_second
        self.requests_per_minute = requests_per_minute
        self._request_timestamps: list[float] = []
        self._last_request_time: float = 0
    
    def wait_if_needed(self) -> None:
        """Enforce rate limiting by sleeping if needed."""
        now = time.time()
        
        # Enforce minimum delay between requests (10ms for 100 req/sec)
        min_delay = 1.0 / self.requests_per_second
        time_since_last = now - self._last_request_time
        if time_since_last < min_delay:
            time.sleep(min_delay - time_since_last)
        
        # Clean up timestamps older than 1 minute
        self._request_timestamps = [
            ts for ts in self._request_timestamps if now - ts < 60
        ]
        
        # If at minute limit, wait for oldest request to expire
        if len(self._request_timestamps) >= self.requests_per_minute:
            sleep_time = 60 - (now - self._request_timestamps[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self._request_timestamps.append(time.time())
        self._last_request_time = time.time()
```

### Retry Logic with Exponential Backoff

```python
def _make_request_with_retry(
    self, 
    method: str, 
    url: str, 
    max_retries: int = 3,
    **kwargs
) -> requests.Response:
    """Make HTTP request with retry and exponential backoff."""
    
    for attempt in range(max_retries + 1):
        self._rate_limiter.wait_if_needed()
        
        response = self._session.request(method, url, **kwargs)
        
        if response.status_code == 429:  # Too Many Requests
            retry_after = int(response.headers.get("Retry-After", 60))
            if attempt < max_retries:
                # Exponential backoff with jitter
                sleep_time = min(retry_after, 2 ** attempt + random.uniform(0, 1))
                time.sleep(sleep_time)
                continue
        
        if response.status_code in (500, 502, 503, 504):
            if attempt < max_retries:
                sleep_time = 2 ** attempt + random.uniform(0, 1)
                time.sleep(sleep_time)
                continue
        
        return response
    
    raise RuntimeError(f"Max retries exceeded for {url}")
```

---

## 2. Class Structure

### File: `sources/actitime/actitime.py`

```python
import base64
import time
import random
from datetime import datetime, timedelta
from typing import Iterator, Dict, List, Any
import requests
from pyspark.sql.types import (
    StructType, StructField, LongType, StringType, 
    BooleanType, ArrayType, MapType
)


class LakeflowConnect:
    """
    actiTIME connector implementing the Lakeflow Connect interface.
    
    Connection Options:
        - base_url (required): actiTIME instance URL (e.g., https://your-company.actitime.com)
        - username (required): actiTIME username
        - password (required): actiTIME password
    """
    
    # Class-level constants
    SUPPORTED_TABLES = [...]
    TABLE_METADATA = {...}
    TABLE_SCHEMAS = {...}
```

---

## 3. Supported Tables (15 tables)

### Core Business Objects (CDC/Append)

| Table | Primary Key | Cursor Field | Ingestion Type | Required Options |
|-------|-------------|--------------|----------------|------------------|
| `customers` | `id` | `created` | `cdc` | - |
| `projects` | `id` | `created` | `cdc` | - |
| `tasks` | `id` | `created` | `cdc` | - |
| `timetrack` | `id` | `date` | `append` | `dateFrom`, `dateTo` |
| `leavetime` | `id` | `date` | `append` | `dateFrom`, `dateTo` |

### User & Organization Objects (CDC/Snapshot)

| Table | Primary Key | Cursor Field | Ingestion Type |
|-------|-------------|--------------|----------------|
| `users` | `id` | `created` | `cdc` |
| `departments` | `id` | - | `snapshot` |
| `userGroups` | `id` | - | `snapshot` |
| `userRates` | `user_id`, `date_from` | - | `snapshot` |

### Configuration Objects (Snapshot)

| Table | Primary Key | Ingestion Type |
|-------|-------------|----------------|
| `typesOfWork` | `id` | `snapshot` |
| `leaveTypes` | `id` | `snapshot` |
| `workflowStatuses` | `id` | `snapshot` |
| `timeZoneGroups` | `id` | `snapshot` |
| `settings` | (singleton) | `snapshot` |
| `holidays` | `date`, `time_zone_group_id` | `snapshot` |

---

## 4. Implementation Details by Method

### 4.1 `__init__(self, options: dict[str, str])`

```python
def __init__(self, options: dict[str, str]) -> None:
    """
    Initialize the actiTIME connector.
    
    Required options:
        - base_url: actiTIME instance URL
        - username: actiTIME username  
        - password: actiTIME password
    """
    # Validate required options
    base_url = options.get("base_url")
    username = options.get("username")
    password = options.get("password")
    
    if not all([base_url, username, password]):
        raise ValueError("actiTIME connector requires 'base_url', 'username', and 'password'")
    
    # Store configuration
    self.base_url = base_url.rstrip("/") + "/api/v1"
    
    # Build auth header (Basic Authentication)
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    
    # Configure session with proper headers
    self._session = requests.Session()
    self._session.headers.update({
        "Authorization": f"Basic {encoded}",
        "Accept": "application/json; charset=UTF-8",
        "Content-Type": "application/json; charset=UTF-8"
    })
    
    # Initialize rate limiter
    self._rate_limiter = RateLimiter(
        requests_per_second=100,
        requests_per_minute=1000
    )
```

### 4.2 `list_tables(self) -> list[str]`

```python
def list_tables(self) -> list[str]:
    """Return static list of supported tables."""
    return [
        "customers",
        "projects", 
        "tasks",
        "timetrack",
        "leavetime",
        "users",
        "departments",
        "userGroups",
        "userRates",
        "typesOfWork",
        "leaveTypes",
        "workflowStatuses",
        "timeZoneGroups",
        "settings",
        "holidays",
    ]
```

### 4.3 `get_table_schema(self, table_name: str, table_options: dict[str, str]) -> StructType`

**Strategy**: Static schemas defined per table (following GitHub pattern).

```python
def get_table_schema(self, table_name: str, table_options: dict[str, str]) -> StructType:
    """Return static schema for the specified table."""
    if table_name not in self.SUPPORTED_TABLES:
        raise ValueError(f"Table '{table_name}' is not supported.")
    
    return self._get_schema_for_table(table_name)
```

**Schema definitions** will be defined as class methods (like GitHub connector):

```python
def _get_customers_schema(self) -> StructType:
    return StructType([
        StructField("id", LongType(), False),
        StructField("name", StringType(), True),
        StructField("description", StringType(), True),
        StructField("archived", BooleanType(), True),
        StructField("created", LongType(), True),  # epoch ms
        StructField("url", StringType(), True),
        StructField("allowedActions", StructType([
            StructField("canModify", BooleanType(), True),
            StructField("canDelete", BooleanType(), True),
        ]), True),
    ])
```

### 4.4 `read_table_metadata(self, table_name: str, table_options: dict[str, str]) -> dict`

```python
def read_table_metadata(self, table_name: str, table_options: dict[str, str]) -> dict:
    """Return metadata for the specified table."""
    if table_name not in self.SUPPORTED_TABLES:
        raise ValueError(f"Table '{table_name}' is not supported.")
    
    metadata_map = {
        "customers": {
            "primary_keys": ["id"],
            "cursor_field": "created",
            "ingestion_type": "cdc",
        },
        "projects": {
            "primary_keys": ["id"],
            "cursor_field": "created", 
            "ingestion_type": "cdc",
        },
        "tasks": {
            "primary_keys": ["id"],
            "cursor_field": "created",
            "ingestion_type": "cdc",
        },
        "timetrack": {
            "primary_keys": ["id"],
            "cursor_field": "date",
            "ingestion_type": "append",
        },
        "leavetime": {
            "primary_keys": ["id"],
            "cursor_field": "date",
            "ingestion_type": "append",
        },
        "users": {
            "primary_keys": ["id"],
            "cursor_field": "created",
            "ingestion_type": "cdc",
        },
        "departments": {
            "primary_keys": ["id"],
            "ingestion_type": "snapshot",
        },
        "userGroups": {
            "primary_keys": ["id"],
            "ingestion_type": "snapshot",
        },
        "userRates": {
            "primary_keys": ["user_id", "date_from"],
            "ingestion_type": "snapshot",
        },
        "typesOfWork": {
            "primary_keys": ["id"],
            "ingestion_type": "snapshot",
        },
        "leaveTypes": {
            "primary_keys": ["id"],
            "ingestion_type": "snapshot",
        },
        "workflowStatuses": {
            "primary_keys": ["id"],
            "ingestion_type": "snapshot",
        },
        "timeZoneGroups": {
            "primary_keys": ["id"],
            "ingestion_type": "snapshot",
        },
        "settings": {
            "primary_keys": [],  # Singleton
            "ingestion_type": "snapshot",
        },
        "holidays": {
            "primary_keys": ["date", "time_zone_group_id"],
            "ingestion_type": "snapshot",
        },
    }
    
    return metadata_map[table_name]
```

### 4.5 `read_table(self, table_name: str, start_offset: dict, table_options: dict[str, str]) -> (Iterator[dict], dict)`

**Strategy**: Route to specific reader methods per table.

```python
def read_table(
    self, table_name: str, start_offset: dict, table_options: dict[str, str]
) -> (Iterator[dict], dict):
    """Read records from the specified table."""
    if table_name not in self.SUPPORTED_TABLES:
        raise ValueError(f"Table '{table_name}' is not supported.")
    
    reader_map = {
        "customers": self._read_customers,
        "projects": self._read_projects,
        "tasks": self._read_tasks,
        "timetrack": self._read_timetrack,
        "leavetime": self._read_leavetime,
        "users": self._read_users,
        "departments": self._read_departments,
        "userGroups": self._read_user_groups,
        "userRates": self._read_user_rates,
        "typesOfWork": self._read_types_of_work,
        "leaveTypes": self._read_leave_types,
        "workflowStatuses": self._read_workflow_statuses,
        "timeZoneGroups": self._read_time_zone_groups,
        "settings": self._read_settings,
        "holidays": self._read_holidays,
    }
    
    return reader_map[table_name](start_offset, table_options)
```

---

## 5. Reader Method Patterns

### 5.1 Paginated List Endpoint (customers, projects, tasks, users)

Following the **GitHub connector pattern**:

```python
def _read_customers(
    self, start_offset: dict, table_options: dict[str, str]
) -> (Iterator[dict], dict):
    """Read customers with pagination support."""
    
    # Pagination settings
    limit = int(table_options.get("limit", 100))
    max_pages = int(table_options.get("max_pages", 100))
    
    # Filter settings
    archived = table_options.get("archived", "false")
    
    records: list[dict] = []
    offset = 0
    pages_fetched = 0
    max_created = start_offset.get("cursor") if start_offset else None
    
    while pages_fetched < max_pages:
        url = f"{self.base_url}/customers"
        params = {
            "offset": offset,
            "limit": limit,
            "archived": archived,
            "sort": "+created",  # Sort by created ascending for incremental
        }
        
        response = self._make_request_with_retry("GET", url, params=params)
        
        if response.status_code != 200:
            raise RuntimeError(
                f"actiTIME API error for customers: {response.status_code} {response.text}"
            )
        
        data = response.json()
        
        if not data or not isinstance(data, list):
            break
        
        for record in data:
            records.append(record)
            
            # Track max created timestamp for cursor
            created = record.get("created")
            if created and (max_created is None or created > max_created):
                max_created = created
        
        if len(data) < limit:
            # No more pages
            break
        
        offset += limit
        pages_fetched += 1
    
    next_offset = {"cursor": max_created} if max_created else {}
    return iter(records), next_offset
```

### 5.2 Date-Range Endpoint (timetrack, leavetime)

```python
def _read_timetrack(
    self, start_offset: dict, table_options: dict[str, str]
) -> (Iterator[dict], dict):
    """Read timetrack entries with date range filtering."""
    
    # Required date range parameters
    date_from = table_options.get("dateFrom")
    date_to = table_options.get("dateTo")
    
    if not date_from or not date_to:
        raise ValueError(
            "table_options for 'timetrack' must include 'dateFrom' and 'dateTo'"
        )
    
    # Optional filters
    user_ids = table_options.get("userIds")
    
    url = f"{self.base_url}/timetrack"
    params = {
        "dateFrom": date_from,
        "dateTo": date_to,
    }
    if user_ids:
        params["userIds"] = user_ids
    
    response = self._make_request_with_retry("GET", url, params=params)
    
    if response.status_code != 200:
        raise RuntimeError(
            f"actiTIME API error for timetrack: {response.status_code} {response.text}"
        )
    
    data = response.json()
    
    # Flatten nested structure: [{userId, date, records: [...]}] -> individual records
    records: list[dict] = []
    max_date = start_offset.get("cursor") if start_offset else None
    
    for user_entry in data:
        user_id = user_entry.get("userId")
        date = user_entry.get("date")
        
        for record in user_entry.get("records", []):
            flattened = {
                "id": record.get("id"),
                "user_id": user_id,
                "date": date,
                "task_id": record.get("taskId"),
                "time": record.get("time"),
                "comment": record.get("comment"),
                "approved": record.get("approved"),
                "locked": record.get("locked"),
                "type_of_work_id": record.get("typeOfWorkId"),
            }
            records.append(flattened)
            
            if date and (max_date is None or date > max_date):
                max_date = date
    
    next_offset = {"cursor": max_date} if max_date else {}
    return iter(records), next_offset
```

### 5.3 Singleton Endpoint (settings)

```python
def _read_settings(
    self, start_offset: dict, table_options: dict[str, str]
) -> (Iterator[dict], dict):
    """Read system settings (singleton)."""
    
    url = f"{self.base_url}/settings"
    response = self._make_request_with_retry("GET", url)
    
    if response.status_code != 200:
        raise RuntimeError(
            f"actiTIME API error for settings: {response.status_code} {response.text}"
        )
    
    data = response.json()
    
    # Settings is a single object, return as single-element iterator
    return iter([data]), {}
```

### 5.4 User-Specific Endpoint (userRates)

```python
def _read_user_rates(
    self, start_offset: dict, table_options: dict[str, str]
) -> (Iterator[dict], dict):
    """Read user rates - requires iterating through all users."""
    
    # First, get all users
    users_iter, _ = self._read_users({}, table_options)
    users = list(users_iter)
    
    records: list[dict] = []
    
    for user in users:
        user_id = user.get("id")
        if not user_id:
            continue
        
        url = f"{self.base_url}/userRates/{user_id}"
        response = self._make_request_with_retry("GET", url)
        
        if response.status_code == 404:
            # User has no rates, skip
            continue
        
        if response.status_code != 200:
            raise RuntimeError(
                f"actiTIME API error for userRates/{user_id}: {response.status_code} {response.text}"
            )
        
        rates_data = response.json()
        
        for rate in rates_data:
            record = {
                "user_id": user_id,
                "date_from": rate.get("dateFrom"),
                "regular_rate": rate.get("regularRate"),
                "overtime_rate": rate.get("overtimeRate"),
                "leave_rates": rate.get("leaveRates"),
            }
            records.append(record)
    
    return iter(records), {}
```

---

## 6. Helper Methods

### 6.1 Rate-Limited Request

```python
def _make_request_with_retry(
    self,
    method: str,
    url: str,
    max_retries: int = 3,
    **kwargs
) -> requests.Response:
    """Make HTTP request with rate limiting and retry logic."""
    
    for attempt in range(max_retries + 1):
        # Apply rate limiting
        self._rate_limiter.wait_if_needed()
        
        try:
            response = self._session.request(method, url, timeout=60, **kwargs)
        except requests.exceptions.RequestException as e:
            if attempt < max_retries:
                sleep_time = 2 ** attempt + random.uniform(0, 1)
                time.sleep(sleep_time)
                continue
            raise RuntimeError(f"Request failed after {max_retries} retries: {e}")
        
        # Handle rate limiting (429)
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            if attempt < max_retries:
                sleep_time = min(retry_after, 2 ** attempt + random.uniform(0, 1))
                time.sleep(sleep_time)
                continue
        
        # Handle server errors (5xx)
        if response.status_code >= 500:
            if attempt < max_retries:
                sleep_time = 2 ** attempt + random.uniform(0, 1)
                time.sleep(sleep_time)
                continue
        
        return response
    
    raise RuntimeError(f"Max retries ({max_retries}) exceeded for {url}")
```

---

## 7. Schema Definitions (Complete List)

Each schema follows the pattern from the API documentation, using:
- `LongType()` for all integers (avoid overflow)
- `StringType()` for text and dates
- `BooleanType()` for booleans
- `StructType()` for nested objects (not flattened)
- `ArrayType()` for arrays

### Key Schemas to Implement:

1. **customers** - id, name, description, archived, created, url, allowedActions
2. **projects** - id, name, description, customerId, archived, created, workflowEnabled, defaultTypeOfWorkId, url, allowedActions
3. **tasks** - id, name, description, projectId, customerId, archived, created, typeOfWorkId, workflowStatusId, deadline, estimatedTime, url, allowedActions
4. **timetrack** - id, user_id, date, task_id, time, comment, approved, locked, type_of_work_id
5. **leavetime** - id, user_id, date, leave_type_id, time, approved
6. **users** - id, firstName, lastName, middleName, username, email, departmentId, active, created, timeZoneGroupId, userGroups, userRoles
7. **departments** - id, name, description, parentId, managerId
8. **userGroups** - id, name, description
9. **userRates** - user_id, date_from, regular_rate, overtime_rate, leave_rates
10. **typesOfWork** - id, name, description, archived, billable
11. **leaveTypes** - id, name, description, archived, paidLeave, autoAccrual
12. **workflowStatuses** - id, name, type, order
13. **timeZoneGroups** - id, name, timeZone
14. **settings** - workdayDuration, weekStartDay, dateFormat, timeFormat, currencyCode, decimalSeparator, thousandsSeparator
15. **holidays** - date, name, timeZoneGroupId

---

## 8. Testing Strategy

### Unit Tests (`test/test_actitime_lakeflow_connect.py`)

```python
from tests.test_suite import LakeflowConnectTester

def test_actitime_connector():
    """Run standard test suite against actiTIME connector."""
    tester = LakeflowConnectTester(
        connector_module="sources.actitime.actitime",
        config_path="sources/actitime/configs/dev_config.json"
    )
    tester.run_all_tests()
```

### Dev Config Template (`configs/dev_config.json`)

```json
{
    "base_url": "https://your-company.actitime.com",
    "username": "your-username",
    "password": "your-password"
}
```

### Table Config (`configs/dev_table_config.json`)

```json
{
    "timetrack": {
        "dateFrom": "2024-01-01",
        "dateTo": "2024-12-31"
    },
    "leavetime": {
        "dateFrom": "2024-01-01", 
        "dateTo": "2024-12-31"
    }
}
```

---

## 9. Implementation Checklist

### Phase 1: Core Structure
- [ ] Create `actitime.py` with class skeleton
- [ ] Implement `__init__` with auth and rate limiting
- [ ] Implement `list_tables()`
- [ ] Implement `get_table_schema()` with static schemas
- [ ] Implement `read_table_metadata()`

### Phase 2: Reader Methods
- [ ] Implement `_make_request_with_retry()` with rate limiting
- [ ] Implement `_read_customers()` (paginated)
- [ ] Implement `_read_projects()` (paginated)
- [ ] Implement `_read_tasks()` (paginated)
- [ ] Implement `_read_users()` (paginated)
- [ ] Implement `_read_timetrack()` (date-range, flattened)
- [ ] Implement `_read_leavetime()` (date-range, flattened)

### Phase 3: Configuration Tables
- [ ] Implement `_read_departments()` (snapshot)
- [ ] Implement `_read_user_groups()` (snapshot)
- [ ] Implement `_read_types_of_work()` (snapshot)
- [ ] Implement `_read_leave_types()` (snapshot)
- [ ] Implement `_read_workflow_statuses()` (snapshot)
- [ ] Implement `_read_time_zone_groups()` (snapshot)
- [ ] Implement `_read_settings()` (singleton)
- [ ] Implement `_read_holidays()` (snapshot)

### Phase 4: Advanced Features
- [ ] Implement `_read_user_rates()` (parent-child pattern)
- [ ] Add error handling for all edge cases
- [ ] Implement incremental cursor logic for CDC tables

### Phase 5: Testing & Documentation
- [ ] Create test configuration files
- [ ] Run test suite
- [ ] Fix any issues found
- [ ] Create README.md (Step 6)
- [ ] Create connector_spec.yaml (Step 7)
- [ ] Run merge script (Step 8)

---

## 10. Key Implementation Notes

1. **Rate Limiting**: actiTIME has generous limits (100/sec, 1000/min) but we still need proper handling to avoid IP bans (3 failed auth attempts = 1 min ban).

2. **Timetrack/Leavetime Flattening**: The API returns nested structures `[{userId, date, records: [...]}]`. We need to flatten these to individual records with `user_id`, `date`, and record fields.

3. **UserRates Pattern**: This is a child-of-parent pattern - we need to iterate through all users and fetch their rates individually.

4. **Cursor Fields**: 
   - For CDC tables: Use `created` timestamp (epoch ms)
   - For append tables (timetrack/leavetime): Use `date` field

5. **No `read_table_deletes`**: actiTIME uses soft deletes (`archived` field). We can track archived records, but the API doesn't provide a separate deleted records endpoint. Consider using `cdc` instead of `cdc_with_deletes`.

6. **Nested Structures**: Follow the guideline to NOT flatten nested objects. Keep `allowedActions` as a StructType.

---

## 11. Dependencies

```python
# Standard library
import base64
import time
import random
from datetime import datetime, timedelta
from typing import Iterator, Dict, List, Any

# Third-party
import requests

# PySpark
from pyspark.sql.types import (
    StructType, StructField, LongType, StringType, 
    BooleanType, ArrayType, MapType, DecimalType
)
```

No additional dependencies required beyond `requests` (already used by other connectors).

---

## 12. Benchmark Enhancements (Post-Review)

Based on benchmarking against Alpha Vantage, Stripe, Mixpanel, GitHub, HubSpot, and Zendesk connectors, the following enhancements are incorporated:

### 12.1 Proactive Rate Limit Header Checking

**Enhancement**: Read rate limit response headers to slow down preemptively.

```python
def _check_rate_limit_headers(self, response: requests.Response) -> None:
    """Proactively slow down if rate limit headers indicate we're close to limits."""
    remaining = response.headers.get("X-Ratelimit-Remaining")
    reset_seconds = response.headers.get("X-Ratelimit-Reset")
    
    if remaining is not None:
        try:
            remaining_int = int(remaining)
            if remaining_int < 10:
                # Slow down preemptively when close to limit
                time.sleep(0.5)
            elif remaining_int < 5:
                time.sleep(1.0)
        except ValueError:
            pass
```

### 12.2 Authentication Failure Tracking (IP Ban Prevention)

**Enhancement**: Track auth failures to avoid the 3-failures-in-10-seconds IP ban.

```python
def __init__(self, options):
    ...
    # Auth failure tracking to prevent IP ban
    self._auth_failure_timestamps: list[float] = []

def _track_auth_failure(self) -> None:
    """Track auth failures to avoid IP ban (3 failures in 10s = 1 min ban)."""
    now = time.time()
    # Keep only failures from the last 10 seconds
    self._auth_failure_timestamps = [
        t for t in self._auth_failure_timestamps if now - t < 10
    ]
    self._auth_failure_timestamps.append(now)
    
    # If we have 2 failures already, preventive delay to avoid ban
    if len(self._auth_failure_timestamps) >= 2:
        time.sleep(5)  # Wait before next attempt
```

### 12.3 Custom Exception Class for Structured Errors

**Enhancement**: Better error handling with actionable messages (inspired by Alpha Vantage).

```python
class ActitimeAPIError(Exception):
    """Custom exception for actiTIME API errors with structured information."""
    
    def __init__(self, status_code: int, key: str, message: str, url: str):
        self.status_code = status_code
        self.key = key  # e.g., "api.error.customer_exists"
        self.message = message
        self.url = url
        super().__init__(f"actiTIME API Error [{status_code}] at {url}: {key} - {message}")
    
    @classmethod
    def from_response(cls, response: requests.Response, url: str) -> "ActitimeAPIError":
        """Factory method to create error from response."""
        try:
            error_data = response.json()
            key = error_data.get("key", "unknown_error")
            message = error_data.get("message", response.text)
        except Exception:
            key = "parse_error"
            message = response.text[:500] if response.text else "No response body"
        
        return cls(response.status_code, key, message, url)
```

### 12.4 Centralized Table Configuration (Stripe Pattern)

**Enhancement**: Single source of truth for all table metadata (adopted from Stripe).

```python
def __init__(self, options):
    ...
    # Centralized table configuration (Stripe pattern)
    self._table_config = {
        "customers": {
            "primary_keys": ["id"],
            "cursor_field": "created",
            "ingestion_type": "cdc",
            "endpoint": "customers",
            "supports_pagination": True,
            "supports_archived_filter": True,
        },
        "projects": {
            "primary_keys": ["id"],
            "cursor_field": "created",
            "ingestion_type": "cdc",
            "endpoint": "projects",
            "supports_pagination": True,
            "supports_archived_filter": True,
        },
        "timetrack": {
            "primary_keys": ["id"],
            "cursor_field": "date",
            "ingestion_type": "append",
            "endpoint": "timetrack",
            "requires_date_range": True,
            "flatten_records": True,
        },
        # ... other tables
    }
```

### 12.5 Reusable Schema Components (Stripe Pattern)

**Enhancement**: Define common nested schemas once and reuse.

```python
def __init__(self, options):
    ...
    # Reusable nested schemas (Stripe best practice)
    self._allowed_actions_schema = StructType([
        StructField("canModify", BooleanType(), True),
        StructField("canDelete", BooleanType(), True),
    ])
    
    self._task_allowed_actions_schema = StructType([
        StructField("canModify", BooleanType(), True),
        StructField("canDelete", BooleanType(), True),
        StructField("canComplete", BooleanType(), True),
    ])
```

### 12.6 Connection Test Method

**Enhancement**: Validate credentials before full sync (new feature).

```python
def test_connection(self) -> dict:
    """
    Test the connection to actiTIME API.
    
    Returns:
        Dictionary with status and message:
        - {"status": "success", "message": "Connection successful"}
        - {"status": "error", "message": "Error details..."}
    """
    try:
        # Use a lightweight endpoint to test connectivity
        url = f"{self.base_url}/settings"
        response = self._make_request_with_retry("GET", url)
        
        if response.status_code == 200:
            return {"status": "success", "message": "Connection successful"}
        elif response.status_code == 401:
            return {"status": "error", "message": "Authentication failed: Invalid credentials"}
        elif response.status_code == 403:
            return {"status": "error", "message": "Authorization failed: Insufficient permissions"}
        else:
            return {"status": "error", "message": f"API error: {response.status_code} {response.text}"}
    except Exception as e:
        return {"status": "error", "message": f"Connection failed: {str(e)}"}
```

### 12.7 CDC Limitation Documentation

**Critical Note**: actiTIME API does NOT provide `updated_at` timestamps for most objects. This has important implications:

| Object Type | Has `created` | Has `updated_at` | True CDC Possible? |
|-------------|---------------|------------------|-------------------|
| customers | ✅ | ❌ | ⚠️ New records only |
| projects | ✅ | ❌ | ⚠️ New records only |
| tasks | ✅ | ❌ | ⚠️ New records only |
| users | ✅ | ❌ | ⚠️ New records only |
| timetrack | ❌ | ❌ | ⚠️ Date-range only |
| leavetime | ❌ | ❌ | ⚠️ Date-range only |

**Recommendation**: 
- For tables marked as `cdc`: Can only capture NEW records, not updates to existing records
- For production use cases requiring update tracking: Use `snapshot` ingestion with periodic full refreshes
- Document this limitation clearly in README.md

### 12.8 Enhanced Unit Tests

```python
# test/test_actitime_lakeflow_connect.py

import pytest
from unittest.mock import Mock, patch, MagicMock
import time

class TestActitimeConnector:
    """Unit tests for actiTIME connector."""
    
    @pytest.fixture
    def mock_options(self):
        return {
            "base_url": "https://test.actitime.com",
            "username": "test_user",
            "password": "test_pass"
        }
    
    @pytest.fixture
    def connector(self, mock_options):
        """Create connector with mock credentials."""
        with patch("requests.Session"):
            return LakeflowConnect(mock_options)
    
    def test_init_validates_required_options(self):
        """Verify initialization fails without required options."""
        with pytest.raises(ValueError, match="requires 'base_url'"):
            LakeflowConnect({})
        
        with pytest.raises(ValueError, match="requires.*username"):
            LakeflowConnect({"base_url": "http://test"})
    
    def test_list_tables_returns_all_15_tables(self, connector):
        """Verify all 15 tables are listed."""
        tables = connector.list_tables()
        assert len(tables) == 15
        assert "customers" in tables
        assert "timetrack" in tables
        assert "settings" in tables
    
    def test_get_table_schema_returns_structtype(self, connector):
        """Verify schemas are valid StructType objects."""
        from pyspark.sql.types import StructType
        
        for table in connector.list_tables():
            schema = connector.get_table_schema(table, {})
            assert isinstance(schema, StructType)
    
    def test_read_table_metadata_returns_required_keys(self, connector):
        """Verify metadata contains required keys."""
        for table in connector.list_tables():
            metadata = connector.read_table_metadata(table, {})
            assert "primary_keys" in metadata
            assert "ingestion_type" in metadata
            assert metadata["ingestion_type"] in ["cdc", "append", "snapshot"]
    
    @patch("requests.Session.request")
    def test_rate_limit_enforced(self, mock_request, connector):
        """Verify rate limiter enforces delays."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.headers = {}
        mock_request.return_value = mock_response
        
        start = time.time()
        for _ in range(5):
            connector._make_request_with_retry("GET", "http://test/customers")
        elapsed = time.time() - start
        
        # With 100 req/sec, 5 requests should take ~50ms minimum
        assert elapsed >= 0.04
    
    @patch("requests.Session.request")
    def test_retry_on_429(self, mock_request, connector):
        """Verify 429 responses trigger retry."""
        # First call returns 429, second returns 200
        mock_429 = Mock()
        mock_429.status_code = 429
        mock_429.headers = {"Retry-After": "1"}
        
        mock_200 = Mock()
        mock_200.status_code = 200
        mock_200.json.return_value = []
        mock_200.headers = {}
        
        mock_request.side_effect = [mock_429, mock_200]
        
        response = connector._make_request_with_retry("GET", "http://test/customers")
        assert response.status_code == 200
        assert mock_request.call_count == 2
    
    @patch("requests.Session.request")
    def test_timetrack_requires_date_range(self, mock_request, connector):
        """Verify timetrack raises error without date range."""
        with pytest.raises(ValueError, match="dateFrom.*dateTo"):
            connector.read_table("timetrack", None, {})
    
    def test_invalid_table_raises_error(self, connector):
        """Verify invalid table names raise appropriate errors."""
        with pytest.raises(ValueError, match="not supported"):
            connector.get_table_schema("invalid_table", {})
        
        with pytest.raises(ValueError, match="not supported"):
            connector.read_table_metadata("invalid_table", {})
```

---

## 13. Implementation Priority Matrix

Based on benchmark analysis, prioritize implementation in this order:

| Priority | Component | Effort | Impact | Notes |
|----------|-----------|--------|--------|-------|
| P0 | Core class structure | Medium | High | Foundation |
| P0 | Rate limiting + retry | Low | High | Prevents bans |
| P0 | Basic table reads | Medium | High | Core functionality |
| P1 | Custom error handling | Low | Medium | Better debugging |
| P1 | Centralized config | Medium | Medium | Maintainability |
| P1 | Connection test | Low | Medium | UX improvement |
| P2 | Auth failure tracking | Low | Low | Edge case handling |
| P2 | Unit tests | Medium | Medium | Quality assurance |
| P3 | Logging framework | Medium | Low | Production debugging |

---

## 14. Final Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       LakeflowConnect                            │
├─────────────────────────────────────────────────────────────────┤
│ __init__(options)                                                │
│   ├── Validate required options (base_url, username, password)  │
│   ├── Build auth header (Basic Auth)                            │
│   ├── Initialize requests.Session                               │
│   ├── Initialize RateLimiter                                    │
│   ├── Initialize _table_config (centralized)                    │
│   └── Initialize reusable schema components                     │
├─────────────────────────────────────────────────────────────────┤
│ list_tables() -> list[str]                                      │
│ get_table_schema(table_name, options) -> StructType             │
│ read_table_metadata(table_name, options) -> dict                │
│ read_table(table_name, offset, options) -> (Iterator, dict)     │
│ test_connection() -> dict                                       │
├─────────────────────────────────────────────────────────────────┤
│ _make_request_with_retry(method, url, **kwargs) -> Response     │
│   ├── RateLimiter.wait_if_needed()                              │
│   ├── _check_rate_limit_headers()                               │
│   ├── Retry with exponential backoff on 429/5xx                 │
│   └── _track_auth_failure() on 401                              │
├─────────────────────────────────────────────────────────────────┤
│ Reader Methods:                                                  │
│   ├── _read_paginated() - customers, projects, tasks, users     │
│   ├── _read_date_range() - timetrack, leavetime                 │
│   ├── _read_simple() - departments, userGroups, typesOfWork...  │
│   ├── _read_singleton() - settings                              │
│   └── _read_user_rates() - parent-child pattern                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         RateLimiter                              │
├─────────────────────────────────────────────────────────────────┤
│ requests_per_second: int = 100                                  │
│ requests_per_minute: int = 1000                                 │
│ _request_timestamps: list[float]                                │
│ _last_request_time: float                                       │
├─────────────────────────────────────────────────────────────────┤
│ wait_if_needed() -> None                                        │
│   ├── Enforce min delay (10ms between requests)                 │
│   ├── Clean old timestamps (>60s)                               │
│   └── Sleep if at minute limit                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      ActitimeAPIError                            │
├─────────────────────────────────────────────────────────────────┤
│ status_code: int                                                │
│ key: str          # e.g., "api.error.customer_exists"           │
│ message: str                                                    │
│ url: str                                                        │
├─────────────────────────────────────────────────────────────────┤
│ from_response(response, url) -> ActitimeAPIError                │
└─────────────────────────────────────────────────────────────────┘
```
