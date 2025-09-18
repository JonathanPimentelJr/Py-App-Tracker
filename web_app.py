#!/usr/bin/env python3
"""
Flask Web Interface for Py-App-Tracker

A web-based interface for the job application tracker that provides
a user-friendly GUI for managing job applications.
"""

import sys
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from models import Application, ApplicationStatus
    from tracker import ApplicationTracker
    from validators import validate_application_data, ValidationError
    from reports import ApplicationReporter
    from job_api import get_job_service
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Change this in production!

# Initialize the application tracker
tracker = ApplicationTracker()

# Helper function to get status color class
def get_status_color_class(status):
    """Get CSS class for application status."""
    color_map = {
        ApplicationStatus.APPLIED: "primary",
        ApplicationStatus.SCREENING: "info", 
        ApplicationStatus.INTERVIEW_SCHEDULED: "warning",
        ApplicationStatus.INTERVIEWED: "secondary",
        ApplicationStatus.OFFER_RECEIVED: "success",
        ApplicationStatus.REJECTED: "danger",
        ApplicationStatus.WITHDRAWN: "light",
        ApplicationStatus.ACCEPTED: "success"
    }
    return color_map.get(status, "secondary")

# Make helper functions available in templates
app.jinja_env.globals.update(get_status_color_class=get_status_color_class)
app.jinja_env.globals.update(datetime=datetime)

@app.route('/')
def index():
    """Main dashboard showing application summary and recent applications."""
    try:
        # Get summary statistics
        summary = tracker.get_status_summary()
        total_apps = len(tracker)
        
        # Get recent applications (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        recent_apps = tracker.get_applications_by_date_range(start_date, end_date)
        recent_apps.sort(key=lambda app: app.updated_at, reverse=True)
        recent_apps = recent_apps[:5]  # Show only 5 most recent
        
        # Get analytics
        reporter = ApplicationReporter(tracker.applications)
        response_analysis = reporter.analyze_response_rates()
        
        return render_template('index.html',
                             summary=summary,
                             total_apps=total_apps,
                             recent_apps=recent_apps,
                             response_analysis=response_analysis)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('index.html', 
                             summary={}, 
                             total_apps=0, 
                             recent_apps=[], 
                             response_analysis={})

@app.route('/applications')
def applications():
    """List all applications with filtering and sorting options."""
    try:
        # Get filter parameters
        status_filter = request.args.get('status')
        company_filter = request.args.get('company', '').strip()
        sort_by = request.args.get('sort', 'updated_at')
        order = request.args.get('order', 'desc')
        
        # Apply filters
        status_enum = None
        if status_filter:
            try:
                status_enum = ApplicationStatus(status_filter)
            except ValueError:
                flash(f'Invalid status filter: {status_filter}', 'warning')
        
        # Get filtered applications
        apps = tracker.list_applications(
            status_filter=status_enum,
            company_filter=company_filter if company_filter else None,
            sort_by=sort_by,
            reverse=(order == 'desc')
        )
        
        # Get unique companies for filter dropdown
        all_companies = list(set(app.company for app in tracker.applications))
        all_companies.sort()
        
        return render_template('applications.html', 
                             applications=apps,
                             all_companies=all_companies,
                             current_filters={
                                 'status': status_filter,
                                 'company': company_filter,
                                 'sort': sort_by,
                                 'order': order
                             },
                             all_statuses=list(ApplicationStatus))
    except Exception as e:
        flash(f'Error loading applications: {str(e)}', 'error')
        return render_template('applications.html', applications=[], all_companies=[], current_filters={})

@app.route('/application/<app_id>')
def view_application(app_id):
    """View detailed information about a specific application."""
    try:
        app = tracker.get_application(app_id)
        if not app:
            flash('Application not found', 'error')
            return redirect(url_for('applications'))
        
        return render_template('view_application.html', application=app)
    except Exception as e:
        flash(f'Error loading application: {str(e)}', 'error')
        return redirect(url_for('applications'))

@app.route('/add', methods=['GET', 'POST'])
def add_application():
    """Add a new job application."""
    if request.method == 'POST':
        try:
            # Get form data
            company = request.form.get('company', '').strip()
            position = request.form.get('position', '').strip()
            status = request.form.get('status', ApplicationStatus.APPLIED.value)
            job_url = request.form.get('job_url', '').strip() or None
            salary_range = request.form.get('salary_range', '').strip() or None
            location = request.form.get('location', '').strip() or None
            notes = request.form.get('notes', '').strip() or None
            contact_person = request.form.get('contact_person', '').strip() or None
            contact_email = request.form.get('contact_email', '').strip() or None
            application_date = request.form.get('application_date', '').strip() or None
            
            # Validate data
            validated_data = validate_application_data(
                company=company,
                position=position,
                job_url=job_url,
                contact_email=contact_email,
                salary_range=salary_range,
                location=location,
                notes=notes,
                contact_person=contact_person,
                application_date=application_date
            )
            
            # Get job posting data if available
            job_posting_id = request.form.get('job_posting_id', '').strip() or None
            job_posting_source = request.form.get('job_posting_source', '').strip() or None
            job_description = request.form.get('job_description', '').strip() or None
            
            # Create application
            app = Application(
                company=validated_data['company'],
                position=validated_data['position'],
                status=ApplicationStatus(status),
                application_date=validated_data['application_date'],
                job_url=validated_data['job_url'],
                salary_range=validated_data['salary_range'],
                location=validated_data['location'],
                notes=validated_data['notes'],
                contact_person=validated_data['contact_person'],
                contact_email=validated_data['contact_email'],
                job_posting_id=job_posting_id,
                job_posting_source=job_posting_source,
                job_description=job_description
            )
            
            # Add to tracker
            app_id = tracker.add_application(app)
            flash(f'Application added successfully: {app.company} - {app.position}', 'success')
            return redirect(url_for('view_application', app_id=app_id))
            
        except ValidationError as e:
            flash(f'Validation error: {str(e)}', 'error')
        except Exception as e:
            flash(f'Error adding application: {str(e)}', 'error')
    
    return render_template('add_application.html', all_statuses=list(ApplicationStatus))

@app.route('/edit/<app_id>', methods=['GET', 'POST'])
def edit_application(app_id):
    """Edit an existing job application."""
    try:
        app = tracker.get_application(app_id)
        if not app:
            flash('Application not found', 'error')
            return redirect(url_for('applications'))
        
        if request.method == 'POST':
            try:
                # Get form data
                company = request.form.get('company', '').strip()
                position = request.form.get('position', '').strip()
                status = request.form.get('status')
                job_url = request.form.get('job_url', '').strip() or None
                salary_range = request.form.get('salary_range', '').strip() or None
                location = request.form.get('location', '').strip() or None
                notes = request.form.get('notes', '').strip() or None
                contact_person = request.form.get('contact_person', '').strip() or None
                contact_email = request.form.get('contact_email', '').strip() or None
                
                # Validate data
                validated_data = validate_application_data(
                    company=company,
                    position=position,
                    job_url=job_url,
                    contact_email=contact_email,
                    salary_range=salary_range,
                    location=location,
                    notes=notes,
                    contact_person=contact_person
                )
                
                # Update application
                updates = {
                    'company': validated_data['company'],
                    'position': validated_data['position'],
                    'status': status,
                    'job_url': validated_data['job_url'],
                    'salary_range': validated_data['salary_range'],
                    'location': validated_data['location'],
                    'notes': validated_data['notes'],
                    'contact_person': validated_data['contact_person'],
                    'contact_email': validated_data['contact_email']
                }
                
                success = tracker.update_application(app_id, **updates)
                if success:
                    flash('Application updated successfully', 'success')
                    return redirect(url_for('view_application', app_id=app_id))
                else:
                    flash('Failed to update application', 'error')
                    
            except ValidationError as e:
                flash(f'Validation error: {str(e)}', 'error')
            except Exception as e:
                flash(f'Error updating application: {str(e)}', 'error')
        
        return render_template('edit_application.html', application=app, all_statuses=list(ApplicationStatus))
        
    except Exception as e:
        flash(f'Error loading application for editing: {str(e)}', 'error')
        return redirect(url_for('applications'))

@app.route('/delete/<app_id>', methods=['POST'])
def delete_application(app_id):
    """Delete a job application."""
    try:
        app = tracker.get_application(app_id)
        if not app:
            flash('Application not found', 'error')
        else:
            success = tracker.delete_application(app_id)
            if success:
                flash(f'Application deleted: {app.company} - {app.position}', 'success')
            else:
                flash('Failed to delete application', 'error')
    except Exception as e:
        flash(f'Error deleting application: {str(e)}', 'error')
    
    return redirect(url_for('applications'))

@app.route('/search')
def search():
    """Search applications."""
    query = request.args.get('q', '').strip()
    results = []
    
    if query:
        try:
            results = tracker.search_applications(query)
        except Exception as e:
            flash(f'Search error: {str(e)}', 'error')
    
    return render_template('search.html', query=query, results=results)

@app.route('/jobs')
def job_search():
    """Job search page."""
    query = request.args.get('q', '').strip()
    location = request.args.get('location', '').strip()
    jobs = []
    error_message = None
    
    if query:
        try:
            job_service = get_job_service()
            jobs = job_service.search_jobs(query, location, limit=20)
        except Exception as e:
            error_message = f'Job search error: {str(e)}'
            flash(error_message, 'error')
    
    return render_template('jobs.html', 
                         query=query, 
                         location=location, 
                         jobs=jobs, 
                         error_message=error_message)

@app.route('/job/<job_id>')
def job_details(job_id):
    """View job details."""
    try:
        job_service = get_job_service()
        job = job_service.get_job_details(job_id)
        
        if not job:
            flash('Job not found', 'error')
            return redirect(url_for('job_search'))
        
        return render_template('job_details.html', job=job)
        
    except Exception as e:
        flash(f'Error loading job details: {str(e)}', 'error')
        return redirect(url_for('job_search'))

@app.route('/apply-from-job/<job_id>')
def apply_from_job(job_id):
    """Apply to a job from job search."""
    try:
        job_service = get_job_service()
        job = job_service.get_job_details(job_id)
        
        if not job:
            flash('Job not found', 'error')
            return redirect(url_for('job_search'))
        
        # Convert job posting to application data
        app_data = job_service.job_to_application_data(job)
        app_data['job_description'] = job.description
        
        return render_template('add_application.html', 
                             prefilled_data=app_data, 
                             from_job_search=True,
                             job=job,
                             all_statuses=list(ApplicationStatus))
        
    except Exception as e:
        flash(f'Error applying to job: {str(e)}', 'error')
        return redirect(url_for('job_search'))

@app.route('/analytics')
def analytics():
    """Show analytics and reports."""
    try:
        reporter = ApplicationReporter(tracker.applications)
        
        # Get various analytics
        response_analysis = reporter.analyze_response_rates()
        company_stats_raw = reporter.get_company_statistics()[:10]  # Top 10 companies
        weekly_summary_raw = reporter.generate_weekly_summary(weeks=8)
        stale_apps = reporter.identify_stale_applications(days=30)
        
        # Transform company stats from tuples to objects for template
        company_stats = []
        for company_name, app_count, status_breakdown in company_stats_raw:
            # Calculate response rate for this company
            responded = app_count - status_breakdown.get('applied', 0)
            response_rate = (responded / app_count * 100) if app_count > 0 else 0
            
            company_stats.append({
                'company': company_name,
                'count': app_count,
                'response_rate': response_rate,
                'status_breakdown': status_breakdown,
                'positions': [app.position for app in tracker.applications if app.company == company_name]
            })
        
        # Transform weekly summary for template
        weekly_summary = {}
        if 'weekly_breakdown' in weekly_summary_raw:
            for week_key, week_data in weekly_summary_raw['weekly_breakdown'].items():
                # Calculate response rate for this week
                week_apps = week_data['applications_count']
                week_applied = week_data['status_breakdown'].get('applied', 0)
                week_responded = week_apps - week_applied
                week_response_rate = (week_responded / week_apps * 100) if week_apps > 0 else 0
                
                weekly_summary[week_key] = {
                    'total': week_apps,
                    'responses': week_responded,
                    'response_rate': week_response_rate
                }
        
        return render_template('analytics.html',
                             response_analysis=response_analysis,
                             company_stats=company_stats,
                             weekly_summary=weekly_summary,
                             stale_apps=stale_apps)
    except Exception as e:
        flash(f'Error loading analytics: {str(e)}', 'error')
        return render_template('analytics.html',
                             response_analysis={},
                             company_stats=[],
                             weekly_summary={},
                             stale_apps=[])

@app.route('/api/summary')
def api_summary():
    """API endpoint for summary data."""
    try:
        summary = tracker.get_status_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/applications', methods=['GET'])
def api_applications():
    """API endpoint to get all applications."""
    try:
        applications = [app.to_dict() for app in tracker.applications]
        return jsonify({'applications': applications})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/applications', methods=['POST'])
def api_add_application():
    """API endpoint to add a new application."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        if not data.get('company') or not data.get('position'):
            return jsonify({'error': 'Company and position are required'}), 400
        
        # Create application
        app = Application(
            company=data['company'],
            position=data['position'],
            status=ApplicationStatus(data.get('status', 'applied')),
            job_url=data.get('job_url'),
            salary_range=data.get('salary_range'),
            location=data.get('location'),
            notes=data.get('notes'),
            contact_person=data.get('contact_person'),
            contact_email=data.get('contact_email'),
            job_posting_id=data.get('job_posting_id'),
            job_posting_source=data.get('job_posting_source'),
            job_description=data.get('job_description')
        )
        
        app_id = tracker.add_application(app)
        return jsonify({'success': True, 'application_id': app_id}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/applications/<app_id>', methods=['GET'])
def api_get_application(app_id):
    """API endpoint to get a specific application."""
    try:
        app = tracker.get_application(app_id)
        if not app:
            return jsonify({'error': 'Application not found'}), 404
        return jsonify(app.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/applications/<app_id>', methods=['PUT'])
def api_update_application(app_id):
    """API endpoint to update an application."""
    try:
        app = tracker.get_application(app_id)
        if not app:
            return jsonify({'error': 'Application not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Update application
        updates = {}
        if 'company' in data:
            updates['company'] = data['company']
        if 'position' in data:
            updates['position'] = data['position']
        if 'status' in data:
            updates['status'] = data['status']
        if 'job_url' in data:
            updates['job_url'] = data['job_url']
        if 'salary_range' in data:
            updates['salary_range'] = data['salary_range']
        if 'location' in data:
            updates['location'] = data['location']
        if 'notes' in data:
            updates['notes'] = data['notes']
        if 'contact_person' in data:
            updates['contact_person'] = data['contact_person']
        if 'contact_email' in data:
            updates['contact_email'] = data['contact_email']
        
        success = tracker.update_application(app_id, **updates)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to update application'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/applications/<app_id>', methods=['DELETE'])
def api_delete_application(app_id):
    """API endpoint to delete an application."""
    try:
        app = tracker.get_application(app_id)
        if not app:
            return jsonify({'error': 'Application not found'}), 404
        
        success = tracker.delete_application(app_id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to delete application'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/search', methods=['GET'])
def api_job_search():
    """API endpoint to search for jobs."""
    try:
        query = request.args.get('q', '').strip()
        location = request.args.get('location', '').strip()
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        job_service = get_job_service()
        jobs = job_service.search_jobs(query, location, limit)
        
        return jsonify({
            'jobs': [job.to_dict() for job in jobs],
            'count': len(jobs)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def api_status():
    """API endpoint to check job search API status."""
    try:
        job_service = get_job_service()
        status = job_service.get_api_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export')
def export_data():
    """Export applications as JSON."""
    try:
        data = [app.to_dict() for app in tracker.applications]
        
        # Create response
        response = app.response_class(
            response=json.dumps(data, indent=2, default=str),
            status=200,
            mimetype='application/json'
        )
        response.headers['Content-Disposition'] = f'attachment; filename=applications_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        return response
        
    except Exception as e:
        flash(f'Export error: {str(e)}', 'error')
        return redirect(url_for('applications'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    print("Starting Py-App-Tracker Web Interface...")
    print("Visit: http://127.0.0.1:9000")
    app.run(debug=True, host='127.0.0.1', port=9000)
