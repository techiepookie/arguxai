# ArguxAI Deployment Guide

## 🐳 Docker Deployment

### Local Testing with Docker

1. **Build the Docker image**:
```bash
docker build -t arguxai:latest .
```

2. **Run with Docker Compose**:
```bash
# Copy environment variables
cp .env .env.local

# Start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

3. **Test the deployment**:
```bash
curl http://localhost:8000/health
```

### Push to Docker Hub

1. **Login to Docker Hub**:
```bash
docker login
```

2. **Tag and push**:
```bash
docker tag arguxai:latest yourusername/arguxai:latest
docker push yourusername/arguxai:latest
```

## 🚀 Render Deployment

### Option 1: Deploy from Docker Hub (Recommended)

1. **Push your image to Docker Hub** (see above)

2. **Create a new Web Service on Render**:
   - Go to https://render.com/
   - Click "New +" → "Web Service"
   - Select "Deploy an existing image from a registry"
   - Enter: `yourusername/arguxai:latest`

3. **Configure the service**:
   - **Name**: arguxai
   - **Region**: Oregon (or closest to you)
   - **Instance Type**: Starter (512MB RAM, $7/month)
   - **Port**: 8000

4. **Add Environment Variables**:
   ```
   API_KEY=your_api_key
   DEEPSEEK_API_KEY=your_deepseek_key
   GITHUB_TOKEN=your_github_token
   GITHUB_DEFAULT_REPO=techiepookie/demo-login-app
   FIGMA_ACCESS_TOKEN=your_figma_token
   JIRA_DOMAIN=your-domain.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your_jira_token
   JIRA_PROJECT_KEY=KAN
   CONVEX_DEPLOYMENT_URL=your_convex_url
   CONVEX_DEPLOY_KEY=your_convex_key
   ENVIRONMENT=production
   DEMO_MODE=false
   ```

5. **Deploy**: Click "Create Web Service"

### Option 2: Deploy from GitHub

1. **Push code to GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/arguxai.git
git push -u origin main
```

2. **Connect Render to GitHub**:
   - Go to https://render.com/
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the `render.yaml` file

3. **Add Environment Variables** (same as Option 1)

4. **Deploy**: Render will automatically build and deploy

### Option 3: Using render.yaml (Blueprint)

1. **Push code with render.yaml to GitHub**

2. **Create Blueprint on Render**:
   - Go to https://render.com/
   - Click "New +" → "Blueprint"
   - Select your repository
   - Render will read `render.yaml` and configure everything

3. **Add secret environment variables** in Render dashboard

## 📊 Memory Optimization for 512MB

The Docker image is optimized for 512MB:

- **Multi-stage build**: Reduces image size by ~40%
- **Slim Python base**: Uses `python:3.11-slim` instead of full image
- **No cache**: `pip install --no-cache-dir` saves ~100MB
- **Minimal dependencies**: Only production packages
- **SQLite**: Lightweight database (~10-20MB)

### Memory Usage Breakdown:
- Python runtime: ~80MB
- FastAPI + Uvicorn: ~120MB
- Dependencies: ~150MB
- SQLite: ~20MB
- Application code: ~30MB
- **Total**: ~400MB (leaves 112MB buffer)

## 🔍 Monitoring

### Health Check
```bash
curl https://your-app.onrender.com/health
```

### View Logs on Render
1. Go to your service dashboard
2. Click "Logs" tab
3. Monitor real-time logs

### Check Memory Usage
```bash
docker stats arguxai-app
```

## 🐛 Troubleshooting

### Out of Memory (OOM)
If you hit memory limits:

1. **Upgrade to Starter Plus** (1GB RAM, $15/month)
2. **Optimize queries**: Add indexes to SQLite
3. **Reduce worker count**: Use single worker
4. **Enable swap**: Add swap file (not recommended on Render)

### Slow Startup
- **Cold starts**: Render free tier sleeps after 15min inactivity
- **Solution**: Upgrade to paid tier or use external monitoring

### Database Persistence
- **Issue**: SQLite data lost on restart
- **Solution**: Use Render Disk (persistent storage)
  - Add in Render dashboard: Settings → Disk
  - Mount path: `/app/data`
  - Size: 1GB (free)

## 🔐 Security Checklist

- [ ] All API keys in environment variables (not in code)
- [ ] `.env` file in `.gitignore`
- [ ] HTTPS enabled (automatic on Render)
- [ ] API key authentication enabled
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] No sensitive data in logs

## 📈 Scaling

### Horizontal Scaling
- Render Starter plan: 1 instance
- Upgrade to Standard: Multiple instances with load balancing

### Database Scaling
- SQLite works for <100K events/day
- For more: Migrate to PostgreSQL (Render provides free tier)

## 💰 Cost Estimate

### Render Pricing:
- **Starter (512MB)**: $7/month
- **Starter Plus (1GB)**: $15/month
- **Standard (2GB)**: $25/month

### Additional Services:
- **Render Disk**: Free (1GB)
- **PostgreSQL**: Free tier available
- **Custom Domain**: Free

## 🚀 Quick Deploy Commands

```bash
# Build and test locally
docker-compose up --build

# Push to Docker Hub
docker tag arguxai:latest yourusername/arguxai:latest
docker push yourusername/arguxai:latest

# Deploy on Render (automatic with GitHub integration)
git push origin main
```

## 📞 Support

- **Render Docs**: https://render.com/docs
- **Docker Docs**: https://docs.docker.com/
- **Issues**: Create an issue on GitHub

---

**Ready to deploy!** 🎉
