#!/usr/bin/env python3
"""
Py-App-Tracker - A Python-based job application tracker

Main entry point for the application tracker CLI.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.cli import main

if __name__ == "__main__":
    main()
