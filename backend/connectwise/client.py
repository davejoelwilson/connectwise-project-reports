from typing import Optional, Dict, Any, List, ClassVar, Callable
import os
import httpx
import base64
import logging
from functools import lru_cache, partial
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ConnectWiseClient:
    # Class-level client for connection pooling
    _http_client: ClassVar[Optional[httpx.AsyncClient]] = None
    
    # Common field sets
    BASIC_FIELDS = ['id', 'name']
    PROJECT_FIELDS = [
        'id', 'name', 'status/name', 'manager/identifier',
        'company/name', 'estimatedHours', 'actualHours',
        'scheduledStart', 'scheduledFinish', 'billingMethod'
    ]
    TIME_ENTRY_FIELDS = [
        'id', 'timeStart', 'timeEnd', 'hoursWorked', 'notes',
        'member/identifier', 'member/name', 'chargeToId', 'chargeToType'
    ]
    TICKET_FIELDS = [
        'id', 'summary', 'status/name', 'priority/name', 'project/id',
        'project/name', 'assignedTo/identifier', 'dateEntered',
        'estimatedHours', 'actualHours'
    ]
    
    def __init__(self):
        self.base_url = os.getenv('CONNECTWISE_URL', os.getenv('CW_BASE_URL'))
        self.company = os.getenv('CONNECTWISE_COMPANY', 'it360nz')
        self.public_key = os.getenv('CONNECTWISE_PUBLIC_KEY', os.getenv('CW_PUBLIC_KEY'))
        self.private_key = os.getenv('CONNECTWISE_PRIVATE_KEY', os.getenv('CW_PRIVATE_KEY'))
        self.client_id = os.getenv('CONNECTWISE_CLIENT_ID', os.getenv('CW_CLIENT_ID'))
        
        if not all([self.base_url, self.company, self.public_key, self.private_key, self.client_id]):
            raise ValueError("Missing required ConnectWise configuration")
        
        logger.debug(f"Initialized ConnectWise client with base URL: {self.base_url}")
        logger.debug(f"Using Company: {self.company}")
        logger.debug(f"Using Client ID: {self.client_id}")

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Get or create the shared HTTP client"""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                timeout=30.0,
                verify=True,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return self._http_client

    @lru_cache(maxsize=1)
    def _get_basic_auth(self) -> str:
        """Generate Basic auth token for ConnectWise API (cached)"""
        credentials = f"{self.company}+{self.public_key}:{self.private_key}"
        encoded = base64.b64encode(credentials.encode()).decode()
        auth = f"Basic {encoded}"
        logger.debug(f"Auth credentials (before encoding): {self.company}+{self.public_key}:****")
        logger.debug(f"Auth header: Basic {encoded[:10]}...")
        return auth

    @lru_cache(maxsize=1)
    async def _get_headers(self) -> Dict[str, str]:
        """Get request headers (cached)"""
        return {
            'Authorization': self._get_basic_auth(),
            'ClientID': self.client_id,
            'Content-Type': 'application/json'
        }

    def _build_params(self, base_params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Build query parameters with defaults"""
        params = {
            'page': 1,
            'pageSize': 100,
            'orderBy': kwargs.get('orderBy', 'name asc'),
            'fields': kwargs.get('fields', self.BASIC_FIELDS),
            **(base_params or {})
        }
        
        # Clean params
        params = {k: v for k, v in params.items() if v is not None}
        for key, value in params.items():
            if isinstance(value, (list, tuple)):
                params[key] = ','.join(str(x) for x in value)
                
        return params

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make a GET request to the ConnectWise API"""
        url = f"{self.base_url}/{endpoint}"
        headers = await self._get_headers()
        
        logger.debug(f"Making request to: {url}")
        logger.debug(f"With params: {params}")
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = await self.http_client.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    return response.json()
                    
                if response.status_code >= 500 and retry_count < max_retries - 1:
                    retry_count += 1
                    logger.warning(f"Request failed with {response.status_code}, retrying ({retry_count}/{max_retries})")
                    continue
                    
                logger.error(f"Request failed: {response.text}")
                raise Exception(f"Request failed: {response.text}")
                
            except httpx.TimeoutException:
                if retry_count < max_retries - 1:
                    retry_count += 1
                    logger.warning(f"Request timed out, retrying ({retry_count}/{max_retries})")
                    continue
                raise
            except Exception as e:
                logger.error(f"Request failed with error: {str(e)}")
                raise

    async def _get_list(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> List[Dict[str, Any]]:
        """Generic method for getting lists of items"""
        return await self.get(endpoint, self._build_params(params, **kwargs))

    async def _get_item(self, endpoint: str, item_id: int, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Generic method for getting a single item"""
        if not isinstance(item_id, int):
            raise ValueError(f"{endpoint} ID must be an integer")
        return await self.get(f"{endpoint}/{item_id}", self._build_params(params, **kwargs))

    # Projects
    async def get_projects(self, params: Optional[Dict[str, Any]] = None, **kwargs) -> List[Dict[str, Any]]:
        return await self._get_list('project/projects', params, fields=self.PROJECT_FIELDS, **kwargs)

    async def get_project(self, project_id: int, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        return await self._get_item('project/projects', project_id, params, **kwargs)

    async def get_project_notes(self, project_id: int, params: Optional[Dict[str, Any]] = None, **kwargs) -> List[Dict[str, Any]]:
        return await self._get_list(f'project/projects/{project_id}/notes', params, orderBy='dateCreated desc', **kwargs)

    async def get_project_tickets(self, project_id: int, params: Optional[Dict[str, Any]] = None, **kwargs) -> List[Dict[str, Any]]:
        base_params = {'conditions': f"project/id={project_id}"}
        if params:
            base_params.update(params)
        return await self._get_list('project/tickets', base_params, fields=self.TICKET_FIELDS, orderBy='dateEntered desc', **kwargs)

    # Time Entries
    async def get_time_entries(self, params: Optional[Dict[str, Any]] = None, **kwargs) -> List[Dict[str, Any]]:
        return await self._get_list('time/entries', params, fields=self.TIME_ENTRY_FIELDS, orderBy='timeStart desc', **kwargs)

    # Members
    async def get_members(self, params: Optional[Dict[str, Any]] = None, **kwargs) -> List[Dict[str, Any]]:
        base_params = {'conditions': "inactiveFlag=false"}
        if params:
            base_params.update(params)
        return await self._get_list('system/members', base_params, orderBy='firstName asc', **kwargs)

    # Tickets
    async def get_tickets(self, params: Optional[Dict[str, Any]] = None, **kwargs) -> List[Dict[str, Any]]:
        return await self._get_list('project/tickets', params, fields=self.TICKET_FIELDS, orderBy='dateEntered desc', **kwargs)

    async def get_ticket(self, ticket_id: int, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        return await self._get_item('project/tickets', ticket_id, params, **kwargs)

    async def get_ticket_notes(self, ticket_id: int, params: Optional[Dict[str, Any]] = None, **kwargs) -> List[Dict[str, Any]]:
        return await self._get_list(f'project/tickets/{ticket_id}/allNotes', params, orderBy='dateCreated desc', **kwargs)

    async def get_ticket_time_entries(self, ticket_id: int, params: Optional[Dict[str, Any]] = None, **kwargs) -> List[Dict[str, Any]]:
        return await self._get_list(f'project/tickets/{ticket_id}/timeentries', params, fields=self.TIME_ENTRY_FIELDS, orderBy='timeStart desc', **kwargs)

    async def verify_credentials(self) -> bool:
        """Verify ConnectWise credentials by making a test request"""
        try:
            await self.get('system/info')
            return True
        except Exception as e:
            logger.error(f"Failed to verify credentials: {str(e)}")
            return False

    async def close(self):
        """Close the HTTP client"""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose() 