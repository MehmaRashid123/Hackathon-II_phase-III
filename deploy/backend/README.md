# Backend Deployment to Hugging Face Spaces

## Prerequisites

1. **Hugging Face Account**: Create account at https://huggingface.co
2. **PostgreSQL Database**: Get a managed database from:
   - [Neon](https://neon.tech) - Free tier available
   - [Supabase](https://supabase.com) - Free tier available
   - [Railway](https://railway.app) - Free tier available
   - [ElephantSQL](https://www.elephantsql.com) - Free tier available

3. **Groq API Key**: Get free API key from https://console.groq.com

## Step 1: Prepare Database

### Option A: Neon (Recommended)
1. Go to https://neon.tech
2. Sign up and create a new project
3. Copy the connection string (looks like: `postgresql://user:pass@host/db`)
4. Database will auto-create tables on first run

### Option B: Supabase
1. Go to https://supabase.com
2. Create new project
3. Go to Settings > Database
4. Copy the connection string
5. Enable "Use connection pooling" for better performance

## Step 2: Create Hugging Face Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Fill in details:
   - **Space name**: `your-username/taskmanager-api`
   - **License**: MIT
   - **SDK**: Docker
   - **Hardware**: CPU Basic (Free)
   - **Visibility**: Public or Private

## Step 3: Configure Space

### Add Secrets (Environment Variables)

Go to Space Settings > Variables and Secrets, add these:

```bash
# Required
DATABASE_URL=postgresql://user:password@host:5432/dbname
BETTER_AUTH_SECRET=generate-a-random-32-char-string
GROQ_API_KEY=your-groq-api-key
CORS_ORIGINS=https://your-vercel-app.vercel.app

# Optional
GROQ_MODEL=llama-3.1-8b-instant
GROQ_MAX_TOKENS=4000
GROQ_TEMPERATURE=0.7
API_HOST=0.0.0.0
API_PORT=7860
ENVIRONMENT=production
```

### Generate BETTER_AUTH_SECRET
```bash
# On Linux/Mac
openssl rand -base64 32

# On Windows (PowerShell)
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))

# Or use online generator
# https://generate-secret.vercel.app/32
```

## Step 4: Upload Files

### Method A: Git (Recommended)

1. Clone your Space:
```bash
git clone https://huggingface.co/spaces/your-username/taskmanager-api
cd taskmanager-api
```

2. Copy backend files:
```bash
# Copy from your project
cp -r ../../backend/* .
cp ../backend/Dockerfile .
```

3. Create `.gitignore`:
```bash
echo "__pycache__/
*.pyc
.env
.env.local
venv/
.pytest_cache/" > .gitignore
```

4. Commit and push:
```bash
git add .
git commit -m "Initial deployment"
git push
```

### Method B: Web Upload

1. Go to your Space page
2. Click "Files" tab
3. Upload these files from `backend/` folder:
   - `Dockerfile` (from deploy/backend/)
   - `requirements.txt`
   - `src/` folder (entire folder)
   - Any other necessary files

## Step 5: Verify Deployment

1. Wait for Space to build (5-10 minutes)
2. Check logs for errors
3. Test endpoints:

```bash
# Health check
curl https://your-username-taskmanager-api.hf.space/health

# API docs
https://your-username-taskmanager-api.hf.space/docs
```

## Step 6: Update Frontend

Update your Vercel environment variables:

```bash
NEXT_PUBLIC_API_URL=https://your-username-taskmanager-api.hf.space
```

## Troubleshooting

### Issue: "Connection refused"
- Check if DATABASE_URL is correct
- Verify database is accessible from internet
- Check Hugging Face logs

### Issue: "CORS error"
- Add your Vercel URL to CORS_ORIGINS
- Format: `https://your-app.vercel.app` (no trailing slash)

### Issue: "Module not found"
- Check requirements.txt includes all dependencies
- Rebuild Space

### Issue: "Database tables not found"
- Tables auto-create on first request
- Or run migrations manually in Space terminal

## Monitoring

### View Logs
1. Go to your Space
2. Click "Logs" tab
3. Monitor real-time logs

### Check Status
```bash
# API health
curl https://your-space.hf.space/health

# Database connection
curl https://your-space.hf.space/api/health
```

## Scaling

### Free Tier Limits
- CPU Basic: Always free
- Sleeps after 48h inactivity
- Wakes up on first request (cold start ~30s)

### Upgrade Options
- CPU Upgrade: $0.03/hour
- GPU: For AI workloads
- Persistent Storage: For file uploads

## Security Checklist

- ✅ Use environment variables for secrets
- ✅ Enable HTTPS (automatic on HF)
- ✅ Set strong BETTER_AUTH_SECRET
- ✅ Restrict CORS_ORIGINS
- ✅ Use managed database with SSL
- ✅ Keep dependencies updated

## Backup

### Database Backup
```bash
# Neon: Automatic daily backups
# Supabase: Automatic backups
# Manual backup:
pg_dump $DATABASE_URL > backup.sql
```

### Code Backup
- Git repository on Hugging Face
- Keep local copy
- Optional: Mirror to GitHub

## Updates

### Deploy Updates
```bash
# Make changes locally
git add .
git commit -m "Update: description"
git push

# Space will auto-rebuild
```

### Zero-Downtime Updates
- Hugging Face handles this automatically
- Old version serves until new one is ready

## Cost Estimate

### Free Tier (Recommended for MVP)
- Hugging Face: $0/month (CPU Basic)
- Neon Database: $0/month (Free tier)
- Groq API: $0/month (Free tier)
- **Total: $0/month**

### Production Tier
- Hugging Face: ~$22/month (CPU Upgrade)
- Neon Database: $19/month (Pro)
- Groq API: $0/month (still free)
- **Total: ~$41/month**

## Support

- Hugging Face Docs: https://huggingface.co/docs/hub/spaces
- Community Forum: https://discuss.huggingface.co
- Discord: https://discord.gg/hugging-face

## Next Steps

1. ✅ Deploy backend to Hugging Face
2. ✅ Deploy frontend to Vercel (see frontend README)
3. ✅ Test end-to-end
4. ✅ Set up monitoring
5. ✅ Configure custom domain (optional)
