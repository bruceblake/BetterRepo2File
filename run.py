#!/usr/bin/env python
"""
Run script for BetterRepo2File v2.0 - RobustRepo
"""
import os
from app import create_app

if __name__ == '__main__':
    # Get environment from FLASK_ENV, default to development
    env = os.environ.get('FLASK_ENV', 'development')
    
    # Create the Flask application
    app = create_app()
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=(env == 'development')
    )