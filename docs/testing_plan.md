# Testing Plan for ConnectWise Project Reporting

This document outlines a comprehensive testing strategy covering each major component of the system. In addition to functional tests for API integration, data aggregation, and AI orchestration, it includes validation of Pydantic models and performance testing under load.

---

## 1. Base Infrastructure & Pydantic Models

### Goals
- Ensure that all Pydantic models correctly validate input data.
- Catch issues such as missing fields or incorrect data types.

### Strategy
- **Model Validations:**
  - Create tests in `tests/test_models.py` to instantiate models with valid inputs.
  - Write tests to intentionally pass invalid data, expecting `ValidationError`.

### Example Test (using pytest)
```python
from models import Project, TimeEntry, Ticket, Note
import pytest
from pydantic import ValidationError

def test_project_model_valid():
    data = {"id": 1, "name": "Test Project", "status": "open", "client": "Client A", "startDate": "2022-01-01"}
    project = Project(**data)
    assert project.id == 1

def test_project_model_invalid():
    # Missing a required field, e.g., "name"
    data = {"id": 1, "status": "open"}
    with pytest.raises(ValidationError):
        Project(**data)
```

---

## 2. ConnectWise API Wrapper Integration

### Goals
- Verify proper functionality of each API endpoint wrapper.
- Validate retry logic and error handling using tenacity.
- Ensure HTTP responses are parsed correctly.

### Strategy
- **Unit Tests:**
  - Use mocking libraries like `respx` or `httpx-mock` to simulate API responses.
  - Test each method in the API wrapper (e.g., `get_projects`, `get_project_details`).
  - Verify that non-200 responses trigger retries and appropriate errors.
  
- **Integration Tests:**
  - When available, communicate with a sandbox/test server.
  - Ensure the data returned conforms to Pydantic models.

### Example Test
```python
import pytest
import respx
import httpx
from backend.connectwise.api import ConnectWiseAPI

@respx.mock
@pytest.mark.asyncio
async def test_get_projects():
    api_route = respx.get("https://api.connectwise.com/project/projects").mock(
        return_value=httpx.Response(200, json=[{"id": 1, "name": "Test Project", "status": "open"}])
    )
    api = ConnectWiseAPI(base_url="https://api.connectwise.com", client_id="test-client-id")
    projects = await api.get_projects("status:open", page=1, page_size=20)
    assert projects[0].id == 1
    assert api_route.called
```

---

## 3. Aggregation Module

### Goals
- Ensure that data from various endpoints is correctly aggregated into a unified structure.
- Validate behavior when receiving incomplete or empty datasets.

### Strategy
- Write tests in `tests/test_aggregator.py`:
  - Provide sample inputs for projects, time entries, tickets, and notes.
  - Verify the output aggregation matches the predefined schema.

### Example Test
```python
from backend.aggregation.aggregator import aggregate_project_data

def test_aggregate_project_data():
    project_data = {"notes": ["Project note 1", "Project note 2"]}
    other_data = {"data": "Additional info"}
    aggregated = aggregate_project_data(project_data, other_data)
    assert "project_notes" in aggregated
    assert aggregated["other_data"] == other_data
```

---

## 4. AI Orchestration Module

### Goals
- Validate that prompt generation and simulated LLM responses follow expected behavior.
- Ensure that the orchestration chain correctly processes aggregated data.

### Strategy
- In `tests/test_orchestrator.py`:
  - Simulate aggregated input data.
  - Verify the chain creates the expected prompt and mock response.
  - Use monkeypatching to simulate LLM response if needed.

### Example Test
```python
import pytest
from ai_orchestration.orchestrator import orchestrate_workflow

def test_orchestrate_workflow():
    sample_data = {
        "project_notes": {"notes": ["Note 1", "Note 2"]},
        "other_data": {"data": "Test data"}
    }
    result = orchestrate_workflow(sample_data)
    assert "prompt" in result
    assert "response" in result
```

---

## 5. FastAPI Endpoints (Backend)

### Goals
- Ensure the API endpoints respond correctly to valid and invalid requests.
- Verify correct integration with the API wrapper and data aggregation layers.

### Strategy
- Use FastAPI's `TestClient` from `starlette.testclient` in tests (e.g., in `tests/test_api_endpoints.py`):
  - Test root endpoint ("/") and any other critical endpoints such as `/projects`.
  - Simulate error scenarios (missing headers, invalid parameters) and check for proper HTTP error responses.

### Example Test
```python
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the ConnectWise Project Reporting API"}
```

---

## 6. Continuous Integration & Performance Testing

### Goals
- Automatically run the full test suite on every commit/PR using CI/CD pipelines (e.g., GitHub Actions).
- Simulate high load to test rate limiting (using asyncio.Semaphore or libraries) and overall system performance.

### Strategy
- **CI/CD:**
  - Configure GitHub Actions to run `pytest` on each commit.
- **Load Testing:**
  - Create asynchronous tests that simulate many concurrent API calls.
  - Verify that the system enforces rate limits and that retry mechanisms do not overwhelm the API.

---

## Summary

This testing plan covers all significant areas:
- **Model Validations:** Ensuring data integrity using Pydantic models.
- **API Integration:** Testing API wrapper functionality with robust error handling and retry logic.
- **Data Aggregation:** Verifying that multiple data sources are combined correctly.
- **AI Orchestration:** Ensuring that the process for generating AI reports works as expected.
- **FastAPI Endpoints:** Validating both functionality and error handling of the REST API.
- **CI/CD & Load Testing:** Maintaining quality and performance during development and production.

Following this plan will help ensure the ConnectWise Project Reporting system is robust, scalable, and easier to maintain.
