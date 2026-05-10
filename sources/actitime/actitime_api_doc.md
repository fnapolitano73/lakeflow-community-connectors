# **actiTIME API Documentation**

## **Authorization**

- **Chosen method**: Basic Authentication via HTTP header.
- **Base URL**: `<your_actitime_url>/api/v1`
- **Auth placement**:
  - HTTP header: `Authorization: Basic <base64_encoded_credentials>`
  - Credentials format: `username:password` (base64 encoded)
- **Content-Type**: `application/json; charset=UTF-8`
- **Accept header**: `application/json; charset=UTF-8`
- **Requirements**:
  - actiTIME Online (paid versions) or Self-Hosted version 2019.2 or later
  - User must have appropriate permissions for the intended operations

Example authenticated request:

```bash
curl -X GET \
  -H "Authorization: Basic $(echo -n 'username:password' | base64)" \
  -H "Accept: application/json; charset=UTF-8" \
  "<actiTIME_URL>/api/v1/customers"
```

Or using `-u` shorthand:

```bash
curl -X GET \
  -H "accept: application/json; charset=UTF-8" \
  -u "username:password" \
  "<actiTIME_URL>/api/v1/customers"
```

Notes:
- The API key is the user's actiTIME credentials (username and password).
- Rate limiting: **100 requests per second** and **1000 requests per minute** per user account.
- After 3 failed authentication attempts within 10 seconds, the IP is banned for 1 minute.
- Rate limit headers are returned: `X-Ratelimit-Remaining`, `X-Ratelimit-Reset`, `Retry-After` (when exceeded).


## **Object List**

The object list is **static** (defined by the connector), based on the actiTIME API v1 endpoints.
actiTIME does not provide a discovery API for available endpoints.

### Core Business Objects

| Object Name | Description | Primary Endpoint | Ingestion Type |
|-------------|-------------|------------------|----------------|
| `customers` | Customer/client entities | `GET /customers` | `cdc` |
| `projects` | Projects belonging to customers | `GET /projects` | `cdc` |
| `tasks` | Tasks within projects | `GET /tasks` | `cdc` |
| `timetrack` | Time tracking entries | `GET /timetrack` | `append` |
| `leavetime` | Leave time entries | `GET /leavetime` | `append` |

### User & Organization Objects

| Object Name | Description | Primary Endpoint | Ingestion Type |
|-------------|-------------|------------------|----------------|
| `users` | User accounts and properties | `GET /users` | `cdc` |
| `departments` | Organizational departments | `GET /departments` | `snapshot` |
| `userGroups` | User groups for permissions | `GET /userGroups` | `snapshot` |
| `userRates` | User billing/cost rates | `GET /userRates/{userId}` | `snapshot` |

### Configuration & Settings Objects

| Object Name | Description | Primary Endpoint | Ingestion Type |
|-------------|-------------|------------------|----------------|
| `typesOfWork` | Work type categories | `GET /typesOfWork` | `snapshot` |
| `leaveTypes` | Leave type definitions | `GET /leaveTypes` | `snapshot` |
| `workflowStatuses` | Task workflow status definitions | `GET /workflowStatuses` | `snapshot` |
| `timeZoneGroups` | Time zone group settings | `GET /timeZoneGroups` | `snapshot` |
| `settings` | System settings | `GET /settings` | `snapshot` |
| `holidays` | Holiday calendar entries | `GET /holidays` | `snapshot` |

### Approval Objects

| Object Name | Description | Primary Endpoint | Ingestion Type |
|-------------|-------------|------------------|----------------|
| `approvalStatus` | Time approval status | `GET /approvalStatus` | `append` |

**Object Hierarchy:**
- **Customers** → **Projects** → **Tasks**
- **Users** belong to **Departments** and **UserGroups**
- **TimeTrack** entries link **Users** to **Tasks** with dates and durations
- **LeaveTime** entries link **Users** to **LeaveTypes** with dates


## **Object Schema**

### General Notes

- actiTIME API returns JSON responses with consistent field naming (camelCase).
- Timestamps are returned as Unix epoch milliseconds (long integers).
- IDs are integer values.
- Boolean fields use JSON true/false.
- Nested objects can be included using the `includeReferenced` query parameter.
- Null values are represented as JSON null or omitted.

### `customers` object

**Source endpoint**:
`GET /api/v1/customers`

**Query parameters**:
- `offset` (optional): Skip first N records (for pagination)
- `limit` (optional): Maximum number of records to return
- `sort` (optional): Sort field with direction (+name, -name, +created, -created)
- `words` (optional): Search filter for name/description
- `ids` (optional): Comma-separated list of customer IDs to retrieve
- `archived` (optional): Filter by archived status (true/false)
- `includeReferenced` (optional): Include related objects (projects, typesOfWork)

**Response structure**:
```json
[
  {
    "id": 1,
    "name": "Customer A",
    "archived": false,
    "description": "Description of Customer A",
    "created": 1625501337000,
    "url": "<actiTIME_URL>/tasks/tasklist.do?customerId=1",
    "allowedActions": {
      "canModify": true,
      "canDelete": true
    }
  }
]
```

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `id` | integer | Unique customer identifier (primary key). |
| `name` | string | Customer name. |
| `description` | string or null | Customer description. |
| `archived` | boolean | Whether the customer is archived. |
| `created` | long (timestamp) | Creation timestamp in epoch milliseconds. |
| `url` | string | Web URL to view the customer in actiTIME UI. |
| `can_modify` | boolean (derived) | Whether current user can modify this customer. |
| `can_delete` | boolean (derived) | Whether current user can delete this customer. |


### `projects` object

**Source endpoint**:
`GET /api/v1/projects`

**Query parameters**:
- `offset` (optional): Skip first N records
- `limit` (optional): Maximum number of records to return
- `sort` (optional): Sort field with direction
- `words` (optional): Search filter
- `ids` (optional): Comma-separated list of project IDs
- `customerIds` (optional): Filter by customer IDs
- `archived` (optional): Filter by archived status
- `includeReferenced` (optional): Include related objects (customers, typesOfWork)

**Response structure**:
```json
[
  {
    "id": 10,
    "name": "Project Alpha",
    "description": "Project description",
    "customerId": 1,
    "archived": false,
    "created": 1625501337000,
    "workflowEnabled": true,
    "defaultTypeOfWorkId": 5,
    "url": "<actiTIME_URL>/tasks/tasklist.do?projectId=10",
    "allowedActions": {
      "canModify": true,
      "canDelete": true
    }
  }
]
```

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `id` | integer | Unique project identifier (primary key). |
| `name` | string | Project name. |
| `description` | string or null | Project description. |
| `customer_id` | integer | Parent customer ID (foreign key). |
| `archived` | boolean | Whether the project is archived. |
| `created` | long (timestamp) | Creation timestamp in epoch milliseconds. |
| `workflow_enabled` | boolean | Whether workflow is enabled for this project. |
| `default_type_of_work_id` | integer or null | Default type of work for tasks. |
| `url` | string | Web URL to view the project. |
| `can_modify` | boolean (derived) | Whether current user can modify. |
| `can_delete` | boolean (derived) | Whether current user can delete. |


### `tasks` object

**Source endpoint**:
`GET /api/v1/tasks`

**Query parameters**:
- `offset` (optional): Skip first N records
- `limit` (optional): Maximum number of records to return
- `sort` (optional): Sort field with direction (+name, -name, +created, etc.)
- `words` (optional): Search filter for name/description
- `ids` (optional): Comma-separated list of task IDs
- `projectIds` (optional): Filter by project IDs
- `customerIds` (optional): Filter by customer IDs
- `typeOfWorkIds` (optional): Filter by type of work IDs
- `workflowStatusIds` (optional): Filter by workflow status IDs
- `archived` (optional): Filter by archived status
- `includeReferenced` (optional): Include related objects (customers, projects, typesOfWork)

**Response structure**:
```json
[
  {
    "id": 100,
    "name": "Task 1",
    "description": "Task description",
    "projectId": 10,
    "customerId": 1,
    "archived": false,
    "created": 1625501337000,
    "typeOfWorkId": 5,
    "workflowStatusId": 2,
    "deadline": "2025-01-31",
    "estimatedTime": 28800,
    "url": "<actiTIME_URL>/tasks/taskview.do?taskId=100",
    "allowedActions": {
      "canModify": true,
      "canDelete": true,
      "canComplete": true
    }
  }
]
```

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `id` | integer | Unique task identifier (primary key). |
| `name` | string | Task name. |
| `description` | string or null | Task description. |
| `project_id` | integer | Parent project ID (foreign key). |
| `customer_id` | integer | Parent customer ID (foreign key). |
| `archived` | boolean | Whether the task is archived. |
| `created` | long (timestamp) | Creation timestamp in epoch milliseconds. |
| `type_of_work_id` | integer or null | Type of work ID. |
| `workflow_status_id` | integer or null | Current workflow status ID. |
| `deadline` | string (date) or null | Task deadline (YYYY-MM-DD). |
| `estimated_time` | integer or null | Estimated time in seconds. |
| `url` | string | Web URL to view the task. |
| `can_modify` | boolean (derived) | Whether current user can modify. |
| `can_delete` | boolean (derived) | Whether current user can delete. |
| `can_complete` | boolean (derived) | Whether current user can complete. |


### `timetrack` object

**Source endpoint**:
`GET /api/v1/timetrack`

**Query parameters** (required for date range):
- `dateFrom` (required): Start date (YYYY-MM-DD)
- `dateTo` (required): End date (YYYY-MM-DD)
- `userIds` (optional): Comma-separated list of user IDs
- `taskIds` (optional): Comma-separated list of task IDs
- `projectIds` (optional): Filter by project IDs
- `customerIds` (optional): Filter by customer IDs
- `includeReferenced` (optional): Include related objects (users, tasks)

**Response structure**:
```json
[
  {
    "userId": 1,
    "date": "2025-01-08",
    "records": [
      {
        "id": 5001,
        "taskId": 100,
        "time": 14400,
        "comment": "Worked on feature X",
        "approved": false,
        "locked": false,
        "typeOfWorkId": 5
      }
    ]
  }
]
```

**High-level schema (connector view - flattened)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `id` | integer | Unique timetrack record identifier (primary key). |
| `user_id` | integer | User ID who logged the time. |
| `date` | string (date) | Date of the time entry (YYYY-MM-DD). |
| `task_id` | integer | Task ID the time was logged against. |
| `time` | integer | Time logged in seconds. |
| `comment` | string or null | Comment/note for the time entry. |
| `approved` | boolean | Whether the time entry is approved. |
| `locked` | boolean | Whether the time entry is locked. |
| `type_of_work_id` | integer or null | Type of work ID. |


### `leavetime` object

**Source endpoint**:
`GET /api/v1/leavetime`

**Query parameters**:
- `dateFrom` (required): Start date (YYYY-MM-DD)
- `dateTo` (required): End date (YYYY-MM-DD)
- `userIds` (optional): Comma-separated list of user IDs
- `leaveTypeIds` (optional): Comma-separated list of leave type IDs
- `includeReferenced` (optional): Include related objects (users, leaveTypes)

**Response structure**:
```json
[
  {
    "userId": 1,
    "date": "2025-01-08",
    "records": [
      {
        "id": 2001,
        "leaveTypeId": 1,
        "time": 28800,
        "approved": true
      }
    ]
  }
]
```

**High-level schema (connector view - flattened)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `id` | integer | Unique leave time record identifier (primary key). |
| `user_id` | integer | User ID. |
| `date` | string (date) | Date of the leave entry (YYYY-MM-DD). |
| `leave_type_id` | integer | Leave type ID. |
| `time` | integer | Leave time in seconds. |
| `approved` | boolean | Whether the leave is approved. |


### `users` object

**Source endpoint**:
`GET /api/v1/users`

**Query parameters**:
- `offset` (optional): Skip first N records
- `limit` (optional): Maximum number of records to return
- `sort` (optional): Sort field with direction
- `ids` (optional): Comma-separated list of user IDs
- `departmentIds` (optional): Filter by department IDs
- `includeReferenced` (optional): Include related objects (departments, userGroups)

**Response structure**:
```json
[
  {
    "id": 1,
    "firstName": "John",
    "lastName": "Doe",
    "middleName": null,
    "username": "johndoe",
    "email": "john.doe@example.com",
    "departmentId": 1,
    "active": true,
    "created": 1625501337000,
    "timeZoneGroupId": 1,
    "userGroups": [1, 2],
    "userRoles": ["ROLE_ADMIN", "ROLE_MANAGER"]
  }
]
```

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `id` | integer | Unique user identifier (primary key). |
| `first_name` | string | User's first name. |
| `last_name` | string | User's last name. |
| `middle_name` | string or null | User's middle name. |
| `username` | string | Username for login. |
| `email` | string | User's email address. |
| `department_id` | integer or null | Department ID the user belongs to. |
| `active` | boolean | Whether the user account is active. |
| `created` | long (timestamp) | Account creation timestamp. |
| `time_zone_group_id` | integer or null | Time zone group ID. |
| `user_groups` | array<integer> | List of user group IDs. |
| `user_roles` | array<string> | List of user role names. |


### `departments` object

**Source endpoint**:
`GET /api/v1/departments`

**Response structure**:
```json
[
  {
    "id": 1,
    "name": "Engineering",
    "description": "Engineering department",
    "parentId": null,
    "managerId": 5
  }
]
```

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `id` | integer | Unique department identifier (primary key). |
| `name` | string | Department name. |
| `description` | string or null | Department description. |
| `parent_id` | integer or null | Parent department ID (for hierarchy). |
| `manager_id` | integer or null | Manager user ID. |


### `userGroups` object

**Source endpoint**:
`GET /api/v1/userGroups`

**Response structure**:
```json
[
  {
    "id": 1,
    "name": "Developers",
    "description": "Developer team"
  }
]
```

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `id` | integer | Unique user group identifier (primary key). |
| `name` | string | User group name. |
| `description` | string or null | User group description. |


### `typesOfWork` object

**Source endpoint**:
`GET /api/v1/typesOfWork`

**Response structure**:
```json
[
  {
    "id": 1,
    "name": "Development",
    "description": "Software development work",
    "archived": false,
    "billable": true
  }
]
```

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `id` | integer | Unique type of work identifier (primary key). |
| `name` | string | Type of work name. |
| `description` | string or null | Description. |
| `archived` | boolean | Whether this type is archived. |
| `billable` | boolean | Whether this type is billable. |


### `leaveTypes` object

**Source endpoint**:
`GET /api/v1/leaveTypes`

**Response structure**:
```json
[
  {
    "id": 1,
    "name": "Vacation",
    "description": "Paid vacation leave",
    "archived": false,
    "paidLeave": true,
    "autoAccrual": true
  }
]
```

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `id` | integer | Unique leave type identifier (primary key). |
| `name` | string | Leave type name. |
| `description` | string or null | Description. |
| `archived` | boolean | Whether this leave type is archived. |
| `paid_leave` | boolean | Whether this is paid leave. |
| `auto_accrual` | boolean | Whether leave accrues automatically. |


### `workflowStatuses` object

**Source endpoint**:
`GET /api/v1/workflowStatuses`

**Response structure**:
```json
[
  {
    "id": 1,
    "name": "In Progress",
    "type": "in_progress",
    "order": 2
  }
]
```

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `id` | integer | Unique workflow status identifier (primary key). |
| `name` | string | Status display name. |
| `type` | string | Status type (open, in_progress, completed). |
| `order` | integer | Display order. |


### `timeZoneGroups` object

**Source endpoint**:
`GET /api/v1/timeZoneGroups`

**Response structure**:
```json
[
  {
    "id": 1,
    "name": "US Eastern",
    "timeZone": "America/New_York"
  }
]
```

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `id` | integer | Unique time zone group identifier (primary key). |
| `name` | string | Time zone group name. |
| `time_zone` | string | IANA time zone identifier. |


### `settings` object

**Source endpoint**:
`GET /api/v1/settings`

**Response structure**:
```json
{
  "workdayDuration": 28800,
  "weekStartDay": 1,
  "dateFormat": "MM/dd/yyyy",
  "timeFormat": "HH:mm",
  "currencyCode": "USD",
  "decimalSeparator": ".",
  "thousandsSeparator": ","
}
```

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `workday_duration` | integer | Standard workday duration in seconds. |
| `week_start_day` | integer | Week start day (0=Sunday, 1=Monday, etc.). |
| `date_format` | string | Date format pattern. |
| `time_format` | string | Time format pattern. |
| `currency_code` | string | Default currency code. |
| `decimal_separator` | string | Decimal separator character. |
| `thousands_separator` | string | Thousands separator character. |


### `holidays` object

**Source endpoint**:
`GET /api/v1/holidays`

**Query parameters**:
- `dateFrom` (optional): Start date (YYYY-MM-DD)
- `dateTo` (optional): End date (YYYY-MM-DD)

**Response structure**:
```json
[
  {
    "date": "2025-01-01",
    "name": "New Year's Day",
    "timeZoneGroupId": null
  }
]
```

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `date` | string (date) | Holiday date (YYYY-MM-DD). |
| `name` | string | Holiday name. |
| `time_zone_group_id` | integer or null | Time zone group ID (null = all groups). |


### `userRates` object

**Source endpoint**:
`GET /api/v1/userRates/{userId}`

**Response structure**:
```json
[
  {
    "dateFrom": "2025-01-01",
    "regularRate": 75.00,
    "overtimeRate": 112.50,
    "leaveRates": {
      "1": 75.00,
      "2": 0.00
    }
  }
]
```

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `user_id` | integer (connector-derived) | User ID (from path parameter). |
| `date_from` | string (date) | Rate effective date. |
| `regular_rate` | decimal | Regular hourly rate. |
| `overtime_rate` | decimal | Overtime hourly rate. |
| `leave_rates` | map<string, decimal> | Leave rates by leave type ID. |


## **Get Object Primary Keys**

There is no dedicated metadata endpoint to get primary keys for actiTIME objects.
Instead, primary keys are defined **statically** based on the resource schema.

### Primary keys by object type:

| Object | Primary Key(s) | Type | Notes |
|--------|---------------|------|-------|
| `customers` | `id` | integer | Unique customer identifier. |
| `projects` | `id` | integer | Unique project identifier. |
| `tasks` | `id` | integer | Unique task identifier. |
| `timetrack` | `id` | integer | Unique time entry identifier. |
| `leavetime` | `id` | integer | Unique leave time entry identifier. |
| `users` | `id` | integer | Unique user identifier. |
| `departments` | `id` | integer | Unique department identifier. |
| `userGroups` | `id` | integer | Unique user group identifier. |
| `typesOfWork` | `id` | integer | Unique type of work identifier. |
| `leaveTypes` | `id` | integer | Unique leave type identifier. |
| `workflowStatuses` | `id` | integer | Unique workflow status identifier. |
| `timeZoneGroups` | `id` | integer | Unique time zone group identifier. |
| `settings` | (single record) | N/A | Settings is a singleton object. |
| `holidays` | `date`, `time_zone_group_id` | date, integer | Composite key (date + time zone group). |
| `userRates` | `user_id`, `date_from` | integer, date | Composite key (user + effective date). |
| `approvalStatus` | `user_id`, `week_start_date` | integer, date | Composite key (user + week). |

The connector will:
- Use the `id` field from most objects for upserts.
- For time-based objects (`timetrack`, `leavetime`), flatten the nested structure to individual records.


## **Object's Ingestion Type**

Supported ingestion types (framework-level definitions):
- `cdc`: Change data capture; supports upserts incrementally.
- `cdc_with_deletes`: CDC with delete synchronization.
- `snapshot`: Full replacement snapshot; no incremental support.
- `append`: Incremental but append-only (no updates/deletes to historical data).

### Ingestion types for actiTIME objects:

| Object | Ingestion Type | Rationale |
|--------|----------------|-----------|
| `customers` | `cdc` | Customers can be created, updated, and archived. Use `id` as key. |
| `projects` | `cdc` | Projects can be created, updated, and archived. Use `id` as key. |
| `tasks` | `cdc` | Tasks can be created, updated, and archived. Use `id` as key. |
| `timetrack` | `append` | Time entries are typically appended by date. Filter by `dateFrom`/`dateTo`. |
| `leavetime` | `append` | Leave entries are typically appended by date. Filter by `dateFrom`/`dateTo`. |
| `users` | `cdc` | Users can be created and updated. Use `id` as key. |
| `departments` | `snapshot` | Small reference table; full refresh is efficient. |
| `userGroups` | `snapshot` | Small reference table; full refresh is efficient. |
| `typesOfWork` | `snapshot` | Small reference table; full refresh is efficient. |
| `leaveTypes` | `snapshot` | Small reference table; full refresh is efficient. |
| `workflowStatuses` | `snapshot` | Small reference table; full refresh is efficient. |
| `timeZoneGroups` | `snapshot` | Small reference table; full refresh is efficient. |
| `settings` | `snapshot` | Single record; always full snapshot. |
| `holidays` | `snapshot` | Calendar data; full refresh recommended. |
| `userRates` | `snapshot` | Rate history per user; snapshot per user. |
| `approvalStatus` | `append` | Approval status changes over time. |

### Incremental strategy for time-based objects:

- **Cursor field**: `date` (for `timetrack` and `leavetime`)
- **Filter parameters**: `dateFrom`, `dateTo`
- **Lookback window**: Recommended 7-day lookback for modified entries.
- **Deletes**: actiTIME allows deletion of time entries; not tracked via API.


## **Read API for Data Retrieval**

### General API Pattern

All actiTIME APIs use the same base URL and authentication:

- **HTTP method**: `GET` for retrieval
- **Base URL**: `<actiTIME_URL>/api/v1`
- **Content-Type**: `application/json; charset=UTF-8`

### Pagination

actiTIME supports pagination via query parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `offset` | integer | Number of records to skip (default: 0). |
| `limit` | integer | Maximum records to return (default: varies by endpoint). |

Example paginated request:
```bash
curl -X GET \
  "<actiTIME_URL>/api/v1/tasks?offset=20&limit=10" \
  -H "accept: application/json; charset=UTF-8" \
  -u "username:password"
```

### Sorting

Sorting is supported via the `sort` parameter:

| Value | Description |
|-------|-------------|
| `+name` | Ascending by name |
| `-name` | Descending by name |
| `+created` | Ascending by creation date |
| `-created` | Descending by creation date |

Example:
```bash
curl -X GET \
  "<actiTIME_URL>/api/v1/customers?sort=+name" \
  -u "username:password"
```

### Filtering

Various filter parameters are available:

| Parameter | Endpoints | Description |
|-----------|-----------|-------------|
| `words` | customers, projects, tasks | Text search in name/description. |
| `ids` | most endpoints | Comma-separated list of IDs. |
| `archived` | customers, projects, tasks | Filter by archived status. |
| `customerIds` | projects, tasks | Filter by parent customer. |
| `projectIds` | tasks, timetrack | Filter by parent project. |
| `userIds` | timetrack, leavetime, users | Filter by user. |
| `dateFrom`, `dateTo` | timetrack, leavetime, holidays | Date range filter. |

### Including Referenced Objects

Use `includeReferenced` to include related objects in responses:

```bash
curl -X GET \
  "<actiTIME_URL>/api/v1/tasks?includeReferenced=customers,projects,typesOfWork" \
  -u "username:password"
```

### Rate Limits

| Limit | Value | Notes |
|-------|-------|-------|
| Per second | 100 requests | Per user account |
| Per minute | 1000 requests | Per user account |
| Ban trigger | 3 failed auth in 10s | IP banned for 1 minute |

**Rate limit response headers**:
- `X-Ratelimit-Remaining`: Requests left in current window
- `X-Ratelimit-Reset`: Seconds until window reset
- `Retry-After`: Seconds to wait (when rate limited)

### Example API Requests

**Get all active customers**:
```bash
curl -X GET \
  "<actiTIME_URL>/api/v1/customers?archived=false" \
  -H "accept: application/json; charset=UTF-8" \
  -u "username:password"
```

**Get time track data for date range**:
```bash
curl -X GET \
  "<actiTIME_URL>/api/v1/timetrack?dateFrom=2025-01-01&dateTo=2025-01-31" \
  -H "accept: application/json; charset=UTF-8" \
  -u "username:password"
```

**Get tasks with related objects**:
```bash
curl -X GET \
  "<actiTIME_URL>/api/v1/tasks?offset=0&limit=100&sort=+name&includeReferenced=customers,projects,typesOfWork" \
  -H "accept: application/json; charset=UTF-8" \
  -u "username:password"
```

### Error Responses

| Code | Explanation |
|------|-------------|
| 200 | Request succeeded. |
| 204 | Request succeeded. Object deleted. |
| 400 | Invalid auth scheme or cannot parse arguments. |
| 401 | User not authorized (invalid credentials). |
| 403 | User lacks permissions or object already exists. |
| 404 | Object with given ID does not exist. |
| 429 | Too many requests (rate limit exceeded). |
| 500 | Internal server error. |

**Error response format**:
```json
{
  "key": "api.error.customer_exists",
  "message": "Customer with specified name already exists"
}
```


## **Write API**

actiTIME provides full CRUD operations for most objects. Write operations are documented for completeness and potential write-back testing.

### Create Resource (POST)

**Create a customer**:
```bash
curl -X POST "<actiTIME_URL>/api/v1/customers" \
  -H "accept: application/json; charset=UTF-8" \
  -H "Content-Type: application/json; charset=UTF-8" \
  -u "username:password" \
  -d '{
    "name": "New Customer",
    "description": "Customer description"
  }'
```

**Create a project**:
```bash
curl -X POST "<actiTIME_URL>/api/v1/projects" \
  -H "accept: application/json; charset=UTF-8" \
  -H "Content-Type: application/json; charset=UTF-8" \
  -u "username:password" \
  -d '{
    "customerId": 1,
    "name": "New Project",
    "description": "Project description"
  }'
```

**Create a task**:
```bash
curl -X POST "<actiTIME_URL>/api/v1/tasks" \
  -H "accept: application/json; charset=UTF-8" \
  -H "Content-Type: application/json; charset=UTF-8" \
  -u "username:password" \
  -d '{
    "projectId": 10,
    "name": "New Task",
    "description": "Task description"
  }'
```

**Create a workflow status**:
```bash
curl -X POST "<actiTIME_URL>/api/v1/workflowStatuses" \
  -H "accept: application/json; charset=UTF-8" \
  -H "Content-Type: application/json; charset=UTF-8" \
  -u "username:password" \
  -d '{
    "name": "Won'\''t Fix",
    "type": "completed"
  }'
```

### Update Resource (PATCH)

**Update a customer**:
```bash
curl -X PATCH "<actiTIME_URL>/api/v1/customers/7" \
  -H "accept: application/json; charset=UTF-8" \
  -H "Content-Type: application/json; charset=UTF-8" \
  -u "username:password" \
  -d '{
    "name": "Customer #15"
  }'
```

### Replace Resource (PUT)

**Replace user rates**:
```bash
curl -X PUT "<actiTIME_URL>/api/v1/userRates/16" \
  -H "accept: application/json; charset=UTF-8" \
  -H "Content-Type: application/json; charset=UTF-8" \
  -u "username:password" \
  -d '[
    {
      "dateFrom": "2025-01-01",
      "regularRate": 75,
      "overtimeRate": 112.50
    }
  ]'
```

### Delete Resource (DELETE)

**Delete a project**:
```bash
curl -X DELETE "<actiTIME_URL>/api/v1/projects/10?revokeApprovedWeeks=true" \
  -H "accept: application/json; charset=UTF-8" \
  -u "username:password"
```

**Delete parameters**:
- `revokeApprovedWeeks` (optional): Revoke approval status of approved weeks (default: false).

### Write Operation Notes

- Only include fields that need to be updated in PATCH requests.
- POST creates return the created object with assigned ID.
- DELETE returns 204 No Content on success.
- Users with appropriate permissions can modify/delete objects.


## **Field Type Mapping**

### General mapping (actiTIME JSON → Connector logical types)

| actiTIME JSON Type | Example Fields | Connector Logical Type | Notes |
|-------------------|----------------|------------------------|-------|
| integer | id, customerId, projectId | `integer` / `long` | 32-bit integers; use long for safety. |
| string | name, description, username | `string` | UTF-8 text. |
| boolean | archived, active, approved | `boolean` | JSON true/false. |
| long (epoch ms) | created | `timestamp` | Unix epoch in milliseconds. |
| string (date) | date, dateFrom, deadline | `date` | ISO 8601 format (YYYY-MM-DD). |
| array<integer> | userGroups | `array<integer>` | Lists of IDs. |
| array<string> | userRoles | `array<string>` | Lists of role names. |
| object | allowedActions, leaveRates | `struct` or `map` | Nested objects. |
| null | optional fields | corresponding type + null | JSON null or absent. |

### Specific type mappings:

| Field Category | Fields | Target Type |
|----------------|--------|-------------|
| Identifiers | id, customerId, projectId, taskId, userId | `integer` (64-bit long) |
| Names | name, firstName, lastName, username | `string` |
| Descriptions | description, comment | `string` |
| Timestamps (epoch ms) | created | `timestamp` |
| Dates | date, dateFrom, dateTo, deadline | `date` |
| Durations | time, estimatedTime, workdayDuration | `integer` (seconds) |
| Rates | regularRate, overtimeRate | `decimal` |
| Booleans | archived, active, approved, locked, billable | `boolean` |
| URLs | url | `string` |

### Special behaviors:

1. **Timestamps**: The `created` field is Unix epoch in milliseconds; divide by 1000 for seconds.
2. **Durations**: Time values (time, estimatedTime) are in seconds; convert to hours by dividing by 3600.
3. **Null handling**: Optional fields may be null or absent; treat both as null.
4. **Nested structures**: `allowedActions` is a struct with boolean fields; flatten or keep as struct.
5. **Arrays**: `userGroups` and `userRoles` are arrays; store as array types or explode to rows.


## **Known Quirks & Edge Cases**

1. **Self-hosted vs Online**: API is available in paid versions starting from actiTIME 2019.2. Ensure your version supports the API.

2. **Timezone handling**: Time zone groups affect how dates are interpreted. Always use explicit date formats.

3. **Archived entities**: Archived customers, projects, and tasks are excluded by default. Use `archived=true` or `archived=all` to include them.

4. **Time track structure**: Time track responses are nested by user and date; flatten for tabular storage.

5. **Rate limits**: 100 req/sec and 1000 req/min per user. Implement exponential backoff.

6. **Authentication bans**: 3 failed auth attempts in 10 seconds triggers a 1-minute IP ban.

7. **Cascade deletes**: Deleting a customer may cascade to projects and tasks depending on system settings.

8. **Approval workflow**: Time entries may be locked after approval; check `approved` and `locked` fields.

9. **Leave time accrual**: Leave balances and accruals are managed separately from leave time entries.

10. **Custom fields**: actiTIME may support custom fields not documented in the standard API.

11. **Permissions**: Users may have limited visibility; some objects may not be accessible to all users.

12. **Empty responses**: Endpoints may return empty arrays `[]` when no data matches the query.


## **Research Log**

| Source Type | URL | Accessed (UTC) | Confidence | What it confirmed |
|------------|-----|----------------|------------|-------------------|
| Official Docs | https://www.actitime.com/api-documentation | 2025-01-08 | Highest | API overview, authentication, endpoints, rate limits. |
| Official Docs | https://www.actitime.com/api-documentation/api-usage | 2025-01-08 | Highest | Basic auth, CRUD operations, error handling, rate limiting. |
| Web Search | actiTIME API documentation endpoints | 2025-01-08 | High | Confirmed customers, projects, tasks, timetrack, users endpoints. |
| Web Search | actiTIME API pagination sort offset limit | 2025-01-08 | High | Pagination parameters, sort syntax, includeReferenced parameter. |
| Reference Impl | sources/github/github_api_doc.md (local repo) | 2025-01-08 | High | Documentation structure and format reference. |
| Reference Impl | sources/alphavantage/alphavantage_api_doc.md (local repo) | 2025-01-08 | High | Documentation structure and format reference. |


## **Sources and References**

- **Official actiTIME API documentation** (highest confidence)
  - Main documentation: https://www.actitime.com/api-documentation
  - API usage guide: https://www.actitime.com/api-documentation/api-usage
  - Interactive API (Swagger): Available at `<your_actitime_url>/api/v1/swagger` (if enabled)

- **API availability**:
  - Paid versions of actiTIME Online
  - Self-Hosted version 2019.2 and later

- **Key endpoints documented**:
  - Core Objects: /customers, /projects, /tasks
  - Time Data: /timetrack, /leavetime
  - Users: /users, /departments, /userGroups, /userRates
  - Configuration: /typesOfWork, /leaveTypes, /workflowStatuses, /timeZoneGroups, /settings, /holidays
  - Approvals: /approvalStatus

- **Reference implementations** (for documentation format):
  - `sources/github/github_api_doc.md` - Structure and completeness reference
  - `sources/alphavantage/alphavantage_api_doc.md` - Schema documentation reference

When conflicts arise, **official actiTIME documentation** is treated as the source of truth.
