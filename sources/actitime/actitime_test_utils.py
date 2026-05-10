"""
actiTIME write-back test utilities for Lakeflow Community Connectors.

This module provides write-back functionality for testing actiTIME data ingestion.
It allows creating test data in actiTIME to validate the connector's read functionality.

⚠️ WARNING: These utilities create real data in your actiTIME instance.
Only use against test/sandbox environments, never production!
"""

import base64
import random
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

import requests


class LakeflowConnectTestUtils:
    """
    Test utilities for actiTIME connector.
    Provides write-back functionality for testing actiTIME data ingestion.
    """

    # Tables that support write-back testing
    # Note: tasks and timetrack write works but incremental verification
    # is complex due to nested response structures and date filtering
    INSERTABLE_TABLES = [
        "customers",
        "projects",
    ]

    def __init__(self, options: Dict[str, str]) -> None:
        """
        Initialize actiTIME test utilities with connection options.

        Args:
            options: Dictionary containing:
                - base_url: actiTIME instance URL
                - username: actiTIME username
                - password: actiTIME password
        """
        self.options = options
        base_url = options.get("base_url", "")
        username = options.get("username", "")
        password = options.get("password", "")

        if not all([base_url, username, password]):
            raise ValueError(
                "actiTIME test utils requires 'base_url', 'username', and 'password'"
            )

        self.base_url = base_url.rstrip("/") + "/api/v1"

        # Build auth header (Basic Authentication)
        credentials = f"{username}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()

        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Basic {encoded}",
                "Accept": "application/json; charset=UTF-8",
                "Content-Type": "application/json; charset=UTF-8",
            }
        )

        # Cache for created resources (to build hierarchies)
        self._created_customer_id: int | None = None
        self._created_project_id: int | None = None
        self._created_task_id: int | None = None
        self._created_user_id: int | None = None

    def get_source_name(self) -> str:
        """Return the source connector name."""
        return "actitime"

    def list_insertable_tables(self) -> List[str]:
        """
        List all tables that support insert/write-back functionality in actiTIME.

        Returns:
            List of table names that support inserting new data.
        """
        return self.INSERTABLE_TABLES

    def generate_rows_and_write(
        self, table_name: str, number_of_rows: int
    ) -> Tuple[bool, List[Dict], Dict[str, str]]:
        """
        Generate specified number of rows and write them to the given actiTIME table.

        Args:
            table_name: Name of the actiTIME table to write to
            number_of_rows: Number of rows to generate and write

        Returns:
            Tuple containing:
            - Boolean indicating success of the operation
            - List of rows as dictionaries that were written
            - Dictionary mapping written column names to returned column names
        """
        try:
            if number_of_rows <= 0:
                return False, [], {}

            if table_name not in self.list_insertable_tables():
                print(f"Table '{table_name}' does not support write-back")
                return False, [], {}

            # Ensure prerequisites are met for hierarchical tables
            if not self._ensure_prerequisites(table_name):
                print(f"Failed to create prerequisites for '{table_name}'")
                return False, [], {}

            # Generate and write rows
            written_rows: List[Dict[str, Any]] = []

            for i in range(number_of_rows):
                row_data = self._generate_row_data(table_name, i)
                if row_data is None:
                    continue

                created_row = self._write_row(table_name, row_data)
                if created_row:
                    written_rows.append(created_row)
                    # Update cached IDs for hierarchical dependencies
                    self._update_cached_ids(table_name, created_row)

                # Small delay to respect rate limits
                time.sleep(0.1)

            if written_rows:
                # Get column mapping
                column_mapping = self._get_column_mapping(table_name, written_rows)
                # Wait for data to be committed
                print(f"Waiting 5 seconds for actiTIME to commit data...")
                time.sleep(5)
                return True, written_rows, column_mapping
            else:
                return False, [], {}

        except Exception as e:
            print(f"Error in generate_rows_and_write for {table_name}: {e}")
            import traceback
            traceback.print_exc()
            return False, [], {}

    def _ensure_prerequisites(self, table_name: str) -> bool:
        """
        Ensure required parent objects exist for hierarchical tables.

        actiTIME hierarchy: Customer → Project → Task → TimeTrack
        """
        try:
            # Projects need a customer
            if table_name in ["projects", "tasks", "timetrack"]:
                if not self._created_customer_id:
                    customer = self._create_test_customer()
                    if not customer:
                        return False
                    self._created_customer_id = customer.get("id")

            # Tasks need a project
            if table_name in ["tasks", "timetrack"]:
                if not self._created_project_id:
                    project = self._create_test_project(self._created_customer_id)
                    if not project:
                        return False
                    self._created_project_id = project.get("id")

            # TimeTrack needs a task and user
            if table_name == "timetrack":
                if not self._created_task_id:
                    task = self._create_test_task(self._created_project_id)
                    if not task:
                        return False
                    self._created_task_id = task.get("id")

                if not self._created_user_id:
                    # Get current user from users endpoint
                    user = self._get_current_user()
                    if not user:
                        return False
                    self._created_user_id = user.get("id")

            return True

        except Exception as e:
            print(f"Error ensuring prerequisites for {table_name}: {e}")
            return False

    def _generate_row_data(self, table_name: str, index: int) -> Dict[str, Any] | None:
        """Generate sample data based on the table type."""
        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(1000, 9999)

        if table_name == "customers":
            return {
                "name": f"Test Customer {index}_{random_suffix}",
                "description": f"Generated test customer at {datetime.now().isoformat()}",
            }

        elif table_name == "projects":
            return {
                "name": f"Test Project {index}_{random_suffix}",
                "customerId": self._created_customer_id,
                "description": f"Generated test project at {datetime.now().isoformat()}",
            }

        elif table_name == "tasks":
            return {
                "name": f"Test Task {index}_{random_suffix}",
                "projectId": self._created_project_id,
                "description": f"Generated test task at {datetime.now().isoformat()}",
            }

        elif table_name == "timetrack":
            # Create timetrack for today
            # Note: timetrack uses PATCH /timetrack/{userId}/{date}/{taskId}
            today = datetime.now().strftime("%Y-%m-%d")
            return {
                "_userId": self._created_user_id,  # Used in URL path
                "_taskId": self._created_task_id,  # Used in URL path
                "_date": today,                     # Used in URL path
                "time": 60 * (index + 1),  # 60 minutes per entry (in body)
                "comment": f"Test time entry {index}_{random_suffix}",
            }

        return None

    def _write_row(self, table_name: str, row_data: Dict[str, Any]) -> Dict[str, Any] | None:
        """Write a single row to actiTIME."""
        try:
            # Timetrack uses a special endpoint: PATCH /timetrack/{userId}/{date}/{taskId}
            if table_name == "timetrack":
                return self._write_timetrack_row(row_data)

            url = f"{self.base_url}/{table_name}"
            response = self._session.post(url, json=row_data, timeout=30)

            if response.status_code in [200, 201]:
                created = response.json()
                print(f"Successfully created {table_name} record: {created.get('id', 'N/A')}")
                return created
            else:
                print(
                    f"Failed to create {table_name} record: "
                    f"{response.status_code} - {response.text}"
                )
                return None

        except Exception as e:
            print(f"Error writing {table_name} row: {e}")
            return None

    def _write_timetrack_row(self, row_data: Dict[str, Any]) -> Dict[str, Any] | None:
        """
        Write a timetrack entry using PATCH /timetrack/{userId}/{date}/{taskId}.
        
        The timetrack API requires path parameters for userId, date, and taskId,
        with time and comment in the request body.
        """
        try:
            # Extract path parameters (prefixed with _)
            user_id = row_data.get("_userId")
            task_id = row_data.get("_taskId")
            date = row_data.get("_date")

            if not all([user_id, task_id, date]):
                print("Missing required path parameters for timetrack")
                return None

            # Build the URL with path parameters
            url = f"{self.base_url}/timetrack/{user_id}/{date}/{task_id}"

            # Build body (only non-path parameters)
            body = {
                "time": row_data.get("time", 60),
            }
            if row_data.get("comment"):
                body["comment"] = row_data["comment"]

            response = self._session.patch(url, json=body, timeout=30)

            if response.status_code in [200, 201, 204]:
                # PATCH may return the updated record or empty response
                if response.text:
                    try:
                        result = response.json()
                    except Exception:
                        result = {}
                else:
                    result = {}

                # Build a response record with the data we know
                created = {
                    "userId": user_id,
                    "taskId": task_id,
                    "date": date,
                    "time": body.get("time"),
                    "comment": body.get("comment"),
                    **result,
                }
                print(f"Successfully created timetrack record for user {user_id} on {date}")
                return created
            else:
                print(
                    f"Failed to create timetrack record: "
                    f"{response.status_code} - {response.text}"
                )
                return None

        except Exception as e:
            print(f"Error writing timetrack row: {e}")
            return None

    def _create_test_customer(self) -> Dict[str, Any] | None:
        """Create a test customer as prerequisite."""
        row_data = {
            "name": f"WriteBack Test Customer {random.randint(1000, 9999)}",
            "description": "Auto-created for write-back testing",
        }
        return self._write_row("customers", row_data)

    def _create_test_project(self, customer_id: int) -> Dict[str, Any] | None:
        """Create a test project as prerequisite."""
        row_data = {
            "name": f"WriteBack Test Project {random.randint(1000, 9999)}",
            "customerId": customer_id,
            "description": "Auto-created for write-back testing",
        }
        return self._write_row("projects", row_data)

    def _create_test_task(self, project_id: int) -> Dict[str, Any] | None:
        """Create a test task as prerequisite."""
        row_data = {
            "name": f"WriteBack Test Task {random.randint(1000, 9999)}",
            "projectId": project_id,
            "description": "Auto-created for write-back testing",
        }
        return self._write_row("tasks", row_data)

    def _get_current_user(self) -> Dict[str, Any] | None:
        """Get the first available user for timetrack entries."""
        try:
            url = f"{self.base_url}/users"
            params = {"limit": 1}
            response = self._session.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                # Handle paginated response
                if isinstance(data, dict) and "items" in data:
                    users = data.get("items", [])
                elif isinstance(data, list):
                    users = data
                else:
                    users = []

                if users:
                    return users[0]

            print(f"Failed to get users: {response.status_code} - {response.text}")
            return None

        except Exception as e:
            print(f"Error getting current user: {e}")
            return None

    def _update_cached_ids(self, table_name: str, created_row: Dict[str, Any]) -> None:
        """Update cached IDs from created rows for hierarchical dependencies."""
        row_id = created_row.get("id")
        if not row_id:
            return

        if table_name == "customers":
            self._created_customer_id = row_id
        elif table_name == "projects":
            self._created_project_id = row_id
        elif table_name == "tasks":
            self._created_task_id = row_id

    def _get_column_mapping(
        self, table_name: str, written_rows: List[Dict]
    ) -> Dict[str, str]:
        """
        Create mapping from written column names to returned column names.
        
        For actiTIME, field names are consistent between write and read operations
        (both use camelCase), so the mapping is identity.
        
        Note: Internal fields prefixed with _ are excluded from the mapping.
        """
        if not written_rows:
            return {}

        # actiTIME uses consistent field names between write and read
        # No transformation needed (except for internal _ prefixed fields)
        column_mapping = {}
        for column in written_rows[0].keys():
            # Skip internal fields used for path parameters
            if column.startswith("_"):
                continue
            column_mapping[column] = column

        return column_mapping

    def cleanup_test_data(self) -> None:
        """
        Clean up test data created during write-back testing.
        
        ⚠️ WARNING: This will delete all test objects created by this utility.
        Only call this if you want to remove test data.
        """
        try:
            # Delete in reverse order of hierarchy (task → project → customer)
            if self._created_task_id:
                self._delete_resource("tasks", self._created_task_id)
                self._created_task_id = None

            if self._created_project_id:
                self._delete_resource("projects", self._created_project_id)
                self._created_project_id = None

            if self._created_customer_id:
                self._delete_resource("customers", self._created_customer_id)
                self._created_customer_id = None

            print("Test data cleanup completed")

        except Exception as e:
            print(f"Error during cleanup: {e}")

    def _delete_resource(self, table_name: str, resource_id: int) -> bool:
        """Delete a resource from actiTIME."""
        try:
            url = f"{self.base_url}/{table_name}/{resource_id}"
            response = self._session.delete(url, timeout=30)

            if response.status_code in [200, 204]:
                print(f"Deleted {table_name}/{resource_id}")
                return True
            else:
                print(
                    f"Failed to delete {table_name}/{resource_id}: "
                    f"{response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            print(f"Error deleting {table_name}/{resource_id}: {e}")
            return False
