#!/usr/bin/env python3
"""Test the Flask API to ensure it handles ultra mode correctly"""

import requests
import time
import os

def test_ultra_mode():
    """Test ultra mode processing through Flask API"""
    base_url = "http://localhost:5000"
    
    # Create a simple test repository
    test_data = {
        'mode': 'ultra',
        'github_url': 'https://github.com/google/zx',  # Small test repo
        'options': {
            'model': 'gpt-4',
            'token_budget': 50000,
            'vibe_statement': 'Testing the ultra mode API',
            'planner_output': 'This is a test planning output'
        }
    }
    
    print("Testing ultra mode API...")
    
    # Send process request
    response = requests.post(f"{base_url}/api/v1/process", json=test_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success! Operation ID: {result['operation_id']}")
        print(f"Output size: {result['stats']['output_size']} bytes")
        print(f"Processing time: {result['stats']['processing_time']:.2f} seconds")
        
        # Save output
        output_file = f"test_output_{result['operation_id']}.txt"
        with open(output_file, 'w') as f:
            f.write(result['content'])
        print(f"Output saved to: {output_file}")
        
        # Check if the output contains our vibe statement
        if 'Testing the ultra mode API' in result['content']:
            print("✓ Vibe statement found in output")
        else:
            print("✗ Vibe statement not found in output")
            
        return True
    else:
        print(f"Error {response.status_code}: {response.json()}")
        return False

if __name__ == "__main__":
    test_ultra_mode()