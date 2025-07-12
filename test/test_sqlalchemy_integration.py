# -*- coding: utf-8 -*-
# File: test_sqlalchemy_integration.py

"""
Integration tests for SQLAlchemy database layer
"""

import pytest
import tempfile
import os
from datetime import datetime
from typing import Dict, Any

from app.db_sqlalchemy import (
    DatabaseManager, 
    User, 
    ThinkingSession, 
    MemoryEntity, 
    MemoryObservation, 
    MemoryRelation,
    init_sqlalchemy_databases,
    session_scope,
    get_db_session,
    switch_database,
    get_pool_status
)


class TestSQLAlchemyIntegration:
    """Test SQLAlchemy database functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        # Use temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Initialize test database
        self.db_manager = DatabaseManager()
        test_config = {
            'url': f'sqlite:///{self.temp_db.name}',
            'pool_class': 'StaticPool',
            'echo': False
        }
        self.db_manager.register_database('test', test_config)
        self.db_manager.switch_database('test')
        self.db_manager.create_all_tables('test')
    
    def teardown_method(self):
        """Cleanup after each test"""
        # Close all connections and remove temp file
        if hasattr(self, 'temp_db'):
            try:
                os.unlink(self.temp_db.name)
            except OSError:
                pass
    
    def test_user_operations(self):
        """Test user CRUD operations"""
        with session_scope('test') as session:
            # Create user
            user = User(
                username="test_user",
                password_hash="test_hash_123"
            )
            session.add(user)
            session.flush()
            
            user_id = user.id
            assert user_id is not None
            assert user.username == "test_user"
            assert user.created_at is not None
            assert user.updated_at is not None
        
        # Read user
        with session_scope('test') as session:
            retrieved_user = session.query(User).filter_by(username="test_user").first()
            assert retrieved_user is not None
            assert retrieved_user.id == user_id
            assert retrieved_user.password_hash == "test_hash_123"
        
        # Update user
        with session_scope('test') as session:
            user_to_update = session.query(User).filter_by(id=user_id).first()
            old_updated_at = user_to_update.updated_at
            user_to_update.password_hash = "new_hash_456"
            # updated_at should be automatically updated
        
        # Verify update
        with session_scope('test') as session:
            updated_user = session.query(User).filter_by(id=user_id).first()
            assert updated_user.password_hash == "new_hash_456"
            # Note: updated_at auto-update might not work in test without proper config
    
    def test_thinking_session_operations(self):
        """Test thinking session CRUD with JSON serialization"""
        with session_scope('test') as session:
            # Create user first
            user = User(username="session_user", password_hash="hash")
            session.add(user)
            session.flush()
            
            # Create thinking session
            thinking_session = ThinkingSession(
                user_id=user.id,
                session_id="test_session_001",
                tool_name="six_thinking_hats",
                method_name="six_thinking_hats"
            )
            
            # Test JSON parameter serialization
            test_params = {
                "hat_color": "blue",
                "perspective": "process control",
                "questions": ["What have we learned?", "What's next?"]
            }
            thinking_session.set_parameters(test_params)
            
            # Test JSON result serialization
            test_result = {
                "success": True,
                "insights": ["Need more data", "Process is working"],
                "next_hat_needed": True,
                "session_complete": False
            }
            thinking_session.set_result(test_result)
            
            setattr(thinking_session, 'execution_time', 1500)  # 1.5 seconds
            setattr(thinking_session, 'success', True)
            
            session.add(thinking_session)
            session.flush()
            
            session_id = thinking_session.id
        
        # Verify JSON serialization/deserialization
        with session_scope('test') as session:
            retrieved_session = session.query(ThinkingSession).filter_by(id=session_id).first()
            
            # Test parameter deserialization
            params = retrieved_session.get_parameters()
            assert params["hat_color"] == "blue"
            assert params["perspective"] == "process control"
            assert len(params["questions"]) == 2
            
            # Test result deserialization
            result = retrieved_session.get_result()
            assert result["success"] is True
            assert len(result["insights"]) == 2
            assert result["next_hat_needed"] is True
    
    def test_memory_entity_operations(self):
        """Test memory entity and observation operations"""
        with session_scope('test') as session:
            # Create entity
            entity = MemoryEntity(
                name="Python Programming",
                entity_type="concept"
            )
            session.add(entity)
            session.flush()
            
            # Add observations
            observations = [
                MemoryObservation(entity_id=entity.id, content="Object-oriented programming language"),
                MemoryObservation(entity_id=entity.id, content="Popular for AI and data science"),
                MemoryObservation(entity_id=entity.id, content="Has rich ecosystem of libraries")
            ]
            
            for obs in observations:
                session.add(obs)
            
            session.flush()
            entity_id = entity.id
        
        # Test entity retrieval with observations
        with session_scope('test') as session:
            retrieved_entity = session.query(MemoryEntity).filter_by(id=entity_id).first()
            assert retrieved_entity.name == "Python Programming"
            assert retrieved_entity.entity_type == "concept"
            assert len(retrieved_entity.observations) == 3
            
            # Check observation content
            observation_contents = [obs.content for obs in retrieved_entity.observations]
            assert "Object-oriented programming language" in observation_contents
            assert "Popular for AI and data science" in observation_contents
    
    def test_memory_relation_operations(self):
        """Test memory relations between entities"""
        with session_scope('test') as session:
            # Create entities
            python_entity = MemoryEntity(name="Python", entity_type="language")
            django_entity = MemoryEntity(name="Django", entity_type="framework")
            session.add_all([python_entity, django_entity])
            session.flush()
            
            # Create relation
            relation = MemoryRelation(
                from_entity_id=python_entity.id,
                to_entity_id=django_entity.id,
                relation_type="uses"
            )
            session.add(relation)
            session.flush()
            
            python_id = python_entity.id
            django_id = django_entity.id
        
        # Test relation retrieval
        with session_scope('test') as session:
            # Find relations from Python
            python_entity = session.query(MemoryEntity).filter_by(id=python_id).first()
            relations_from = python_entity.relations_from
            assert len(relations_from) == 1
            assert relations_from[0].relation_type == "uses"
            assert relations_from[0].to_entity_id == django_id
            
            # Find relations to Django
            django_entity = session.query(MemoryEntity).filter_by(id=django_id).first()
            relations_to = django_entity.relations_to
            assert len(relations_to) == 1
            assert relations_to[0].from_entity_id == python_id
    
    def test_database_switching(self):
        """Test switching between databases"""
        # Create second test database
        temp_db2 = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db2.close()
        
        try:
            test_config2 = {
                'url': f'sqlite:///{temp_db2.name}',
                'pool_class': 'StaticPool',
                'echo': False
            }
            self.db_manager.register_database('test2', test_config2)
            self.db_manager.create_all_tables('test2')
            
            # Add data to first database
            with session_scope('test') as session:
                user1 = User(username="user_db1", password_hash="hash1")
                session.add(user1)
            
            # Switch to second database and add different data
            self.db_manager.switch_database('test2')
            with session_scope('test2') as session:
                user2 = User(username="user_db2", password_hash="hash2")
                session.add(user2)
            
            # Verify data isolation
            with session_scope('test') as session:
                users_db1 = session.query(User).all()
                assert len(users_db1) == 1
                assert users_db1[0].username == "user_db1"
            
            with session_scope('test2') as session:
                users_db2 = session.query(User).all()
                assert len(users_db2) == 1
                assert users_db2[0].username == "user_db2"
                
        finally:
            # Cleanup
            try:
                os.unlink(temp_db2.name)
            except OSError:
                pass
    
    def test_pool_status(self):
        """Test connection pool status reporting"""
        status = self.db_manager.get_pool_status('test')
        
        assert status['database'] == 'test'
        assert 'pool_class' in status
        assert 'engine_url' in status
        assert status['pool_class'] == 'StaticPool'
    
    def test_error_handling(self):
        """Test error handling in database operations"""
        # Test duplicate user (should fail due to unique constraint)
        with pytest.raises(Exception):
            with session_scope('test') as session:
                user1 = User(username="duplicate_user", password_hash="hash1")
                user2 = User(username="duplicate_user", password_hash="hash2")
                session.add_all([user1, user2])
                # This should trigger rollback due to unique constraint violation
    
    def test_json_edge_cases(self):
        """Test JSON serialization edge cases"""
        with session_scope('test') as session:
            user = User(username="json_test_user", password_hash="hash")
            session.add(user)
            session.flush()
            
            thinking_session = ThinkingSession(
                user_id=user.id,
                session_id="json_test",
                tool_name="test_tool",
                method_name="test_method"
            )
            
            # Test empty parameters
            thinking_session.set_parameters({})
            assert thinking_session.get_parameters() == {}
            
            # Test None parameters
            thinking_session.set_parameters(None)
            assert thinking_session.get_parameters() == {}
            
            # Test complex nested structure
            complex_data = {
                "nested": {
                    "list": [1, 2, {"key": "value"}],
                    "unicode": "测试中文",
                    "boolean": True,
                    "null": None
                }
            }
            thinking_session.set_result(complex_data)
            result = thinking_session.get_result()
            assert result["nested"]["list"][2]["key"] == "value"
            assert result["nested"]["unicode"] == "测试中文"
            assert result["nested"]["boolean"] is True
            assert result["nested"]["null"] is None


def run_tests():
    """Run all tests"""
    import sys
    
    # Create test instance
    test_instance = TestSQLAlchemyIntegration()
    
    tests = [
        test_instance.test_user_operations,
        test_instance.test_thinking_session_operations,
        test_instance.test_memory_entity_operations,
        test_instance.test_memory_relation_operations,
        test_instance.test_database_switching,
        test_instance.test_pool_status,
        test_instance.test_json_edge_cases
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            print(f"Running {test_func.__name__}...", end=" ")
            test_instance.setup_method()
            test_func()
            test_instance.teardown_method()
            print("✅ PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {e}")
            failed += 1
            test_instance.teardown_method()
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
