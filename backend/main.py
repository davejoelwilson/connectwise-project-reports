from fastapi import FastAPI, HTTPException, Query, Depends, Path
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, List
from datetime import datetime, timedelta

from connectwise.client import ConnectWiseClient

app = FastAPI(title="ConnectWise Project Reporting Backend", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for ConnectWise client
async def get_cw_client():
    try:
        client = ConnectWiseClient()
        return client
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {"status": "healthy", "service": "ConnectWise Project Reporting API"}

@app.get("/projects")
async def get_projects(
    client: ConnectWiseClient = Depends(get_cw_client),
    test_mode: bool = Query(False, description="Use test mode with minimal parameters"),
    status: Optional[str] = Query(None, description="Filter by project status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    try:
        if test_mode:
            return await client.test_basic_projects_request()
            
        params = {
            'page': page,
            'pageSize': page_size,
            'conditions': f"status/name='{status}'" if status else None
        }
        return await client.get_projects(params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}")
async def get_project(
    project_id: int = Path(..., description="The ID of the project to retrieve"),
    client: ConnectWiseClient = Depends(get_cw_client)
):
    try:
        return await client.get_project(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}/tickets")
async def get_project_tickets(
    project_id: int = Path(..., description="The ID of the project"),
    client: ConnectWiseClient = Depends(get_cw_client),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    try:
        params = {'page': page, 'pageSize': page_size}
        return await client.get_project_tickets(project_id, params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}/notes")
async def get_project_notes(
    project_id: int = Path(..., description="The ID of the project"),
    client: ConnectWiseClient = Depends(get_cw_client),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    try:
        params = {'page': page, 'pageSize': page_size}
        return await client.get_project_notes(project_id, params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tickets")
async def get_tickets(
    client: ConnectWiseClient = Depends(get_cw_client),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by ticket status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    try:
        conditions = []
        if project_id:
            conditions.append(f"project/id={project_id}")
        if status:
            conditions.append(f"status/name like '{status}'")

        params = {
            'page': page,
            'pageSize': page_size,
            'conditions': " and ".join(conditions) if conditions else None
        }
        return await client.get_tickets(params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tickets/{ticket_id}")
async def get_ticket(
    ticket_id: int = Path(..., description="The ID of the ticket to retrieve"),
    client: ConnectWiseClient = Depends(get_cw_client)
):
    try:
        return await client.get_ticket(ticket_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tickets/{ticket_id}/time-entries")
async def get_ticket_time_entries(
    ticket_id: int = Path(..., description="The ID of the ticket"),
    client: ConnectWiseClient = Depends(get_cw_client),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    try:
        params = {'page': page, 'pageSize': page_size}
        return await client.get_ticket_time_entries(ticket_id, params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tickets/{ticket_id}/notes")
async def get_ticket_notes(
    ticket_id: int = Path(..., description="The ID of the ticket"),
    client: ConnectWiseClient = Depends(get_cw_client),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    try:
        params = {'page': page, 'pageSize': page_size}
        return await client.get_ticket_notes(ticket_id, params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/time-entries")
async def get_time_entries(
    client: ConnectWiseClient = Depends(get_cw_client),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    try:
        conditions = []
        if project_id:
            conditions.append(f"chargeToId={project_id}")
        if start_date:
            conditions.append(f"timeStart>=[{start_date}]")
        if end_date:
            conditions.append(f"timeEnd<=[{end_date}]")

        params = {
            'conditions': " and ".join(conditions) if conditions else None
        }
        return await client.get_time_entries(params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/members")
async def get_members(
    client: ConnectWiseClient = Depends(get_cw_client),
    active_only: bool = Query(True, description="Only show active members")
):
    try:
        params = {
            'conditions': "inactiveFlag=false" if active_only else None
        }
        return await client.get_members(params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
