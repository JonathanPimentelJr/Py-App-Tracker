# 🔑 API Registration Guide

Use this information when registering for job search APIs.

## 📋 Project Information

**Project Name:** Py-App-Tracker  
**Website URL:** https://jonathanpimenteljr.github.io/Py-App-Tracker/  
**GitHub Repository:** https://github.com/JonathanPimentelJr/Py-App-Tracker  
**Description:** Professional Job Application Management System with API Integration  
**Category:** Productivity / Career Tools  
**License:** MIT License  

---

## 🌍 Adzuna API Registration

### Registration Link
🔗 **https://developer.adzuna.com/**

### Registration Details
- **Application Name:** `Py-App-Tracker`
- **Website:** `https://jonathanpimenteljr.github.io/Py-App-Tracker/`
- **Description:** `Open-source job application tracking system that helps users manage their job search process with analytics and insights.`
- **Purpose:** `Educational/Personal Project`
- **Category:** `Job Search / Career Tools`
- **Expected Usage:** `Up to 1000 API calls per month`

### After Registration
1. Get your **App ID** and **API Key**
2. Set environment variables:
   ```bash
   export ADZUNA_APP_ID="your-app-id"
   export ADZUNA_API_KEY="your-api-key"
   ```
3. Test with: `python setup_apis.py`

---

## 🇺🇸 USAJobs.gov API

### Registration Link
🔗 **https://developer.usajobs.gov/**

### Registration Details
- **Application Name:** `Py-App-Tracker`
- **Website:** `https://jonathanpimenteljr.github.io/Py-App-Tracker/`
- **Description:** `Job application management system for tracking government job applications`
- **Contact Email:** `your-email@example.com`

### After Registration
1. Get your **API Key**
2. Set environment variable:
   ```bash
   export USAJOBS_API_KEY="your-api-key"
   export USAJOBS_EMAIL="your-email@example.com"
   ```

---

## 🔧 RapidAPI (JSearch)

### Registration Link
🔗 **https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch/**

### Registration Details
- **Application Name:** `Py-App-Tracker`
- **Website:** `https://jonathanpimenteljr.github.io/Py-App-Tracker/`
- **Description:** `Job application tracking system with comprehensive job search capabilities`
- **Plan:** Start with free tier

### After Registration
1. Subscribe to JSearch API (free tier available)
2. Get your **RapidAPI Key**
3. Set environment variable:
   ```bash
   export RAPIDAPI_KEY="your-rapidapi-key"
   ```

---

## ✅ Verification Steps

After setting up APIs:

1. **Test APIs:**
   ```bash
   python setup_apis.py
   ```

2. **Check API Status:**
   ```bash
   curl http://localhost:9000/api/status
   ```

3. **Test Job Search:**
   - Start the web app: `python web_app.py`
   - Visit: http://localhost:9000/jobs
   - Search for "python developer"

---

## 🚨 Common Issues

### GitHub Pages Not Working
- Go to GitHub → Settings → Pages
- Select "main" branch and "/docs" folder
- Wait 2-3 minutes for deployment

### API Registration Rejected
- Use GitHub repository URL as backup
- Ensure website shows professional content
- Contact API support if needed

### Environment Variables Not Loading
```bash
# Add to ~/.zshrc or ~/.bashrc
export ADZUNA_APP_ID="your-app-id"
export ADZUNA_API_KEY="your-api-key"
source ~/.zshrc  # or ~/.bashrc
```

---

## 📞 Support

- **GitHub Issues:** https://github.com/JonathanPimentelJr/Py-App-Tracker/issues
- **Documentation:** https://github.com/JonathanPimentelJr/Py-App-Tracker/blob/main/API_SETUP.md
- **Website:** https://jonathanpimenteljr.github.io/Py-App-Tracker/

---

**✅ Ready to register!** Use the information above for any API registrations.
