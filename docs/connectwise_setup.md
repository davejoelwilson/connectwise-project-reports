# ConnectWise Integration Setup

## Authentication Setup

### 1. API Credentials
To connect to ConnectWise, you need the following credentials:
```env
CW_COMPANY_ID=your_company_id
CW_PUBLIC_KEY=your_public_key
CW_PRIVATE_KEY=your_private_key
CW_CLIENT_ID=your_client_id
CW_BASE_URL=https://your-instance.connectwise.com/v4_6_release/apis/3.0
```

### 2. Getting API Access
1. Log into ConnectWise Manage as an admin
2. Navigate to System > Members > API Members
3. Create a new API Member
4. Generate Public/Private key pair
5. Note down the Client ID

## Project Configuration

### 1. Project Mapping
Create a `project_config.json` in the root directory:

```json
{
    "managed_projects": {
        "12345": {
            "name": "Project A",
            "team": ["member1", "member2"],
            "reporting_frequency": "weekly",
            "report_recipients": ["email1@domain.com", "email2@domain.com"],
            "metrics": {
                "track_time": true,
                "track_tickets": true,
                "track_budget": true
            }
        }
    },
    "global_settings": {
        "default_reporting_frequency": "monthly",
        "time_zone": "UTC",
        "work_hours": {
            "start": "09:00",
            "end": "17:00"
        }
    }
}
```

## API Endpoints

### Projects
- `GET /projects` - List all projects
  - Query params:
    - `status`: Filter by status (e.g., "Active", "Completed")
    - `page`: Page number (default: 1)
    - `page_size`: Items per page (default: 50)

### Tickets
- `GET /tickets` - List all tickets
  - Query params:
    - `project_id`: Filter by project
    - `status`: Filter by status
    - `page`: Page number
    - `page_size`: Items per page

### Time Entries
- `GET /time-entries` - List time entries
  - Query params:
    - `project_id`: Filter by project
    - `start_date`: Start date (YYYY-MM-DD)
    - `end_date`: End date (YYYY-MM-DD)

## Field References

### Project Fields
```python
fields = [
    'id',                  # Project ID
    'name',               # Project Name
    'status/name',        # Project Status
    'manager/identifier', # Project Manager
    'company/name',       # Company Name
    'estimatedHours',    # Estimated Hours
    'actualHours',       # Actual Hours
    'budgetHours'        # Budget Hours
]
```

### Ticket Fields
```python
fields = [
    'id',                    # Ticket ID
    'summary',              # Ticket Summary
    'status/name',          # Ticket Status
    'priority/name',        # Priority
    'project/id',           # Project ID
    'project/name',         # Project Name
    'assignedTo/identifier' # Assigned To
]
```

## Common Issues & Solutions

### Authentication Errors
- **401 Unauthorized**: Check if your API keys are correct
- **403 Forbidden**: Verify API member permissions
- **400 Bad Request**: Check field names and query format

### Rate Limiting
ConnectWise implements rate limiting:
- 1000 requests per minute per company
- Use pagination to handle large data sets
- Implement retry logic for rate limit errors

### Best Practices
1. Always use field selection to minimize response size
2. Use conditions to filter server-side
3. Implement proper error handling
4. Cache frequently accessed data
5. Use pagination for large datasets

## Example Usage

### Basic Project Query
```python
# Get all active projects
response = await client.get_projects({
    'conditions': "status/name like 'Active'",
    'page': 1,
    'pageSize': 50
})

# Get specific project with tickets
project = await client.get_project(project_id)
tickets = await client.get_project_tickets(project_id)
```

### Time Entry Query
```python
# Get time entries for last week
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=7)

time_entries = await client.get_time_entries({
    'conditions': f"timeStart>=[{start_date.date()}] and timeEnd<=[{end_date.date()}]"
})
``` 