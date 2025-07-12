#!/usr/bin/env python3
# Test Six Hats implementation

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.six_hats_logic import (
    HatColor, 
    validate_six_hats_params, 
    create_six_hats_response,
    get_recommended_hat_sequence
)

def test_six_hats():
    print("🧪 Testing Six Hats Implementation")
    print("=" * 50)
    
    # Test 1: Hat Color enum
    print("\n1. Testing Hat Colors:")
    for hat in HatColor:
        print(f"   {hat.emoji} {hat.name.title()}: {hat.description}")
    
    # Test 2: Validation
    print("\n2. Testing Validation:")
    test_params = {
        "hat_color": "white",
        "perspective": "Analyzing the facts and data available",
        "insights": [
            "Current toolkit has 24 thinking tools",
            "Missing parallel thinking approach",
            "Strong foundation in Python with FastAPI"
        ],
        "questions": [
            "What specific data supports Six Hats integration?",
            "How will users discover this new capability?"
        ],
        "next_hat_needed": True,
        "session_complete": False
    }
    
    try:
        validate_six_hats_params(test_params)
        print("   ✅ Validation passed")
    except Exception as e:
        print(f"   ❌ Validation failed: {e}")
        return
    
    # Test 3: Response creation
    print("\n3. Testing Response Creation:")
    try:
        response = create_six_hats_response(test_params)
        print("   ✅ Response created successfully")
        print(f"   📊 Method: {response['method']}")
        print(f"   🎯 Hat: {response['hat_data']['hat_name']}")
        print(f"   💡 Insights: {response['hat_data']['insights_count']}")
        print(f"   ❓ Questions: {response['hat_data']['questions_count']}")
    except Exception as e:
        print(f"   ❌ Response creation failed: {e}")
        return
    
    # Test 4: Formatted output
    print("\n4. Testing Formatted Output:")
    print(response['formatted_display'])
    
    # Test 5: Sequence recommendation
    print("\n5. Testing Sequence Recommendation:")
    sequence = get_recommended_hat_sequence()
    print(f"   📋 Total steps: {len(sequence)}")
    for step in sequence[:3]:  # Show first 3 steps
        print(f"   {step['order']}. {step['hat'].upper()} Hat - {step['purpose']}")
    
    print("\n🎉 All tests completed successfully!")
    print("✅ Six Hats implementation is ready for integration")

if __name__ == "__main__":
    test_six_hats()
