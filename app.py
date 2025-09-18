#!/usr/bin/env python3
"""
Production Entry Point for Py-App-Tracker

This file is used by hosting services to start the Flask application.
It handles production environment configuration and port binding.
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

# Import and configure the Flask app
from web_app import app

if __name__ == "__main__":
    # Production configuration
    port = int(os.environ.get('PORT', 9000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV', 'production').lower() != 'production'
    
    print(f"🚀 Starting Py-App-Tracker on {host}:{port}")
    print(f"🔧 Environment: {'Development' if debug else 'Production'}")
    
    # Check for API configuration
    if os.getenv('ADZUNA_APP_ID'):
        print("✅ Adzuna API configured")
    else:
        print("⚠️  No API keys configured - using mock data")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )
