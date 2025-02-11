# ConnectWise API Endpoints Documentation

This document outlines the REST API endpoints for interacting with ConnectWise data. The endpoints are grouped by their purpose and include required parameters and a brief description of each.

---

## Important Notes
- Base URL: `https://[your-instance].connectwise.com/v4_6_release/apis/3.0`
- All endpoints require authentication headers
- Rate limiting is enforced at 1000 requests per minute

## Key Enum Values

### Time Entry Types
- `chargeToType`: 
  - `"ProjectTicket"` - For project-related time entries
  - `"ServiceTicket"` - For service-related time entries
  - `"Activity"` - For general activities

## Endpoints

### Projects
```
GET /project/projects
Fields: id,name,status/name,manager/identifier,company/name,estimatedHours,actualHours,scheduledStart,scheduledFinish,billingMethod
OrderBy: lastUpdated desc (default)
```

### Project Notes
```
GET /project/projects/{id}/notes
Fields: id,text,detailDescriptionFlag,internalAnalysisFlag,resolutionFlag,dateCreated,createdBy
```

### Project Tickets
```
GET /project/tickets
Fields: id,summary,status/name,priority/name,project/id,project/name,assignedTo/identifier,dateEntered,estimatedHours,actualHours
Conditions: project/id={projectId}
OrderBy: dateEntered desc (default)
```

### Time Entries
```
GET /time/entries
Fields: id,timeStart,timeEnd,hoursWorked,notes,member/identifier,member/name,chargeToId,chargeToType
Conditions: chargeToId={projectId} AND chargeToType="ProjectTicket"
OrderBy: timeStart desc (default)
```

### Members
```
GET /system/members
Fields: id,name
Conditions: identifier IN (comma-separated-list)
OrderBy: firstName asc (default)
```

## Common Parameters
- `page`: Page number (default: 1)
- `pageSize`: Items per page (default: 100, max: 1000)
- `fields`: Comma-separated list of fields to return
- `conditions`: Filter conditions
- `orderBy`: Sort order

## Response Format
All responses are JSON and follow this general structure:
```json
{
    "id": integer,
    "field1": value1,
    "field2": value2,
    ...
}
```

## Error Handling
- 400: Bad Request (invalid parameters)
- 401: Unauthorized (invalid credentials)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 429: Too Many Requests (rate limit exceeded)
- 500: Internal Server Error

## Rate Limiting
- 1000 requests per minute per client
- Rate limit headers:
  - `X-Rate-Limit-Limit`
  - `X-Rate-Limit-Remaining`
  - `X-Rate-Limit-Reset`

---

## 1. Project Data Collection

### GET /project/projects
- **Description:** Retrieve a list of all projects with filtering and pagination support.
- **Parameters:**
  - `conditions` (query): Filtering conditions (e.g., `status:open`).
  - `page` (query): Page number for pagination.
  - `pageSize` (query): Number of records per page.
- **Headers:** 
  - `clientId`: Client ID for authentication.

---

### GET /project/projects/{id}
- **Description:** Get detailed information about a specific project.
- **Parameters:**
  - `id` (path): The project ID.
- **Headers:** 
  - `clientId`: Client ID for authentication.

---

## 2. Time Entry Collection

### GET /time/entries
- **Description:** Retrieve time entries for selected projects.
- **Parameters:**
  - `conditions` (query): Filtering conditions to select time entries relevant to a project.
  - `orderBy` (query): Field by which to sort the results (e.g., date).
  - `fields` (query): Comma-separated list of fields to be retrieved.
- **Headers:** 
  - `clientId`: Client ID for authentication.

---

### GET /time/entries/count
- **Description:** Obtain the count of time entries (useful for pagination).
- **Parameters:**
  - `conditions` (query): Same filtering conditions as used for retrieving time entries.
- **Headers:** 
  - `clientId`: Client ID for authentication.

---

## 3. Ticket Information

### GET /project/tickets
- **Description:** Retrieve all tickets for selected projects.
- **Parameters:**
  - `conditions` (query): Filtering conditions to select tickets.
  - `fields` (query): Comma-separated list of fields to retrieve (e.g., names, statuses).
- **Headers:** 
  - `clientId`: Client ID for authentication.

---

### GET /project/tickets/{id}
- **Description:** Get detailed information about a specific ticket.
- **Parameters:**
  - `id` (path): The ticket ID.
- **Headers:** 
  - `clientId`: Client ID for authentication.

---

### GET /project/tickets/{parentId}/timeentries
- **Description:** Retrieve time entries specific to a given ticket.
- **Parameters:**
  - `parentId` (path): The ID of the parent ticket.
- **Headers:** 
  - `clientId`: Client ID for authentication.

---

## 4. Notes Collection

### GET /project/tickets/{parentId}/allNotes
- **Description:** Get all notes associated with a specific ticket.
- **Parameters:**
  - `parentId` (path): The ticket ID.
- **Headers:** 
  - `clientId`: Client ID for authentication.

---

### GET /project/projects/{parentId}/notes
- **Description:** Get project-level notes for a given project.
- **Parameters:**
  - `parentId` (path): The project ID.
- **Headers:** 
  - `clientId`: Client ID for authentication.

---

## Additional Notes

- **Authentication:** Each request must include a header `clientId` with the appropriate client identifier.
- **Error Handling:** Endpoints return standard HTTP status codes. Clients should handle errors such as timeouts and invalid responses appropriately.
- **Asynchronous Operations:** The API wrapper utilizes asynchronous HTTP requests for improved performance with concurrent calls.

This documentation serves as a reference for developers integrating with the ConnectWise API using our asynchronous API wrapper.
