#!/usr/bin/env python3
"""
Py-App-Tracker API Setup Wizard

This script helps you set up real job search APIs step by step.
"""

import os
import sys
import webbrowser
import time
from pathlib import Path

sys.path.insert(0, 'src')

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_step(step, description):
    print(f"\n🔸 Step {step}: {description}")

def check_website():
    print_header("🌐 Checking Website Status")
    website_url = "https://jonathanpimenteljr.github.io/Py-App-Tracker/"
    
    try:
        import requests
        response = requests.get(website_url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Website is live: {website_url}")
            return True
        else:
            print(f"❌ Website returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot reach website: {e}")
        print("💡 Your website might still be deploying. Wait a few minutes and try again.")
        return False

def setup_environment_file():
    print_header("📝 Environment File Setup")
    
    env_file = Path('.env')
    if env_file.exists():
        print("Found existing .env file:")
        with open(env_file, 'r') as f:
            content = f.read()
            # Show masked credentials
            for line in content.split('\n'):
                if '=' in line and any(key in line for key in ['API', 'KEY']):
                    key, value = line.split('=', 1)
                    print(f"  {key}=***")
                elif line.strip():
                    print(f"  {line}")
    else:
        print("No .env file found. Creating one...")
        env_file.touch()
    
    return env_file

def setup_adzuna_api():
    print_header("🌍 Adzuna API Setup (FREE)")
    
    print("Adzuna provides 1,000 FREE API calls per month - perfect for job searching!")
    print("\n📋 Registration Information:")
    print(f"• Website: https://jonathanpimenteljr.github.io/Py-App-Tracker/")
    print(f"• App Name: Py-App-Tracker")
    print(f"• Description: Job application tracking system")
    print(f"• Purpose: Educational/Personal Project")
    
    choice = input("\n🚀 Ready to register for Adzuna API? (y/n): ").strip().lower()
    
    if choice == 'y':
        print("\n🌐 Opening Adzuna registration page...")
        webbrowser.open('https://developer.adzuna.com/')
        print("\n📋 Follow these steps in your browser:")
        print("1. Click 'Get API Key' or 'Sign Up'")
        print("2. Create an account (free)")
        print("3. Create a new application with the details above")
        print("4. Get your App ID and API Key")
        
        input("\nPress Enter when you have your credentials...")
        
        app_id = input("Enter your Adzuna App ID: ").strip()
        api_key = input("Enter your Adzuna API Key: ").strip()
        
        if app_id and api_key:
            # Save to .env file
            env_lines = []
            env_file = Path('.env')
            
            if env_file.exists():
                with open(env_file, 'r') as f:
                    env_lines = [line.strip() for line in f.readlines()]
            
            # Remove existing Adzuna entries
            env_lines = [line for line in env_lines if not line.startswith('ADZUNA_')]
            
            # Add new entries
            env_lines.append(f"ADZUNA_APP_ID={app_id}")
            env_lines.append(f"ADZUNA_API_KEY={api_key}")
            
            # Write back to file
            with open(env_file, 'w') as f:
                f.write('\n'.join(env_lines) + '\n')
            
            print("✅ Adzuna credentials saved to .env file")
            
            # Set environment variables for current session
            os.environ['ADZUNA_APP_ID'] = app_id
            os.environ['ADZUNA_API_KEY'] = api_key
            
            return True
        else:
            print("❌ No credentials provided. You can set them up later.")
            return False
    else:
        print("⏭️  Skipping Adzuna setup for now")
        return False

def test_apis():
    print_header("🧪 Testing APIs")
    
    try:
        from job_api import get_job_service
        
        service = get_job_service()
        status = service.get_api_status()
        
        print(f"📊 Total APIs configured: {status['total_apis']}")
        print(f"🔧 Current primary API: {status['current_api'] or 'None'}")
        
        print("\n📋 Available APIs:")
        for api in status['available_apis']:
            cost_color = "🟢" if api['cost'] == 'Free' else "🟡" if api['cost'] == 'Free Tier' else "🔴"
            print(f"  {cost_color} {api['name']}: {api['cost']} ({api['type']})")
        
        # Test job search
        print("\n🔍 Testing job search...")
        jobs = service.search_jobs("python developer", limit=3)
        
        if jobs:
            print(f"✅ Success! Found {len(jobs)} jobs")
            
            sources = set(job.source for job in jobs)
            print(f"📊 Job sources: {', '.join(sources)}")
            
            # Check if we're using real APIs
            real_sources = [s for s in sources if s != 'Mock']
            if real_sources:
                print(f"🎉 Using real APIs: {', '.join(real_sources)}")
            else:
                print("📝 Currently using mock data (no real APIs configured)")
                
            print("\n📄 Sample jobs:")
            for job in jobs[:2]:
                print(f"  • {job.title} at {job.company} ({job.source})")
        else:
            print("❌ No jobs found")
            
        return len([api for api in status['available_apis'] if api['type'] == 'External']) > 0
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    print_header("🎯 Py-App-Tracker API Setup Wizard")
    print("This wizard will help you set up real job search APIs step by step.")
    
    # Step 1: Check website
    website_ok = check_website()
    if not website_ok:
        print("\n❌ Website is not accessible. Please wait a few minutes for GitHub Pages to deploy.")
        print("   Then run this script again.")
        return
    
    # Step 2: Setup environment file
    env_file = setup_environment_file()
    
    # Step 3: Setup Adzuna API
    adzuna_ok = setup_adzuna_api()
    
    # Step 4: Test APIs
    has_real_apis = test_apis()
    
    # Final summary
    print_header("📋 Setup Summary")
    
    if website_ok:
        print("✅ Website: Live and accessible")
    else:
        print("❌ Website: Not accessible")
    
    if adzuna_ok:
        print("✅ Adzuna API: Configured")
    else:
        print("⏭️  Adzuna API: Not configured (optional)")
    
    if has_real_apis:
        print("✅ Real APIs: Working!")
    else:
        print("📝 Real APIs: Using mock data (set up APIs above)")
    
    print(f"\n🎯 Next Steps:")
    
    if not adzuna_ok:
        print("1. 📋 Register for Adzuna API (recommended - free 1000 calls/month)")
        print("   Run this script again after registration")
    
    print("2. 🚀 Start the web app:")
    print("   python web_app.py")
    
    print("3. 🔍 Test job search:")
    print("   Visit http://127.0.0.1:9000/jobs")
    
    if has_real_apis:
        print("\n🎉 Congratulations! You now have real job search APIs working!")
        print("   Your application will show actual job postings from real job boards!")
    else:
        print("\n📝 Currently using mock data for demonstration.")
        print("   Set up at least one real API for actual job postings.")
    
    print(f"\n💡 Pro Tip: Run 'python setup_apis.py' anytime to check API status")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup wizard cancelled. You can run it again anytime!")
    except Exception as e:
        print(f"\n❌ Setup wizard error: {e}")
        print("💡 Try running 'python setup_apis.py' for basic testing")
