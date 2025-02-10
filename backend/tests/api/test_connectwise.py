import pytest
from backend.connectwise.client import ConnectWiseClient
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def cw_client():
    """Create and return a ConnectWise client instance"""
    client = ConnectWiseClient()
    # Debug log the auth token
    logger.debug(f"Auth token: {client._get_basic_auth()}")
    return client

@pytest.mark.asyncio
async def test_verify_credentials(cw_client):
    """Test basic credential verification"""
    headers = await cw_client._get_headers()
    logger.debug(f"Request headers: {headers}")
    result = await cw_client.verify_credentials()
    assert result == True, "Credentials verification failed"

@pytest.mark.asyncio
async def test_basic_project_list(cw_client):
    """Test simplest possible project list request"""
    params = {
        'page': 1,
        'pageSize': 1,  # Just get one result
        'fields': 'id,name'  # Minimum fields
    }
    
    try:
        result = await cw_client.get_projects(params)
        logger.info(f"Project result: {result}")
        assert isinstance(result, list), "Expected list response"
        assert len(result) > 0, "Expected at least one project"
        assert all(isinstance(p, dict) for p in result), "Expected list of dictionaries"
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_raw_project_request(cw_client):
    """Test raw project endpoint with minimal parameters"""
    try:
        result = await cw_client.get('project/projects', {
            'page': 1,
            'pageSize': 1
        })
        logger.info(f"Raw project result: {result}")
        assert isinstance(result, list), "Expected list response"
        assert len(result) > 0, "Expected at least one project"
        assert all(isinstance(p, dict) for p in result), "Expected list of dictionaries"
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_system_info(cw_client):
    """Test basic system info endpoint"""
    try:
        result = await cw_client.get('system/info', {})
        logger.info(f"System info result: {result}")
        assert isinstance(result, dict), "Expected dictionary response"
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        raise
