import asyncio
from typing import Optional, Dict
import httpx

class ConnectWiseAPI:
    """
    A wrapper class to interact with ConnectWise API endpoints asynchronously.
    
    Attributes:
        base_url (str): The base URL of the ConnectWise API.
        client_id (str): The client ID for authentication, passed in HTTP headers.
        timeout (float): The timeout for HTTP requests.
    """
    def __init__(self, base_url: str, client_id: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip('/')
        self.client_id = client_id
        self.timeout = timeout
        self.headers = {"clientId": self.client_id}

    async def _request(self, method: str, endpoint: str, params: Optional[dict] = None) -> Dict:
        """
        Internal helper method to perform HTTP requests.

        Args:
            method (str): HTTP method ("GET", "POST", etc.).
            endpoint (str): API endpoint (appended to base_url).
            params (Optional[dict]): Query parameters for the request.
        
        Returns:
            Dict: Parsed JSON response.
        """
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(method, url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

    # 1. Project Data Collection Endpoints

    async def get_projects(self, conditions: str, page: int, pageSize: int) -> Dict:
        """
        Get list of all projects with filtering and pagination.
        
        Parameters:
            conditions (str): Filtering conditions (e.g., 'status:open').
            page (int): Page number for pagination.
            pageSize (int): Number of records per page.
        
        Returns:
            Dict: JSON response with list of projects.
        """
        endpoint = "/project/projects"
        params = {"conditions": conditions, "page": page, "pageSize": pageSize}
        return await self._request("GET", endpoint, params=params)

    async def get_project_details(self, project_id: int) -> Dict:
        """
        Get specific project details by project ID.
        
        Parameters:
            project_id (int): The ID of the project.
        
        Returns:
            Dict: JSON response with project details.
        """
        endpoint = f"/project/projects/{project_id}"
        return await self._request("GET", endpoint)

    # 2. Time Entry Collection Endpoints

    async def get_time_entries(self, conditions: str, orderBy: str, fields: str) -> Dict:
        """
        Get time entries for selected projects.
        
        Parameters:
            conditions (str): Filtering conditions for the time entries.
            orderBy (str): Field to sort the results.
            fields (str): Specific fields to be retrieved.
        
        Returns:
            Dict: JSON response with time entries.
        """
        endpoint = "/time/entries"
        params = {"conditions": conditions, "orderBy": orderBy, "fields": fields}
        return await self._request("GET", endpoint, params=params)

    async def get_time_entries_count(self, conditions: str) -> Dict:
        """
        Get count of time entries for pagination.
        
        Parameters:
            conditions (str): Filtering conditions for the time entries.
        
        Returns:
            Dict: JSON response with count of time entries.
        """
        endpoint = "/time/entries/count"
        params = {"conditions": conditions}
        return await self._request("GET", endpoint, params=params)

    # 3. Ticket Information Endpoints

    async def get_tickets(self, conditions: str, fields: str) -> Dict:
        """
        Get all tickets for selected projects.
        
        Parameters:
            conditions (str): Filtering conditions for tickets.
            fields (str): Specific fields to be retrieved.
        
        Returns:
            Dict: JSON response with tickets list.
        """
        endpoint = "/project/tickets"
        params = {"conditions": conditions, "fields": fields}
        return await self._request("GET", endpoint, params=params)

    async def get_ticket_details(self, ticket_id: int) -> Dict:
        """
        Get details for a specific ticket.
        
        Parameters:
            ticket_id (int): The ID of the ticket.
        
        Returns:
            Dict: JSON response with ticket details.
        """
        endpoint = f"/project/tickets/{ticket_id}"
        return await self._request("GET", endpoint)

    async def get_ticket_time_entries(self, parent_id: int) -> Dict:
        """
        Get time entries linked to a specific ticket.
        
        Parameters:
            parent_id (int): The ID of the parent ticket.
        
        Returns:
            Dict: JSON response with ticket-specific time entries.
        """
        endpoint = f"/project/tickets/{parent_id}/timeentries"
        return await self._request("GET", endpoint)

    # 4. Notes Collection Endpoints

    async def get_ticket_notes(self, parent_id: int) -> Dict:
        """
        Get all notes associated with a specific ticket.
        
        Parameters:
            parent_id (int): The ID of the ticket.
        
        Returns:
            Dict: JSON response with ticket notes.
        """
        endpoint = f"/project/tickets/{parent_id}/allNotes"
        return await self._request("GET", endpoint)

    async def get_project_notes(self, parent_id: int) -> Dict:
        """
        Get project-level notes by project ID.
        
        Parameters:
            parent_id (int): The ID of the project.
        
        Returns:
            Dict: JSON response with project notes.
        """
        endpoint = f"/project/projects/{parent_id}/notes"
        return await self._request("GET", endpoint)

if __name__ == "__main__":
    async def test_api():
        # Instantiate with a sample base URL and client ID
        api = ConnectWiseAPI(base_url="https://api.connectwise.com", client_id="your-client-id")
        
        # Example test: Fetch projects with filtering and pagination.
        try:
            projects = await api.get_projects("status:open", page=1, pageSize=20)
            print("Projects:", projects)
        except Exception as e:
            print("API call failed:", e)
    
    asyncio.run(test_api())
