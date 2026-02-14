# Frontend Deployment to Vercel

## Prerequisites

1. **Vercel Account**: Create account at https://vercel.com
2. **GitHub Account**: For connecting repository
3. **Backend URL**: Your Hugging Face Space URL (deploy backend first)

## Step 1: Prepare Repository

### Option A: Deploy from GitHub (Recommended)

1. Push your code to GitHub:
```bash
cd frontend
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/taskmanager-frontend.git
git push -u origin main
```

### Option B: Deploy from Local (Vercel CLI)

```bash
npm install -g vercel
cd frontend
vercel
```

## Step 2: Deploy to Vercel

### Via Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Click "Add New" > "Project"
3. Import your GitHub repository
4. Configure project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `./` (or `frontend` if monorepo)
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`

## Step 3: Configure Environment Variables

In Vercel Dashboard > Settings > Environment Variables, add:

### Required Variables

```bash
# Backend API URL (from Hugging Face Space)
NEXT_PUBLIC_API_URL=https://your-username-taskmanager-api.hf.space

# App URL (your Vercel URL)
NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
```

### Optional Variables

```bash
# Google Analytics (optional)
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX

# Sentry Error Tracking (optional)
NEXT_PUBLIC_SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

## Step 4: Deploy

1. Click "Deploy"
2. Wait for build to complete (2-5 minutes)
3. Get your deployment URL: `https://your-app.vercel.app`

## Step 5: Update Backend CORS

Update your Hugging Face Space environment variables:

```bash
CORS_ORIGINS=https://your-app.vercel.app
```

Redeploy backend if needed.

## Step 6: Test Deployment

1. Visit your Vercel URL
2. Try to sign up/login
3. Create a task
4. Test all features

## Custom Domain (Optional)

### Add Custom Domain

1. Go to Vercel Dashboard > Settings > Domains
2. Add your domain: `taskmanager.yourdomain.com`
3. Follow DNS configuration instructions
4. Update environment variables:

```bash
NEXT_PUBLIC_APP_URL=https://taskmanager.yourdomain.com
```

5. Update backend CORS:
```bash
CORS_ORIGINS=https://taskmanager.yourdomain.com
```

## Vercel Configuration Files

### vercel.json (Optional)
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "regions": ["iad1"]
}
```

### .vercelignore (Optional)
```
node_modules
.next
.env.local
.env
*.log
```

## Environment-Specific Builds

### Production
```bash
NEXT_PUBLIC_API_URL=https://your-space.hf.space
```

### Preview (for PR branches)
```bash
NEXT_PUBLIC_API_URL=https://your-space-dev.hf.space
```

### Development
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Automatic Deployments

### Production Branch
- Push to `main` → Auto-deploy to production
- URL: `https://your-app.vercel.app`

### Preview Branches
- Push to any branch → Auto-deploy preview
- URL: `https://your-app-git-branch.vercel.app`

### Pull Requests
- Open PR → Auto-deploy preview
- Comment with preview URL

## Performance Optimization

### Enable in vercel.json
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

### Image Optimization
- Vercel automatically optimizes images
- Use Next.js `<Image>` component
- Automatic WebP conversion

### Caching
- Static assets: Cached automatically
- API routes: Configure in code
- ISR: Incremental Static Regeneration

## Monitoring

### Vercel Analytics
1. Go to Analytics tab
2. View:
   - Page views
   - Performance metrics
   - Web Vitals
   - Real User Monitoring

### Error Tracking
- Vercel logs: Dashboard > Deployments > Logs
- Or integrate Sentry for detailed tracking

## Troubleshooting

### Issue: "API calls failing"
- Check NEXT_PUBLIC_API_URL is correct
- Verify backend is running
- Check CORS settings on backend

### Issue: "Environment variables not working"
- Must start with `NEXT_PUBLIC_` for client-side
- Redeploy after adding variables
- Check variable scope (Production/Preview/Development)

### Issue: "Build failing"
- Check build logs in Vercel
- Verify all dependencies in package.json
- Test build locally: `npm run build`

### Issue: "404 on refresh"
- Next.js handles this automatically
- Check vercel.json configuration
- Verify rewrites/redirects

## Rollback

### Instant Rollback
1. Go to Deployments
2. Find previous working deployment
3. Click "..." > "Promote to Production"
4. Instant rollback (no rebuild)

## Cost

### Hobby Plan (Free)
- Unlimited deployments
- 100GB bandwidth/month
- Automatic HTTPS
- **Cost: $0/month**

### Pro Plan ($20/month)
- Unlimited bandwidth
- Advanced analytics
- Team collaboration
- Password protection

## Security Checklist

- ✅ Use environment variables for API URLs
- ✅ Enable HTTPS (automatic)
- ✅ Set security headers
- ✅ Validate user input
- ✅ Use CSP headers
- ✅ Keep dependencies updated

## CI/CD Pipeline

### GitHub Actions (Optional)
```yaml
name: Deploy to Vercel
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

## Updates

### Deploy Updates
```bash
# Make changes
git add .
git commit -m "Update: description"
git push

# Vercel auto-deploys
```

### Manual Deploy
```bash
vercel --prod
```

## Performance Metrics

### Target Metrics
- First Contentful Paint: < 1.8s
- Largest Contentful Paint: < 2.5s
- Time to Interactive: < 3.8s
- Cumulative Layout Shift: < 0.1

### Check Performance
- Vercel Analytics
- Lighthouse (Chrome DevTools)
- WebPageTest.org

## Support

- Vercel Docs: https://vercel.com/docs
- Community: https://github.com/vercel/vercel/discussions
- Discord: https://vercel.com/discord

## Next Steps

1. ✅ Deploy frontend to Vercel
2. ✅ Configure environment variables
3. ✅ Test end-to-end with backend
4. ✅ Set up custom domain (optional)
5. ✅ Enable analytics
6. ✅ Set up error tracking
