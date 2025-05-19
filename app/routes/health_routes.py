"""Health check endpoints for RobustRepo."""
from flask import Blueprint, jsonify
from datetime import datetime

from app.observability.health import (
    run_health_check,
    run_all_health_checks,
    get_overall_health,
    HealthStatus
)

# Create blueprint
health_bp = Blueprint('health', __name__, url_prefix='/health')


@health_bp.route('/', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    overall_status = get_overall_health()
    
    response = {
        'status': overall_status.value,
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'robustrepo',
        'version': '2.0.0'
    }
    
    # Return appropriate HTTP status code
    if overall_status == HealthStatus.HEALTHY:
        return jsonify(response), 200
    elif overall_status == HealthStatus.DEGRADED:
        return jsonify(response), 200  # Still return 200 for degraded
    else:
        return jsonify(response), 503  # Service unavailable


@health_bp.route('/live', methods=['GET'])
def liveness_check():
    """Kubernetes liveness check - is the service running?"""
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """Kubernetes readiness check - is the service ready to handle requests?"""
    # Check critical dependencies only
    redis_check = run_health_check('redis')
    celery_check = run_health_check('celery')
    
    if (redis_check.status == HealthStatus.HEALTHY and 
        celery_check.status == HealthStatus.HEALTHY):
        return jsonify({
            'status': 'ready',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    else:
        return jsonify({
            'status': 'not_ready',
            'timestamp': datetime.utcnow().isoformat(),
            'failures': [
                check.name for check in [redis_check, celery_check]
                if check.status != HealthStatus.HEALTHY
            ]
        }), 503


@health_bp.route('/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check with all component statuses."""
    all_checks = run_all_health_checks()
    overall_status = get_overall_health()
    
    # Convert results to JSON-friendly format
    checks = {}
    for name, result in all_checks.items():
        checks[name] = {
            'status': result.status.value,
            'message': result.message,
            'duration_ms': result.duration_ms,
            'timestamp': result.timestamp.isoformat(),
            'metadata': result.metadata
        }
    
    response = {
        'overall_status': overall_status.value,
        'timestamp': datetime.utcnow().isoformat(),
        'checks': checks
    }
    
    # Return appropriate HTTP status code
    if overall_status == HealthStatus.HEALTHY:
        return jsonify(response), 200
    elif overall_status == HealthStatus.DEGRADED:
        return jsonify(response), 200
    else:
        return jsonify(response), 503


@health_bp.route('/check/<check_name>', methods=['GET'])
def specific_health_check(check_name: str):
    """Run a specific health check."""
    result = run_health_check(check_name)
    
    response = {
        'name': result.name,
        'status': result.status.value,
        'message': result.message,
        'duration_ms': result.duration_ms,
        'timestamp': result.timestamp.isoformat(),
        'metadata': result.metadata
    }
    
    # Return appropriate HTTP status code
    if result.status == HealthStatus.HEALTHY:
        return jsonify(response), 200
    else:
        return jsonify(response), 503