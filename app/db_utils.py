# -*- coding: utf-8 -*-
# app/db_utils.py
"""
Database utilities and helpers for MCP project
"""

from typing import Dict, Any, List
from app.db import (
    mcp_db_init, 
    get_mcp_query_stats, 
    get_memory_structure_stats,
    get_recent_mcp_queries,
    get_recent_memory_structures,
    delete_old_mcp_queries
)
from app.logger import get_logger

logger = get_logger(__name__)


def initialize_all_databases():
    """Initialize all databases including MCP tables"""
    try:
        from app.db import init_database
        # Initialize user database
        init_database()
        # Initialize MCP specific tables
        mcp_db_init()
        logger.info("All databases initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing databases: {e}")
        return False


def get_dashboard_stats() -> Dict[str, Any]:
    """Get comprehensive dashboard statistics"""
    try:
        mcp_stats = get_mcp_query_stats()
        memory_stats = get_memory_structure_stats()
        
        return {
            "mcp_queries": mcp_stats,
            "memory_structures": memory_stats,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return {"status": "error", "message": str(e)}


def get_recent_activity(limit: int = 10) -> Dict[str, Any]:
    """Get recent activity from both MCP queries and memory structures"""
    try:
        recent_queries = get_recent_mcp_queries(limit)
        recent_structures = get_recent_memory_structures(limit)
        
        return {
            "recent_queries": recent_queries,
            "recent_structures": recent_structures,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        return {"status": "error", "message": str(e)}


def cleanup_old_data(days: int = 30) -> Dict[str, Any]:
    """Cleanup old data from database"""
    try:
        deleted_queries = delete_old_mcp_queries(days)
        
        return {
            "deleted_queries": deleted_queries,
            "cleanup_days": days,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return {"status": "error", "message": str(e)}


def health_check() -> Dict[str, Any]:
    """Perform database health check"""
    try:
        # Try to get stats to test database connectivity
        mcp_stats = get_mcp_query_stats()
        memory_stats = get_memory_structure_stats()
        
        return {
            "database_status": "healthy",
            "mcp_tables": "accessible",
            "memory_tables": "accessible",
            "total_queries": mcp_stats.get("total_queries", 0),
            "total_structures": memory_stats.get("total_structures", 0),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "database_status": "error",
            "error_message": str(e),
            "status": "error"
        }
