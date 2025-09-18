"""
Data models for the Application Tracker.

This module defines the core data structures for tracking job applications.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
import uuid


class ApplicationStatus(Enum):
    """Enum for application statuses."""
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWED = "interviewed"
    OFFER_RECEIVED = "offer_received"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    ACCEPTED = "accepted"


class Application:
    """Represents a job application."""
    
    def __init__(
        self,
        company: str,
        position: str,
        status: ApplicationStatus = ApplicationStatus.APPLIED,
        application_date: Optional[datetime] = None,
        job_url: Optional[str] = None,
        salary_range: Optional[str] = None,
        location: Optional[str] = None,
        notes: Optional[str] = None,
        contact_person: Optional[str] = None,
        contact_email: Optional[str] = None,
        app_id: Optional[str] = None,
        job_posting_id: Optional[str] = None,
        job_posting_source: Optional[str] = None,
        job_description: Optional[str] = None
    ):
        """
        Initialize a new job application.
        
        Args:
            company: Company name
            position: Job position/title
            status: Current application status
            application_date: Date when application was submitted
            job_url: URL to the job posting
            salary_range: Salary range for the position
            location: Job location
            notes: Additional notes about the application
            contact_person: Name of contact person
            contact_email: Email of contact person
            app_id: Unique identifier for the application
            job_posting_id: ID from the job posting source
            job_posting_source: Source of the job posting (e.g., 'JSearch', 'Manual')
            job_description: Full job description from the original posting
        """
        self.id = app_id or str(uuid.uuid4())
        self.company = company
        self.position = position
        self.status = status
        self.application_date = application_date or datetime.now()
        self.job_url = job_url
        self.salary_range = salary_range
        self.location = location
        self.notes = notes
        self.contact_person = contact_person
        self.contact_email = contact_email
        self.job_posting_id = job_posting_id
        self.job_posting_source = job_posting_source or "Manual"
        self.job_description = job_description
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def update_status(self, new_status: ApplicationStatus, notes: Optional[str] = None):
        """Update the application status."""
        self.status = new_status
        self.updated_at = datetime.now()
        if notes:
            if self.notes:
                self.notes += f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {notes}"
            else:
                self.notes = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {notes}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the application to a dictionary for serialization."""
        return {
            'id': self.id,
            'company': self.company,
            'position': self.position,
            'status': self.status.value,
            'application_date': self.application_date.isoformat() if self.application_date else None,
            'job_url': self.job_url,
            'salary_range': self.salary_range,
            'location': self.location,
            'notes': self.notes,
            'contact_person': self.contact_person,
            'contact_email': self.contact_email,
            'job_posting_id': self.job_posting_id,
            'job_posting_source': self.job_posting_source,
            'job_description': self.job_description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Application':
        """Create an Application instance from a dictionary."""
        app = cls(
            company=data['company'],
            position=data['position'],
            status=ApplicationStatus(data['status']),
            application_date=datetime.fromisoformat(data['application_date']) if data.get('application_date') else None,
            job_url=data.get('job_url'),
            salary_range=data.get('salary_range'),
            location=data.get('location'),
            notes=data.get('notes'),
            contact_person=data.get('contact_person'),
            contact_email=data.get('contact_email'),
            app_id=data['id'],
            job_posting_id=data.get('job_posting_id'),
            job_posting_source=data.get('job_posting_source'),
            job_description=data.get('job_description')
        )
        if data.get('created_at'):
            app.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            app.updated_at = datetime.fromisoformat(data['updated_at'])
        return app
    
    def __str__(self) -> str:
        """String representation of the application."""
        return f"{self.company} - {self.position} ({self.status.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the application."""
        return f"Application(id='{self.id}', company='{self.company}', position='{self.position}', status='{self.status.value}')"
