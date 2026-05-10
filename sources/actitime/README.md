# Lakeflow actiTIME Community Connector

This documentation provides setup instructions and reference information for the actiTIME source connector. The connector allows you to extract time tracking, project management, and user data from actiTIME and load it into your data lake or warehouse.

## Key Features

- **13 supported tables** covering time tracking, projects, customers, users, and configuration data
- **Automatic rate limiting** - Respects actiTIME's API limits (100 req/sec, 1000 req/min)
- **Retry with exponential backoff** - Handles transient failures gracefully
- **Incremental sync** - Cursor-based sync for customers, projects, tasks, and users
- **Date range filtering** - Efficient time tracking and leave time data retrieval

## Prerequisites

- **actiTIME account**: You need an actiTIME account with API access enabled.
- **API credentials**: Username and password for Basic Authentication.
- **Network access**: The environment running the connector must be able to reach your actiTIME instance (e.g., `https://your-company.actitime.com`).

## Setup

### Required Connection Parameters

To configure the connector, provide the following parameters in your connector options:

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `base_url` | string | Yes | actiTIME instance URL | `https://your-company.actitime.com` |
| `username` | string | Yes | actiTIME username | `admin@company.com` |
| `password` | string | Yes | actiTIME password | `your-password` |
| `externalOptionsAllowList` | string | Yes | Comma-separated list of table-specific options | `dateFrom,dateTo,userIds,taskIds,leaveTypeIds,archived,limit,max_pages` |

### Table-Specific Options (externalOptionsAllowList)

The following table-specific options must be included in the `externalOptionsAllowList` connection parameter:

```
dateFrom,dateTo,userIds,taskIds,leaveTypeIds,archived,limit,max_pages
```

| Option | Description | Used By |
|--------|-------------|---------|
| `dateFrom` | Start date (YYYY-MM-DD) | timetrack, leavetime, holidays |
| `dateTo` | End date (YYYY-MM-DD) | timetrack, leavetime, holidays |
| `userIds` | Comma-separated user IDs to filter | timetrack, leavetime |
| `taskIds` | Comma-separated task IDs to filter | timetrack |
| `leaveTypeIds` | Comma-separated leave type IDs | leavetime |
| `archived` | Include archived records ("true"/"false") | customers, projects, tasks |
| `limit` | Page size for pagination (default: 100) | paginated endpoints |
| `max_pages` | Maximum pages to fetch (default: 100) | paginated endpoints |

### Getting Your actiTIME Credentials

1. Log in to your actiTIME instance
2. API access uses your regular actiTIME login credentials
3. Ensure your user account has appropriate permissions to read the data you need
4. **Important**: Keep your credentials secure - never share them publicly

### Using Databricks Secrets (Recommended)

For production deployments, store your credentials in Databricks Secrets:

```bash
# Create a secret scope
databricks secrets create-scope --scope actitime_secrets

# Add your credentials
databricks secrets put --scope actitime_secrets --key username
databricks secrets put --scope actitime_secrets --key password
```

Then in your pipeline:
```python
USERNAME = dbutils.secrets.get("actitime_secrets", "username")
PASSWORD = dbutils.secrets.get("actitime_secrets", "password")
```

### Create a Unity Catalog Connection

A Unity Catalog connection for this connector can be created in two ways via the UI:

1. Follow the Lakeflow Community Connector UI flow from the "Add Data" page
2. Select any existing Lakeflow Community Connector connection for this source or create a new one
3. Set `externalOptionsAllowList` to: `dateFrom,dateTo,userIds,taskIds,leaveTypeIds,archived,limit,max_pages`

The connection can also be created using the standard Unity Catalog API.

## Supported Objects

The actiTIME connector supports **13 tables** across multiple categories:

### Core Business Tables (5 tables)

| Table Name | Primary Key | Cursor Field | Ingestion Type | Description |
|------------|-------------|--------------|----------------|-------------|
| `customers` | `id` | `created` | cdc | Client/customer records |
| `projects` | `id` | `created` | cdc | Project records |
| `tasks` | `id` | `created` | cdc | Task records |
| `timetrack` | `id`, `userId`, `date` | `date` | append | Time entries |
| `leavetime` | `id`, `userId`, `date` | `date` | append | Leave/time-off entries |

**Required Options for timetrack and leavetime:**
- `dateFrom`: Start date (YYYY-MM-DD)
- `dateTo`: End date (YYYY-MM-DD)

**Optional Options for customers, projects, tasks:**
- `archived`: Include archived records ("true"/"false", default: "false")

### User Tables (3 tables)

| Table Name | Primary Key | Ingestion Type | Description |
|------------|-------------|----------------|-------------|
| `users` | `id` | cdc | User accounts |
| `departments` | `id` | snapshot | Department definitions |
| `userRates` | `userId`, `dateFrom` | snapshot | User billing rates |

### Configuration Tables (5 tables)

| Table Name | Primary Key | Ingestion Type | Description |
|------------|-------------|----------------|-------------|
| `typesOfWork` | `id` | snapshot | Work type definitions |
| `leaveTypes` | `id` | snapshot | Leave type definitions |
| `workflowStatuses` | `id` | snapshot | Task workflow statuses |
| `timeZoneGroups` | `id` | snapshot | Time zone configurations |
| `info` | `id` | snapshot | System settings (company info, formats, features) |

**Note**: The actiTIME API does not provide endpoints for `userGroups` or `holidays` - these are managed through the web interface only.

### Ingestion Types

- **cdc**: Change Data Capture - incremental sync using cursor field, supports upserts
- **append**: Append-only - new records are added, no updates or deletes
- **snapshot**: Full refresh - entire table is replaced on each sync

## Data Type Mapping

| actiTIME Type | Spark Type | Notes |
|---------------|------------|-------|
| Integer ID | LongType | Primary keys like `id`, `userId` |
| String | StringType | Names, descriptions, URLs |
| Boolean | BooleanType | Flags like `archived`, `approved` |
| Timestamp (epoch ms) | LongType | `created` field stored as epoch milliseconds |
| Date (YYYY-MM-DD) | StringType | Date fields like `dateFrom`, `dateTo` |
| Decimal | DecimalType(18,2) | Rates, amounts |
| Nested Object | MapType/StructType | Objects like `allowedActions` |
| Array | ArrayType | Lists like `leaveRates` |

## How to Run

### Step 1: Clone/Copy the Source Connector Code

Follow the Lakeflow Community Connector UI, which will guide you through setting up a pipeline using the selected source connector code.

### Step 2: Configure Your Pipeline

1. Update the `pipeline_spec` in the main pipeline file (e.g., `ingest.py`).
2. Configure each table with its required options.

#### Example Pipeline Configuration

```python
# Get credentials from secrets
BASE_URL = "https://your-company.actitime.com"
USERNAME = dbutils.secrets.get("actitime_secrets", "username")
PASSWORD = dbutils.secrets.get("actitime_secrets", "password")

pipeline_spec = {
    "connection_name": "actitime_connection",
    "objects": [
        # Customers - incremental sync
        {
            "table": {
                "source_table": "customers",
                "destination_catalog": "my_catalog",
                "destination_schema": "bronze",
                "destination_table": "actitime_customers",
                "table_configuration": {
                    "base_url": BASE_URL,
                    "username": USERNAME,
                    "password": PASSWORD,
                    "archived": "false"
                }
            }
        },
        # Projects - incremental sync
        {
            "table": {
                "source_table": "projects",
                "destination_catalog": "my_catalog",
                "destination_schema": "bronze",
                "destination_table": "actitime_projects",
                "table_configuration": {
                    "base_url": BASE_URL,
                    "username": USERNAME,
                    "password": PASSWORD,
                    "archived": "false"
                }
            }
        },
        # Time tracking - date range required
        {
            "table": {
                "source_table": "timetrack",
                "destination_catalog": "my_catalog",
                "destination_schema": "bronze",
                "destination_table": "actitime_timetrack",
                "table_configuration": {
                    "base_url": BASE_URL,
                    "username": USERNAME,
                    "password": PASSWORD,
                    "dateFrom": "2024-01-01",
                    "dateTo": "2024-12-31"
                }
            }
        },
        # Users - incremental sync
        {
            "table": {
                "source_table": "users",
                "destination_catalog": "my_catalog",
                "destination_schema": "bronze",
                "destination_table": "actitime_users",
                "table_configuration": {
                    "base_url": BASE_URL,
                    "username": USERNAME,
                    "password": PASSWORD
                }
            }
        },
        # Types of work - snapshot
        {
            "table": {
                "source_table": "typesOfWork",
                "destination_catalog": "my_catalog",
                "destination_schema": "bronze",
                "destination_table": "actitime_types_of_work",
                "table_configuration": {
                    "base_url": BASE_URL,
                    "username": USERNAME,
                    "password": PASSWORD
                }
            }
        }
    ]
}
```

3. (Optional) Customize the source connector code if needed for special use cases.

### Step 3: Run and Schedule the Pipeline

#### Best Practices

- **Start Small**: Begin by syncing a subset of tables to test your pipeline
- **Use Date Ranges**: For timetrack and leavetime, use appropriate date ranges to limit data volume
- **Use Incremental Sync**: Leverage cursor-based sync for customers, projects, tasks, and users
- **Set Appropriate Schedules**: Balance data freshness requirements with API usage
- **Respect Rate Limits**: actiTIME enforces 100 req/sec and 1000 req/min - the connector handles this automatically
- **Store Credentials Securely**: Use Databricks Secrets instead of hardcoding credentials

#### Rate Limits

actiTIME enforces the following rate limits:

| Limit | Value | Description |
|-------|-------|-------------|
| Per Second | 100 requests | Per user account |
| Per Minute | 1000 requests | Per user account |
| Auth Failures | 3 in 10 seconds | Results in IP ban |

The connector automatically handles rate limiting with built-in delays and backoff.

#### Troubleshooting

**Common Issues:**

1. **Authentication Failed (401)**:
   - Verify your username and password are correct
   - Ensure your user account has API access enabled
   - Check that you haven't exceeded authentication failure limits (3 failures in 10 seconds = IP ban)

2. **Rate Limit Exceeded (429)**:
   - The connector handles this automatically with exponential backoff
   - If persistent, reduce the frequency of your pipeline runs

3. **Endpoint Not Found (404)**:
   - Some endpoints may not be available depending on your actiTIME subscription
   - Note: `userGroups` and `holidays` are not exposed via the actiTIME API

4. **Missing Date Range**:
   - `timetrack` and `leavetime` tables require `dateFrom` and `dateTo` options
   - Ensure dates are in YYYY-MM-DD format

5. **Empty Results**:
   - Verify the date range contains data
   - Check if `archived=false` is filtering out records you need
   - Ensure your user has read permissions for the requested data

## References

- [actiTIME API Documentation](https://www.actitime.com/api-documentation)
- [actiTIME Website](https://www.actitime.com)
- [actiTIME Help Center](https://www.actitime.com/help)
