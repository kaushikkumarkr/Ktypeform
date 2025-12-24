# 🚀 Free Stack Deployment Guide

Deploy KTypeform with **100% free services** - no credit card required!

## Stack Overview

| Component | Service | Free Limit |
|-----------|---------|------------|
| Frontend | **Vercel** | Unlimited |
| Backend | **Render** | 750 hrs/month |
| Database | **Neon** | 0.5 GB PostgreSQL |
| Storage | **Cloudflare R2** | 10 GB + free egress |

---

## Step 1: Neon PostgreSQL

1. Go to [neon.tech](https://neon.tech) → Sign up
2. Create project → Copy connection details:
   - `POSTGRES_USER`
   - `POSTGRES_PASSWORD`  
   - `POSTGRES_SERVER` (e.g., `ep-xxx.us-east-2.aws.neon.tech`)
   - `POSTGRES_DB` (usually `neondb`)

---

## Step 2: Cloudflare R2

1. Go to [dash.cloudflare.com](https://dash.cloudflare.com) → Sign up
2. Go to **R2 Object Storage** → **Create bucket**
3. Name: `submissions`
4. Go to **Manage R2 API Tokens** → Create token with read/write
5. Copy:
   - **Account ID** (from URL or overview)
   - **Access Key ID**
   - **Secret Access Key**
   - **Endpoint**: `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`

---

## Step 3: Render Backend

1. Go to [render.com](https://render.com) → Sign up with GitHub
2. **New** → **Web Service** → Connect `kaushikkumarkr/Ktypeform`
3. Settings:
   - **Root Directory**: `backend`
   - **Environment**: Docker
   - **Plan**: Free

4. Add Environment Variables:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | `openssl rand -hex 32` (run locally) |
| `POSTGRES_USER` | From Neon |
| `POSTGRES_PASSWORD` | From Neon |
| `POSTGRES_SERVER` | From Neon |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_DB` | From Neon |
| `MINIO_ENDPOINT` | `<ACCOUNT_ID>.r2.cloudflarestorage.com` |
| `MINIO_SECURE` | `true` |
| `MINIO_ROOT_USER` | R2 Access Key ID |
| `MINIO_ROOT_PASSWORD` | R2 Secret Access Key |
| `GROQ_API_KEY` | Your Groq key |

5. Click **Create Web Service** → Wait for deploy (~5-10 min)
6. Copy your backend URL: `https://xxx.onrender.com`

---

## Step 4: Vercel Frontend

1. Go to [vercel.com](https://vercel.com) → Sign up with GitHub
2. **New Project** → Import `kaushikkumarkr/Ktypeform`
3. Settings:
   - **Root Directory**: `frontend`
   - **Framework**: Next.js

4. Add Environment Variable:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | Your Render backend URL |

5. Click **Deploy** → Wait (~2-3 min)

---

## Step 5: Create Admin User

```bash
curl -X POST https://YOUR-BACKEND.onrender.com/api/v1/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@yourcompany.com", "password": "your-secure-password"}'
```

---

## ✅ Done!

Your app is live at your Vercel URL!

| Service | Monthly Cost |
|---------|-------------|
| Vercel | $0 |
| Render | $0 |
| Neon | $0 |
| Cloudflare R2 | $0 |
| **Total** | **$0** |

---

## Troubleshooting

**Backend won't start**: Check Render logs, verify all env vars
**PDF upload fails**: Verify R2 bucket exists and API token has write access
**Frontend 401 errors**: Check `NEXT_PUBLIC_API_URL` is correct
