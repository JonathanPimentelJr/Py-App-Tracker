#!/bin/bash

echo "🔍 Py-App-Tracker API Environment Setup"
echo "======================================"
echo

# Check if .env file exists
if [ -f .env ]; then
    echo "📄 Found existing .env file"
    echo "Current environment variables:"
    cat .env | grep -E "(ADZUNA|USAJOBS|RAPIDAPI)" | sed 's/=.*/=***/' || echo "   No API keys configured yet"
    echo
else
    echo "📝 Creating new .env file"
    touch .env
fi

echo "🌍 Setting up Adzuna API (Recommended - Free Tier)"
echo "----------------------------------------"
echo "Adzuna provides 1,000 free API calls per month"
echo "Sign up at: https://developer.adzuna.com/"
echo

read -p "Do you have Adzuna API credentials? (y/n): " has_adzuna

if [ "$has_adzuna" = "y" ] || [ "$has_adzuna" = "Y" ]; then
    read -p "Enter your Adzuna App ID: " adzuna_id
    read -p "Enter your Adzuna API Key: " adzuna_key
    
    # Remove existing Adzuna entries
    grep -v "ADZUNA" .env > .env.tmp && mv .env.tmp .env
    
    # Add new entries
    echo "ADZUNA_APP_ID=$adzuna_id" >> .env
    echo "ADZUNA_API_KEY=$adzuna_key" >> .env
    
    echo "✅ Adzuna API credentials saved to .env"
else
    echo "📋 To get Adzuna API credentials:"
    echo "1. Visit https://developer.adzuna.com/"
    echo "2. Create a free account"
    echo "3. Create a new application"
    echo "4. Get your App ID and API Key"
    echo "5. Run this script again"
fi

echo
echo "📧 Setting up USAJobs.gov API (Optional)"
echo "---------------------------------------"
echo "USAJobs.gov API is free but has restrictions"

read -p "Enter your email for USAJobs API (or press Enter to skip): " usajobs_email

if [ ! -z "$usajobs_email" ]; then
    # Remove existing USAJobs entry
    grep -v "USAJOBS_EMAIL" .env > .env.tmp && mv .env.tmp .env
    
    # Add new entry
    echo "USAJOBS_EMAIL=$usajobs_email" >> .env
    
    echo "✅ USAJobs email saved to .env"
fi

echo
echo "🔑 RapidAPI Setup (Optional - Paid)"
echo "-----------------------------------"
echo "RapidAPI provides access to JSearch API (paid service)"

read -p "Do you have a RapidAPI key for JSearch? (y/n): " has_rapidapi

if [ "$has_rapidapi" = "y" ] || [ "$has_rapidapi" = "Y" ]; then
    read -p "Enter your RapidAPI key: " rapidapi_key
    
    # Remove existing RapidAPI entry
    grep -v "RAPIDAPI_KEY" .env > .env.tmp && mv .env.tmp .env
    
    # Add new entry
    echo "RAPIDAPI_KEY=$rapidapi_key" >> .env
    
    echo "✅ RapidAPI key saved to .env"
fi

echo
echo "📄 Final .env file contents:"
echo "=============================="
cat .env | grep -E "(ADZUNA|USAJOBS|RAPIDAPI)" | sed 's/=.*/=***/' || echo "No API keys configured"

echo
echo "🚀 Next Steps:"
echo "=============="
echo "1. Load environment variables: source .env"
echo "2. Test APIs: python setup_apis.py"
echo "3. Start the web app: python web_app.py"
echo "4. Visit http://127.0.0.1:9000/jobs to search for jobs"

echo
if [ -f .env ] && grep -q "ADZUNA_APP_ID" .env; then
    echo "🎉 You're ready to use real job APIs!"
else
    echo "📝 Currently using mock data only."
    echo "   Sign up for Adzuna API for real job postings."
fi
