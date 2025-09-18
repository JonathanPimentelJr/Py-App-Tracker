"""
Command-line interface for the Application Tracker.

This module provides a comprehensive CLI for managing job applications.
"""

import argparse
import sys
from datetime import datetime, timedelta
from typing import Optional

try:
    from .models import Application, ApplicationStatus
    from .tracker import ApplicationTracker
except ImportError:
    from models import Application, ApplicationStatus
    from tracker import ApplicationTracker


class ApplicationCLI:
    """Command-line interface for the Application Tracker."""
    
    def __init__(self):
        self.tracker = ApplicationTracker()
        self.parser = self.create_parser()
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser with all commands."""
        parser = argparse.ArgumentParser(
            prog='app-tracker',
            description='Track and manage job applications',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  app-tracker add "Google" "Software Engineer" --location "Mountain View, CA"
  app-tracker list --status applied
  app-tracker update abc123 --status interviewed --notes "Great interview!"
  app-tracker search "engineer"
  app-tracker summary
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Add command
        add_parser = subparsers.add_parser('add', help='Add a new application')
        add_parser.add_argument('company', help='Company name')
        add_parser.add_argument('position', help='Position/job title')
        add_parser.add_argument('--status', choices=[s.value for s in ApplicationStatus],
                               default=ApplicationStatus.APPLIED.value, help='Application status')
        add_parser.add_argument('--url', help='Job posting URL')
        add_parser.add_argument('--salary', help='Salary range')
        add_parser.add_argument('--location', help='Job location')
        add_parser.add_argument('--notes', help='Additional notes')
        add_parser.add_argument('--contact-person', help='Contact person name')
        add_parser.add_argument('--contact-email', help='Contact person email')
        add_parser.add_argument('--date', help='Application date (YYYY-MM-DD)')
        
        # List command
        list_parser = subparsers.add_parser('list', help='List applications')
        list_parser.add_argument('--status', choices=[s.value for s in ApplicationStatus],
                                help='Filter by status')
        list_parser.add_argument('--company', help='Filter by company name')
        list_parser.add_argument('--limit', type=int, help='Limit number of results')
        list_parser.add_argument('--sort', choices=['company', 'position', 'application_date', 'updated_at'],
                                default='updated_at', help='Sort by field')
        list_parser.add_argument('--reverse', action='store_true', default=True,
                                help='Sort in reverse order')
        list_parser.add_argument('--no-reverse', dest='reverse', action='store_false',
                                help='Sort in ascending order')
        
        # Show command
        show_parser = subparsers.add_parser('show', help='Show detailed application info')
        show_parser.add_argument('app_id', help='Application ID')
        
        # Update command
        update_parser = subparsers.add_parser('update', help='Update an application')
        update_parser.add_argument('app_id', help='Application ID')
        update_parser.add_argument('--company', help='Company name')
        update_parser.add_argument('--position', help='Position/job title')
        update_parser.add_argument('--status', choices=[s.value for s in ApplicationStatus],
                                  help='Application status')
        update_parser.add_argument('--url', help='Job posting URL')
        update_parser.add_argument('--salary', help='Salary range')
        update_parser.add_argument('--location', help='Job location')
        update_parser.add_argument('--notes', help='Additional notes')
        update_parser.add_argument('--contact-person', help='Contact person name')
        update_parser.add_argument('--contact-email', help='Contact person email')
        
        # Delete command
        delete_parser = subparsers.add_parser('delete', help='Delete an application')
        delete_parser.add_argument('app_id', help='Application ID')
        delete_parser.add_argument('--yes', '-y', action='store_true',
                                  help='Skip confirmation prompt')
        
        # Search command
        search_parser = subparsers.add_parser('search', help='Search applications')
        search_parser.add_argument('query', help='Search query')
        
        # Summary command
        subparsers.add_parser('summary', help='Show application summary')
        
        # Recent command
        recent_parser = subparsers.add_parser('recent', help='Show recent applications')
        recent_parser.add_argument('--days', type=int, default=7,
                                  help='Number of days to look back (default: 7)')
        
        return parser
    
    def format_application_brief(self, app: Application) -> str:
        """Format application for brief listing."""
        status_color = self.get_status_color(app.status)
        date_str = app.application_date.strftime('%Y-%m-%d') if app.application_date else 'N/A'
        
        return (f"{app.id[:8]} | {app.company:<20} | {app.position:<25} | "
                f"{status_color}{app.status.value:<15}\033[0m | {date_str}")
    
    def format_application_detailed(self, app: Application) -> str:
        """Format application for detailed view."""
        lines = [
            f"ID: {app.id}",
            f"Company: {app.company}",
            f"Position: {app.position}",
            f"Status: {self.get_status_color(app.status)}{app.status.value}\033[0m",
            f"Application Date: {app.application_date.strftime('%Y-%m-%d %H:%M') if app.application_date else 'N/A'}",
            f"Created: {app.created_at.strftime('%Y-%m-%d %H:%M')}",
            f"Updated: {app.updated_at.strftime('%Y-%m-%d %H:%M')}",
        ]
        
        if app.job_url:
            lines.append(f"Job URL: {app.job_url}")
        if app.salary_range:
            lines.append(f"Salary Range: {app.salary_range}")
        if app.location:
            lines.append(f"Location: {app.location}")
        if app.contact_person:
            lines.append(f"Contact Person: {app.contact_person}")
        if app.contact_email:
            lines.append(f"Contact Email: {app.contact_email}")
        if app.notes:
            lines.append(f"Notes:\\n{app.notes}")
        
        return "\\n".join(lines)
    
    def get_status_color(self, status: ApplicationStatus) -> str:
        """Get ANSI color code for status."""
        color_map = {
            ApplicationStatus.APPLIED: "\\033[94m",  # Blue
            ApplicationStatus.SCREENING: "\\033[96m",  # Cyan
            ApplicationStatus.INTERVIEW_SCHEDULED: "\\033[93m",  # Yellow
            ApplicationStatus.INTERVIEWED: "\\033[95m",  # Magenta
            ApplicationStatus.OFFER_RECEIVED: "\\033[92m",  # Green
            ApplicationStatus.REJECTED: "\\033[91m",  # Red
            ApplicationStatus.WITHDRAWN: "\\033[90m",  # Gray
            ApplicationStatus.ACCEPTED: "\\033[92m",  # Bright Green
        }
        return color_map.get(status, "")
    
    def _find_application_by_id(self, app_id: str):
        """Find application by full or partial ID."""
        # Try exact match first
        app = self.tracker.get_application(app_id)
        if app:
            return app
        
        # Try partial match (for 8-character shortened IDs)
        matching_apps = [app for app in self.tracker.applications if app.id.startswith(app_id)]
        if len(matching_apps) == 1:
            return matching_apps[0]
        elif len(matching_apps) > 1:
            print(f"Ambiguous application ID '{app_id}'. Found {len(matching_apps)} matches:")
            for app in matching_apps[:5]:  # Show first 5 matches
                print(f"  {app.id[:8]} - {app.company} - {app.position}")
            return None
        
        return None
    
    def cmd_add(self, args):
        """Handle add command."""
        # Parse date if provided
        application_date = None
        if args.date:
            try:
                application_date = datetime.strptime(args.date, '%Y-%m-%d')
            except ValueError:
                print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD.")
                return 1
        
        # Create application
        app = Application(
            company=args.company,
            position=args.position,
            status=ApplicationStatus(args.status),
            application_date=application_date,
            job_url=args.url,
            salary_range=args.salary,
            location=args.location,
            notes=args.notes,
            contact_person=args.contact_person,
            contact_email=args.contact_email
        )
        
        app_id = self.tracker.add_application(app)
        print(f"Added application: {app_id[:8]} - {args.company} - {args.position}")
        return 0
    
    def cmd_list(self, args):
        """Handle list command."""
        status_filter = ApplicationStatus(args.status) if args.status else None
        
        applications = self.tracker.list_applications(
            status_filter=status_filter,
            company_filter=args.company,
            limit=args.limit,
            sort_by=args.sort,
            reverse=args.reverse
        )
        
        if not applications:
            print("No applications found.")
            return 0
        
        # Print header
        print(f"{'ID':<8} | {'Company':<20} | {'Position':<25} | {'Status':<15} | {'Date'}")
        print("-" * 80)
        
        # Print applications
        for app in applications:
            print(self.format_application_brief(app))
        
        print(f"\\nShowing {len(applications)} application(s)")
        return 0
    
    def cmd_show(self, args):
        """Handle show command."""
        # Try to find application by full ID or partial ID
        app = self._find_application_by_id(args.app_id)
        if not app:
            print(f"Application with ID '{args.app_id}' not found.")
            return 1
        
        print(self.format_application_detailed(app))
        return 0
    
    def cmd_update(self, args):
        """Handle update command."""
        # Prepare updates
        updates = {}
        for field in ['company', 'position', 'status', 'job_url', 'salary_range', 
                     'location', 'notes', 'contact_person', 'contact_email']:
            value = getattr(args, field.replace('_', ''), None) or getattr(args, field.replace('_', '_'), None)
            if value is not None:
                updates[field] = value
        
        if not updates:
            print("No updates provided.")
            return 1
        
        # Find the application first
        app = self._find_application_by_id(args.app_id)
        if not app:
            print(f"Application with ID '{args.app_id}' not found.")
            return 1
        
        success = self.tracker.update_application(app.id, **updates)
        if success:
            print(f"Updated application {app.id[:8]}")
            # Show updated application
            updated_app = self.tracker.get_application(app.id)
            if updated_app:
                print("\\n" + self.format_application_detailed(updated_app))
        else:
            print(f"Failed to update application.")
            return 1
        
        return 0
    
    def cmd_delete(self, args):
        """Handle delete command."""
        app = self._find_application_by_id(args.app_id)
        if not app:
            print(f"Application with ID '{args.app_id}' not found.")
            return 1
        
        # Confirm deletion unless --yes flag is used
        if not args.yes:
            print(f"Are you sure you want to delete this application?")
            print(self.format_application_detailed(app))
            response = input("\\nDelete? (y/N): ")
            if response.lower() != 'y':
                print("Deletion cancelled.")
                return 0
        
        success = self.tracker.delete_application(app.id)
        if success:
            print(f"Deleted application {app.id[:8]} - {app.company} - {app.position}")
        else:
            print(f"Failed to delete application.")
            return 1
        
        return 0
    
    def cmd_search(self, args):
        """Handle search command."""
        results = self.tracker.search_applications(args.query)
        
        if not results:
            print(f"No applications found matching '{args.query}'.")
            return 0
        
        # Print header
        print(f"Found {len(results)} application(s) matching '{args.query}':")
        print(f"{'ID':<8} | {'Company':<20} | {'Position':<25} | {'Status':<15} | {'Date'}")
        print("-" * 80)
        
        # Print applications
        for app in results:
            print(self.format_application_brief(app))
        
        return 0
    
    def cmd_summary(self, args):
        """Handle summary command."""
        summary = self.tracker.get_status_summary()
        total = len(self.tracker)
        
        print(f"Application Summary ({total} total):")
        print("-" * 30)
        
        for status in ApplicationStatus:
            count = summary[status.value]
            percentage = (count / total * 100) if total > 0 else 0
            color = self.get_status_color(status)
            print(f"{color}{status.value.replace('_', ' ').title():<20}\\033[0m: {count:>3} ({percentage:5.1f}%)")
        
        return 0
    
    def cmd_recent(self, args):
        """Handle recent command."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)
        
        recent_apps = self.tracker.get_applications_by_date_range(start_date, end_date)
        recent_apps.sort(key=lambda app: app.application_date or datetime.min, reverse=True)
        
        if not recent_apps:
            print(f"No applications found in the last {args.days} days.")
            return 0
        
        print(f"Applications from the last {args.days} days:")
        print(f"{'ID':<8} | {'Company':<20} | {'Position':<25} | {'Status':<15} | {'Date'}")
        print("-" * 80)
        
        for app in recent_apps:
            print(self.format_application_brief(app))
        
        print(f"\\nShowing {len(recent_apps)} recent application(s)")
        return 0
    
    def run(self, args=None):
        """Run the CLI with the given arguments."""
        try:
            parsed_args = self.parser.parse_args(args)
            
            if parsed_args.command is None:
                self.parser.print_help()
                return 1
            
            # Call the appropriate command handler
            handler_name = f"cmd_{parsed_args.command}"
            handler = getattr(self, handler_name, None)
            
            if handler:
                return handler(parsed_args)
            else:
                print(f"Unknown command: {parsed_args.command}")
                return 1
                
        except KeyboardInterrupt:
            print("\\nOperation cancelled.")
            return 1
        except Exception as e:
            print(f"Error: {e}")
            return 1


def main():
    """Main entry point for the CLI."""
    cli = ApplicationCLI()
    exit_code = cli.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
