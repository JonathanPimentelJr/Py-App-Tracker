"""
Data validation and error handling utilities for the Application Tracker.

This module provides validation functions and custom exceptions for the application tracker.
"""

import re
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class ApplicationTrackerError(Exception):
    """Base exception for application tracker errors."""
    pass


class DataNotFoundError(ApplicationTrackerError):
    """Exception raised when requested data is not found."""
    pass


class DataIntegrityError(ApplicationTrackerError):
    """Exception raised when data integrity is compromised."""
    pass


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    if not email:
        return True  # Email is optional
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    if not url:
        return True  # URL is optional
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_date_string(date_str: str) -> Optional[datetime]:
    """
    Validate and parse date string.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        Parsed datetime object or None if invalid
        
    Raises:
        ValidationError: If date format is invalid
    """
    if not date_str:
        return None
    
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValidationError(f"Invalid date format '{date_str}'. Use YYYY-MM-DD.")


def validate_company_name(company: str) -> str:
    """
    Validate and clean company name.
    
    Args:
        company: Company name to validate
        
    Returns:
        Cleaned company name
        
    Raises:
        ValidationError: If company name is invalid
    """
    if not company or not company.strip():
        raise ValidationError("Company name cannot be empty.")
    
    company = company.strip()
    if len(company) > 100:
        raise ValidationError("Company name cannot exceed 100 characters.")
    
    return company


def validate_position_title(position: str) -> str:
    """
    Validate and clean position title.
    
    Args:
        position: Position title to validate
        
    Returns:
        Cleaned position title
        
    Raises:
        ValidationError: If position title is invalid
    """
    if not position or not position.strip():
        raise ValidationError("Position title cannot be empty.")
    
    position = position.strip()
    if len(position) > 100:
        raise ValidationError("Position title cannot exceed 100 characters.")
    
    return position


def validate_notes(notes: str) -> Optional[str]:
    """
    Validate and clean notes.
    
    Args:
        notes: Notes to validate
        
    Returns:
        Cleaned notes or None if empty
        
    Raises:
        ValidationError: If notes are too long
    """
    if not notes:
        return None
    
    notes = notes.strip()
    if not notes:
        return None
    
    if len(notes) > 2000:
        raise ValidationError("Notes cannot exceed 2000 characters.")
    
    return notes


def validate_salary_range(salary: str) -> Optional[str]:
    """
    Validate and clean salary range.
    
    Args:
        salary: Salary range to validate
        
    Returns:
        Cleaned salary range or None if empty
        
    Raises:
        ValidationError: If salary format is invalid
    """
    if not salary:
        return None
    
    salary = salary.strip()
    if not salary:
        return None
    
    if len(salary) > 50:
        raise ValidationError("Salary range cannot exceed 50 characters.")
    
    return salary


def validate_location(location: str) -> Optional[str]:
    """
    Validate and clean location.
    
    Args:
        location: Location to validate
        
    Returns:
        Cleaned location or None if empty
        
    Raises:
        ValidationError: If location is too long
    """
    if not location:
        return None
    
    location = location.strip()
    if not location:
        return None
    
    if len(location) > 100:
        raise ValidationError("Location cannot exceed 100 characters.")
    
    return location


def validate_contact_name(name: str) -> Optional[str]:
    """
    Validate and clean contact person name.
    
    Args:
        name: Contact name to validate
        
    Returns:
        Cleaned contact name or None if empty
        
    Raises:
        ValidationError: If name is too long
    """
    if not name:
        return None
    
    name = name.strip()
    if not name:
        return None
    
    if len(name) > 100:
        raise ValidationError("Contact name cannot exceed 100 characters.")
    
    return name


def validate_application_data(
    company: str,
    position: str,
    job_url: Optional[str] = None,
    contact_email: Optional[str] = None,
    salary_range: Optional[str] = None,
    location: Optional[str] = None,
    notes: Optional[str] = None,
    contact_person: Optional[str] = None,
    application_date: Optional[str] = None
) -> dict:
    """
    Validate all application data at once.
    
    Args:
        company: Company name
        position: Position title
        job_url: Job posting URL
        contact_email: Contact email
        salary_range: Salary range
        location: Job location
        notes: Additional notes
        contact_person: Contact person name
        application_date: Application date string
        
    Returns:
        Dictionary of validated data
        
    Raises:
        ValidationError: If any validation fails
    """
    validated_data = {
        'company': validate_company_name(company),
        'position': validate_position_title(position),
        'job_url': None,
        'contact_email': None,
        'salary_range': validate_salary_range(salary_range),
        'location': validate_location(location),
        'notes': validate_notes(notes),
        'contact_person': validate_contact_name(contact_person),
        'application_date': None
    }
    
    # Validate optional URL
    if job_url:
        if not validate_url(job_url):
            raise ValidationError(f"Invalid URL format: '{job_url}'")
        validated_data['job_url'] = job_url.strip()
    
    # Validate optional email
    if contact_email:
        if not validate_email(contact_email):
            raise ValidationError(f"Invalid email format: '{contact_email}'")
        validated_data['contact_email'] = contact_email.strip().lower()
    
    # Validate optional date
    if application_date:
        validated_data['application_date'] = validate_date_string(application_date)
    
    return validated_data


def safe_get_application(tracker, app_id: str):
    """
    Safely get an application by ID with better error handling.
    
    Args:
        tracker: ApplicationTracker instance
        app_id: Application ID
        
    Returns:
        Application instance
        
    Raises:
        DataNotFoundError: If application is not found
        ValidationError: If app_id format is invalid
    """
    if not app_id or not app_id.strip():
        raise ValidationError("Application ID cannot be empty.")
    
    app_id = app_id.strip()
    
    # Try to find application by full ID first
    app = tracker.get_application(app_id)
    if app:
        return app
    
    # If not found and it looks like a short ID (8 chars), try to find by prefix
    if len(app_id) == 8:
        matching_apps = [app for app in tracker.applications if app.id.startswith(app_id)]
        if len(matching_apps) == 1:
            return matching_apps[0]
        elif len(matching_apps) > 1:
            raise ValidationError(f"Ambiguous application ID '{app_id}'. Found {len(matching_apps)} matches.")
    
    raise DataNotFoundError(f"Application with ID '{app_id}' not found.")
