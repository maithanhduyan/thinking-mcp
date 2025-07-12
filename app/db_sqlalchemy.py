# -*- coding: utf-8 -*-
# File: app/db_sqlalchemy.py

"""
SQLAlchemy Database Layer with Multi-Database Support
Provides connection pooling and easy database switching
"""

import os
import json
from typing import Dict, Any, Optional, List, Type, Union
from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import (
    create_engine, 
    MetaData, 
    Table, 
    Column, 
    Integer, 
    String, 
    Text, 
    DateTime, 
    Boolean,
    ForeignKey,
    Index,
    event
)
from sqlalchemy.orm import (
    declarative_base, 
    sessionmaker, 
    Session,
    relationship
)
from sqlalchemy.pool import StaticPool, QueuePool
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.logger import get_logger
from app.config import DB_PATH

logger = get_logger(__name__)

# Base class for all models
Base = declarative_base()

# Database configurations
DATABASE_CONFIGS = {
    'sqlite': {
        'url': f'sqlite:///{DB_PATH}',
        'pool_class': StaticPool,
        'pool_size': 1,
        'max_overflow': 0,
        'pool_timeout': 30,
        'pool_recycle': -1,
        'echo': False
    },
    'postgresql': {
        'url': 'postgresql+psycopg2://user:password@localhost:5432/thinking_mcp',
        'pool_class': QueuePool,
        'pool_size': 5,
        'max_overflow': 10,
        'pool_timeout': 30,
        'pool_recycle': 3600,
        'echo': False
    },
    'mysql': {
        'url': 'mysql+pymysql://user:password@localhost:3306/thinking_mcp',
        'pool_class': QueuePool,
        'pool_size': 5,
        'max_overflow': 10,
        'pool_timeout': 30,
        'pool_recycle': 3600,
        'echo': False
    }
}


class DatabaseManager:
    """Multi-database manager with connection pooling"""
    
    def __init__(self):
        self.engines: Dict[str, Engine] = {}
        self.session_factories: Dict[str, sessionmaker] = {}
        self.current_db = 'sqlite'  # Default database
        
    def register_database(self, name: str, config: Dict[str, Any]):
        """Register a new database configuration"""
        try:
            # Prepare engine arguments
            engine_args = {
                'echo': config.get('echo', False)
            }
            
            # Add pool configuration based on database type
            # Check if URL contains sqlite
            is_sqlite = 'sqlite' in config['url'].lower()
            
            if is_sqlite:
                engine_args.update({
                    'poolclass': config.get('pool_class', StaticPool),
                    'connect_args': {'check_same_thread': False}
                })
            else:
                engine_args.update({
                    'poolclass': config.get('pool_class', QueuePool),
                    'pool_size': config.get('pool_size', 5),
                    'max_overflow': config.get('max_overflow', 10),
                    'pool_timeout': config.get('pool_timeout', 30),
                    'pool_recycle': config.get('pool_recycle', 3600)
                })
            
            engine = create_engine(config['url'], **engine_args)
            
            # Enable WAL mode for SQLite
            if is_sqlite:
                @event.listens_for(engine, "connect")
                def set_sqlite_pragma(dbapi_connection, connection_record):
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA journal_mode=WAL")
                    cursor.execute("PRAGMA synchronous=NORMAL")
                    cursor.execute("PRAGMA temp_store=MEMORY")
                    cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
                    cursor.close()
            
            self.engines[name] = engine
            self.session_factories[name] = sessionmaker(bind=engine)
            
            logger.info(f"Database '{name}' registered successfully")
            
        except Exception as e:
            logger.error(f"Failed to register database '{name}': {e}")
            raise
    
    def switch_database(self, name: str):
        """Switch to a different database"""
        if name not in self.engines:
            raise ValueError(f"Database '{name}' not registered")
        
        old_db = self.current_db
        self.current_db = name
        logger.info(f"Switched database from '{old_db}' to '{name}'")
    
    def get_engine(self, db_name: Optional[str] = None) -> Engine:
        """Get engine for specified database or current database"""
        db_name = db_name or self.current_db
        if db_name not in self.engines:
            raise ValueError(f"Database '{db_name}' not registered")
        return self.engines[db_name]
    
    def get_session(self, db_name: Optional[str] = None) -> Session:
        """Get session for specified database or current database"""
        db_name = db_name or self.current_db
        if db_name not in self.session_factories:
            raise ValueError(f"Database '{db_name}' not registered")
        return self.session_factories[db_name]()
    
    @contextmanager
    def session_scope(self, db_name: Optional[str] = None):
        """Session context manager with automatic rollback on error"""
        session = self.get_session(db_name)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_all_tables(self, db_name: Optional[str] = None):
        """Create all tables in specified database"""
        engine = self.get_engine(db_name)
        Base.metadata.create_all(engine)
        logger.info(f"Created all tables in database '{db_name or self.current_db}'")
    
    def drop_all_tables(self, db_name: Optional[str] = None):
        """Drop all tables in specified database"""
        engine = self.get_engine(db_name)
        Base.metadata.drop_all(engine)
        logger.info(f"Dropped all tables in database '{db_name or self.current_db}'")
    
    def get_pool_status(self, db_name: Optional[str] = None) -> Dict[str, Any]:
        """Get connection pool status"""
        engine = self.get_engine(db_name)
        pool = engine.pool
        
        # Simple pool status for all pool types
        status = {
            'database': db_name or self.current_db,
            'pool_class': pool.__class__.__name__,
            'engine_url': str(engine.url)
        }
        
        return status


# Models
class User(Base):
    """User model"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    thinking_sessions = relationship("ThinkingSession", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class ThinkingSession(Base):
    """Thinking session model for tracking tool usage"""
    __tablename__ = 'thinking_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    session_id = Column(String(50), nullable=False, index=True)
    tool_name = Column(String(50), nullable=False, index=True)
    method_name = Column(String(50), nullable=False)
    parameters = Column(Text, nullable=True)  # JSON as text
    result = Column(Text, nullable=True)      # JSON as text
    execution_time = Column(Integer, nullable=True)  # milliseconds
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="thinking_sessions")
    
    # Indexes
    __table_args__ = (
        Index('idx_session_tool', 'session_id', 'tool_name'),
        Index('idx_user_tool', 'user_id', 'tool_name'),
        Index('idx_created_at', 'created_at'),
    )
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get parameters as dict"""
        params_val = getattr(self, 'parameters', None)
        if params_val is not None:
            try:
                return json.loads(params_val)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def set_parameters(self, params: Dict[str, Any]):
        """Set parameters from dict"""
        setattr(self, 'parameters', json.dumps(params) if params else None)
    
    def get_result(self) -> Dict[str, Any]:
        """Get result as dict"""
        result_val = getattr(self, 'result', None)
        if result_val is not None:
            try:
                return json.loads(result_val)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def set_result(self, result: Dict[str, Any]):
        """Set result from dict"""
        setattr(self, 'result', json.dumps(result) if result else None)
    
    def __repr__(self):
        return f"<ThinkingSession(id={self.id}, tool='{self.tool_name}', session='{self.session_id}')>"


class MemoryEntity(Base):
    """Memory entities for knowledge graph"""
    __tablename__ = 'memory_entities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    observations = relationship("MemoryObservation", back_populates="entity", cascade="all, delete-orphan")
    relations_from = relationship("MemoryRelation", foreign_keys="MemoryRelation.from_entity_id", back_populates="from_entity")
    relations_to = relationship("MemoryRelation", foreign_keys="MemoryRelation.to_entity_id", back_populates="to_entity")
    
    def __repr__(self):
        return f"<MemoryEntity(id={self.id}, name='{self.name}', type='{self.entity_type}')>"


class MemoryObservation(Base):
    """Observations for memory entities"""
    __tablename__ = 'memory_observations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_id = Column(Integer, ForeignKey('memory_entities.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    entity = relationship("MemoryEntity", back_populates="observations")
    
    # Indexes
    __table_args__ = (
        Index('idx_entity_created', 'entity_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<MemoryObservation(id={self.id}, entity_id={self.entity_id})>"


class MemoryRelation(Base):
    """Relations between memory entities"""
    __tablename__ = 'memory_relations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    from_entity_id = Column(Integer, ForeignKey('memory_entities.id'), nullable=False)
    to_entity_id = Column(Integer, ForeignKey('memory_entities.id'), nullable=False)
    relation_type = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    from_entity = relationship("MemoryEntity", foreign_keys=[from_entity_id], back_populates="relations_from")
    to_entity = relationship("MemoryEntity", foreign_keys=[to_entity_id], back_populates="relations_to")
    
    # Indexes
    __table_args__ = (
        Index('idx_from_to', 'from_entity_id', 'to_entity_id'),
        Index('idx_relation_type', 'relation_type'),
    )
    
    def __repr__(self):
        return f"<MemoryRelation(from={self.from_entity_id}, to={self.to_entity_id}, type='{self.relation_type}')>"


# Global database manager instance
db_manager = DatabaseManager()


def init_sqlalchemy_databases():
    """Initialize all configured databases"""
    try:
        # Register databases from config
        for name, config in DATABASE_CONFIGS.items():
            # Skip if database URL is not properly configured
            if name == 'postgresql' and 'user:password@localhost' in config['url']:
                logger.info(f"Skipping PostgreSQL - not configured")
                continue
            if name == 'mysql' and 'user:password@localhost' in config['url']:
                logger.info(f"Skipping MySQL - not configured")
                continue
                
            db_manager.register_database(name, config)
        
        # Create tables in default database (SQLite)
        db_manager.create_all_tables('sqlite')
        
        logger.info("SQLAlchemy databases initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize SQLAlchemy databases: {e}")
        raise


def get_db_session(db_name: Optional[str] = None) -> Session:
    """Get database session (convenience function)"""
    return db_manager.get_session(db_name)


def session_scope(db_name: Optional[str] = None):
    """Session context manager (convenience function)"""
    return db_manager.session_scope(db_name)


def switch_database(db_name: str):
    """Switch to different database (convenience function)"""
    db_manager.switch_database(db_name)


def get_pool_status(db_name: Optional[str] = None) -> Dict[str, Any]:
    """Get connection pool status (convenience function)"""
    return db_manager.get_pool_status(db_name)


# Migration utilities
def migrate_from_sqlite():
    """Migrate data from existing SQLite db.py to SQLAlchemy"""
    try:
        import sqlite3
        from app.db import get_db_connection
        
        # Get old data
        old_conn = get_db_connection()
        
        # Migrate users
        cursor = old_conn.execute("SELECT username, password_hash, created_at FROM users")
        users_data = cursor.fetchall()
        
        with session_scope() as session:
            for row in users_data:
                user = User(
                    username=row[0],
                    password_hash=row[1],
                    created_at=datetime.fromisoformat(row[2]) if row[2] else datetime.utcnow()
                )
                session.merge(user)  # Use merge to handle duplicates
        
        old_conn.close()
        logger.info(f"Migrated {len(users_data)} users from old SQLite database")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


if __name__ == "__main__":
    # Test the database setup
    init_sqlalchemy_databases()
    
    # Test database operations
    with session_scope() as session:
        # Create test user
        user = User(username="test_user", password_hash="test_hash")
        session.add(user)
        session.flush()  # Get the ID
        
        # Create test session
        thinking_session = ThinkingSession(
            user_id=user.id,
            session_id="test_session_001",
            tool_name="six_thinking_hats",
            method_name="six_thinking_hats"
        )
        thinking_session.set_parameters({"hat_color": "blue", "perspective": "test"})
        thinking_session.set_result({"success": True})
        setattr(thinking_session, 'execution_time', 150)
        session.add(thinking_session)
    
    # Check pool status
    pool_status = get_pool_status()
    print(f"Pool status: {pool_status}")
    
    print("✅ SQLAlchemy database test completed successfully")
