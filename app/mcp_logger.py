# -*- coding: utf-8 -*-
# File: app/mcp_logger.py
"""
MCP Query Logger - Auto log MCP tool calls to database
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from app.db import create_mcp_query
from app.logger import get_logger

logger = get_logger(__name__)


class MCPQueryLogger:
    """Logger for MCP tool queries and responses"""
    
    @staticmethod
    def log_query(tool_name: str, input_data: dict, output_data: dict, 
                  execution_time_ms: Optional[int] = None, 
                  success: bool = True, error_message: Optional[str] = None) -> str:
        """
        Log an MCP query to database
        Returns the query ID
        """
        try:
            query_id = str(uuid.uuid4())
            
            # Clean sensitive data if needed
            cleaned_input = MCPQueryLogger._clean_sensitive_data(input_data)
            cleaned_output = MCPQueryLogger._clean_sensitive_data(output_data)
            
            success = create_mcp_query(
                query_id=query_id,
                tool_name=tool_name,
                input_data=cleaned_input,
                output_data=cleaned_output,
                execution_time_ms=execution_time_ms,
                success=success,
                error_message=error_message
            )
            
            if success:
                logger.debug(f"MCP query {query_id} logged successfully")
            else:
                logger.warning(f"Failed to log MCP query {query_id}")
                
            return query_id
            
        except Exception as e:
            logger.error(f"Error logging MCP query: {e}")
            return ""
    
    @staticmethod
    def _clean_sensitive_data(data: dict) -> dict:
        """Remove sensitive information from data before logging"""
        if not isinstance(data, dict):
            return data
            
        cleaned = data.copy()
        sensitive_keys = ['password', 'token', 'secret', 'key', 'auth']
        
        for key in list(cleaned.keys()):
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                cleaned[key] = "[REDACTED]"
            elif isinstance(cleaned[key], dict):
                cleaned[key] = MCPQueryLogger._clean_sensitive_data(cleaned[key])
                
        return cleaned


def mcp_tool_wrapper(tool_name: str):
    """
    Decorator to automatically log MCP tool calls
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            query_id = None
            input_data = {}
            
            try:
                # Extract input data
                if args:
                    input_data['args'] = args
                if kwargs:
                    input_data['kwargs'] = kwargs
                
                # Execute the tool
                result = await func(*args, **kwargs)
                
                # Calculate execution time
                execution_time_ms = int((time.time() - start_time) * 1000)
                
                # Log successful query
                query_id = MCPQueryLogger.log_query(
                    tool_name=tool_name,
                    input_data=input_data,
                    output_data=result if isinstance(result, dict) else {"result": str(result)},
                    execution_time_ms=execution_time_ms,
                    success=True
                )
                
                return result
                
            except Exception as e:
                # Calculate execution time
                execution_time_ms = int((time.time() - start_time) * 1000)
                
                # Log failed query
                query_id = MCPQueryLogger.log_query(
                    tool_name=tool_name,
                    input_data=input_data,
                    output_data={"error": str(e)},
                    execution_time_ms=execution_time_ms,
                    success=False,
                    error_message=str(e)
                )
                
                # Re-raise the exception
                raise
                
        return wrapper
    return decorator


# Convenience function for manual logging
def log_mcp_call(tool_name: str, input_data: dict, output_data: dict, 
                 success: bool = True, error_message: Optional[str] = None) -> str:
    """Convenience function to manually log MCP calls"""
    return MCPQueryLogger.log_query(
        tool_name=tool_name,
        input_data=input_data,
        output_data=output_data,
        success=success,
        error_message=error_message
    )
