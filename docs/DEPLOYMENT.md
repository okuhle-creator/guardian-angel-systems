# Guardian Angel Systems (GAS) — Production Deployment Guide
## Target: Vercel (Frontend) + Render (Backend) + Neon (PostgreSQL Database)

---

## 10-Step Production Deployment Checklist

### Step 1: Push Repository to GitHub
```bash
git add .
git commit -m "Guardian Angel Systems (GAS) Production-Ready Architecture"
git remote add origin https://github.com/YOUR_ORGANISATION/guardian-angel-systems.git
git branch -M main
git push -u origin main
```

### Step 2: Create Neon PostgreSQL Database
1. Navigate to [https://neon.tech](https://neon.tech) and create a free project named `guardian-angel-db`.
2. Copy the Connection String URI:
   `postgresql://neondb_owner:YOUR_PASSWORD@ep-sample-123456.us-east-2.aws.neon.tech/neondb?sslmode=require`

### Step 3: Configure Render Backend
1. Sign in to [https://render.com](https://render.com).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Set the following parameters:
   - **Name**: `guardian-angel-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 4: Set Production Environment Variables on Render
Add the following in Render Dashboard -> Environment:
- `ENVIRONMENT`: `production`
- `PROJECT_NAME`: `Guardian Angel Systems (GAS)`
- `SECRET_KEY`: `<Generate a random 64-char string>`
- `DATABASE_URL`: `<Paste your Neon PostgreSQL connection string>`
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `1440`

### Step 5: Initialize Production Tables
On startup, FastAPI automatically registers all SQLAlchemy tables into Neon PostgreSQL via `Base.metadata.create_all(bind=engine)` and seeds the default analyst credentials and threat intelligence indicators.

### Step 6: Deploy Frontend to Vercel
1. Sign in to [https://vercel.com](https://vercel.com).
2. Click **Add New...** -> **Project**.
3. Import your GitHub repository.
4. Configure Project:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### Step 7: Configure Frontend Environment Variable on Vercel
In Vercel -> Settings -> Environment Variables, add:
- `VITE_API_BASE_URL`: `https://guardian-angel-backend.onrender.com`
Click **Deploy**.

### Step 8: Configure Backend CORS
In Render, your backend's `CORS_ORIGINS` already permits wildcard and `https://*.vercel.app`. If you have a custom domain, add it to `CORS_ORIGINS`.

### Step 9: Verify Health Check Endpoints
Open:
`https://guardian-angel-backend.onrender.com/api/v1/health`
Verify JSON response:
```json
{
  "status": "HEALTHY",
  "platform": "Guardian Angel Systems (GAS)",
  "mode": "production",
  "database": "CONNECTED"
}
```

### Step 10: Verify the Live Application
1. Open your Vercel URL: `https://guardian-angel-systems.vercel.app`.
2. Observe all 9 navigation modules.
3. Click **Run Demo Scenario -> Scenario A: Phishing & Credential Compromise**.
4. Observe real-time correlated incidents, MITRE ATT&CK mappings, and human approval queue.
5. Authorize an action in Response Centre and execute simulated response.
6. Check Audit Centre and click **Verify Cryptographic Chain** to verify end-to-end ledger integrity.
