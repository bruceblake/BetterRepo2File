"""
UI Routes Blueprint for BetterRepo2File v2.0
Handles all user interface routes and static page serving
"""
from flask import Blueprint, render_template, jsonify, session
import os

ui_bp = Blueprint('ui', __name__)


@ui_bp.route('/')
def index():
    """Main page with drag-and-drop interface"""
    return render_template('index.html')


@ui_bp.route('/loop-dashboard')
def loop_dashboard():
    """Vibe Coder Loop dashboard page"""
    return render_template('loop_dashboard.html')


@ui_bp.route('/debug')
def debug():
    """Debug page for testing"""
    return render_template('debug.html')


@ui_bp.route('/test-endpoints')
def test_endpoints():
    """Test endpoints page"""
    return render_template('test_endpoints.html')


@ui_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'BetterRepo2File',
        'version': '2.0'
    })


@ui_bp.route('/api/ui-config')
def ui_config():
    """Get UI configuration"""
    return jsonify({
        'max_file_size': 50 * 1024 * 1024,  # 50MB
        'supported_modes': ['standard', 'smart', 'token', 'ultra'],
        'default_mode': 'smart',
        'features': {
            'github_support': True,
            'file_upload': True,
            'profiles': True,
            'async_processing': True
        }
    })