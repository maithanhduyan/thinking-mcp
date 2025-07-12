# -*- coding: utf-8 -*-
# app/db.py
import sqlite3
import hashlib
import os
import json
from typing import Optional, Dict, Any, List
from app.logger import get_logger
from app.config import DB_PATH

logger = get_logger(__name__)


def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrent access
    conn.execute('PRAGMA journal_mode=WAL')
    return conn


def init_database():
    """Initialize database with users table."""
    conn = get_db_connection()
    try:
        # Create users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create default admin user if not exists
        admin_password = hash_password("admin123")
        conn.execute('''
            INSERT OR IGNORE INTO users (username, password_hash) 
            VALUES (?, ?)
        ''', ("admin", admin_password))
        
        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()


def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == password_hash


def create_user(username: str, password: str) -> bool:
    """Create new user."""
    conn = get_db_connection()
    try:
        password_hash = hash_password(password)
        conn.execute('''
            INSERT INTO users (username, password_hash) 
            VALUES (?, ?)
        ''', (username, password_hash))
        conn.commit()
        logger.info(f"User {username} created successfully")
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"User {username} already exists")
        return False
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return False
    finally:
        conn.close()


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user credentials."""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            SELECT id, username, password_hash 
            FROM users 
            WHERE username = ?
        ''', (username,))
        user = cursor.fetchone()
        
        if user and verify_password(password, user['password_hash']):
            return {
                'id': user['id'],
                'username': user['username']
            }
        return None
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        return None
    finally:
        conn.close()


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get user by username."""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            SELECT id, username, created_at
            FROM users 
            WHERE username = ?
        ''', (username,))
        user = cursor.fetchone()
        
        if user:
            return {
                'id': user['id'],
                'username': user['username'],
                'created_at': user['created_at']
            }
        return None
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return None
    finally:
        conn.close()


def get_all_users() -> list:
    """Get all users from database."""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            SELECT id, username, created_at
            FROM users 
            ORDER BY created_at DESC
        ''')
        users = cursor.fetchall()
        
        return [
            {
                'id': user['id'],
                'username': user['username'],
                'created_at': user['created_at']
            }
            for user in users
        ]
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return []
    finally:
        conn.close()

def mcp_db_init():
    """Initialize the MCP database with thinking-related tables."""
    conn = get_db_connection()
    try:
        # Create MCP queries table - lưu trữ các truy vấn MCP
        conn.execute('''
            CREATE TABLE IF NOT EXISTS mcp_queries (
                id TEXT PRIMARY KEY,
                tool_name TEXT NOT NULL,
                input_data TEXT NOT NULL,
                output_data TEXT NOT NULL,
                execution_time_ms INTEGER,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create memory structures table - lưu trữ cấu trúc memory
        conn.execute('''
            CREATE TABLE IF NOT EXISTS memory_structures (
                id TEXT PRIMARY KEY,
                problem_statement TEXT NOT NULL,
                structure_type TEXT NOT NULL,
                json_data TEXT NOT NULL,
                entities_count INTEGER DEFAULT 0,
                relations_count INTEGER DEFAULT 0,
                metadata TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_mcp_queries_tool_name 
            ON mcp_queries(tool_name)
        ''')
        
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_mcp_queries_created_date 
            ON mcp_queries(created_date)
        ''')
        
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_memory_structures_type 
            ON memory_structures(structure_type)
        ''')
        
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_memory_structures_created_date 
            ON memory_structures(created_date)
        ''')
        
        conn.commit()
        logger.info("MCP database tables initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing MCP database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

# ========================= MCP QUERIES CRUD =========================

def create_mcp_query(query_id: str, tool_name: str, input_data: dict, 
                     output_data: dict, execution_time_ms: Optional[int] = None, 
                     success: bool = True, error_message: Optional[str] = None) -> bool:
    """Create a new MCP query record."""
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO mcp_queries 
            (id, tool_name, input_data, output_data, execution_time_ms, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            query_id,
            tool_name,
            json.dumps(input_data, ensure_ascii=False),
            json.dumps(output_data, ensure_ascii=False),
            execution_time_ms,
            success,
            error_message
        ))
        conn.commit()
        logger.info(f"MCP query {query_id} created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating MCP query: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_mcp_query(query_id: str) -> Optional[Dict[str, Any]]:
    """Get MCP query by ID."""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            SELECT * FROM mcp_queries WHERE id = ?
        ''', (query_id,))
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row['id'],
                'tool_name': row['tool_name'],
                'input_data': json.loads(row['input_data']),
                'output_data': json.loads(row['output_data']),
                'execution_time_ms': row['execution_time_ms'],
                'success': bool(row['success']),
                'error_message': row['error_message'],
                'created_date': row['created_date']
            }
        return None
    except Exception as e:
        logger.error(f"Error getting MCP query: {e}")
        return None
    finally:
        conn.close()


def get_mcp_queries_by_tool(tool_name: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get MCP queries by tool name."""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            SELECT * FROM mcp_queries 
            WHERE tool_name = ? 
            ORDER BY created_date DESC 
            LIMIT ?
        ''', (tool_name, limit))
        rows = cursor.fetchall()
        
        return [
            {
                'id': row['id'],
                'tool_name': row['tool_name'],
                'input_data': json.loads(row['input_data']),
                'output_data': json.loads(row['output_data']),
                'execution_time_ms': row['execution_time_ms'],
                'success': bool(row['success']),
                'error_message': row['error_message'],
                'created_date': row['created_date']
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error getting MCP queries by tool: {e}")
        return []
    finally:
        conn.close()


def get_recent_mcp_queries(limit: int = 50) -> List[Dict[str, Any]]:
    """Get recent MCP queries."""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            SELECT * FROM mcp_queries 
            ORDER BY created_date DESC 
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        
        return [
            {
                'id': row['id'],
                'tool_name': row['tool_name'],
                'input_data': json.loads(row['input_data']),
                'output_data': json.loads(row['output_data']),
                'execution_time_ms': row['execution_time_ms'],
                'success': bool(row['success']),
                'error_message': row['error_message'],
                'created_date': row['created_date']
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error getting recent MCP queries: {e}")
        return []
    finally:
        conn.close()


def get_mcp_query_stats() -> Dict[str, Any]:
    """Get MCP query statistics."""
    conn = get_db_connection()
    try:
        # Total queries
        cursor = conn.execute('SELECT COUNT(*) as total FROM mcp_queries')
        total = cursor.fetchone()['total']
        
        # Success rate
        cursor = conn.execute('SELECT COUNT(*) as success FROM mcp_queries WHERE success = 1')
        success = cursor.fetchone()['success']
        
        # Tool usage
        cursor = conn.execute('''
            SELECT tool_name, COUNT(*) as count 
            FROM mcp_queries 
            GROUP BY tool_name 
            ORDER BY count DESC
        ''')
        tool_usage = {row['tool_name']: row['count'] for row in cursor.fetchall()}
        
        # Average execution time
        cursor = conn.execute('''
            SELECT AVG(execution_time_ms) as avg_time 
            FROM mcp_queries 
            WHERE execution_time_ms IS NOT NULL
        ''')
        avg_time = cursor.fetchone()['avg_time'] or 0
        
        return {
            'total_queries': total,
            'successful_queries': success,
            'success_rate': (success / total * 100) if total > 0 else 0,
            'tool_usage': tool_usage,
            'average_execution_time_ms': round(avg_time, 2)
        }
    except Exception as e:
        logger.error(f"Error getting MCP query stats: {e}")
        return {}
    finally:
        conn.close()


def delete_old_mcp_queries(days: int = 30) -> int:
    """Delete MCP queries older than specified days."""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            DELETE FROM mcp_queries 
            WHERE created_date < datetime('now', '-' || ? || ' days')
        ''', (days,))
        deleted_count = cursor.rowcount
        conn.commit()
        logger.info(f"Deleted {deleted_count} old MCP queries")
        return deleted_count
    except Exception as e:
        logger.error(f"Error deleting old MCP queries: {e}")
        conn.rollback()
        return 0
    finally:
        conn.close()

# ========================= MEMORY STRUCTURES CRUD =========================

def create_memory_structure(structure_id: str, problem_statement: str, 
                           structure_type: str, json_data: dict, 
                           entities_count: int = 0, relations_count: int = 0,
                           metadata: Optional[dict] = None) -> bool:
    """Create a new memory structure record."""
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO memory_structures 
            (id, problem_statement, structure_type, json_data, entities_count, relations_count, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            structure_id,
            problem_statement,
            structure_type,
            json.dumps(json_data, ensure_ascii=False),
            entities_count,
            relations_count,
            json.dumps(metadata, ensure_ascii=False) if metadata else None
        ))
        conn.commit()
        logger.info(f"Memory structure {structure_id} created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating memory structure: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_memory_structure(structure_id: str) -> Optional[Dict[str, Any]]:
    """Get memory structure by ID."""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            SELECT * FROM memory_structures WHERE id = ?
        ''', (structure_id,))
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row['id'],
                'problem_statement': row['problem_statement'],
                'structure_type': row['structure_type'],
                'json_data': json.loads(row['json_data']),
                'entities_count': row['entities_count'],
                'relations_count': row['relations_count'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else None,
                'created_date': row['created_date'],
                'updated_date': row['updated_date']
            }
        return None
    except Exception as e:
        logger.error(f"Error getting memory structure: {e}")
        return None
    finally:
        conn.close()


def get_memory_structures_by_type(structure_type: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get memory structures by type."""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            SELECT * FROM memory_structures 
            WHERE structure_type = ? 
            ORDER BY updated_date DESC 
            LIMIT ?
        ''', (structure_type, limit))
        rows = cursor.fetchall()
        
        return [
            {
                'id': row['id'],
                'problem_statement': row['problem_statement'],
                'structure_type': row['structure_type'],
                'json_data': json.loads(row['json_data']),
                'entities_count': row['entities_count'],
                'relations_count': row['relations_count'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else None,
                'created_date': row['created_date'],
                'updated_date': row['updated_date']
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error getting memory structures by type: {e}")
        return []
    finally:
        conn.close()


def update_memory_structure(structure_id: str, json_data: dict, 
                           entities_count: Optional[int] = None, 
                           relations_count: Optional[int] = None,
                           metadata: Optional[dict] = None) -> bool:
    """Update memory structure."""
    conn = get_db_connection()
    try:
        # Build dynamic update query
        update_fields = ['json_data = ?', 'updated_date = CURRENT_TIMESTAMP']
        params: List[Any] = [json.dumps(json_data, ensure_ascii=False)]
        
        if entities_count is not None:
            update_fields.append('entities_count = ?')
            params.append(entities_count)
            
        if relations_count is not None:
            update_fields.append('relations_count = ?')
            params.append(relations_count)
            
        if metadata is not None:
            update_fields.append('metadata = ?')
            params.append(json.dumps(metadata, ensure_ascii=False))
        
        params.append(structure_id)
        
        query = f'''
            UPDATE memory_structures 
            SET {', '.join(update_fields)}
            WHERE id = ?
        '''
        
        cursor = conn.execute(query, params)
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Memory structure {structure_id} updated successfully")
            return True
        else:
            logger.warning(f"Memory structure {structure_id} not found for update")
            return False
            
    except Exception as e:
        logger.error(f"Error updating memory structure: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def search_memory_structures(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Search memory structures by problem statement or metadata."""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            SELECT * FROM memory_structures 
            WHERE problem_statement LIKE ? OR json_data LIKE ? OR metadata LIKE ?
            ORDER BY updated_date DESC 
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))
        rows = cursor.fetchall()
        
        return [
            {
                'id': row['id'],
                'problem_statement': row['problem_statement'],
                'structure_type': row['structure_type'],
                'json_data': json.loads(row['json_data']),
                'entities_count': row['entities_count'],
                'relations_count': row['relations_count'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else None,
                'created_date': row['created_date'],
                'updated_date': row['updated_date']
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error searching memory structures: {e}")
        return []
    finally:
        conn.close()


def get_memory_structure_stats() -> Dict[str, Any]:
    """Get memory structure statistics."""
    conn = get_db_connection()
    try:
        # Total structures
        cursor = conn.execute('SELECT COUNT(*) as total FROM memory_structures')
        total = cursor.fetchone()['total']
        
        # Structure types
        cursor = conn.execute('''
            SELECT structure_type, COUNT(*) as count 
            FROM memory_structures 
            GROUP BY structure_type 
            ORDER BY count DESC
        ''')
        type_distribution = {row['structure_type']: row['count'] for row in cursor.fetchall()}
        
        # Total entities and relations
        cursor = conn.execute('''
            SELECT 
                SUM(entities_count) as total_entities,
                SUM(relations_count) as total_relations,
                AVG(entities_count) as avg_entities,
                AVG(relations_count) as avg_relations
            FROM memory_structures
        ''')
        counts = cursor.fetchone()
        
        return {
            'total_structures': total,
            'type_distribution': type_distribution,
            'total_entities': counts['total_entities'] or 0,
            'total_relations': counts['total_relations'] or 0,
            'average_entities_per_structure': round(counts['avg_entities'] or 0, 2),
            'average_relations_per_structure': round(counts['avg_relations'] or 0, 2)
        }
    except Exception as e:
        logger.error(f"Error getting memory structure stats: {e}")
        return {}
    finally:
        conn.close()


def delete_memory_structure(structure_id: str) -> bool:
    """Delete memory structure by ID."""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            DELETE FROM memory_structures WHERE id = ?
        ''', (structure_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Memory structure {structure_id} deleted successfully")
            return True
        else:
            logger.warning(f"Memory structure {structure_id} not found for deletion")
            return False
            
    except Exception as e:
        logger.error(f"Error deleting memory structure: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_recent_memory_structures(limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent memory structures."""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            SELECT * FROM memory_structures 
            ORDER BY updated_date DESC 
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        
        return [
            {
                'id': row['id'],
                'problem_statement': row['problem_statement'],
                'structure_type': row['structure_type'],
                'json_data': json.loads(row['json_data']),
                'entities_count': row['entities_count'],
                'relations_count': row['relations_count'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else None,
                'created_date': row['created_date'],
                'updated_date': row['updated_date']
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error getting recent memory structures: {e}")
        return []
    finally:
        conn.close()
