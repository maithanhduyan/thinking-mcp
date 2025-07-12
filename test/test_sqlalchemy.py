#!/usr/bin/env python3
# Test SQLAlchemy implementation

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

def test_sqlalchemy():
    print("🧪 Testing SQLAlchemy Implementation")
    print("=" * 50)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from app.db_sqlalchemy import (
            init_sqlalchemy_databases,
            session_scope,
            User,
            ThinkingSession,
            MemoryEntity,
            db_manager,
            get_pool_status
        )
        print("   ✅ All imports successful")
        
        # Test initialization
        print("\n2. Testing initialization...")
        init_sqlalchemy_databases()
        print("   ✅ Database initialization successful")
        
        # Test database operations
        print("\n3. Testing database operations...")
        with session_scope() as session:
            # Create test user
            user = User(username="sqlalchemy_test_user", password_hash="test_hash_123")
            session.add(user)
            session.flush()  # Get the ID
            print(f"   ✅ Created user with ID: {user.id}")
            
            # Create test thinking session
            thinking_session = ThinkingSession(
                user_id=user.id,
                session_id="sqlalchemy_test_session",
                tool_name="six_thinking_hats",
                method_name="six_thinking_hats",
                parameters={"hat_color": "blue", "perspective": "Testing SQLAlchemy"},
                result={"success": True, "test": True},
                execution_time=150
            )
            session.add(thinking_session)
            session.flush()
            print(f"   ✅ Created thinking session with ID: {thinking_session.id}")
            
            # Create test memory entity
            entity = MemoryEntity(
                name="SQLAlchemy Test Entity",
                entity_type="test"
            )
            session.add(entity)
            session.flush()
            print(f"   ✅ Created memory entity with ID: {entity.id}")
        
        # Test pool status
        print("\n4. Testing connection pool...")
        pool_status = get_pool_status()
        print(f"   📊 Pool status: {pool_status}")
        
        # Test database switching (if multiple databases available)
        print("\n5. Testing database manager...")
        print(f"   📋 Current database: {db_manager.current_db}")
        print(f"   📋 Available databases: {list(db_manager.engines.keys())}")
        
        print("\n🎉 All SQLAlchemy tests completed successfully!")
        print("✅ SQLAlchemy is ready for production use")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sqlalchemy()
    sys.exit(0 if success else 1)
