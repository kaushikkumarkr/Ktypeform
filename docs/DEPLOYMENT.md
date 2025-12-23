# 🚀 KTypeform Deployment Guide (Free Tier)

This guide walks you through deploying KTypeform using **100% free tier** services.

## Services Used

| Component | Service | Free Tier Limits |
|-----------|---------|------------------|
| Backend | [Render](https://render.com) | 750 hrs/month |
| Frontend | [Vercel](https://vercel.com) | Unlimited |
| Database | [Neon](https://neon.tech) | 0.5 GB, 1 project |
| Storage | [Supabase](https://supabase.com) | 1 GB storage |

---

## Step 1: Set Up Neon PostgreSQL

1. Go to [neon.tech](https://neon.tech) and create account
2. Create new project → Choose region → Create
3. Copy connection string from dashboard:
   ```
   postgresql://user:password@host.neon.tech/neondb
   ```
4. Extract these values:
   - `POSTGRES_USER`: user
   - `POSTGRES_PASSWORD`: password
   - `POSTGRES_SERVER`: host.neon.tech
   - `POSTGRES_DB`: neondb

---

## Step 2: Set Up Supabase Storage

1. Go to [supabase.com](https://supabase.com) and create account
2. Create new project
3. Go to **Storage** → Create bucket named `submissions`
4. Set bucket to **Public**
5. Go to **Settings** → **API** and copy:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **Service Role Key** (under Service Role)

For S3 config:
- `MINIO_ENDPOINT`: `xxxxx.supabase.co/storage/v1/s3`
- `MINIO_SECURE`: `true`
- `MINIO_ROOT_USER`: Your project reference (from URL)
- `MINIO_ROOT_PASSWORD`: Service Role Key

---

## Step 3: Deploy Backend to Render

### 3.1 Push to GitHub
```bash
cd /path/to/Ktypeform
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/ktypeform.git
git push -u origin main
```

### 3.2 Create Render Service
1. Go to [render.com](https://render.com) → New → Web Service
2. Connect GitHub repo
3. Configure:
   - **Name**: `ktypeform-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Docker`
   - **Plan**: Free

### 3.3 Set Environment Variables
In Render dashboard, add these env vars:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Generate: `openssl rand -hex 32` |
| `POSTGRES_USER` | From Neon |
| `POSTGRES_PASSWORD` | From Neon |
| `POSTGRES_SERVER` | From Neon (e.g., `ep-xxx.neon.tech`) |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_DB` | From Neon (e.g., `neondb`) |
| `MINIO_ENDPOINT` | From Supabase |
| `MINIO_SECURE` | `true` |
| `MINIO_ROOT_USER` | Supabase project ref |
| `MINIO_ROOT_PASSWORD` | Supabase service role key |
| `GROQ_API_KEY` | Your Groq API key |

### 3.4 Deploy
Click **Create Web Service** → Wait for build (~5-10 min)

Note your backend URL: `https://ktypeform-backend.onrender.com`

---

## Step 4: Deploy Frontend to Vercel

### 4.1 Create Vercel Project
1. Go to [vercel.com](https://vercel.com) → New Project
2. Import from GitHub
3. Select **frontend** directory as root
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`

### 4.2 Set Environment Variables
| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://ktypeform-backend.onrender.com` |

### 4.3 Deploy
Click **Deploy** → Wait for build (~2-3 min)

Your app is now live! 🎉

---

## Step 5: Initialize Database

The database tables are created automatically on first backend startup.

To create the initial admin user, use the API:

```bash
curl -X POST https://ktypeform-backend.onrender.com/api/v1/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "your-secure-password"}'
```

---

## Troubleshooting

### Backend won't start
- Check Render logs for errors
- Verify all environment variables are set
- Ensure Neon database is accessible

### Storage uploads fail
- Verify Supabase bucket is public
- Check MINIO_* env vars are correct
- Confirm service role key (not anon key)

### Frontend can't reach backend
- Check NEXT_PUBLIC_API_URL is correct
- Ensure backend is deployed and running
- Check CORS settings

---

## Production Checklist

- [ ] Change `SECRET_KEY` to random value
- [ ] Set up custom domain (optional)
- [ ] Configure email (SMTP settings)
- [ ] Add Stripe key for payments (optional)
- [ ] Enable monitoring/logging

---

## Cost Summary

| Service | Monthly Cost |
|---------|-------------|
| Render (Backend) | $0 |
| Vercel (Frontend) | $0 |
| Neon (Database) | $0 |
| Supabase (Storage) | $0 |
| **Total** | **$0** |

> ⚠️ Free tiers have limits. For production traffic, consider paid plans.
