# 🚀 BACKEND DEPLOYMENT GUIDE

## ✅ YOU DON'T NEED AWS!

Your Docker Compose stack is production-ready. Here are the best deployment options:

---

## 🎯 RECOMMENDED: DigitalOcean App Platform

**Cost:** ~$12/month
**Setup Time:** 10 minutes

### Steps:
1. Push code to GitHub
2. Go to https://cloud.digitalocean.com/apps
3. Click "Create App" → Connect GitHub repo
4. Configure:
   - **API Service:** Dockerfile, port 8000
   - **Scanner:** `python -m src.scanner.main --interval 3600`
   - **Database:** Managed PostgreSQL ($15/mo) or Dev DB ($7/mo)
5. Add environment variables from `.env`
6. Click "Launch"

**Pros:**
- Auto-scaling
- Built-in PostgreSQL
- Automatic SSL/HTTPS
- GitHub auto-deploy

---

## 💚 OPTION 2: Render.com (FREE TIER!)

**Cost:** $0 - $25/month
**Setup Time:** 15 minutes

### Steps:
1. Push to GitHub
2. Go to https://render.com
3. Create services:
   - **Web Service:** FastAPI app
   - **Background Worker:** Scanner
   - **PostgreSQL:** Free tier (expires after 90 days)
4. Add environment variables
5. Deploy

**Free tier limits:**
- Spins down after 15 min inactivity
- 750 hours/month free

---

## ⚡ OPTION 3: Railway.app

**Cost:** $5/month (500 hours included)
**Setup Time:** 5 minutes

### Steps:
1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Railway auto-detects Docker Compose!
4. Add environment variables
5. Deploy

**Pros:**
- Easiest setup
- Supports Docker Compose natively
- Free $5 credit/month

---

## 🐳 OPTION 4: VPS (DigitalOcean Droplet, Linode, etc.)

**Cost:** $6/month
**Setup Time:** 30 minutes

### Steps:
1. Create Ubuntu 22.04 droplet ($6/mo)
2. SSH into server:
   ```bash
   ssh root@your-server-ip
   ```
3. Install Docker:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```
4. Clone repo:
   ```bash
   git clone https://github.com/yourusername/cheapflights.git
   cd cheapflights
   ```
5. Create `.env` file with your API keys
6. Launch:
   ```bash
   docker-compose up -d
   ```
7. Configure Nginx reverse proxy for HTTPS

---

## 📱 CONNECTING WEBSITE TO BACKEND

### Current Issue:
Website form submits to `/api/subscribe` (doesn't exist locally)

### Fix:

**Option A: Same Domain (Recommended)**
- Deploy backend to `api.fareglitch.com`
- Update `script.js`:
  ```javascript
  const response = await fetch('https://api.fareglitch.com/api/subscribe', {
  ```

**Option B: CORS Proxy**
- Keep website on `fareglitch.com`
- Backend on `fareglitch-api.onrender.com`
- Already configured CORS in `src/api/main.py`

### Update Required in `script.js`:
```javascript
// Line 37-41
const response = await fetch('https://YOUR-BACKEND-URL/api/subscribe', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ phone: phoneNumber })
});
```

---

## 🔧 LOCAL TESTING

Start entire stack locally:
```bash
docker-compose up
```

Access:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: localhost:5432

---

## 📊 DATABASE INITIALIZATION

Run once to create tables:
```bash
docker-compose exec api python -c "from src.models.database import init_db; init_db()"
```

Or use Alembic migrations:
```bash
docker-compose exec api alembic upgrade head
```

---

## 🎯 RECOMMENDATION

**For MVP Launch:**
1. **Railway.app** (easiest) or **Render.com** (free)
2. Deploy backend
3. Get API URL (e.g., `https://fareglitch-api.up.railway.app`)
4. Update `website/script.js` line 37 with your API URL
5. Deploy website to Netlify/Vercel (free)

**Total Cost:** $0-5/month

**When you have paying users:**
- Upgrade to DigitalOcean App Platform ($12-25/mo)
- Add managed PostgreSQL ($7-15/mo)
- Scale as needed

---

## ⚠️ CRITICAL: API Keys Required

Before deploying, you MUST set up:
1. ✅ Amadeus API (free test account)
2. ✅ HubSpot API (free)
3. ✅ Sinch SMS (pay-as-you-go)

Without these, the backend will crash on startup!
