# ConnectWise API Endpoints Documentation

This document outlines the REST API endpoints for interacting with ConnectWise data. The endpoints are grouped by their purpose and include required parameters and a brief description of each.

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
