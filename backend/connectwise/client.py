from typing import Optional, Dict, Any, List, ClassVar, Callable
import os
import httpx
import base64
import logging
import asyncio
from datetime import datetime, timedelta
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter using token bucket algorithm"""
    def __init__(self, rate_limit: int = 1000, time_window: int = 60):
        self.rate_limit = rate_limit  # requests per time window
        self.time_window = time_window  # time window in seconds
        self.tokens = rate_limit
        self.last_update = datetime.now()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire a token for making a request"""
        async with self._lock:
            now = datetime.now()
            time_passed = (now - self.last_update).total_seconds()
            
            # Replenish tokens based on time passed
            self.tokens = min(
                self.rate_limit,
                self.tokens + int((time_passed * self.rate_limit) / self.time_window)
            )
            self.last_update = now
            
            if self.tokens > 0:
                self.tokens -= 1
                return True
            
            # Calculate wait time if no tokens available
            wait_time = (self.time_window / self.rate_limit) - time_passed
            if wait_time > 0:
                logger.warning(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
                self.tokens = 1
                self.tokens -= 1
            return True

class ConnectWiseClient:
    # Class-level client for connection pooling
    _http_client: ClassVar[Optional[httpx.AsyncClient]] = None
    _rate_limiter: ClassVar[Optional[RateLimiter]] = None
    
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
    NOTE_FIELDS = [
        'id', 'text', 'detailDescriptionFlag', 'internalAnalysisFlag',
        'resolutionFlag', 'dateCreated', 'createdBy'
    ]
    
    def __init__(self):
        self.base_url = os.getenv('CONNECTWISE_URL', os.getenv('CW_BASE_URL'))
        self.company = os.getenv('CONNECTWISE_COMPANY', 'it360nz')
        self.public_key = os.getenv('CONNECTWISE_PUBLIC_KEY', os.getenv('CW_PUBLIC_KEY'))
        self.private_key = os.getenv('CONNECTWISE_PRIVATE_KEY', os.getenv('CW_PRIVATE_KEY'))
        self.client_id = os.getenv('CONNECTWISE_CLIENT_ID', os.getenv('CW_CLIENT_ID'))
        
        if not all([self.base_url, self.company, self.public_key, self.private_key, self.client_id]):
            raise ValueError("Missing required ConnectWise configuration")
        
        # Initialize rate limiter if not exists
        if ConnectWiseClient._rate_limiter is None:
            ConnectWiseClient._rate_limiter = RateLimiter()
        
        # Generate auth token once
        self._auth_token = self._generate_auth_token()
        
        # Create headers once
        self._headers = {
            'Authorization': self._auth_token,
            'ClientID': self.client_id,
            'Content-Type': 'application/json'
        }
        
        logger.info(f"Initialized ConnectWise client for {self.company}")

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

    @property
    def rate_limiter(self) -> RateLimiter:
        """Get the rate limiter instance"""
        return self._rate_limiter

    def _generate_auth_token(self) -> str:
        """Generate Basic auth token for ConnectWise API"""
        credentials = f"{self.company}+{self.public_key}:{self.private_key}"
        encoded = base64.b64encode(credentials.encode()).decode()
        auth = f"Basic {encoded}"
        return auth

    def _build_params(self, base_params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Build query parameters with defaults"""
        params = {
            'page': 1,
            'pageSize': 100,
            'fields': kwargs.get('fields', self.BASIC_FIELDS),
            **(base_params or {})
        }
        
        # Add orderBy if specified and not None
        if 'orderBy' in kwargs and kwargs['orderBy'] is not None:
            params['orderBy'] = kwargs['orderBy']
        
        # Clean params
        params = {k: v for k, v in params.items() if v is not None}
        for key, value in params.items():
            if isinstance(value, (list, tuple)):
                params[key] = ','.join(str(x) for x in value)
                
        return params

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make a GET request to the ConnectWise API with rate limiting"""
        url = f"{self.base_url}/{endpoint}"
        
        logger.debug(f"Making request to: {url}")
        logger.debug(f"With params: {params}")
        
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = await self.http_client.get(url, headers=self._headers, params=params)
                
                if response.status_code == 200:
                    return response.json()
                
                if response.status_code == 429:  # Too Many Requests
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limit exceeded, waiting {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    continue
                    
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
        return await self._get_list('project/projects', params, fields=self.PROJECT_FIELDS, orderBy='lastUpdated desc', **kwargs)

    async def get_project(self, project_id: int, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        return await self._get_item('project/projects', project_id, params, fields=self.PROJECT_FIELDS, **kwargs)

    async def get_project_notes(self, project_id: int, params: Optional[Dict[str, Any]] = None, **kwargs) -> List[Dict[str, Any]]:
        """Get notes for a project"""
        return await self._get_list(f'project/projects/{project_id}/notes', params, fields=self.NOTE_FIELDS, **kwargs)

    async def get_project_tickets(self, project_id: int, params: Optional[Dict[str, Any]] = None, **kwargs) -> List[Dict[str, Any]]:
        base_params = {'conditions': f"project/id={project_id}"}
        if params:
            base_params.update(params)
        return await self._get_list('project/tickets', base_params, fields=self.TICKET_FIELDS, orderBy='dateEntered desc', **kwargs)

    # Time Entries
    async def get_time_entries(self, params=None, **kwargs):
        """Get time entries with optional filtering parameters."""
        if params is None:
            params = {}
        if 'conditions' in params and 'chargeToType' in params['conditions']:
            # Replace "Project" with ProjectTicket which is the correct enum value
            params['conditions'] = params['conditions'].replace('chargeToType="Project"', 'chargeToType="ProjectTicket"')
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
        return await self._get_item('project/tickets', ticket_id, params, fields=self.TICKET_FIELDS, **kwargs)

    async def get_ticket_notes(self, ticket_id: int, params: Optional[Dict[str, Any]] = None, **kwargs) -> List[Dict[str, Any]]:
        return await self._get_list(f'project/tickets/{ticket_id}/allNotes', params, fields=self.NOTE_FIELDS, **kwargs)

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