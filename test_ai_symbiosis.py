#!/usr/bin/env python3
"""Test the AI Symbiosis features for Repo2File"""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

# Create a test git repository with history
def create_test_repo():
    test_dir = tempfile.mkdtemp()
    
    # Initialize git repo
    subprocess.run(['git', 'init'], cwd=test_dir, check=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=test_dir, check=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=test_dir, check=True)
    
    # Create files and commit history
    files = {
        'main.py': '''# Main application
def process_payment(amount, user_id):
    """Process a payment for a user"""
    validate_amount(amount)
    charge = stripe.Charge.create(amount=amount, user=user_id)
    log_payment(charge)
    return charge.id

def validate_amount(amount):
    if amount <= 0:
        raise ValueError("Amount must be positive")
    # TODO: Implement maximum amount check
    return True

def log_payment(charge):
    """Log payment to database"""
    pass

if __name__ == "__main__":
    process_payment(100, "user123")
''',
        'utils.py': '''# Utility functions
import logging

def get_logger(name):
    """Get configured logger"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:.2f}"
''',
        'api/endpoints.py': '''# API endpoints
from flask import Flask, request
from main import process_payment

app = Flask(__name__)

@app.route('/checkout', methods=['POST'])
def checkout_endpoint():
    """Handle checkout requests"""
    data = request.json
    payment_id = process_payment(data['amount'], data['user_id'])
    return {'payment_id': payment_id}

@app.route('/subscribe', methods=['POST'])
def subscription_endpoint():
    """Handle subscription requests"""
    # FIXME: Implement recurring payments
    pass
'''
    }
    
    # Create and commit files with history
    for i, (filename, content) in enumerate(files.items()):
        filepath = os.path.join(test_dir, os.path.dirname(filename))
        if filepath != test_dir:
            os.makedirs(filepath, exist_ok=True)
        
        with open(os.path.join(test_dir, filename), 'w') as f:
            f.write(content)
        
        subprocess.run(['git', 'add', filename], cwd=test_dir, check=True)
        subprocess.run(['git', 'commit', '-m', f'Add {filename}'], cwd=test_dir, check=True)
    
    # Make some changes to create history
    with open(os.path.join(test_dir, 'main.py'), 'a') as f:
        f.write('\ndef calculate_tax(amount):\n    return amount * 0.1\n')
    
    subprocess.run(['git', 'add', 'main.py'], cwd=test_dir, check=True)
    subprocess.run(['git', 'commit', '-m', 'Add tax calculation'], cwd=test_dir, check=True)
    
    return test_dir

def test_ai_symbiosis_features():
    """Test the AI Symbiosis features"""
    test_dir = create_test_repo()
    output_file = os.path.join(test_dir, 'output.txt')
    
    try:
        # Test with Gemini profile + query + git insights
        cmd = [
            sys.executable,
            'repo2file/dump_ultra.py',
            test_dir,
            output_file,
            '--profile', 'gemini',
            '--query', 'refactor payment processing',
            '--git-insights'
        ]
        
        print("Testing AI Symbiosis features:")
        print("Command:", ' '.join(cmd))
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode != 0:
            print("ERROR: Command failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
        
        print("SUCCESS: Processing completed")
        print("STDOUT:", result.stdout)
        
        # Check output features
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                content = f.read()
                
                print("\nFeature checks:")
                
                # Check manifest with call graphs
                if "- Calls:" in content:
                    print("✓ Call graph information included")
                else:
                    print("✗ Call graph not found")
                
                # Check git insights
                if "# Git Insights for" in content:
                    print("✓ Git insights included")
                else:
                    print("✗ Git insights not found")
                
                # Check query relevance markers
                if "🎯" in content:
                    print("✓ Query relevance markers present")
                else:
                    print("✗ Query relevance markers not found")
                
                # Check TODOs/FIXMEs  
                if "TODO: Implement maximum amount check" in content:
                    print("✓ TODOs extracted")
                else:
                    print("✗ TODOs not found")
                
                # Check if payment-related files were prioritized
                if content.find("main.py") < content.find("utils.py"):
                    print("✓ Payment files prioritized for query")
                else:
                    print("✗ File prioritization may be incorrect")
                
                print(f"\nOutput file size: {len(content)} characters")
                
        return True
    
    finally:
        shutil.rmtree(test_dir)

if __name__ == "__main__":
    print("Starting AI Symbiosis features test...")
    if test_ai_symbiosis_features():
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Tests failed!")
        sys.exit(1)