#!/usr/bin/env python3
# Test Six Hats via HTTP

import requests
import json

def test_six_hats_http():
    print("🧪 Testing Six Hats via HTTP")
    print("=" * 50)
    
    # Test data
    payload = {
        "jsonrpc": "2.0",
        "method": "six_thinking_hats",
        "params": {
            "hat_color": "blue",
            "perspective": "Process control - Testing Six Hats HTTP integration",
            "insights": [
                "Six Hats successfully integrated into thinking-mcp",
                "HTTP endpoint responding correctly",
                "JSON-RPC 2.0 protocol working",
                "Ready for VS Code MCP client"
            ],
            "questions": [
                "How will VS Code reload the new tools?",
                "Should we add tool discovery endpoint?",
                "What documentation do users need?"
            ],
            "next_hat_needed": True,
            "session_complete": False
        },
        "id": 1
    }
    
    try:
        response = requests.post(
            "http://localhost:8000",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        
        print(f"📡 HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Six Hats HTTP test successful!")
            print(f"🎯 Method: {result.get('result', {}).get('method', 'unknown')}")
            print(f"🔵 Hat: {result.get('result', {}).get('hat_data', {}).get('hat_name', 'unknown')}")
            print(f"💡 Insights: {result.get('result', {}).get('hat_data', {}).get('insights_count', 0)}")
            print(f"❓ Questions: {result.get('result', {}).get('hat_data', {}).get('questions_count', 0)}")
            
            # Show formatted output
            formatted = result.get('result', {}).get('formatted_display', '')
            if formatted:
                print("\n📋 Formatted Output:")
                print(formatted)
                
        else:
            print(f"❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_six_hats_http()
