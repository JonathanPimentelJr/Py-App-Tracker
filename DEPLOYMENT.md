# 🚀 Deploy Py-App-Tracker

## Option 1: Railway (Recommended)

1. **Go to** https://railway.app/
2. **Login with GitHub**
3. **New Project** → **Deploy from GitHub repo**
4. **Select** `Py-App-Tracker` repository
5. **Add Environment Variables:**
   ```
   ADZUNA_APP_ID=your-app-id
   ADZUNA_API_KEY=your-api-key
   PORT=8000
   FLASK_ENV=production
   ```
6. **Deploy** - Railway auto-configures everything
7. **Access your app** at the provided URL

---

## Option 2: Render

1. **Go to** https://render.com/
2. **Sign up with GitHub**
3. **New** → **Web Service**
4. **Connect** `Py-App-Tracker` repository
5. **Configure:**
   ```
   Build Command: pip install -r requirements.txt
   Start Command: python app.py
   Plan: Free
   ```
6. **Environment Variables:**
   ```
   ADZUNA_APP_ID=your-app-id
   ADZUNA_API_KEY=your-api-key
   FLASK_ENV=production
   ```
7. **Create Web Service**
8. **Access your app** at `https://py-app-tracker.onrender.com`

---

## Option 3: Fly.io

1. **Install Fly CLI:**
   ```bash
   brew install flyctl
   ```
2. **Login:**
   ```bash
   fly auth login
   ```
3. **Deploy:**
   ```bash
   cd Py-App-Tracker
   fly launch --name py-app-tracker
   fly secrets set ADZUNA_APP_ID=your-app-id
   fly secrets set ADZUNA_API_KEY=your-api-key
   fly deploy
   ```

---

## Environment Variables

**For Real APIs:**
```
ADZUNA_APP_ID=your-app-id
ADZUNA_API_KEY=your-api-key
```

**Optional:**
```
USAJOBS_EMAIL=your-email@example.com
FLASK_ENV=production
```

**No variables = Mock data**

---

## Test Your Deployment

1. **Home:** `https://your-app-url.com/`
2. **Jobs:** `https://your-app-url.com/jobs`
3. **API Status:** `https://your-app-url.com/api/status`

Search "python developer" to verify real API data.

---

**✅ Files ready for deployment - just push and deploy!**
