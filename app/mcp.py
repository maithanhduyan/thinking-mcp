# -*- coding: utf-8 -*-
# app/mcp
# This file is part of the Thinking MCP project.

"""
Các dạng tư duy chính:

1. Linear Thinking (Tư duy tuyến tính)
Tư duy theo trình tự logic từ A → B → C
Phù hợp cho các vấn đề có bước rõ ràng

2. Lateral Thinking (Tư duy bên)
Tìm giải pháp sáng tạo, phi truyền thống
Edward de Bono's Six Thinking Hats
Brainstorming, tạo ý tưởng mới

3. Critical Thinking (Tư duy phản biện)
Phân tích, đánh giá thông tin
Tìm lỗ hổng trong lập luận
Kiểm tra tính hợp lý

4. Systems Thinking (Tư duy hệ thống)
Nhìn nhận toàn cục, mối quan hệ
Hiểu các thành phần tương tác
Root cause analysis

5. Dialectical Thinking (Tư duy biện chứng)
Thesis → Antithesis → Synthesis
Xem xét mâu thuẫn để tìm giải pháp

6. Parallel Thinking (Tư duy song song)
Six Thinking Hats method
Mỗi người cùng góc nhìn

7. Divergent vs Convergent Thinking
Divergent: Tạo nhiều ý tưởng
Convergent: Thu hẹp về giải pháp tối ưu

8. Analogical Thinking (Tư duy so sánh)
Sử dụng phép tương tự
Học từ trường hợp tương tự

9. Inductive vs Deductive Thinking
Inductive: Từ cụ thể → tổng quát
Deductive: Từ tổng quát → cụ thể

10. Design Thinking
Empathize → Define → Ideate → Prototype → Test
Tập trung vào người dùng


"""

import json
import time
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request
from app.json_rpc import (
    JsonRpcRequest, 
    JsonRpcResponse, 
    JsonRpcErrorResponse,
    UnicodeJSONResponse,
    create_error_response,
    create_success_response
)
from app.sequential import think_sequentially, quick_analysis
from app.memory import (
    memory_create_entities,
    memory_create_relations,
    memory_add_observations,
    memory_delete_entities,
    memory_delete_observations,
    memory_delete_relations,
    memory_read_graph,
    memory_search_nodes,
    memory_open_nodes
)

from typing import Dict, Any, Callable, Optional, Union
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


# MCP Method Handlers Registry
METHOD_HANDLERS: Dict[str, Callable] = {}


def register_method(method_name: str):
    """Decorator để đăng ký method handlers"""
    def decorator(func: Callable):
        METHOD_HANDLERS[method_name] = func
        return func
    return decorator


@register_method("echo")
async def handle_echo(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Echo method - returns the input parameters back
    Params can be either dict or list
    """
    return {
        "method": "echo",
        "received_params": params,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": "Echo successful"
    }


@register_method("time")
async def handle_time(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Time method - returns current server time in various formats
    """
    now = datetime.now(timezone.utc)
    return {
        "method": "time",
        "server_time": {
            "iso_format": now.isoformat(),
            "timestamp": now.timestamp(),
            "unix_timestamp": int(now.timestamp()),
            "formatted": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "timezone": "UTC"
        },
        "message": "Time retrieved successfully"
    }


@register_method("ping")
async def handle_ping(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Ping method - simple health check
    """
    return {
        "method": "ping",
        "status": "pong",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": "Server is alive"
    }


@register_method("tools.list")
async def handle_list_tools(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    List all available tools/methods
    """
    tools = []
    for method_name in METHOD_HANDLERS.keys():
        tools.append({
            "name": method_name,
            "description": f"Handler for {method_name} method"
        })
    
    return {
        "method": "tools.list", 
        "tools": tools,
        "count": len(tools),
        "message": "Available tools listed successfully"
    }


@register_method("calculate")
async def handle_calculate(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Calculate method - performs basic arithmetic operations
    Expected params: {"operation": "add|subtract|multiply|divide", "a": number, "b": number}
    """
    if not params or not isinstance(params, dict):
        raise ValueError("Calculate method requires params as dict with 'operation', 'a', and 'b'")
    
    operation = params.get("operation")
    a = params.get("a")
    b = params.get("b")
    
    if not all([operation, a is not None, b is not None]):
        raise ValueError("Missing required parameters: operation, a, b")
    
    try:
        # Type assertion after validation
        a_val = float(a)  # type: ignore
        b_val = float(b)  # type: ignore
    except (TypeError, ValueError):
        raise ValueError("Parameters 'a' and 'b' must be numbers")
    
    result = None
    if operation == "add":
        result = a_val + b_val
    elif operation == "subtract":
        result = a_val - b_val
    elif operation == "multiply":
        result = a_val * b_val
    elif operation == "divide":
        if b_val == 0:
            raise ValueError("Division by zero is not allowed")
        result = a_val / b_val
    else:
        raise ValueError(f"Unsupported operation: {operation}. Supported: add, subtract, multiply, divide")
    
    return {
        "method": "calculate",
        "operation": operation,
        "operands": {"a": a_val, "b": b_val},
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": f"Calculation successful: {a_val} {operation} {b_val} = {result}"
    }


@register_method("server.info")
async def handle_server_info(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Server info method - returns detailed server information
    """
    import platform
    import sys
    
    return {
        "method": "server.info",
        "server": {
            "name": "Thinking MCP Server",
            "version": "1.0.0",
            "protocol": "JSON-RPC 2.0",
            "description": "Model Context Protocol server with extensible architecture"
        },
        "runtime": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor()
        },
        "capabilities": {
            "methods_count": len(METHOD_HANDLERS),
            "available_methods": list(METHOD_HANDLERS.keys()),
            "supports_batch_requests": False,
            "supports_notifications": False
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": "Server information retrieved successfully"
    }


@register_method("initialize")
async def handle_initialize(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Initialize method - MCP protocol initialization
    This is called when a client first connects to establish capabilities
    """
    client_info = params if isinstance(params, dict) else {}
    
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {
                "listChanged": False
            },
            "prompts": {
                "listChanged": False
            },
            "resources": {
                "subscribe": False,
                "listChanged": False
            },
            "logging": {}
        },
        "serverInfo": {
            "name": "thinking-mcp",
            "version": "1.0.0"
        },
        "instructions": "Thinking MCP Server initialized successfully"
    }


@register_method("tools/list")
async def handle_tools_list(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    List available tools - MCP standard method
    """
    tools = [
        {
            "name": "echo",
            "description": "Echo back the provided parameters",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to echo back"
                    }
                }
            }
        },
        {
            "name": "time",
            "description": "Get current server time",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "ping",
            "description": "Ping the server for health check",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "calculate",
            "description": "Perform basic arithmetic operations",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "Arithmetic operation to perform"
                    },
                    "a": {
                        "type": "number",
                        "description": "First operand"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second operand"
                    }
                },
                "required": ["operation", "a", "b"]
            }
        },
        {
            "name": "sequential_thinking",
            "description": "Perform step-by-step reasoning analysis",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": "Problem statement to analyze"
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional context information"
                    },
                    "max_steps": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 10,
                        "description": "Maximum number of thinking steps"
                    }
                },
                "required": ["problem"]
            }
        },
        {
            "name": "quick_analysis",
            "description": "Perform rapid problem analysis",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": "Problem statement to analyze quickly"
                    }
                },
                "required": ["problem"]
            }
        },
        {
            "name": "memory_create_entities",
            "description": "Create multiple new entities in the knowledge graph",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "The name of the entity"},
                                "entityType": {"type": "string", "description": "The type of the entity"},
                                "observations": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "An array of observation contents associated with the entity"
                                }
                            },
                            "required": ["name", "entityType", "observations"]
                        }
                    }
                },
                "required": ["entities"]
            }
        },
        {
            "name": "memory_create_relations",
            "description": "Create multiple new relations between entities in the knowledge graph",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "relations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "from": {"type": "string", "description": "The name of the entity where the relation starts"},
                                "to": {"type": "string", "description": "The name of the entity where the relation ends"},
                                "relationType": {"type": "string", "description": "The type of the relation"}
                            },
                            "required": ["from", "to", "relationType"]
                        }
                    }
                },
                "required": ["relations"]
            }
        },
        {
            "name": "memory_add_observations",
            "description": "Add new observations to existing entities in the knowledge graph",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "observations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entityName": {"type": "string", "description": "The name of the entity to add the observations to"},
                                "contents": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "An array of observation contents to add"
                                }
                            },
                            "required": ["entityName", "contents"]
                        }
                    }
                },
                "required": ["observations"]
            }
        },
        {
            "name": "memory_delete_entities",
            "description": "Delete multiple entities and their associated relations from the knowledge graph",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "entityNames": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "An array of entity names to delete"
                    }
                },
                "required": ["entityNames"]
            }
        },
        {
            "name": "memory_delete_observations",
            "description": "Delete specific observations from entities in the knowledge graph",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deletions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entityName": {"type": "string", "description": "The name of the entity containing the observations"},
                                "observations": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "An array of observations to delete"
                                }
                            },
                            "required": ["entityName", "observations"]
                        }
                    }
                },
                "required": ["deletions"]
            }
        },
        {
            "name": "memory_delete_relations",
            "description": "Delete multiple relations from the knowledge graph",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "relations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "from": {"type": "string", "description": "The name of the entity where the relation starts"},
                                "to": {"type": "string", "description": "The name of the entity where the relation ends"},
                                "relationType": {"type": "string", "description": "The type of the relation"}
                            },
                            "required": ["from", "to", "relationType"]
                        }
                    }
                },
                "required": ["relations"]
            }
        },
        {
            "name": "memory_read_graph",
            "description": "Read the entire knowledge graph",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "memory_search_nodes",
            "description": "Search for nodes in the knowledge graph based on a query",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query to match against entity names, types, and observation content"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "memory_open_nodes",
            "description": "Open specific nodes in the knowledge graph by their names",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "An array of entity names to retrieve"
                    }
                },
                "required": ["names"]
            }
        }
    ]
    
    return {
        "tools": tools
    }


@register_method("tools/call")
async def handle_tools_call(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Call a specific tool - MCP standard method
    """
    if not params or not isinstance(params, dict):
        raise ValueError("tools/call requires params with 'name' and 'arguments'")
    
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    if not tool_name:
        raise ValueError("Missing required parameter: name")
    
    # Map tool calls to internal methods
    tool_method_map = {
        "echo": "echo",
        "time": "time", 
        "ping": "ping",
        "calculate": "calculate",
        "sequential_thinking": "sequential_thinking",
        "quick_analysis": "quick_analysis",
        "memory_create_entities": "memory_create_entities",
        "memory_create_relations": "memory_create_relations",
        "memory_add_observations": "memory_add_observations",
        "memory_delete_entities": "memory_delete_entities",
        "memory_delete_observations": "memory_delete_observations",
        "memory_delete_relations": "memory_delete_relations",
        "memory_read_graph": "memory_read_graph",
        "memory_search_nodes": "memory_search_nodes",
        "memory_open_nodes": "memory_open_nodes"
    }
    
    internal_method = tool_method_map.get(tool_name)
    if not internal_method or internal_method not in METHOD_HANDLERS:
        raise ValueError(f"Tool '{tool_name}' not found")
    
    # Call the internal method handler
    handler = METHOD_HANDLERS[internal_method]
    result = await handler(arguments)
    
    # Format as MCP tool call response
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(result, ensure_ascii=False, indent=2)
            }
        ],
        "isError": False
    }


@register_method("prompts/list")
async def handle_prompts_list(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    List available prompts - MCP standard method
    """
    return {
        "prompts": []
    }


@register_method("resources/list")
async def handle_resources_list(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    List available resources - MCP standard method
    """
    return {
        "resources": []
    }


@register_method("notifications/initialized")
async def handle_notifications_initialized(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Handle initialized notification from client
    This is a notification (no response expected) but we'll return empty for consistency
    """
    logger.info("Client initialization completed")
    return {
        "status": "acknowledged",
        "message": "Server ready for requests"
    }


@register_method("sequential_thinking")
async def handle_sequential_thinking(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Sequential thinking method - performs step-by-step reasoning analysis
    Expected params: {"problem": "problem statement", "context": {...}, "max_steps": 10}
    """
    if not params or not isinstance(params, dict):
        raise ValueError("Sequential thinking requires params as dict with 'problem'")
    
    problem = params.get("problem")
    if not problem:
        raise ValueError("Missing required parameter: problem")
    
    context = params.get("context", {})
    max_steps = params.get("max_steps", 10)
    
    try:
        # Validate max_steps
        if not isinstance(max_steps, int) or max_steps < 1 or max_steps > 20:
            max_steps = 10
        
        # Process sequential thinking
        result = await think_sequentially(problem, context, max_steps)
        
        return {
            "method": "sequential_thinking",
            "input": {
                "problem": problem,
                "context": context,
                "max_steps": max_steps
            },
            "thinking_result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Sequential thinking process completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error in sequential thinking: {e}")
        raise ValueError(f"Sequential thinking failed: {str(e)}")


@register_method("quick_analysis")
async def handle_quick_analysis(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Quick analysis method - performs rapid problem analysis
    Expected params: {"problem": "problem statement"}
    """
    if not params or not isinstance(params, dict):
        raise ValueError("Quick analysis requires params as dict with 'problem'")
    
    problem = params.get("problem")
    if not problem:
        raise ValueError("Missing required parameter: problem")
    
    try:
        # Process quick analysis
        result = await quick_analysis(problem)
        
        return {
            "method": "quick_analysis",
            "input": {
                "problem": problem
            },
            "analysis_result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Quick analysis completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error in quick analysis: {e}")
        raise ValueError(f"Quick analysis failed: {str(e)}")


@register_method("memory_create_entities")
async def handle_memory_create_entities(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Create multiple new entities in the knowledge graph
    Expected params: {"entities": [{"name": "...", "entityType": "...", "observations": [...]}]}
    """
    if not params or not isinstance(params, dict):
        raise ValueError("Memory create entities requires params as dict with 'entities'")
    
    entities_data = params.get("entities")
    if not entities_data or not isinstance(entities_data, list):
        raise ValueError("Missing or invalid 'entities' parameter")
    
    try:
        result = await memory_create_entities(entities_data)
        return {
            "method": "memory_create_entities",
            "created_entities": result,
            "count": len(result),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": f"Successfully created {len(result)} entities"
        }
    except Exception as e:
        logger.error(f"Error in memory_create_entities: {e}")
        raise ValueError(f"Memory create entities failed: {str(e)}")


@register_method("memory_create_relations")
async def handle_memory_create_relations(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Create multiple new relations between entities
    Expected params: {"relations": [{"from": "...", "to": "...", "relationType": "..."}]}
    """
    if not params or not isinstance(params, dict):
        raise ValueError("Memory create relations requires params as dict with 'relations'")
    
    relations_data = params.get("relations")
    if not relations_data or not isinstance(relations_data, list):
        raise ValueError("Missing or invalid 'relations' parameter")
    
    try:
        result = await memory_create_relations(relations_data)
        return {
            "method": "memory_create_relations",
            "created_relations": result,
            "count": len(result),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": f"Successfully created {len(result)} relations"
        }
    except Exception as e:
        logger.error(f"Error in memory_create_relations: {e}")
        raise ValueError(f"Memory create relations failed: {str(e)}")


@register_method("memory_add_observations")
async def handle_memory_add_observations(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Add new observations to existing entities
    Expected params: {"observations": [{"entityName": "...", "contents": [...]}]}
    """
    if not params or not isinstance(params, dict):
        raise ValueError("Memory add observations requires params as dict with 'observations'")
    
    observations_data = params.get("observations")
    if not observations_data or not isinstance(observations_data, list):
        raise ValueError("Missing or invalid 'observations' parameter")
    
    try:
        result = await memory_add_observations(observations_data)
        return {
            "method": "memory_add_observations",
            "results": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": f"Successfully added observations to {len(result)} entities"
        }
    except Exception as e:
        logger.error(f"Error in memory_add_observations: {e}")
        raise ValueError(f"Memory add observations failed: {str(e)}")


@register_method("memory_delete_entities")
async def handle_memory_delete_entities(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Delete multiple entities and their associated relations
    Expected params: {"entityNames": ["name1", "name2", ...]}
    """
    if not params or not isinstance(params, dict):
        raise ValueError("Memory delete entities requires params as dict with 'entityNames'")
    
    entity_names = params.get("entityNames")
    if not entity_names or not isinstance(entity_names, list):
        raise ValueError("Missing or invalid 'entityNames' parameter")
    
    try:
        result = await memory_delete_entities(entity_names)
        return {
            "method": "memory_delete_entities",
            "deleted_count": len(entity_names),
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": result
        }
    except Exception as e:
        logger.error(f"Error in memory_delete_entities: {e}")
        raise ValueError(f"Memory delete entities failed: {str(e)}")


@register_method("memory_delete_observations")
async def handle_memory_delete_observations(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Delete specific observations from entities
    Expected params: {"deletions": [{"entityName": "...", "observations": [...]}]}
    """
    if not params or not isinstance(params, dict):
        raise ValueError("Memory delete observations requires params as dict with 'deletions'")
    
    deletions_data = params.get("deletions")
    if not deletions_data or not isinstance(deletions_data, list):
        raise ValueError("Missing or invalid 'deletions' parameter")
    
    try:
        result = await memory_delete_observations(deletions_data)
        return {
            "method": "memory_delete_observations",
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": result
        }
    except Exception as e:
        logger.error(f"Error in memory_delete_observations: {e}")
        raise ValueError(f"Memory delete observations failed: {str(e)}")


@register_method("memory_delete_relations")
async def handle_memory_delete_relations(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Delete multiple relations from the knowledge graph
    Expected params: {"relations": [{"from": "...", "to": "...", "relationType": "..."}]}
    """
    if not params or not isinstance(params, dict):
        raise ValueError("Memory delete relations requires params as dict with 'relations'")
    
    relations_data = params.get("relations")
    if not relations_data or not isinstance(relations_data, list):
        raise ValueError("Missing or invalid 'relations' parameter")
    
    try:
        result = await memory_delete_relations(relations_data)
        return {
            "method": "memory_delete_relations",
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": result
        }
    except Exception as e:
        logger.error(f"Error in memory_delete_relations: {e}")
        raise ValueError(f"Memory delete relations failed: {str(e)}")


@register_method("memory_read_graph")
async def handle_memory_read_graph(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Read the entire knowledge graph
    Expected params: {} (no parameters needed)
    """
    try:
        result = await memory_read_graph()
        return {
            "method": "memory_read_graph",
            "knowledge_graph": result,
            "entities_count": len(result.get("entities", [])),
            "relations_count": len(result.get("relations", [])),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Successfully read knowledge graph"
        }
    except Exception as e:
        logger.error(f"Error in memory_read_graph: {e}")
        raise ValueError(f"Memory read graph failed: {str(e)}")


@register_method("memory_search_nodes")
async def handle_memory_search_nodes(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Search for nodes in the knowledge graph based on a query
    Expected params: {"query": "search term"}
    """
    if not params or not isinstance(params, dict):
        raise ValueError("Memory search nodes requires params as dict with 'query'")
    
    query = params.get("query")
    if not query or not isinstance(query, str):
        raise ValueError("Missing or invalid 'query' parameter")
    
    try:
        result = await memory_search_nodes(query)
        return {
            "method": "memory_search_nodes",
            "query": query,
            "search_results": result,
            "entities_found": len(result.get("entities", [])),
            "relations_found": len(result.get("relations", [])),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": f"Search completed for query: '{query}'"
        }
    except Exception as e:
        logger.error(f"Error in memory_search_nodes: {e}")
        raise ValueError(f"Memory search nodes failed: {str(e)}")


@register_method("memory_open_nodes")
async def handle_memory_open_nodes(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Open specific nodes in the knowledge graph by their names
    Expected params: {"names": ["name1", "name2", ...]}
    """
    if not params or not isinstance(params, dict):
        raise ValueError("Memory open nodes requires params as dict with 'names'")
    
    names = params.get("names")
    if not names or not isinstance(names, list):
        raise ValueError("Missing or invalid 'names' parameter")
    
    try:
        result = await memory_open_nodes(names)
        return {
            "method": "memory_open_nodes",
            "requested_names": names,
            "opened_nodes": result,
            "entities_found": len(result.get("entities", [])),
            "relations_found": len(result.get("relations", [])),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": f"Successfully opened {len(result.get('entities', []))} nodes"
        }
    except Exception as e:
        logger.error(f"Error in memory_open_nodes: {e}")
        raise ValueError(f"Memory open nodes failed: {str(e)}")


async def process_jsonrpc_request(request_data: dict) -> dict:
    """
    Process JSON-RPC 2.0 request and return appropriate response
    """
    try:
        # Validate JSON-RPC request structure
        rpc_request = JsonRpcRequest(**request_data)
        
        # Check if method exists
        if rpc_request.method not in METHOD_HANDLERS:
            error_response = create_error_response(
                "METHOD_NOT_FOUND",
                f"Method '{rpc_request.method}' not found",
                rpc_request.id
            )
            return error_response.model_dump()
        
        # Execute method handler
        handler = METHOD_HANDLERS[rpc_request.method]
        
        try:
            result = await handler(rpc_request.params)
            success_response = create_success_response(result, rpc_request.id)
            return success_response.model_dump()
            
        except Exception as handler_error:
            logger.error(f"Error in method handler '{rpc_request.method}': {handler_error}")
            error_response = create_error_response(
                "INTERNAL_ERROR",
                f"Error executing method '{rpc_request.method}': {str(handler_error)}",
                rpc_request.id
            )
            return error_response.model_dump()
            
    except Exception as validation_error:
        logger.error(f"Invalid JSON-RPC request structure: {validation_error}")
        error_response = create_error_response(
            "INVALID_REQUEST",
            f"Invalid request structure: {str(validation_error)}"
        )
        return error_response.model_dump()


# Main MCP endpoint for VS Code integration  
@router.api_route("/", methods=["GET", "POST"])
@router.api_route("", methods=["GET", "POST"])
async def mcp_endpoint(request: Request):
    """
    Main endpoint for MCP API.
    Handles both GET and POST requests with JSON-RPC 2.0 protocol.
    """
    if request.method == "GET":
        # Get list of available methods dynamically
        available_methods = list(METHOD_HANDLERS.keys())
        
        return UnicodeJSONResponse({
            "message": "Welcome to the Thinking MCP API!",
            "protocol": "JSON-RPC 2.0",
            "server": {
                "name": "Thinking MCP Server",
                "version": "1.0.0",
                "description": "Model Context Protocol server with extensible JSON-RPC 2.0 architecture"
            },
            "endpoint": "/mcp",
            "methods": ["GET", "POST"],
            "available_tools": available_methods,
            "usage": {
                "get_info": "GET /mcp",
                "call_method": "POST /mcp with JSON-RPC 2.0 format",
                "example_request": {
                    "jsonrpc": "2.0",
                    "method": "echo",
                    "params": {"message": "Hello World"},
                    "id": 1
                }
            }
        })
    
    elif request.method == "POST":
        try:
            request_data = await request.json()
            logger.info(f"Received JSON-RPC request: {request_data}")
            
            # Process JSON-RPC request
            response_data = await process_jsonrpc_request(request_data)
            
            logger.info(f"Sending JSON-RPC response: {response_data}")
            return UnicodeJSONResponse(response_data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request: {e}")
            error_response = create_error_response(
                "PARSE_ERROR", 
                "Invalid JSON"
            )
            return UnicodeJSONResponse(error_response.model_dump(), status_code=400)
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            error_response = create_error_response(
                "INTERNAL_ERROR", 
                "Internal server error"
            )
            return UnicodeJSONResponse(error_response.model_dump(), status_code=500)
    
    else:
        raise HTTPException(status_code=405, detail="Method Not Allowed")



