# Files to Upload to Hugging Face Space

## Required Files (Must Upload)

### 1. Dockerfile
```
Location: deploy/backend/Dockerfile
Purpose: Tells Hugging Face how to build and run your app
```

### 2. requirements.txt
```
Location: backend/requirements.txt
Purpose: Python dependencies (includes email-validator for Pydantic)
```

### 3. src/ folder (Complete)
```
Location: backend/src/
Purpose: All your application code
Upload entire folder with all subfolders:
- src/main.py
- src/config.py
- src/database.py
- src/api/
- src/models/
- src/services/
- src/agents/
- src/schemas/
- src/middleware/
- src/core/
- src/mcp/ (if exists)
```

### 4. .gitignore (Optional but recommended)
```
Create new file in Hugging Face Space
Content:
__pycache__/
*.pyc
.env
.env.local
venv/
.pytest_cache/
*.log
.DS_Store
```

## Files NOT to Upload

### ❌ Don't Upload These:
- `.env` (contains secrets - use HF Secrets instead)
- `.env.local`
- `__pycache__/` folders
- `*.pyc` files
- `venv/` or `env/` folders
- `.pytest_cache/`
- `*.log` files
- `.DS_Store`
- `node_modules/` (if any)
- Test files (optional, can skip)
- `alembic/` (if you have migrations)

## File Structure in Hugging Face Space

Your Space should look like this:

```
your-space/
├── Dockerfile                 ← From deploy/backend/
├── requirements.txt           ← From backend/
├── .gitignore                ← Create new
├── README.md                 ← Optional (HF auto-creates)
└── src/                      ← From backend/src/
    ├── __init__.py
    ├── main.py
    ├── config.py
    ├── database.py
    ├── api/
    │   ├── __init__.py
    │   ├── auth.py
    │   ├── chat.py
    │   ├── tasks.py
    │   └── ...
    ├── models/
    │   ├── __init__.py
    │   ├── user.py
    │   ├── task.py
    │   └── ...
    ├── services/
    │   ├── __init__.py
    │   ├── task_service.py
    │   ├── chat_service.py
    │   └── ...
    ├── agents/
    │   ├── __init__.py
    │   ├── groq_assistant.py
    │   ├── tool_executors.py
    │   └── ...
    ├── schemas/
    │   ├── __init__.py
    │   ├── task.py
    │   └── ...
    ├── middleware/
    │   ├── __init__.py
    │   └── auth.py
    └── core/
        ├── __init__.py
        ├── config.py
        └── database.py
```

## Quick Upload Commands

### Method 1: Git Clone and Copy

```bash
# 1. Clone your Hugging Face Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
cd YOUR_SPACE_NAME

# 2. Copy Dockerfile
cp ../path/to/deploy/backend/Dockerfile .

# 3. Copy requirements.txt
cp ../path/to/backend/requirements.txt .

# 4. Copy src folder
cp -r ../path/to/backend/src .

# 5. Create .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.env
.env.local
venv/
.pytest_cache/
*.log
.DS_Store
EOF

# 6. Commit and push
git add .
git commit -m "Initial deployment"
git push
```

### Method 2: Web Upload

1. Go to your Space: `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`
2. Click "Files" tab
3. Click "Add file" > "Upload files"
4. Upload these files:
   - `Dockerfile` (from deploy/backend/)
   - `requirements.txt` (from backend/)
5. Click "Add file" > "Create a new file"
   - Name: `.gitignore`
   - Paste content from above
6. Upload `src/` folder:
   - Click "Add file" > "Upload files"
   - Select entire `src` folder from backend/
   - Or upload files one by one

## Environment Variables (Secrets)

Don't upload these in files! Add as Secrets in HF Space Settings:

```bash
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...
GROQ_API_KEY=...
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

## Verification Checklist

After uploading, verify:

- ✅ Dockerfile exists in root
- ✅ requirements.txt exists in root
- ✅ src/ folder exists with all subfolders
- ✅ .gitignore exists
- ✅ No .env file uploaded
- ✅ All Secrets added in HF Settings
- ✅ Space is building (check Logs tab)

## Common Issues

### Issue: "ModuleNotFoundError"
**Solution**: Check requirements.txt includes all dependencies

### Issue: "No such file or directory: src/main.py"
**Solution**: Ensure src/ folder structure is correct

### Issue: "Port 7860 already in use"
**Solution**: Dockerfile should use port 7860 (HF default)

### Issue: "Database connection failed"
**Solution**: Check DATABASE_URL in Secrets

## File Sizes

Hugging Face Limits:
- Individual file: 50MB max
- Total Space: 50GB max (free tier)
- Git LFS for files > 10MB

Your backend should be well under these limits (~50MB total).

## Next Steps After Upload

1. Wait for build to complete (5-10 minutes)
2. Check Logs tab for errors
3. Test API: `https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/docs`
4. Update frontend NEXT_PUBLIC_API_URL
5. Test end-to-end

## Quick Reference

**What to upload:**
- ✅ Dockerfile
- ✅ requirements.txt
- ✅ src/ (entire folder)
- ✅ .gitignore

**What NOT to upload:**
- ❌ .env
- ❌ __pycache__
- ❌ venv/
- ❌ *.pyc

**Where to add secrets:**
- 🔐 Hugging Face Space Settings > Variables and Secrets
