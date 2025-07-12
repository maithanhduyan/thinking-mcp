# -*- coding: utf-8 -*-
# File: app/mcp.py
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
import sys
import platform
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
from app.mcp_logger import mcp_tool_wrapper
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
    memory_open_nodes,
    memory_sync_to_database,
    use_memory_structures_for_analysis
)
from app.critical import (
    critical_thinking_analysis,
    get_critical_analysis_history,
    get_critical_analysis_stats
)
from app.lateral import (
    lateral_thinking_analysis,
    get_lateral_thinking_history,
    get_lateral_thinking_stats
)
from app.root_cause import (
    root_cause_analysis,
    get_rca_history,
    get_rca_stats
)
from app.systems_thinking import (
    systems_thinking_analysis,
    get_systems_thinking_history,
    get_systems_thinking_stats
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
@mcp_tool_wrapper("echo")
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
@mcp_tool_wrapper("time")
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
@mcp_tool_wrapper("ping")
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
@mcp_tool_wrapper("calculate")
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
        },
        {
            "name": "critical_thinking",
            "description": "Perform systematic critical analysis and evaluation of claims, arguments, and information",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "claim": {
                        "type": "string",
                        "description": "The main claim or argument being analyzed"
                    },
                    "evidence": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Evidence supporting the claim"
                    },
                    "assumptions": {
                        "type": "array", 
                        "items": {"type": "string"},
                        "description": "Underlying assumptions identified"
                    },
                    "counterarguments": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Arguments against the claim"
                    },
                    "logical_fallacies": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Logical fallacies identified"
                    },
                    "credibility_assessment": {
                        "type": "string",
                        "description": "Assessment of source credibility"
                    },
                    "conclusion": {
                        "type": "string",
                        "description": "Final reasoned conclusion"
                    },
                    "confidence_level": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 100,
                        "description": "Confidence level in conclusion (0-100%)"
                    },
                    "next_analysis_needed": {
                        "type": "boolean",
                        "description": "Whether further analysis is needed"
                    }
                },
                "required": ["claim", "evidence", "assumptions", "counterarguments", "logical_fallacies", "credibility_assessment", "conclusion", "confidence_level", "next_analysis_needed"]
            }
        },
        {
            "name": "critical_analysis_history",
            "description": "Get history of all critical thinking analyses performed",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "critical_analysis_stats",
            "description": "Get statistics about critical thinking analyses",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "lateral_thinking",
            "description": "Creative problem-solving using Edward de Bono's lateral thinking techniques",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "technique": {
                        "type": "string",
                        "enum": ["random_word", "provocation", "alternative", "reversal", "metaphor", "assumption_challenge"],
                        "description": "Lateral thinking technique to use"
                    },
                    "stimulus": {
                        "type": "string",
                        "description": "The stimulus or prompt used for the technique"
                    },
                    "connection": {
                        "type": "string",
                        "description": "How the stimulus connects to the problem"
                    },
                    "idea": {
                        "type": "string",
                        "description": "The creative idea generated"
                    },
                    "evaluation": {
                        "type": "string",
                        "description": "Brief evaluation of the idea's potential"
                    },
                    "next_technique_needed": {
                        "type": "boolean",
                        "description": "Whether to try another technique"
                    }
                },
                "required": ["technique", "stimulus", "connection", "idea", "evaluation", "next_technique_needed"]
            }
        },
        {
            "name": "lateral_thinking_history",
            "description": "Get history of all lateral thinking sessions performed",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "lateral_thinking_stats",
            "description": "Get statistics about lateral thinking sessions",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "root_cause_analysis",
            "description": "Systematic analysis to identify root causes of problems using various RCA techniques",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "problem_statement": {
                        "type": "string",
                        "description": "Clear description of the problem to analyze"
                    },
                    "technique": {
                        "type": "string",
                        "enum": ["5_whys", "fishbone", "fault_tree", "timeline", "barrier_analysis"],
                        "description": "RCA technique to use: 5_whys (Ask why repeatedly), fishbone (Ishikawa diagram), fault_tree (Top-down analysis), timeline (Chronological analysis), barrier_analysis (Failed controls analysis)"
                    },
                    "symptoms": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Observable symptoms of the problem"
                    },
                    "immediate_actions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Immediate actions taken to contain the problem"
                    },
                    "root_causes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Identified root causes"
                    },
                    "contributing_factors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Factors that contributed to the problem"
                    },
                    "preventive_actions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Actions to prevent recurrence"
                    },
                    "verification": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Steps to verify the root cause and effectiveness of solutions"
                    },
                    "next_analysis_needed": {
                        "type": "boolean",
                        "description": "Whether additional analysis is needed"
                    }
                },
                "required": ["problem_statement", "technique", "symptoms", "immediate_actions", "root_causes", "contributing_factors", "preventive_actions", "verification", "next_analysis_needed"]
            }
        },
        {
            "name": "root_cause_analysis_history",
            "description": "Get history of all root cause analyses performed",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "root_cause_analysis_stats",
            "description": "Get statistics about root cause analyses",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "systems_thinking",
            "description": "Holistic analysis of complex systems, identifying relationships, patterns, and leverage points",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "system_name": {
                        "type": "string",
                        "description": "Name of the system being analyzed"
                    },
                    "purpose": {
                        "type": "string",
                        "description": "Main purpose or function of the system"
                    },
                    "components": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {
                                    "type": "string",
                                    "enum": ["input", "process", "output", "feedback", "environment"]
                                },
                                "description": {"type": "string"},
                                "relationships": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            },
                            "required": ["name", "type", "description", "relationships"]
                        },
                        "description": "System components and their relationships"
                    },
                    "feedback_loops": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Feedback loops identified in the system"
                    },
                    "constraints": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Constraints limiting system performance"
                    },
                    "emergent_properties": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Properties that emerge from system interactions"
                    },
                    "leverage_points": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "High-impact intervention points"
                    },
                    "systemic_issues": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Systemic issues vs surface symptoms"
                    },
                    "interventions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Proposed system interventions"
                    },
                    "next_analysis_needed": {
                        "type": "boolean",
                        "description": "Whether deeper analysis is needed"
                    }
                },
                "required": ["system_name", "purpose", "components", "feedback_loops", "constraints", "emergent_properties", "leverage_points", "systemic_issues", "interventions", "next_analysis_needed"]
            }
        },
        {
            "name": "systems_thinking_history",
            "description": "Get history of all systems thinking analyses performed",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "systems_thinking_stats",
            "description": "Get statistics about systems thinking analyses",
            "inputSchema": {
                "type": "object",
                "properties": {}
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
        "memory_open_nodes": "memory_open_nodes",
        "critical_thinking": "critical_thinking",
        "critical_analysis_history": "critical_analysis_history",
        "critical_analysis_stats": "critical_analysis_stats",
        "lateral_thinking": "lateral_thinking",
        "lateral_thinking_history": "lateral_thinking_history",
        "lateral_thinking_stats": "lateral_thinking_stats",
        "root_cause_analysis": "root_cause_analysis",
        "root_cause_analysis_history": "root_cause_analysis_history",
        "root_cause_analysis_stats": "root_cause_analysis_stats",
        "systems_thinking": "systems_thinking",
        "systems_thinking_history": "systems_thinking_history",
        "systems_thinking_stats": "systems_thinking_stats"
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
@mcp_tool_wrapper("sequential_thinking")
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
@mcp_tool_wrapper("quick_analysis")
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
@mcp_tool_wrapper("memory_create_entities")
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
@mcp_tool_wrapper("memory_create_relations")
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
@mcp_tool_wrapper("memory_add_observations")
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
@mcp_tool_wrapper("memory_delete_entities")
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
@mcp_tool_wrapper("memory_delete_observations")
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
@mcp_tool_wrapper("memory_delete_relations")
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
@mcp_tool_wrapper("memory_read_graph")
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
@mcp_tool_wrapper("memory_search_nodes")
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
@mcp_tool_wrapper("memory_open_nodes")
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


@register_method("critical_thinking")
@mcp_tool_wrapper("critical_thinking")
async def handle_critical_thinking(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Critical thinking analysis method
    Expected params with all required fields for critical analysis
    """
    if not params or not isinstance(params, dict):
        raise ValueError("Critical thinking requires params as dict with analysis data")
    
    try:
        result = await critical_thinking_analysis(params)
        return {
            "method": "critical_thinking",
            "input_data": params,
            "analysis_result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Critical thinking analysis completed successfully"
        }
    except Exception as e:
        logger.error(f"Error in critical thinking: {e}")
        raise ValueError(f"Critical thinking analysis failed: {str(e)}")


@register_method("critical_analysis_history")
async def handle_critical_analysis_history(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Get history of all critical thinking analyses
    """
    try:
        result = await get_critical_analysis_history()
        return {
            "method": "critical_analysis_history",
            "analysis_history": result,
            "total_analyses": len(result),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": f"Retrieved {len(result)} critical analyses from history"
        }
    except Exception as e:
        logger.error(f"Error in critical analysis history: {e}")
        raise ValueError(f"Critical analysis history failed: {str(e)}")


@register_method("critical_analysis_stats")
async def handle_critical_analysis_stats(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Get statistics about critical thinking analyses
    """
    try:
        result = await get_critical_analysis_stats()
        return {
            "method": "critical_analysis_stats",
            "statistics": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Critical analysis statistics retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error in critical analysis stats: {e}")
        raise ValueError(f"Critical analysis stats failed: {str(e)}")


@register_method("lateral_thinking")
@mcp_tool_wrapper("lateral_thinking")
async def handle_lateral_thinking(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Lateral thinking analysis method - Edward de Bono's creative problem solving
    Expected params with all required fields for lateral analysis
    """
    if not params or not isinstance(params, dict):
        raise ValueError("Lateral thinking requires params as dict with thinking data")
    
    try:
        result = await lateral_thinking_analysis(params)
        return {
            "method": "lateral_thinking",
            "input_data": params,
            "thinking_result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Lateral thinking analysis completed successfully"
        }
    except Exception as e:
        logger.error(f"Error in lateral thinking: {e}")
        raise ValueError(f"Lateral thinking analysis failed: {str(e)}")


@register_method("lateral_thinking_history")
async def handle_lateral_thinking_history(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Get history of all lateral thinking sessions
    """
    try:
        result = await get_lateral_thinking_history()
        return {
            "method": "lateral_thinking_history",
            "thinking_history": result,
            "total_sessions": len(result),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": f"Retrieved {len(result)} lateral thinking sessions from history"
        }
    except Exception as e:
        logger.error(f"Error in lateral thinking history: {e}")
        raise ValueError(f"Lateral thinking history failed: {str(e)}")


@register_method("lateral_thinking_stats")
async def handle_lateral_thinking_stats(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Get statistics about lateral thinking sessions
    """
    try:
        result = await get_lateral_thinking_stats()
        return {
            "method": "lateral_thinking_stats",
            "statistics": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Lateral thinking statistics retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error in lateral thinking stats: {e}")
        raise ValueError(f"Lateral thinking stats failed: {str(e)}")


@register_method("root_cause_analysis")
@mcp_tool_wrapper("root_cause_analysis")
async def handle_root_cause_analysis(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Perform root cause analysis using systematic RCA techniques
    """
    if not params or not isinstance(params, dict):
        raise ValueError("root_cause_analysis requires analysis parameters")
    
    try:
        result = await root_cause_analysis(params)
        return {
            "method": "root_cause_analysis",
            "input_data": params,
            "analysis_result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Root cause analysis completed successfully"
        }
    except Exception as e:
        logger.error(f"Error in root cause analysis: {e}")
        raise ValueError(f"Root cause analysis failed: {str(e)}")


@register_method("root_cause_analysis_history")
async def handle_root_cause_analysis_history(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Get history of all root cause analyses
    """
    try:
        result = await get_rca_history()
        return {
            "method": "root_cause_analysis_history",
            "analysis_history": result,
            "total_analyses": len(result),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": f"Retrieved {len(result)} root cause analyses from history"
        }
    except Exception as e:
        logger.error(f"Error in root cause analysis history: {e}")
        raise ValueError(f"Root cause analysis history failed: {str(e)}")


@register_method("root_cause_analysis_stats")
async def handle_root_cause_analysis_stats(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Get statistics about root cause analyses
    """
    try:
        result = await get_rca_stats()
        return {
            "method": "root_cause_analysis_stats",
            "statistics": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Root cause analysis statistics retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error in root cause analysis stats: {e}")
        raise ValueError(f"Root cause analysis stats failed: {str(e)}")


@register_method("systems_thinking")
@mcp_tool_wrapper("systems_thinking")
async def handle_systems_thinking(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Systems thinking analysis method - holistic analysis of complex systems
    Expected params with all required fields for systems analysis
    """
    if not params or not isinstance(params, dict):
        raise ValueError("Systems thinking requires params as dict with system data")
    
    try:
        result = await systems_thinking_analysis(params)
        return {
            "method": "systems_thinking",
            "input_data": params,
            "analysis_result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Systems thinking analysis completed successfully"
        }
    except Exception as e:
        logger.error(f"Error in systems thinking: {e}")
        raise ValueError(f"Systems thinking analysis failed: {str(e)}")


@register_method("systems_thinking_history")
async def handle_systems_thinking_history(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Get history of all systems thinking analyses
    """
    try:
        result = await get_systems_thinking_history()
        return {
            "method": "systems_thinking_history",
            "analysis_history": result,
            "total_analyses": len(result),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": f"Retrieved {len(result)} systems thinking analyses from history"
        }
    except Exception as e:
        logger.error(f"Error in systems thinking history: {e}")
        raise ValueError(f"Systems thinking history failed: {str(e)}")


@register_method("systems_thinking_stats")
async def handle_systems_thinking_stats(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Get statistics about systems thinking analyses
    """
    try:
        result = await get_systems_thinking_stats()
        return {
            "method": "systems_thinking_stats",
            "statistics": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Systems thinking statistics retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error in systems thinking stats: {e}")
        raise ValueError(f"Systems thinking stats failed: {str(e)}")


@register_method("memory_sync_to_database")
@mcp_tool_wrapper("memory_sync_to_database")
async def handle_memory_sync_to_database(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Synchronize current memory graph to database memory_structures table
    Expected params: {"problem_statement": "..."}
    """
    problem_statement = "Current e-commerce performance ecosystem analysis"
    if params and isinstance(params, dict):
        problem_statement = params.get("problem_statement", problem_statement)
    
    try:
        structure_id = await memory_sync_to_database(problem_statement)
        return {
            "method": "memory_sync_to_database",
            "structure_id": structure_id,
            "problem_statement": problem_statement,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Memory graph synchronized to database successfully"
        }
    except Exception as e:
        logger.error(f"Error in memory sync: {e}")
        raise ValueError(f"Memory sync failed: {str(e)}")


@register_method("memory_use_structures_analysis")
@mcp_tool_wrapper("memory_use_structures_analysis")
async def handle_memory_use_structures_analysis(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Use existing memory structures for comprehensive problem analysis
    Expected params: {"problem_type": "knowledge_graph"}
    """
    problem_type = "knowledge_graph"
    if params and isinstance(params, dict):
        problem_type = params.get("problem_type", problem_type)
    
    try:
        result = await use_memory_structures_for_analysis(problem_type)
        return result
    except Exception as e:
        logger.error(f"Error in memory structures analysis: {e}")
        raise ValueError(f"Memory structures analysis failed: {str(e)}")


# FastAPI route handlers for MCP JSON-RPC requests

@router.post("/")
async def handle_mcp_request(request: JsonRpcRequest) -> Union[JsonRpcResponse, JsonRpcErrorResponse]:
    """
    Handle MCP JSON-RPC requests
    """
    try:
        method = request.method
        params = request.params
        
        logger.info(f"Handling MCP request: {method}")
        
        if method not in METHOD_HANDLERS:
            return create_error_response(
                "METHOD_NOT_FOUND",
                f"Method not found: {method}",
                request.id,
                None
            )
        
        handler = METHOD_HANDLERS[method]
        result = await handler(params)
        
        return create_success_response(result, request.id)
        
    except Exception as e:
        logger.error(f"Error handling MCP request {request.method}: {e}")
        return create_error_response(
            "INTERNAL_ERROR",
            f"Internal error: {str(e)}",
            request.id,
            None
        )


@router.get("/health")
async def mcp_health_check():
    """MCP health check endpoint"""
    return {
        "status": "ok",
        "methods": len(METHOD_HANDLERS),
        "registered_methods": list(METHOD_HANDLERS.keys())
    }