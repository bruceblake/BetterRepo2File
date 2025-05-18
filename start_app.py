#!/usr/bin/env python
"""Starter script for BetterRepo2File Flask application"""

if __name__ == '__main__':
    from app.app import app
    print("Starting BetterRepo2File UI server...")
    print("Access the application at: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)