"""Tests for MCP Service"""
import pytest
from src.services.mcp_service import MCPService, MCPAgentRegistry
from src.schemas.mcp import MCPRequest, MCPResponse


@pytest.fixture
def registry():
    """Create a new registry for each test"""
    return MCPAgentRegistry()


@pytest.fixture
def mcp_service(registry):
    """Create MCP service with new registry"""
    return MCPService(registry)


@pytest.mark.asyncio
async def test_register_agent(registry):
    """Test agent registration"""
    registry.register_agent(
        "test-agent",
        {"name": "Test Agent", "type": "Test"}
    )
    
    agent = registry.get_agent("test-agent")
    assert agent is not None
    assert agent["name"] == "Test Agent"


@pytest.mark.asyncio
async def test_register_handler(registry):
    """Test handler registration"""
    async def test_handler(params):
        return {"result": "success", "params": params}
    
    registry.register_agent("test-agent", {"name": "Test"})
    registry.register_handler("test-agent", "test_method", test_handler)
    
    handler = registry.get_handler("test-agent", "test_method")
    assert handler is not None
    
    result = await handler({"test": "data"})
    assert result["result"] == "success"


@pytest.mark.asyncio
async def test_send_request_success(mcp_service):
    """Test successful MCP request"""
    async def handler(params):
        return {"processed": params.get("data", "default")}
    
    mcp_service.registry.register_agent("test-agent", {"name": "Test"})
    mcp_service.registry.register_handler("test-agent", "process", handler)
    
    response = await mcp_service.send_request(
        "test-agent",
        "process",
        {"data": "test_value"}
    )
    
    assert response.error is None
    assert response.result is not None
    assert response.result["processed"] == "test_value"


@pytest.mark.asyncio
async def test_send_request_agent_not_found(mcp_service):
    """Test MCP request with non-existent agent"""
    response = await mcp_service.send_request(
        "non-existent-agent",
        "method",
        {}
    )
    
    assert response.error is not None
    assert response.error["code"] == "AGENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_send_request_method_not_found(mcp_service):
    """Test MCP request with non-existent method"""
    mcp_service.registry.register_agent("test-agent", {"name": "Test"})
    
    response = await mcp_service.send_request(
        "test-agent",
        "non-existent-method",
        {}
    )
    
    assert response.error is not None
    assert response.error["code"] == "METHOD_NOT_FOUND"


@pytest.mark.asyncio
async def test_broadcast_notification(mcp_service):
    """Test broadcast notification to all agents"""
    async def handler1(params):
        return {"agent": "agent1", "data": params}
    
    async def handler2(params):
        return {"agent": "agent2", "data": params}
    
    mcp_service.registry.register_agent("agent1", {"name": "Agent 1"})
    mcp_service.registry.register_agent("agent2", {"name": "Agent 2"})
    
    mcp_service.registry.register_handler("agent1", "notify", handler1)
    mcp_service.registry.register_handler("agent2", "notify", handler2)
    
    results = await mcp_service.broadcast_notification(
        "notify",
        {"message": "test"}
    )
    
    assert len(results) == 2
    assert "agent1" in results
    assert "agent2" in results


@pytest.mark.asyncio
async def test_list_agents(registry):
    """Test listing all agents"""
    registry.register_agent("agent1", {"name": "Agent 1"})
    registry.register_agent("agent2", {"name": "Agent 2"})
    
    agents = registry.list_agents()
    assert len(agents) == 2
    assert "agent1" in agents
    assert "agent2" in agents

