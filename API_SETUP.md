# 🔍 Job Search API Configuration Guide

This guide will help you set up **free job search APIs** for your Py-App-Tracker application.

## 📋 Available Free APIs

### 1. 🇺🇸 USAJobs.gov API (100% Free)
- **Cost**: Completely free
- **Coverage**: US Government jobs only
- **Setup**: No registration required!
- **Rate Limits**: Very generous

**Setup:**
```bash
# Optional: Set your email for better API etiquette
export USAJOBS_EMAIL="your-email@example.com"
```

### 2. 🌍 Adzuna API (Free Tier)
- **Cost**: Free tier with 1000 calls/month
- **Coverage**: Jobs worldwide (US, UK, Canada, etc.)
- **Setup**: Requires free registration
- **Rate Limits**: 1000 requests/month

**Setup Steps:**
1. Visit [Adzuna Developer Portal](https://developer.adzuna.com/)
2. Create a free account
3. Create an app to get your credentials
4. Set environment variables:

```bash
export ADZUNA_APP_ID="your-app-id"
export ADZUNA_API_KEY="your-api-key"
```

### 3. 🔧 Mock API (Always Available)
- **Cost**: Free (built-in)
- **Coverage**: Sample data for testing
- **Setup**: No configuration needed
- **Rate Limits**: None

## 🚀 Quick Start

### Option 1: No Setup (Uses Free APIs Automatically)
```bash
# Just run the app - it will automatically use USAJobs.gov
python web_app.py
```

### Option 2: Add Adzuna for More Jobs
```bash
# Set up Adzuna API (after registration)
export ADZUNA_APP_ID="your-app-id-here"
export ADZUNA_API_KEY="your-api-key-here"

# Run the app
python web_app.py
```

### Option 3: Environment File (.env)
Create a `.env` file in your project root:

```env
# Free APIs
USAJOBS_EMAIL=your-email@example.com
ADZUNA_APP_ID=your-app-id
ADZUNA_API_KEY=your-api-key

# Optional: RapidAPI (paid) 
# RAPIDAPI_KEY=your-rapidapi-key
```

## 🔍 API Comparison

| API | Cost | Jobs/Month | Coverage | Registration |
|-----|------|------------|----------|-------------|
| **USAJobs.gov** | 100% Free | Unlimited | US Gov Jobs | None ✅ |
| **Adzuna** | Free Tier | 1,000 searches | Global | Required |
| **JSearch (RapidAPI)** | $10+/month | 1,000+ | Global | Required |
| **Mock Data** | Free | Unlimited | Sample | None ✅ |

## 🛠️ How It Works

The application will automatically:

1. **Try USAJobs.gov first** (always available, completely free)
2. **Try Adzuna** (if configured)
3. **Try JSearch** (if configured and paid)
4. **Fall back to Mock data** (if all else fails)

## 📊 Check API Status

Visit `/api/status` in your browser to see which APIs are active:
```
http://localhost:9000/api/status
```

## 🎯 Recommended Setup for Maximum Jobs

### For US Job Seekers:
```bash
export USAJOBS_EMAIL="your-email@example.com"
export ADZUNA_APP_ID="your-app-id"
export ADZUNA_API_KEY="your-api-key"
```

### For International Job Seekers:
```bash
export ADZUNA_APP_ID="your-app-id"  
export ADZUNA_API_KEY="your-api-key"
# Note: USAJobs will still work but only shows US government positions
```

## 🔧 Troubleshooting

### No Jobs Found?
1. Check your API credentials are set correctly
2. Try a simpler search term (e.g., "developer" instead of "senior full stack developer")
3. Check the browser console for error messages

### API Not Working?
1. Check your internet connection
2. Verify API credentials are valid
3. Check if you've exceeded rate limits (wait an hour and try again)

### Getting Mock Data Only?
This means no external APIs are configured. The app will show sample jobs for demonstration.

## 🆓 Why These APIs Are Great

- **USAJobs.gov**: Official US government API, completely free, well-maintained
- **Adzuna**: Aggregates jobs from major job boards, generous free tier
- **No vendor lock-in**: Easy to add/remove APIs as needed
- **Automatic fallbacks**: If one API is down, others keep working

## 🔮 Future APIs (Coming Soon)

We're working on adding:
- **RemoteOK API** (remote jobs)
- **AngelList API** (startup jobs)  
- **Stack Overflow Jobs** (tech jobs)
- **Web scraping fallbacks** for popular job sites

## 💡 Tips

1. **Start with USAJobs.gov** - it's completely free and requires no setup
2. **Add Adzuna** for broader coverage (1000 free searches/month is plenty for most users)
3. **Use specific keywords** for better results ("Python developer" vs "developer")
4. **Monitor your usage** - most free tiers are quite generous

---

**Need Help?** 
- Check the logs in your terminal for detailed error messages
- Open an issue on GitHub if you're stuck
- The app will always fall back to mock data, so it never completely breaks

**Happy Job Hunting!** 🎯
