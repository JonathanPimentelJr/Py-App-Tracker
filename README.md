# Py-App-Tracker 📋

A Python-based command-line application tracker for managing job applications. Keep track of your job search progress, application statuses, and important details all from your terminal.

## Features ✨

- **Complete Application Management**: Add, view, update, and delete job applications
- **Status Tracking**: Track applications through various stages (Applied, Screening, Interview, Offer, etc.)
- **Search & Filter**: Find applications by company, position, status, or date range
- **Rich Reporting**: Generate summaries, analytics, and progress reports
- **Data Persistence**: JSON-based storage with automatic backup
- **Command-Line Interface**: Intuitive CLI with colored output and formatting
- **Web Interface**: Modern, responsive web interface with Bootstrap styling
- **Data Validation**: Built-in validation for emails, URLs, and data integrity

## Quick Start 🚀

### Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Make the main script executable (optional):
   ```bash
   chmod +x app_tracker.py
   ```

### Basic Usage

**Command Line Interface:**
```bash
# Add a new application
python3 app_tracker.py add "Google" "Software Engineer" --location "Mountain View, CA" --salary "$120k-150k"

# List all applications
python3 app_tracker.py list

# Show application summary
python3 app_tracker.py summary

# Search for applications
python3 app_tracker.py search "engineer"

# Update application status
python3 app_tracker.py update abc12345 --status interviewed --notes "Great technical interview"
```

**Web Interface:**
```bash
# Install Flask (first time only)
pip install Flask

# Start the web server
python3 web_app.py

# Open your browser to http://127.0.0.1:5000
```

The web interface provides:
- 📊 **Dashboard** with visual summaries and recent activity
- 📝 **Easy Forms** for adding and editing applications
- 🔍 **Advanced Search** with highlighting
- 📱 **Responsive Design** that works on mobile devices
- ⚡ **Real-time Updates** and status tracking

## Command Reference 📖

### Adding Applications

```bash
# Basic application
python3 app_tracker.py add "Company Name" "Job Title"

# Application with full details
python3 app_tracker.py add "TechCorp" "Senior Developer" \\
  --status applied \\
  --url "https://techcorp.com/jobs/123" \\
  --salary "$100k-130k" \\
  --location "San Francisco, CA" \\
  --contact-person "Jane Smith" \\
  --contact-email "jane.smith@techcorp.com" \\
  --notes "Applied through referral" \\
  --date "2024-01-15"
```

### Viewing Applications

```bash
# List all applications
python3 app_tracker.py list

# Filter by status
python3 app_tracker.py list --status applied
python3 app_tracker.py list --status interviewed

# Filter by company
python3 app_tracker.py list --company "Google"

# Sort and limit results
python3 app_tracker.py list --sort company --limit 10 --no-reverse

# Show detailed information
python3 app_tracker.py show abc12345
```

### Updating Applications

```bash
# Update status
python3 app_tracker.py update abc12345 --status screening

# Update multiple fields
python3 app_tracker.py update abc12345 \\
  --status interviewed \\
  --notes "Phone screening completed. Technical interview scheduled." \\
  --contact-person "John Doe"
```

### Searching and Filtering

```bash
# Search across all fields
python3 app_tracker.py search "python developer"

# Show recent applications (last 7 days)
python3 app_tracker.py recent

# Show recent applications (custom timeframe)
python3 app_tracker.py recent --days 14
```

### Reports and Analytics

```bash
# Show application summary
python3 app_tracker.py summary

# This displays:
# - Total applications
# - Status breakdown with percentages
# - Color-coded status indicators
```

### Deleting Applications

```bash
# Delete with confirmation
python3 app_tracker.py delete abc12345

# Delete without confirmation
python3 app_tracker.py delete abc12345 --yes
```

## Application Statuses 📊

The tracker supports the following application statuses:

- **applied**: Initial application submitted
- **screening**: Initial screening or phone interview
- **interview_scheduled**: Interview has been scheduled
- **interviewed**: Interview completed, awaiting results
- **offer_received**: Job offer received
- **rejected**: Application rejected
- **withdrawn**: Application withdrawn by you
- **accepted**: Offer accepted

## Data Storage 💾

- Applications are stored in `data/applications.json`
- Data is automatically saved after each operation
- The JSON format makes it easy to backup or migrate data
- No external database required

## Advanced Features 🔧

### Application IDs

Each application gets a unique UUID. For convenience, you can use the first 8 characters of the ID in commands:

```bash
# Full ID
python3 app_tracker.py show 12345678-1234-1234-1234-123456789012

# Short ID (first 8 characters)
python3 app_tracker.py show 12345678
```

### Color-Coded Output

The CLI uses colors to make information easier to read:
- 🔵 **Blue**: Applied
- 🔷 **Cyan**: Screening  
- 🟡 **Yellow**: Interview Scheduled
- 🟣 **Magenta**: Interviewed
- 🟢 **Green**: Offer Received / Accepted
- 🔴 **Red**: Rejected
- ⚫ **Gray**: Withdrawn

### Data Validation

The application includes comprehensive data validation:
- Email format validation
- URL format validation
- Date format validation (YYYY-MM-DD)
- Field length limits
- Required field checking

## File Structure 📁

```
Py-App-Tracker/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── models.py            # Data models (Application, ApplicationStatus)
│   ├── tracker.py           # Main ApplicationTracker class
│   ├── cli.py              # Command-line interface
│   ├── validators.py        # Data validation utilities
│   └── reports.py           # Advanced reporting features
├── templates/
│   ├── base.html           # Base template with navigation
│   ├── index.html          # Dashboard with summaries
│   ├── applications.html   # Application listing with filters
│   ├── add_application.html # Add new application form
│   ├── edit_application.html # Edit application form
│   ├── view_application.html # Detailed application view
│   └── search.html         # Search interface with highlighting
├── data/
│   └── applications.json    # Application data storage
├── tests/
│   └── (test files)
├── venv/                    # Python virtual environment
├── app_tracker.py          # CLI executable script
├── web_app.py              # Flask web application
├── requirements.txt         # Dependencies (Flask for web interface)
└── README.md               # This file
```

## Examples 💡

### Job Search Workflow

```bash
# 1. Add applications as you apply
python3 app_tracker.py add "Startup Inc" "Full Stack Developer" \\
  --url "https://startup.com/careers" \\
  --salary "$90k-120k"

# 2. Update status as you progress
python3 app_tracker.py update abc12345 --status screening
python3 app_tracker.py update abc12345 --status interview_scheduled \\
  --notes "Technical interview on Friday 2pm"

# 3. Track your progress
python3 app_tracker.py summary
python3 app_tracker.py recent --days 7

# 4. Find specific applications
python3 app_tracker.py search "full stack"
python3 app_tracker.py list --status interviewed
```

### Bulk Management

```bash
# List all pending applications (not rejected/accepted)
python3 app_tracker.py list --status applied
python3 app_tracker.py list --status screening
python3 app_tracker.py list --status interviewed

# Find applications by company
python3 app_tracker.py list --company "Google"
python3 app_tracker.py search "FAANG"
```

## Tips & Best Practices 💪

1. **Regular Updates**: Update application statuses promptly to maintain accurate tracking
2. **Detailed Notes**: Use the notes field to track interview feedback, next steps, and important details
3. **Consistent Naming**: Use consistent company names and position titles for better organization
4. **Regular Reviews**: Use `summary` and `recent` commands to review your application pipeline
5. **Data Backup**: Periodically backup your `data/applications.json` file

## Troubleshooting 🔧

### Common Issues

**"Application not found" errors:**
- Make sure you're using the correct application ID
- Try using the full ID instead of the shortened version
- Use `python3 app_tracker.py list` to see all application IDs

**Permission errors:**
- Make sure you have write permissions in the project directory
- The `data/` directory will be created automatically if it doesn't exist

**Date format errors:**
- Use YYYY-MM-DD format for dates (e.g., "2024-01-15")
- Dates are optional for most operations

## Requirements 📋

- Python 3.7 or higher
- No external dependencies (uses only Python standard library)
- Terminal with color support (recommended)

## Development 🛠️

To extend or modify the application:

1. **Virtual Environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

2. **Code Structure**: The application uses a modular design with separate modules for models, data handling, CLI, and validation.

3. **Adding Features**: New commands can be added to `src/cli.py`, and new data fields can be added to the `Application` model in `src/models.py`.

### Web Interface Deployment

For production deployment of the web interface:

1. **Production Server**: Use a WSGI server like Gunicorn
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 web_app:app
   ```

2. **Environment Variables**: Set production configurations
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-secure-secret-key
   ```

3. **Reverse Proxy**: Use Nginx or Apache for static files and SSL

4. **Process Management**: Use systemd, supervisor, or Docker for process management

## License 📄

This project is open source. Feel free to modify and distribute as needed.

## Contributing 🤝

Contributions are welcome! Please feel free to submit issues, suggestions, or pull requests.

---

Happy job hunting! 🎯
