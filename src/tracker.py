"""
Application Tracker for managing job applications.

This module provides the main ApplicationTracker class for managing job applications
with JSON file persistence.
"""

import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

try:
    from .models import Application, ApplicationStatus
except ImportError:
    from models import Application, ApplicationStatus


class ApplicationTracker:
    """Main class for managing job applications."""
    
    def __init__(self, data_file: Optional[str] = None):
        """
        Initialize the Application Tracker.
        
        Args:
            data_file: Path to the JSON file for storing applications.
                      If None, uses default location in data directory.
        """
        if data_file is None:
            # Default to data directory relative to the project root
            project_root = Path(__file__).parent.parent
            data_dir = project_root / "data"
            data_dir.mkdir(exist_ok=True)
            self.data_file = data_dir / "applications.json"
        else:
            self.data_file = Path(data_file)
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.applications: List[Application] = []
        self.load_applications()
    
    def load_applications(self):
        """Load applications from the JSON file."""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.applications = [Application.from_dict(app_data) for app_data in data]
            else:
                self.applications = []
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Warning: Could not load applications from {self.data_file}: {e}")
            print("Starting with empty application list.")
            self.applications = []
    
    def save_applications(self):
        """Save applications to the JSON file."""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([app.to_dict() for app in self.applications], f, indent=2)
        except Exception as e:
            print(f"Error saving applications to {self.data_file}: {e}")
            raise
    
    def add_application(self, application: Application) -> str:
        """
        Add a new application.
        
        Args:
            application: The Application instance to add
            
        Returns:
            The ID of the added application
        """
        self.applications.append(application)
        self.save_applications()
        return application.id
    
    def get_application(self, app_id: str) -> Optional[Application]:
        """
        Get an application by ID.
        
        Args:
            app_id: The application ID
            
        Returns:
            The Application instance or None if not found
        """
        for app in self.applications:
            if app.id == app_id:
                return app
        return None
    
    def update_application(self, app_id: str, **updates) -> bool:
        """
        Update an application.
        
        Args:
            app_id: The application ID
            **updates: Fields to update
            
        Returns:
            True if the application was updated, False if not found
        """
        app = self.get_application(app_id)
        if not app:
            return False
        
        for field, value in updates.items():
            if hasattr(app, field):
                if field == 'status' and isinstance(value, str):
                    app.status = ApplicationStatus(value)
                else:
                    setattr(app, field, value)
        
        app.updated_at = datetime.now()
        self.save_applications()
        return True
    
    def delete_application(self, app_id: str) -> bool:
        """
        Delete an application.
        
        Args:
            app_id: The application ID
            
        Returns:
            True if the application was deleted, False if not found
        """
        for i, app in enumerate(self.applications):
            if app.id == app_id:
                del self.applications[i]
                self.save_applications()
                return True
        return False
    
    def list_applications(
        self, 
        status_filter: Optional[ApplicationStatus] = None,
        company_filter: Optional[str] = None,
        limit: Optional[int] = None,
        sort_by: str = 'updated_at',
        reverse: bool = True
    ) -> List[Application]:
        """
        List applications with optional filtering and sorting.
        
        Args:
            status_filter: Filter by application status
            company_filter: Filter by company name (case-insensitive partial match)
            limit: Limit the number of results
            sort_by: Field to sort by (default: updated_at)
            reverse: Sort in reverse order (default: True for newest first)
            
        Returns:
            List of filtered and sorted applications
        """
        filtered_apps = self.applications.copy()
        
        # Apply filters
        if status_filter:
            filtered_apps = [app for app in filtered_apps if app.status == status_filter]
        
        if company_filter:
            company_lower = company_filter.lower()
            filtered_apps = [app for app in filtered_apps if company_lower in app.company.lower()]
        
        # Sort applications
        if sort_by == 'application_date':
            filtered_apps.sort(
                key=lambda app: app.application_date or datetime.min, 
                reverse=reverse
            )
        elif sort_by == 'company':
            filtered_apps.sort(key=lambda app: app.company.lower(), reverse=reverse)
        elif sort_by == 'position':
            filtered_apps.sort(key=lambda app: app.position.lower(), reverse=reverse)
        else:  # default to updated_at
            filtered_apps.sort(key=lambda app: app.updated_at, reverse=reverse)
        
        # Apply limit
        if limit:
            filtered_apps = filtered_apps[:limit]
        
        return filtered_apps
    
    def get_status_summary(self) -> Dict[str, int]:
        """
        Get a summary of applications by status.
        
        Returns:
            Dictionary mapping status to count
        """
        summary = {}
        for status in ApplicationStatus:
            summary[status.value] = 0
        
        for app in self.applications:
            summary[app.status.value] += 1
        
        return summary
    
    def search_applications(self, query: str) -> List[Application]:
        """
        Search applications by company, position, or notes.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching applications
        """
        query_lower = query.lower()
        results = []
        
        for app in self.applications:
            # Search in company, position, and notes
            if (query_lower in app.company.lower() or
                query_lower in app.position.lower() or
                (app.notes and query_lower in app.notes.lower()) or
                (app.contact_person and query_lower in app.contact_person.lower())):
                results.append(app)
        
        return results
    
    def get_applications_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Application]:
        """
        Get applications within a date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of applications within the date range
        """
        return [
            app for app in self.applications
            if app.application_date and start_date <= app.application_date <= end_date
        ]
    
    def __len__(self) -> int:
        """Return the number of applications."""
        return len(self.applications)
    
    def __str__(self) -> str:
        """String representation of the tracker."""
        return f"ApplicationTracker({len(self.applications)} applications)"
