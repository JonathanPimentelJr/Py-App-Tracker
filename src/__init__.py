"""
Py-App-Tracker: A Python-based application tracker for job applications.

This package provides tools for tracking and managing job applications,
including data models, persistence, and command-line interface.
"""

from .models import Application, ApplicationStatus
from .tracker import ApplicationTracker

__version__ = "1.0.0"
__author__ = "Your Name"

__all__ = ["Application", "ApplicationStatus", "ApplicationTracker"]
