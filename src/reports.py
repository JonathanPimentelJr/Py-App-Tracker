"""
Advanced reporting and analytics for the Application Tracker.

This module provides additional reporting capabilities and analytics for job applications.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any
from collections import defaultdict, Counter

try:
    from .models import Application, ApplicationStatus
except ImportError:
    from models import Application, ApplicationStatus


class ApplicationReporter:
    """Advanced reporting and analytics for job applications."""
    
    def __init__(self, applications: List[Application]):
        self.applications = applications
    
    def generate_weekly_summary(self, weeks: int = 4) -> Dict[str, Any]:
        """
        Generate a weekly summary of application activity.
        
        Args:
            weeks: Number of weeks to analyze
            
        Returns:
            Dictionary containing weekly summary data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=weeks)
        
        # Filter applications within date range
        relevant_apps = [
            app for app in self.applications
            if app.application_date and start_date <= app.application_date <= end_date
        ]
        
        # Group by week
        weekly_data = defaultdict(list)
        for app in relevant_apps:
            # Get the start of the week (Monday)
            week_start = app.application_date - timedelta(days=app.application_date.weekday())
            week_key = week_start.strftime('%Y-%m-%d')
            weekly_data[week_key].append(app)
        
        # Calculate weekly statistics
        weekly_stats = {}
        for week_key, week_apps in weekly_data.items():
            weekly_stats[week_key] = {
                'applications_count': len(week_apps),
                'companies': list(set(app.company for app in week_apps)),
                'status_breakdown': dict(Counter(app.status.value for app in week_apps))
            }
        
        return {
            'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            'total_applications': len(relevant_apps),
            'weekly_breakdown': weekly_stats,
            'average_per_week': len(relevant_apps) / weeks if weeks > 0 else 0
        }
    
    def analyze_response_rates(self) -> Dict[str, Any]:
        """
        Analyze response rates and conversion metrics.
        
        Returns:
            Dictionary containing response rate analysis
        """
        total_applied = len([app for app in self.applications if app.status == ApplicationStatus.APPLIED])
        total_screening = len([app for app in self.applications if app.status == ApplicationStatus.SCREENING])
        total_interviewed = len([app for app in self.applications 
                               if app.status in [ApplicationStatus.INTERVIEW_SCHEDULED, ApplicationStatus.INTERVIEWED]])
        total_offers = len([app for app in self.applications if app.status == ApplicationStatus.OFFER_RECEIVED])
        total_rejected = len([app for app in self.applications if app.status == ApplicationStatus.REJECTED])
        total_accepted = len([app for app in self.applications if app.status == ApplicationStatus.ACCEPTED])
        
        total_apps = len(self.applications)
        
        if total_apps == 0:
            return {
                'total_applications': 0,
                'response_rate': 0,
                'interview_rate': 0,
                'offer_rate': 0,
                'acceptance_rate': 0,
                'rejection_rate': 0
            }
        
        return {
            'total_applications': total_apps,
            'response_rate': (total_apps - total_applied) / total_apps * 100,
            'interview_rate': total_interviewed / total_apps * 100,
            'offer_rate': total_offers / total_apps * 100,
            'acceptance_rate': total_accepted / total_apps * 100,
            'rejection_rate': total_rejected / total_apps * 100,
            'breakdown': {
                'applied': total_applied,
                'screening': total_screening,
                'interviewed': total_interviewed,
                'offers': total_offers,
                'rejected': total_rejected,
                'accepted': total_accepted
            }
        }
    
    def get_company_statistics(self) -> List[Tuple[str, int, Dict[str, int]]]:
        """
        Get statistics grouped by company.
        
        Returns:
            List of tuples (company_name, application_count, status_breakdown)
        """
        company_stats = defaultdict(list)
        for app in self.applications:
            company_stats[app.company].append(app)
        
        result = []
        for company, apps in company_stats.items():
            status_breakdown = dict(Counter(app.status.value for app in apps))
            result.append((company, len(apps), status_breakdown))
        
        # Sort by application count (descending)
        result.sort(key=lambda x: x[1], reverse=True)
        return result
    
    def identify_stale_applications(self, days: int = 30) -> List[Application]:
        """
        Identify applications that haven't been updated recently.
        
        Args:
            days: Number of days to consider as stale
            
        Returns:
            List of stale applications
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        stale_apps = [
            app for app in self.applications
            if (app.updated_at < cutoff_date and 
                app.status not in [ApplicationStatus.REJECTED, ApplicationStatus.ACCEPTED, ApplicationStatus.WITHDRAWN])
        ]
        
        return sorted(stale_apps, key=lambda app: app.updated_at)
    
    def get_application_timeline(self, app_id: str) -> Dict[str, Any]:
        """
        Get a timeline view of a specific application.
        
        Args:
            app_id: Application ID
            
        Returns:
            Dictionary containing timeline information
        """
        app = next((a for a in self.applications if a.id == app_id), None)
        if not app:
            return None
        
        timeline = [
            {
                'date': app.created_at,
                'event': 'Application Created',
                'status': app.status.value,
                'details': f"Applied to {app.company} for {app.position}"
            }
        ]
        
        if app.application_date and app.application_date != app.created_at:
            timeline.append({
                'date': app.application_date,
                'event': 'Application Submitted',
                'status': 'applied',
                'details': f"Submitted application to {app.company}"
            })
        
        if app.updated_at != app.created_at:
            timeline.append({
                'date': app.updated_at,
                'event': 'Status Updated',
                'status': app.status.value,
                'details': f"Status changed to {app.status.value}"
            })
        
        timeline.sort(key=lambda x: x['date'])
        return {
            'application': app,
            'timeline': timeline,
            'duration_days': (datetime.now() - app.created_at).days
        }
    
    def generate_monthly_trends(self, months: int = 6) -> Dict[str, Any]:
        """
        Generate monthly trend analysis.
        
        Args:
            months: Number of months to analyze
            
        Returns:
            Dictionary containing monthly trends
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        # Filter applications within date range
        relevant_apps = [
            app for app in self.applications
            if app.application_date and start_date <= app.application_date <= end_date
        ]
        
        # Group by month
        monthly_data = defaultdict(list)
        for app in relevant_apps:
            month_key = app.application_date.strftime('%Y-%m')
            monthly_data[month_key].append(app)
        
        # Calculate monthly statistics
        monthly_stats = {}
        for month_key, month_apps in monthly_data.items():
            monthly_stats[month_key] = {
                'applications_count': len(month_apps),
                'unique_companies': len(set(app.company for app in month_apps)),
                'status_breakdown': dict(Counter(app.status.value for app in month_apps)),
                'top_companies': [company for company, count in 
                                Counter(app.company for app in month_apps).most_common(3)]
            }
        
        return {
            'period': f"{start_date.strftime('%Y-%m')} to {end_date.strftime('%Y-%m')}",
            'total_applications': len(relevant_apps),
            'monthly_breakdown': monthly_stats,
            'average_per_month': len(relevant_apps) / months if months > 0 else 0
        }
    
    def export_summary_report(self) -> str:
        """
        Generate a comprehensive text summary report.
        
        Returns:
            Formatted string report
        """
        if not self.applications:
            return "No applications found."
        
        lines = []
        lines.append("APPLICATION TRACKER SUMMARY REPORT")
        lines.append("=" * 40)
        lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Basic statistics
        total_apps = len(self.applications)
        lines.append(f"Total Applications: {total_apps}")
        
        # Status breakdown
        status_counts = Counter(app.status.value for app in self.applications)
        lines.append("")
        lines.append("Status Breakdown:")
        for status in ApplicationStatus:
            count = status_counts.get(status.value, 0)
            percentage = (count / total_apps * 100) if total_apps > 0 else 0
            lines.append(f"  {status.value.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
        
        # Response rate analysis
        response_analysis = self.analyze_response_rates()
        lines.append("")
        lines.append("Response Rate Analysis:")
        lines.append(f"  Response Rate: {response_analysis['response_rate']:.1f}%")
        lines.append(f"  Interview Rate: {response_analysis['interview_rate']:.1f}%")
        lines.append(f"  Offer Rate: {response_analysis['offer_rate']:.1f}%")
        
        # Company statistics (top 5)
        company_stats = self.get_company_statistics()[:5]
        lines.append("")
        lines.append("Top Companies (by application count):")
        for company, count, _ in company_stats:
            lines.append(f"  {company}: {count} applications")
        
        # Recent activity
        recent_apps = [app for app in self.applications 
                      if (datetime.now() - app.created_at).days <= 7]
        lines.append("")
        lines.append(f"Recent Activity (last 7 days): {len(recent_apps)} applications")
        
        # Stale applications
        stale_apps = self.identify_stale_applications()
        lines.append(f"Stale Applications (>30 days): {len(stale_apps)} applications")
        
        return "\\n".join(lines)
