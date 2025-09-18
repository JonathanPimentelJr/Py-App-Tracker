#!/usr/bin/env python3
"""
API Setup Helper for Py-App-Tracker

This script helps you set up and test real job search APIs.
"""

import os
import sys
sys.path.insert(0, 'src')

from job_api import get_job_service, USAJobsAPI, AdzunaAPI
import webbrowser

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_step(step, description):
    print(f"\n🔸 Step {step}: {description}")

def test_usajobs_api():
    print_header("Testing USAJobs.gov API (Free)")
    
    try:
        api = USAJobsAPI()
        print("✅ USAJobs API initialized")
        
        # Test search
        print("🔍 Testing search for 'data analyst'...")
        jobs = api.search_jobs("data analyst", limit=3)
        
        if jobs:
            print(f"✅ Success! Found {len(jobs)} jobs")
            for job in jobs:
                print(f"  📝 {job.title} at {job.company}")
            return True
        else:
            print("⚠️  No jobs found, but API is working")
            return True
            
    except Exception as e:
        print(f"❌ USAJobs API test failed: {e}")
        print("💡 This is normal - USAJobs API has strict requirements")
        print("   It will work better with proper User-Agent headers")
        return False

def setup_adzuna_api():
    print_header("Setting up Adzuna API (Free Tier)")
    
    app_id = os.getenv('ADZUNA_APP_ID')
    api_key = os.getenv('ADZUNA_API_KEY')
    
    if app_id and api_key:
        print("✅ Adzuna credentials found in environment variables")
        try:
            api = AdzunaAPI()
            print("🔍 Testing Adzuna API...")
            jobs = api.search_jobs("software engineer", limit=2)
            
            if jobs:
                print(f"✅ Success! Found {len(jobs)} jobs")
                for job in jobs:
                    print(f"  📝 {job.title} at {job.company}")
                return True
            else:
                print("⚠️  No jobs found")
                return True
                
        except Exception as e:
            print(f"❌ Adzuna API test failed: {e}")
            return False
    else:
        print("❌ Adzuna API credentials not found")
        print("\n📋 To set up Adzuna API (FREE):")
        print_step(1, "Visit https://developer.adzuna.com/")
        print_step(2, "Create a free account")
        print_step(3, "Create a new application")
        print_step(4, "Get your App ID and API Key")
        print_step(5, "Set environment variables:")
        print("     export ADZUNA_APP_ID='your-app-id'")
        print("     export ADZUNA_API_KEY='your-api-key'")
        
        open_browser = input("\n🌐 Open Adzuna registration page? (y/n): ").strip().lower()
        if open_browser == 'y':
            webbrowser.open('https://developer.adzuna.com/')
            
        return False

def test_current_setup():
    print_header("Testing Current API Setup")
    
    service = get_job_service()
    status = service.get_api_status()
    
    print(f"📊 Total APIs configured: {status['total_apis']}")
    print(f"🔧 Current primary API: {status['current_api'] or 'None'}")
    
    print("\n📋 Available APIs:")
    for api in status['available_apis']:
        cost_color = "🟢" if api['cost'] == 'Free' else "🟡" if api['cost'] == 'Free Tier' else "🔴"
        print(f"  {cost_color} {api['name']}: {api['cost']} ({api['type']})")
    
    if status['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in status['recommendations']:
            print(f"  • {rec}")
    
    # Test job search
    print("\n🔍 Testing job search with current setup...")
    try:
        jobs = service.search_jobs("python developer", limit=3)
        print(f"✅ Found {len(jobs)} jobs")
        
        sources = set(job.source for job in jobs)
        print(f"📊 Job sources: {', '.join(sources)}")
        
        for job in jobs[:2]:  # Show first 2 jobs
            print(f"  📝 {job.title} at {job.company} ({job.source})")
            
    except Exception as e:
        print(f"❌ Job search test failed: {e}")

def main():
    print_header("🔍 Py-App-Tracker API Setup Helper")
    print("This tool will help you set up and test real job search APIs")
    
    # Test current setup
    test_current_setup()
    
    # Test USAJobs API
    usajobs_works = test_usajobs_api()
    
    # Setup/test Adzuna API
    adzuna_works = setup_adzuna_api()
    
    # Final summary
    print_header("📋 Setup Summary")
    
    if usajobs_works:
        print("✅ USAJobs.gov API: Working (Free)")
    else:
        print("⚠️  USAJobs.gov API: Needs configuration")
        
    if adzuna_works:
        print("✅ Adzuna API: Working (Free Tier)")
    else:
        print("❌ Adzuna API: Not configured")
    
    print(f"\n🎯 Next Steps:")
    
    if not adzuna_works:
        print("1. Set up Adzuna API for more job coverage (recommended)")
        print("2. Run this script again after setup")
    
    print("3. Start the web app: python web_app.py")
    print("4. Visit http://127.0.0.1:9000/jobs to search for jobs")
    
    if usajobs_works or adzuna_works:
        print("\n🎉 You have at least one real API working!")
        print("   Mock data will only be used as a fallback.")
    else:
        print("\n📝 Currently using mock data only.")
        print("   Set up at least one real API for actual job postings.")

if __name__ == "__main__":
    main()
