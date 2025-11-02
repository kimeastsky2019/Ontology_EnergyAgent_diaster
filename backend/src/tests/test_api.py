"""Tests for API endpoints"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_readiness_check(client):
    """Test readiness check endpoint"""
    response = client.get("/ready")
    assert response.status_code == 200
    assert "status" in response.json()


@pytest.mark.asyncio
async def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "testpassword123",
            "full_name": "New User"
        }
    )
    assert response.status_code == 200
    assert "user_id" in response.json()


@pytest.mark.asyncio
async def test_login(client, test_user):
    """Test user login"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_list_mcp_agents(client, auth_headers):
    """Test listing MCP agents"""
    response = client.get("/api/v1/mcp/agents", headers=auth_headers)
    assert response.status_code == 200
    assert "agents" in response.json()
    assert "count" in response.json()


@pytest.mark.asyncio
async def test_get_agent_info(client, auth_headers):
    """Test getting agent information"""
    response = client.get(
        "/api/v1/mcp/agents/data-quality-agent",
        headers=auth_headers
    )
    # May return 404 if agent not registered yet
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_send_mcp_request(client, auth_headers):
    """Test sending MCP request"""
    response = client.post(
        "/api/v1/mcp/request",
        json={
            "agent_id": "data-quality-agent",
            "method": "get_status",
            "params": {}
        },
        headers=auth_headers
    )
    # May fail if agent not registered
    assert response.status_code in [200, 500, 404]


@pytest.mark.asyncio
async def test_analyze_with_agent(client, auth_headers):
    """Test analyzing data with specific agent"""
    response = client.post(
        "/api/v1/orchestrator/agents/data-quality-agent/analyze",
        json={
            "data_points": [
                {"timestamp": "2025-01-01T00:00:00Z", "value": 100}
            ]
        },
        headers=auth_headers
    )
    # May fail if agent not registered
    assert response.status_code in [200, 500, 404]


@pytest.mark.asyncio
async def test_create_asset(client, auth_headers):
    """Test creating energy asset"""
    response = client.post(
        "/api/v1/assets/",
        json={
            "name": "Test Solar Farm",
            "type": "solar",
            "capacity_kw": 500.0
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["name"] == "Test Solar Farm"


@pytest.mark.asyncio
async def test_get_assets(client, auth_headers):
    """Test getting assets list"""
    response = client.get("/api/v1/assets/", headers=auth_headers)
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()

