# -*- coding: utf-8 -*-
# File: test_sqlalchemy_simple.py

"""
Simple integration tests for SQLAlchemy database layer
"""

import tempfile
import os
from datetime import datetime
from sqlalchemy.pool import StaticPool

from app.db_sqlalchemy import (
    DatabaseManager, 
    User, 
    ThinkingSession, 
    MemoryEntity, 
    MemoryObservation, 
    MemoryRelation,
    session_scope
)


def test_sqlalchemy_integration():
    """Simple integration test for SQLAlchemy functionality"""
    
    # Setup temporary database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        # Initialize test database
        db_manager = DatabaseManager()
        test_config = {
            'url': f'sqlite:///{temp_db.name}',
            'pool_class': StaticPool,
            'echo': False
        }
        db_manager.register_database('test', test_config)
        db_manager.switch_database('test')
        db_manager.create_all_tables('test')
        
        print("✅ Database setup completed")
        
        # Test 1: User operations
        print("🧪 Testing user operations...")
        with db_manager.session_scope('test') as session:
            user = User(
                username="test_user_123",
                password_hash="test_hash_456"
            )
            session.add(user)
            session.flush()
            user_id = user.id
            print(f"   Created user with ID: {user_id}")
        
        # Verify user was created
        with db_manager.session_scope('test') as session:
            retrieved_user = session.query(User).filter_by(username="test_user_123").first()
            if retrieved_user:
                print(f"   Retrieved user: {retrieved_user.username}")
                print("✅ User operations test passed")
            else:
                print("❌ User operations test failed")
                return False
        
        # Test 2: Thinking Session with JSON
        print("🧪 Testing thinking session operations...")
        with db_manager.session_scope('test') as session:
            thinking_session = ThinkingSession(
                user_id=user_id,
                session_id="test_session_json",
                tool_name="six_thinking_hats",
                method_name="six_thinking_hats"
            )
            
            # Test JSON serialization
            test_params = {
                "hat_color": "blue",
                "perspective": "process control",
                "questions": ["What works?", "What doesn't?"]
            }
            thinking_session.set_parameters(test_params)
            
            test_result = {
                "success": True,
                "insights": ["Good progress", "Need improvements"],
                "confidence": 85.5
            }
            thinking_session.set_result(test_result)
            
            session.add(thinking_session)
            session.flush()
            session_id = thinking_session.id
            print(f"   Created thinking session with ID: {session_id}")
        
        # Verify JSON serialization/deserialization
        with db_manager.session_scope('test') as session:
            retrieved_session = session.query(ThinkingSession).filter_by(id=session_id).first()
            if retrieved_session:
                params = retrieved_session.get_parameters()
                result = retrieved_session.get_result()
                
                if (params.get("hat_color") == "blue" and 
                    result.get("success") is True and 
                    result.get("confidence") == 85.5):
                    print("   JSON serialization/deserialization works")
                    print("✅ Thinking session operations test passed")
                else:
                    print("❌ JSON serialization/deserialization failed")
                    return False
            else:
                print("❌ Thinking session retrieval failed")
                return False
        
        # Test 3: Memory entities and observations
        print("🧪 Testing memory entity operations...")
        with db_manager.session_scope('test') as session:
            entity = MemoryEntity(
                name="SQLAlchemy Testing",
                entity_type="concept"
            )
            session.add(entity)
            session.flush()
            
            # Add observations
            obs1 = MemoryObservation(entity_id=entity.id, content="Database ORM for Python")
            obs2 = MemoryObservation(entity_id=entity.id, content="Supports multiple databases")
            session.add_all([obs1, obs2])
            session.flush()
            
            entity_id = entity.id
            print(f"   Created memory entity with ID: {entity_id}")
        
        # Verify entity and observations
        with db_manager.session_scope('test') as session:
            retrieved_entity = session.query(MemoryEntity).filter_by(id=entity_id).first()
            if retrieved_entity and len(retrieved_entity.observations) == 2:
                print(f"   Retrieved entity with {len(retrieved_entity.observations)} observations")
                print("✅ Memory entity operations test passed")
            else:
                print("❌ Memory entity operations test failed")
                return False
        
        # Test 4: Memory relations
        print("🧪 Testing memory relation operations...")
        with db_manager.session_scope('test') as session:
            # Create two entities
            python_entity = MemoryEntity(name="Python", entity_type="language")
            sqlalchemy_entity = MemoryEntity(name="SQLAlchemy", entity_type="library")
            session.add_all([python_entity, sqlalchemy_entity])
            session.flush()
            
            # Create relation
            relation = MemoryRelation(
                from_entity_id=python_entity.id,
                to_entity_id=sqlalchemy_entity.id,
                relation_type="uses"
            )
            session.add(relation)
            session.flush()
            
            python_id = python_entity.id
            sqlalchemy_id = sqlalchemy_entity.id
            print(f"   Created relation: Python({python_id}) uses SQLAlchemy({sqlalchemy_id})")
        
        # Verify relations
        with db_manager.session_scope('test') as session:
            python_entity = session.query(MemoryEntity).filter_by(id=python_id).first()
            if python_entity and len(python_entity.relations_from) == 1:
                relation = python_entity.relations_from[0]
                if relation.relation_type == "uses" and relation.to_entity_id == sqlalchemy_id:
                    print("   Relation verified successfully")
                    print("✅ Memory relation operations test passed")
                else:
                    print("❌ Relation verification failed")
                    return False
            else:
                print("❌ Memory relation operations test failed")
                return False
        
        # Test 5: Database switching
        print("🧪 Testing database switching...")
        
        # Create second database
        temp_db2 = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db2.close()
        
        try:
            test_config2 = {
                'url': f'sqlite:///{temp_db2.name}',
                'pool_class': StaticPool,
                'echo': False
            }
            db_manager.register_database('test2', test_config2)
            db_manager.create_all_tables('test2')
            
            # Add data to second database
            db_manager.switch_database('test2')
            with db_manager.session_scope('test2') as session:
                user2 = User(username="user_db2", password_hash="hash2")
                session.add(user2)
                session.flush()
                print("   Added user to second database")
            
            # Switch back and verify isolation
            db_manager.switch_database('test')
            with db_manager.session_scope('test') as session:
                users_count = session.query(User).count()
                print(f"   First database has {users_count} users")
            
            with db_manager.session_scope('test2') as session:
                users_count2 = session.query(User).count()
                print(f"   Second database has {users_count2} users")
            
            if users_count >= 1 and users_count2 == 1:
                print("✅ Database switching test passed")
            else:
                print("❌ Database switching test failed")
                return False
                
        finally:
            try:
                os.unlink(temp_db2.name)
            except OSError:
                pass
        
        # Test 6: Pool status
        print("🧪 Testing pool status...")
        status = db_manager.get_pool_status('test')
        if (status.get('database') == 'test' and 
            'pool_class' in status and 
            'engine_url' in status):
            print(f"   Pool status: {status}")
            print("✅ Pool status test passed")
        else:
            print("❌ Pool status test failed")
            return False
        
        print("\n🎉 All SQLAlchemy integration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        try:
            os.unlink(temp_db.name)
        except OSError:
            pass


if __name__ == "__main__":
    print("🚀 Starting SQLAlchemy Integration Tests")
    print("=" * 50)
    
    success = test_sqlalchemy_integration()
    
    print("=" * 50)
    if success:
        print("✅ All tests completed successfully!")
        exit(0)
    else:
        print("❌ Some tests failed!")
        exit(1)
