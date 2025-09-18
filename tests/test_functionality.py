#!/usr/bin/env python3
"""
Comprehensive test script for the Py-App-Tracker application.

This script tests all major functionality to ensure everything works correctly.
"""

import sys
import os
import tempfile
import json
from datetime import datetime

# Add the src directory to the Python path
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

from models import Application, ApplicationStatus
from tracker import ApplicationTracker
from validators import validate_application_data, ValidationError


def test_application_model():
    """Test the Application model."""
    print("Testing Application model...")
    
    # Test basic application creation
    app = Application(
        company="Test Company",
        position="Software Engineer",
        location="San Francisco, CA",
        notes="Test application"
    )
    
    assert app.company == "Test Company"
    assert app.position == "Software Engineer"
    assert app.status == ApplicationStatus.APPLIED
    assert app.location == "San Francisco, CA"
    assert app.notes == "Test application"
    assert app.id is not None
    
    # Test status update
    app.update_status(ApplicationStatus.SCREENING, "Phone screening scheduled")
    assert app.status == ApplicationStatus.SCREENING
    assert "Phone screening scheduled" in app.notes
    
    # Test serialization
    data = app.to_dict()
    assert data['company'] == "Test Company"
    assert data['status'] == "screening"
    
    # Test deserialization
    app2 = Application.from_dict(data)
    assert app2.company == app.company
    assert app2.position == app.position
    assert app2.status == app.status
    
    print("✓ Application model tests passed")


def test_application_tracker():
    """Test the ApplicationTracker class."""
    print("Testing ApplicationTracker...")
    
    # Create temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        # Test tracker initialization
        tracker = ApplicationTracker(temp_file)
        assert len(tracker) == 0
        
        # Test adding applications
        app1 = Application("Google", "SWE", location="Mountain View")
        app2 = Application("Apple", "iOS Dev", location="Cupertino")
        
        id1 = tracker.add_application(app1)
        id2 = tracker.add_application(app2)
        
        assert len(tracker) == 2
        assert id1 == app1.id
        assert id2 == app2.id
        
        # Test getting applications
        retrieved_app = tracker.get_application(id1)
        assert retrieved_app is not None
        assert retrieved_app.company == "Google"
        
        # Test updating applications
        success = tracker.update_application(id1, status="screening", notes="Updated notes")
        assert success
        
        updated_app = tracker.get_application(id1)
        assert updated_app.status == ApplicationStatus.SCREENING
        assert updated_app.notes == "Updated notes"
        
        # Test listing applications
        all_apps = tracker.list_applications()
        assert len(all_apps) == 2
        
        # Test filtering by status
        screening_apps = tracker.list_applications(status_filter=ApplicationStatus.SCREENING)
        assert len(screening_apps) == 1
        assert screening_apps[0].company == "Google"
        
        # Test searching
        search_results = tracker.search_applications("Google")
        assert len(search_results) == 1
        assert search_results[0].company == "Google"
        
        # Test summary
        summary = tracker.get_status_summary()
        assert summary["applied"] == 1
        assert summary["screening"] == 1
        
        # Test persistence (reload from file)
        tracker2 = ApplicationTracker(temp_file)
        assert len(tracker2) == 2
        
        # Test deleting applications
        success = tracker.delete_application(id2)
        assert success
        assert len(tracker) == 1
        
        # Test deleting non-existent application
        success = tracker.delete_application("nonexistent")
        assert not success
        
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    print("✓ ApplicationTracker tests passed")


def test_validators():
    """Test validation functions."""
    print("Testing validators...")
    
    # Test valid data
    valid_data = validate_application_data(
        company="Test Corp",
        position="Developer",
        job_url="https://example.com/job",
        contact_email="test@example.com",
        salary_range="$100k-120k",
        location="Remote",
        notes="Great opportunity",
        contact_person="John Doe",
        application_date="2024-01-15"
    )
    
    assert valid_data['company'] == "Test Corp"
    assert valid_data['position'] == "Developer"
    assert valid_data['job_url'] == "https://example.com/job"
    assert valid_data['contact_email'] == "test@example.com"
    
    # Test validation errors
    try:
        validate_application_data("", "Developer")  # Empty company
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass  # Expected
    
    try:
        validate_application_data("Company", "")  # Empty position
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass  # Expected
    
    try:
        validate_application_data(
            "Company", "Position", 
            contact_email="invalid-email"  # Invalid email
        )
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass  # Expected
    
    try:
        validate_application_data(
            "Company", "Position", 
            job_url="not-a-url"  # Invalid URL
        )
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass  # Expected
    
    print("✓ Validator tests passed")


def test_cli_integration():
    """Test CLI integration (basic smoke test)."""
    print("Testing CLI integration...")
    
    # Import CLI after setting up path
    from cli import ApplicationCLI
    
    # Create CLI with temporary data file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        # Test CLI initialization
        cli = ApplicationCLI()
        assert cli.tracker is not None
        
        # Test help command (should not crash)
        exit_code = cli.run(['--help'])
        # Note: This will exit with 0 and print help, which is expected behavior
        
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    print("✓ CLI integration tests passed")


def run_all_tests():
    """Run all tests."""
    print("Running Py-App-Tracker Test Suite")
    print("=" * 40)
    
    try:
        test_application_model()
        test_application_tracker() 
        test_validators()
        test_cli_integration()
        
        print()
        print("=" * 40)
        print("🎉 All tests passed! Application is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
