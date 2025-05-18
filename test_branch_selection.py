#!/usr/bin/env python3
"""Test branch selection feature for GitHub repositories"""

import requests
import json
import time

# Test API endpoint
API_URL = "http://localhost:5000/api/v1/process"

def test_branch_selection():
    """Test cloning different branches of a repository"""
    
    # Test repository with multiple branches
    test_cases = [
        {
            "name": "Default branch",
            "data": {
                "mode": "smart",
                "github_url": "https://github.com/octocat/Hello-World",
                "options": {
                    "file_types": [".md", ".txt"]
                }
            }
        },
        {
            "name": "Specific branch (test)",
            "data": {
                "mode": "smart",
                "github_url": "https://github.com/octocat/Hello-World",
                "options": {
                    "github_branch": "test",
                    "file_types": [".md", ".txt"]
                }
            }
        },
        {
            "name": "Non-existent branch (should fail)",
            "data": {
                "mode": "smart",
                "github_url": "https://github.com/octocat/Hello-World",
                "options": {
                    "github_branch": "nonexistent-branch",
                    "file_types": [".md", ".txt"]
                }
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print(f"Data: {json.dumps(test_case['data'], indent=2)}")
        
        try:
            response = requests.post(API_URL, json=test_case['data'])
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Success: Operation ID: {result['operation_id']}")
                print(f"  Content length: {len(result.get('content', ''))} characters")
                
                # Check if branch-specific content is present
                content = result.get('content', '')
                if 'github_branch' in test_case['data']['options']:
                    branch = test_case['data']['options']['github_branch']
                    print(f"  Branch '{branch}' content detected: {'Yes' if branch in content else 'No'}")
                
            else:
                error = response.json()
                if "non-existent" in test_case['name'].lower():
                    print(f"✓ Expected failure: {error.get('error', 'Unknown error')}")
                else:
                    print(f"✗ Failed: {error.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"✗ Error: {str(e)}")
        
        time.sleep(1)  # Rate limit

if __name__ == "__main__":
    print("Testing branch selection feature...")
    print(f"API URL: {API_URL}")
    
    # Note: This test requires the Flask app to be running
    print("\nNote: Make sure the Flask app is running on port 5000")
    print("You can start it with: python app/app.py")
    
    try:
        test_branch_selection()
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to the API. Is the Flask app running?")
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
    
    print("\nTest completed!")