# -*- coding: utf-8 -*-
# File: app/migrate_to_sqlalchemy.py

"""
Migration script from old SQLite schema to SQLAlchemy schema
"""

import sqlite3
import os
from datetime import datetime

from app.config import DB_PATH
from app.logger import get_logger

logger = get_logger(__name__)


def backup_database():
    """Create backup of existing database"""
    if not os.path.exists(DB_PATH):
        logger.info("No existing database to backup")
        return
    
    backup_path = f"{DB_PATH}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Copy database file
    import shutil
    shutil.copy2(DB_PATH, backup_path)
    logger.info(f"Database backed up to: {backup_path}")
    return backup_path


def migrate_database_schema():
    """Migrate existing database schema to SQLAlchemy format"""
    if not os.path.exists(DB_PATH):
        logger.info("No existing database to migrate")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if updated_at column exists in users table
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'updated_at' not in columns:
            logger.info("Adding updated_at column to users table")
            # SQLite doesn't allow adding columns with non-constant defaults
            # Add column with NULL default, then update
            cursor.execute("ALTER TABLE users ADD COLUMN updated_at DATETIME")
            
            # Update existing records
            cursor.execute("""
                UPDATE users 
                SET updated_at = created_at 
                WHERE updated_at IS NULL
            """)
        
        # Check thinking_sessions table structure
        cursor.execute("PRAGMA table_info(thinking_sessions)")
        ts_columns = [col[1] for col in cursor.fetchall()]
        
        required_ts_columns = [
            'user_id', 'session_id', 'tool_name', 'method_name', 
            'parameters', 'result', 'execution_time', 'success', 
            'error_message', 'created_at'
        ]
        
        missing_columns = [col for col in required_ts_columns if col not in ts_columns]
        
        for col in missing_columns:
            if col == 'user_id':
                cursor.execute("ALTER TABLE thinking_sessions ADD COLUMN user_id INTEGER")
            elif col == 'session_id':
                cursor.execute("ALTER TABLE thinking_sessions ADD COLUMN session_id TEXT")
            elif col == 'tool_name':
                cursor.execute("ALTER TABLE thinking_sessions ADD COLUMN tool_name TEXT")
            elif col == 'method_name':
                cursor.execute("ALTER TABLE thinking_sessions ADD COLUMN method_name TEXT")
            elif col == 'parameters':
                cursor.execute("ALTER TABLE thinking_sessions ADD COLUMN parameters TEXT")
            elif col == 'result':
                cursor.execute("ALTER TABLE thinking_sessions ADD COLUMN result TEXT")
            elif col == 'execution_time':
                cursor.execute("ALTER TABLE thinking_sessions ADD COLUMN execution_time INTEGER")
            elif col == 'success':
                cursor.execute("ALTER TABLE thinking_sessions ADD COLUMN success BOOLEAN DEFAULT 1")
            elif col == 'error_message':
                cursor.execute("ALTER TABLE thinking_sessions ADD COLUMN error_message TEXT")
            elif col == 'created_at':
                cursor.execute("ALTER TABLE thinking_sessions ADD COLUMN created_at DATETIME")
            
            logger.info(f"Added column {col} to thinking_sessions table")
        
        conn.commit()
        logger.info("Database schema migration completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def create_indexes():
    """Create indexes for better performance"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create indexes that don't exist
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_thinking_sessions_session_tool ON thinking_sessions(session_id, tool_name)",
            "CREATE INDEX IF NOT EXISTS idx_thinking_sessions_user_tool ON thinking_sessions(user_id, tool_name)",
            "CREATE INDEX IF NOT EXISTS idx_thinking_sessions_created_at ON thinking_sessions(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_memory_entities_name ON memory_entities(name)",
            "CREATE INDEX IF NOT EXISTS idx_memory_entities_type ON memory_entities(entity_type)",
            "CREATE INDEX IF NOT EXISTS idx_memory_observations_entity_created ON memory_observations(entity_id, created_at)",
            "CREATE INDEX IF NOT EXISTS idx_memory_relations_from_to ON memory_relations(from_entity_id, to_entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_memory_relations_type ON memory_relations(relation_type)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
            
        conn.commit()
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Index creation failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def verify_migration():
    """Verify migration was successful"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check users table
        cursor.execute("PRAGMA table_info(users)")
        users_columns = [col[1] for col in cursor.fetchall()]
        expected_users_columns = ['id', 'username', 'password_hash', 'created_at', 'updated_at']
        
        for col in expected_users_columns:
            if col not in users_columns:
                logger.error(f"Missing column {col} in users table")
                return False
        
        # Check data integrity
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        logger.info(f"Users table has {user_count} records")
        
        cursor.execute("SELECT COUNT(*) FROM thinking_sessions")
        session_count = cursor.fetchone()[0]
        logger.info(f"Thinking sessions table has {session_count} records")
        
        cursor.execute("SELECT COUNT(*) FROM memory_entities")
        entity_count = cursor.fetchone()[0]
        logger.info(f"Memory entities table has {entity_count} records")
        
        logger.info("Migration verification completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Migration verification failed: {e}")
        return False
    finally:
        conn.close()


def main():
    """Run full migration process"""
    logger.info("Starting database migration to SQLAlchemy")
    
    # Backup existing database
    backup_path = backup_database()
    
    try:
        # Migrate schema
        migrate_database_schema()
        
        # Create indexes
        create_indexes()
        
        # Verify migration
        if verify_migration():
            logger.info("✅ Database migration completed successfully")
            print("✅ Database migration completed successfully")
            if backup_path:
                print(f"📁 Backup created at: {backup_path}")
        else:
            logger.error("❌ Migration verification failed")
            print("❌ Migration verification failed")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        print(f"❌ Migration failed: {e}")
        if backup_path:
            print(f"📁 Restore from backup: {backup_path}")


if __name__ == "__main__":
    main()
