#!/usr/bin/env python3
"""Quick setup verification script for RobustRepo v2.0"""

import sys
import importlib

def check_imports():
    """Check if all critical imports work correctly"""
    print("Checking critical imports...")
    
    tests = [
        ("Flask", "flask", "Flask"),
        ("Celery", "celery", "Celery"),
        ("Redis", "redis", "Redis"),
        ("MinIO", "minio", "Minio"),
        ("OpenTelemetry API", "opentelemetry.api", "trace"),
        ("OpenTelemetry SDK", "opentelemetry.sdk", "trace"),
        ("App Logger", "app.logger", "logger"),
        ("App Observability", "app.observability", "initialize_tracing"),
    ]
    
    failed = []
    
    for name, module_name, attr_name in tests:
        try:
            module = importlib.import_module(module_name)
            if attr_name:
                getattr(module, attr_name)
            print(f"✓ {name}")
        except ImportError as e:
            print(f"✗ {name}: {e}")
            failed.append(name)
        except AttributeError as e:
            print(f"✗ {name}: {e}")
            failed.append(name)
    
    return failed

def check_config():
    """Check if configuration is properly loaded"""
    print("\nChecking configuration...")
    
    try:
        from app.config import Config
        print(f"✓ Config loaded - Version: {Config.VERSION}")
        print(f"✓ Redis URL: {Config.REDIS_URL[:20]}...")
        print(f"✓ MinIO Endpoint: {Config.MINIO_ENDPOINT}")
        print(f"✓ OTEL Enabled: {Config.OTEL_ENABLED}")
        return True
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False

def check_app_factory():
    """Check if app factory works"""
    print("\nChecking app factory...")
    
    try:
        from app import create_app
        app = create_app('development')
        print("✓ App factory works")
        print(f"✓ App created with {len(app.blueprints)} blueprints")
        return True
    except Exception as e:
        print(f"✗ App factory error: {e}")
        return False

def main():
    print("=== RobustRepo v2.0 Setup Verification ===\n")
    
    # Add parent directory to path for imports
    sys.path.insert(0, '/home/proxyie/MySoftware/BetterRepo2File')
    
    failed_imports = check_imports()
    config_ok = check_config()
    app_ok = check_app_factory()
    
    print("\n=== Summary ===")
    if not failed_imports and config_ok and app_ok:
        print("✓ All checks passed! The application should start correctly.")
        return 0
    else:
        print("✗ Some checks failed:")
        if failed_imports:
            print(f"  - Failed imports: {', '.join(failed_imports)}")
        if not config_ok:
            print("  - Configuration issues")
        if not app_ok:
            print("  - App factory issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())