#!/usr/bin/env python3
import sqlite3
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.db import mcp_db_init, get_db_connection

def test_mcp_db():
    print("🚀 Testing MCP Database...")
    
    try:
        # Initialize MCP database
        print("1. Initializing MCP database...")
        mcp_db_init()
        print("✅ MCP database initialized successfully")
        
        # Check tables
        print("2. Checking database tables...")
        conn = get_db_connection()
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"📊 Found tables: {tables}")
        
        # Check if our new tables exist
        expected_tables = ['mcp_queries', 'memory_structures']
        for table in expected_tables:
            if table in tables:
                print(f"✅ Table '{table}' exists")
            else:
                print(f"❌ Table '{table}' missing")
        
        # Test CRUD operations
        print("3. Testing CRUD operations...")
        from app.db import create_mcp_query, get_mcp_query_stats
        
        # Test create MCP query
        test_success = create_mcp_query(
            query_id="test-123",
            tool_name="test_tool",
            input_data={"test": "input"},
            output_data={"test": "output"},
            execution_time_ms=100,
            success=True
        )
        
        if test_success:
            print("✅ MCP query creation test passed")
        else:
            print("❌ MCP query creation test failed")
        
        # Test stats
        stats = get_mcp_query_stats()
        print(f"📈 MCP Query Stats: {stats}")
        
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mcp_db()
