# 🚂 Railway Deployment Guide

Quick setup for deploying KTypeform on Railway (100% free tier).

## Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub

## Step 2: Create New Project
1. Click **New Project** → **Deploy from GitHub repo**
2. Select `kaushikkumarkr/Ktypeform`
3. Railway will detect the monorepo

## Step 3: Add PostgreSQL
1. In your project, click **New** → **Database** → **PostgreSQL**
2. Railway auto-configures `DATABASE_URL`

## Step 4: Configure Backend Service
1. Click on the backend service
2. Go to **Settings** → **General**
3. Set **Root Directory**: `backend`
4. Go to **Variables** and add:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | Generate: `openssl rand -hex 32` |
| `POSTGRES_USER` | `${{ PGUSER }}` (Railway variable) |
| `POSTGRES_PASSWORD` | `${{ PGPASSWORD }}` |
| `POSTGRES_SERVER` | `${{ PGHOST }}` |
| `POSTGRES_PORT` | `${{ PGPORT }}` |
| `POSTGRES_DB` | `${{ PGDATABASE }}` |
| `GROQ_API_KEY` | Your Groq API key |
| `MINIO_ENDPOINT` | Leave empty for now |

## Step 5: Configure Frontend Service  
1. Click **New** → **Deploy from GitHub repo** (same repo)
2. Set **Root Directory**: `frontend`
3. Add variable:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | Copy from backend service URL |

## Step 6: Generate Public URLs
1. For each service, go to **Settings** → **Networking**
2. Click **Generate Domain**

## Done! 🎉
Your app is now live on Railway.

---

## GitHub Actions (Optional)

To auto-deploy on push:
1. Go to [railway.app/account/tokens](https://railway.app/account/tokens)
2. Create token
3. Add to GitHub: **Repo → Settings → Secrets → Actions**
   - Name: `RAILWAY_TOKEN`
   - Value: Your token

The workflow in `.github/workflows/railway-backend.yml` will auto-deploy.
