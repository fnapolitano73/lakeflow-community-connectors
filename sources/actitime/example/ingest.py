"""
actiTIME Ingestion Pipeline Example

This example demonstrates how to ingest time tracking and project management
data from actiTIME into Databricks. All 13 supported tables are included.

Tables included:
=================
Core Business Tables (5):
  1. customers   - Client/customer records (CDC)
  2. projects    - Project records (CDC)
  3. tasks       - Task records (CDC)
  4. timetrack   - Time entries (Append, requires dateFrom/dateTo)
  5. leavetime   - Leave/time-off entries (Append, requires dateFrom/dateTo)

User Tables (3):
  6. users       - User accounts (CDC)
  7. departments - Department definitions (Snapshot)
  8. userRates   - User billing rates (Snapshot)

Configuration Tables (5):
  9. typesOfWork      - Work type definitions (Snapshot)
  10. leaveTypes      - Leave type definitions (Snapshot)
  11. workflowStatuses - Task workflow statuses (Snapshot)
  12. timeZoneGroups   - Time zone configurations (Snapshot)
  13. info            - System settings/company info (Snapshot)

Credentials:
    Store credentials in Databricks secrets for production:
    - Create scope: databricks secrets create-scope --scope actitime_secrets
    - Add secrets: databricks secrets put --scope actitime_secrets --key username
                   databricks secrets put --scope actitime_secrets --key password

Rate Limits:
    actiTIME enforces rate limits (100 req/sec, 1000 req/min).
    The connector handles this automatically with built-in rate limiting.
"""

from pipeline.ingestion_pipeline import ingest
from libs.source_loader import get_register_function

# =============================================================================
# CONFIGURATION VARIABLES
# =============================================================================
# Connector source name
SOURCE_NAME = "actitime"

# Destination catalog and schema (update these for your environment)
DESTINATION_CATALOG = "fna_demo"
DESTINATION_SCHEMA = "bronze_actitime"

# Unity Catalog connection name (update with your connection name)
CONNECTION_NAME = "fna_actitime_conn"

# Date range for time-based tables (timetrack, leavetime)
# Adjust these for your incremental load window
DATE_FROM = "2024-01-01"
DATE_TO = "2024-12-31"


# =============================================================================
# PIPELINE SPECIFICATION
# =============================================================================
# Organized by category: Core Business, Users, Configuration
# Each table is configured with appropriate ingestion type and options
# =============================================================================

pipeline_spec = {
    "connection_name": CONNECTION_NAME,
    "objects": [
        # =====================================================================
        # CORE BUSINESS TABLES (5 tables)
        # =====================================================================
        
        # 1. Customers - Client/customer records
        # Ingestion: CDC (incremental with upserts using 'created' cursor)
        {
            "table": {
                "source_table": "customers",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "customers",
                "table_configuration": {
                    "archived": "false",  # Set to "true" to include archived
                },
            }
        },
        
        # 2. Projects - Project records
        # Ingestion: CDC (incremental with upserts using 'created' cursor)
        {
            "table": {
                "source_table": "projects",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "projects",
                "table_configuration": {
                    "archived": "false",
                },
            }
        },
        
        # 3. Tasks - Task records
        # Ingestion: CDC (incremental with upserts using 'created' cursor)
        {
            "table": {
                "source_table": "tasks",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "tasks",
                "table_configuration": {
                    "archived": "false",
                },
            }
        },
        
        # 4. Timetrack - Time entries
        # Ingestion: Append (requires date range)
        {
            "table": {
                "source_table": "timetrack",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "timetrack",
                "table_configuration": {
                    "dateFrom": DATE_FROM,
                    "dateTo": DATE_TO,
                    # Optional filters:
                    # "userIds": "1,2,3",    # Filter by specific users
                    # "taskIds": "10,20,30", # Filter by specific tasks
                },
            }
        },
        
        # 5. Leavetime - Leave/time-off entries
        # Ingestion: Append (requires date range)
        {
            "table": {
                "source_table": "leavetime",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "leavetime",
                "table_configuration": {
                    "dateFrom": DATE_FROM,
                    "dateTo": DATE_TO,
                    # Optional filters:
                    # "userIds": "1,2,3",           # Filter by specific users
                    # "leaveTypeIds": "100,200",    # Filter by leave types
                },
            }
        },
        
        # =====================================================================
        # USER TABLES (3 tables)
        # =====================================================================
        
        # 6. Users - User accounts
        # Ingestion: CDC (incremental with upserts)
        {
            "table": {
                "source_table": "users",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "users",
                "table_configuration": {},
            }
        },
        
        # 7. Departments - Department definitions
        # Ingestion: Snapshot (full refresh each sync)
        {
            "table": {
                "source_table": "departments",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "departments",
                "table_configuration": {},
            }
        },
        
        # 8. User Rates - User billing rates
        # Ingestion: Snapshot (full refresh each sync)
        {
            "table": {
                "source_table": "userRates",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "user_rates",
                "table_configuration": {},
            }
        },
        
        # =====================================================================
        # CONFIGURATION TABLES (5 tables)
        # =====================================================================
        
        # 9. Types of Work - Work type definitions
        # Ingestion: Snapshot (full refresh each sync)
        {
            "table": {
                "source_table": "typesOfWork",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "types_of_work",
                "table_configuration": {},
            }
        },
        
        # 10. Leave Types - Leave type definitions
        # Ingestion: Snapshot (full refresh each sync)
        {
            "table": {
                "source_table": "leaveTypes",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "leave_types",
                "table_configuration": {},
            }
        },
        
        # 11. Workflow Statuses - Task workflow statuses
        # Ingestion: Snapshot (full refresh each sync)
        {
            "table": {
                "source_table": "workflowStatuses",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "workflow_statuses",
                "table_configuration": {},
            }
        },
        
        # 12. Time Zone Groups - Time zone configurations
        # Ingestion: Snapshot (full refresh each sync)
        {
            "table": {
                "source_table": "timeZoneGroups",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "time_zone_groups",
                "table_configuration": {},
            }
        },
        
        # 13. Info - System settings (company info, formats, features)
        # Ingestion: Snapshot (full refresh each sync)
        {
            "table": {
                "source_table": "info",
                "destination_catalog": DESTINATION_CATALOG,
                "destination_schema": DESTINATION_SCHEMA,
                "destination_table": "system_info",
                "table_configuration": {},
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
