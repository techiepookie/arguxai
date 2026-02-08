# 🚀 ArguxAI - AI-Powered Conversion Funnel Monitoring

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Node.js](https://img.shields.io/badge/Node.js-16+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**ArguxAI** is an intelligent, automated system that detects conversion drops in your user funnels, diagnoses root causes using AI, and generates production-ready code fixes via GitHub pull requests. Built for modern product teams that want to catch revenue leaks before customers notice them.

## 🎯 What is ArguxAI?

ArguxAI combines **statistical anomaly detection**, **AI-powered root cause analysis**, and **automated code generation** to give your engineering team superpowers for conversion optimization:

- **🔍 Real-time Detection**: Continuous statistical monitoring of funnel metrics
- **🧠 AI Diagnosis**: DeepSeek AI analyzes patterns and identifies root causes in plain English
- **💻 Automated Fixes**: Generates production-ready GitHub PRs with tests and rollout flags
- **📊 Design Analysis**: AI-powered UX review from Figma designs
- **🎟️ Ticket Creation**: Auto-creates Jira tickets with full context
- **📈 ROI Dashboards**: Track revenue recovered and funnel improvements

<video controls src="https://pub-84744dd4dd0b498f983c9f340a4e71f7.r2.dev/arguxai/arguxai.mp4"></video>

### Real-World Use Case

Your OTP verification funnel drops from 48% to 27% overnight. ArguxAI:
1. **Detects** the drop in 2-4 minutes
2. **Diagnoses** "OTP provider timeout spike in India region" (89% confidence)
3. **Generates** a PR with fallback logic and tests
4. **Proves** the fix recovered $8.4K/day

---

## ⭐ Key Features

### Conversion Funnel Monitoring
- Track multi-step user journeys (signup → verification → payment)
- Monitor conversion rates with real-time alerts
- Segment anomalies by geography, device, user cohort
- Statistical significance testing (sigma-based detection)

### AI-Powered Root Cause Analysis
- Correlates conversion drops with:
  - Error rate spikes
  - Latency increases
  - Provider outages (Stripe, Twilio, Auth0, etc.)
  - User segmentation issues
  - Geographic variations
- Returns confidence scores for each diagnosis
- Explains findings in plain, actionable English

### Automated Code Generation
- Generates GitHub PRs with:
  - Complete, compilable code fixes
  - Comprehensive test coverage
  - Monitoring and alerting integration
  - Rollout flags and gradual deployment configs
  - Design-system-aware UI components
- Works with any tech stack (Node, Python, Go, Java, etc.)

### GitHub Integration
- Authenticate via OAuth
- Auto-create branches (`fix/funnel-drop-2024-02-07`)
- Commit changes with detailed messages
- Create pull requests with context and evidence
- Link to dashboards for review
- Track PR metrics (merge time, impact)

### Jira Integration
- Auto-create tickets from issues
- Link PRs to Jira tickets
- Track SLA and time-to-fix
- Escalate critical funnels
- Custom field mapping

### Figma Design Review
- Upload Figma design files
- AI analyzes UX for conversion killers:
  - CTA button size/color/prominence
  - Form field clarity
  - Trust signals (badges, testimonials)
  - Mobile responsiveness
- Generates actionable feedback
- Links to Figma components for fixes

### Interactive Dashboard
- Real-time funnel visualization
- Anomaly timeline
- Issue backlog
- PR deployment status
- ROI metrics (revenue recovered, funnel improvement %)
- Search and filter issues

---

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.10 or higher
- **Node.js**: 16 or higher (for Convex)
- **RAM**: 2GB minimum (4GB recommended for dev)
- **Disk**: 1GB for dependencies
- **OS**: Linux, macOS, or Windows (WSL2 recommended)

### External Services (Free Tier Available)
- **DeepSeek API** (AI diagnosis) - [Sign up free](https://platform.deepseek.com)
- **GitHub** (code generation) - Free with personal token
- **Convex** (database) - Free tier for development
- **Jira** (optional, issue tracking) - Free for small teams
- **Figma** (optional, design review) - Free tier available

---

## 🚀 Quick Start (5 Minutes)

### Option 1: Docker Compose (Recommended)

The easiest way to get ArguxAI running:

```bash
# Clone repository
git clone https://github.com/techiepookie/arguxai.git
cd arguxai

# Create environment file (see below for full config)
cp .env.example .env

# Edit .env with your API keys
# Then start all services with Docker Compose
docker-compose up -d

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f app

# Access dashboard
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### Option 2: Local Setup (Without Docker)

```bash
# Clone and navigate
git clone https://github.com/techiepookie/arguxai.git
cd arguxai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python init_sqlite.py

# Start backend
uvicorn app.main:app --reload --port 8000

# In another terminal, serve frontend
cd frontend
python -m http.server 3000

# Access dashboard at http://localhost:3000
```

---

## 📦 Installation & Configuration

### Step 1: Clone Repository

```bash
git clone https://github.com/techiepookie/arguxai.git
cd arguxai
```

### Step 2: Environment Configuration

Create `.env` file in project root:

```env
# ============================================
# SERVER CONFIGURATION
# ============================================
API_KEY=your-secret-api-key-min-32-chars
ENVIRONMENT=production  # development | production
DEBUG=false
HOST=0.0.0.0
PORT=8000

# ============================================
# DATABASE (Convex)
# ============================================
CONVEX_DEPLOYMENT_URL=https://your-deployment.convex.cloud
CONVEX_DEPLOY_KEY=your_convex_deployment_key

# Optional: Use SQLite for local development
USE_SQLITE=true
SQLITE_DB_PATH=./arguxai.db

# ============================================
# AI & LANGUAGE MODELS (DeepSeek)
# ============================================
# Get API key from: https://platform.deepseek.com
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL_CHAT=deepseek-chat           # For text analysis
DEEPSEEK_MODEL_VISION=deepseek-vl           # For image/design analysis
DEEPSEEK_TEMPERATURE=0.7
DEEPSEEK_MAX_TOKENS=2000

# ============================================
# GITHUB INTEGRATION
# ============================================
# Generate token: https://github.com/settings/tokens
# Scopes needed: repo, workflow, read:user, user:email
GITHUB_TOKEN=ghp_your_personal_access_token
GITHUB_DEFAULT_REPO=owner/repository-name
GITHUB_DEFAULT_BRANCH=main
GITHUB_COMMIT_EMAIL=your-email@example.com
GITHUB_COMMIT_NAME=ArguxAI Bot
GITHUB_PR_DRAFT=false  # Create draft PRs by default?

# ============================================
# FIGMA INTEGRATION (Optional)
# ============================================
# Get token: https://www.figma.com/settings/tokens
FIGMA_ACCESS_TOKEN=your_figma_access_token
FIGMA_API_BASE_URL=https://api.figma.com/v1

# ============================================
# JIRA INTEGRATION (Optional)
# ============================================
# Create token: https://id.atlassian.com/manage-profile/security/api-tokens
JIRA_DOMAIN=your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_jira_api_token
JIRA_PROJECT_KEY=YOUR_PROJECT
JIRA_ISSUE_TYPE=Bug
JIRA_CUSTOM_FIELD_DIAGNOSIS=customfield_10000  # Optional

# ============================================
# ANOMALY DETECTION TUNING
# ============================================
# Minimum conversion drop percentage to trigger alert
MIN_DROP_PERCENT=12.0

# Minimum sessions/conversions to consider for anomaly
MIN_SAMPLE_SIZE=100

# Statistical threshold (2.0 = 95% confidence, 3.0 = 99.7%)
SIGMA_THRESHOLD=2.0

# Cooldown between alerts for same funnel (minutes)
ALERT_COOLDOWN_MINUTES=5

# Lookback window for baseline calculation (hours)
BASELINE_WINDOW_HOURS=24

# Recent window for anomaly detection (minutes)
RECENT_WINDOW_MINUTES=30

# ============================================
# DEMO & TESTING
# ============================================
DEMO_MODE=false
DEMO_EVENTS_PER_SECOND=5

# ============================================
# LOGGING & MONITORING
# ============================================
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR | CRITICAL
LOG_FILE=./logs/arguxai.log
SENTRY_DSN=  # Optional: for error tracking

# ============================================
# CORS & SECURITY
# ============================================
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
CORS_ALLOW_CREDENTIALS=true
CORS_MAX_AGE=600

# ============================================
# RATE LIMITING
# ============================================
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60  # seconds

# ============================================
# REDIS (Optional: for caching & sessions)
# ============================================
REDIS_URL=redis://localhost:6379/0
REDIS_TTL=3600
```

### Step 3: Install Dependencies

**Python Backend:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install  # If using Node build tools
```

### Step 4: Initialize Database

```bash
# SQLite (local development)
python init_sqlite.py

# Convex (production)
npx convex deploy
```

### Step 5: Verify Setup

```bash
# Test DeepSeek connection
python -c "from app.integrations.deepseek_client import DeepSeekClient; print('✓ DeepSeek configured')"

# Test GitHub connection
python -c "from app.integrations.github_client import GitHubClient; print('✓ GitHub configured')"

# Test database
python -c "from app.database import get_db; print('✓ Database connected')"
```

---

## 🐳 Docker Deployment

### Docker Compose (All-in-One)

**docker-compose.yml** (included in repo):

```yaml
version: '3.9'

services:
  # Backend API
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: arguxai-backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=sqlite:///./arguxai.db
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - arguxai-network

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: arguxai-frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - arguxai-network

  # Redis (optional: for caching)
  redis:
    image: redis:7-alpine
    container_name: arguxai-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - arguxai-network

volumes:
  redis_data:

networks:
  arguxai-network:
    driver: bridge
```

**Dockerfile** (Backend):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p logs data

# Run migrations/init
RUN python init_sqlite.py || true

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Dockerfile.frontend** (Frontend):

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy frontend files
COPY frontend/package*.json ./
RUN npm ci

COPY frontend . .

# Build (if using build tools)
RUN npm run build || true

EXPOSE 3000

CMD ["npm", "start"]
```

### Deploy to Production

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale services
docker-compose up -d --scale backend=3

# Stop services
docker-compose down

# Clean up (remove volumes)
docker-compose down -v
```

### Deploy to Cloud (AWS, GCP, DigitalOcean)

#### AWS ECS:

```bash
# Install AWS CLI and configure credentials
aws configure

# Create ECR repository
aws ecr create-repository --repository-name arguxai

# Tag and push image
docker tag arguxai:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/arguxai:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/arguxai:latest

# Deploy to ECS Fargate
aws ecs create-service \
  --cluster arguxai-cluster \
  --service-name arguxai-service \
  --task-definition arguxai-task \
  --desired-count 2 \
  --launch-type FARGATE
```

#### Docker Hub:

```bash
# Tag image
docker tag arguxai:latest techiepookie/arguxai:latest

# Login
docker login

# Push
docker push techiepookie/arguxai:latest

# Run from Hub
docker run -d -p 8000:8000 techiepookie/arguxai:latest
```

---

## 💡 Usage Guide

### Dashboard Overview

Access the dashboard at `http://localhost:3000` (or your deployed URL).

**Sections:**

1. **Home/Overview**
   - Active issues count
   - Funnel health status
   - Recent anomalies
   - ROI metrics (revenue recovered)
   - System health

2. **Funnels**
   - Create new funnels
   - Define conversion steps
   - Set baseline periods
   - View funnel visualizations
   - Download metrics

3. **Issues & Anomalies**
   - List all detected anomalies
   - Filter by funnel, severity, date
   - View anomaly details
   - Run AI diagnosis
   - Generate GitHub PR
   - Create Jira ticket

4. **GitHub Integration**
   - View open pull requests
   - Track merge status
   - See PR impact metrics
   - Link to deployed code

5. **Settings**
   - Manage API integrations
   - Configure anomaly thresholds
   - Team and permissions
   - Billing and usage

### Creating Your First Funnel

#### Via Dashboard:

```
1. Click "Create Funnel"
2. Name: "Signup Flow"
3. Add steps:
   - Step 1: page_view (event: "page_view" where page="/signup")
   - Step 2: form_submit (event: "form_submitted")
   - Step 3: email_verify (event: "email_verified")
   - Step 4: account_created (event: "account_created")
4. Set baseline: Last 7 days
5. Save
6. System starts monitoring
```

#### Via API:

```bash
curl -X POST http://localhost:8000/api/funnels \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "name": "Signup Flow",
    "description": "User signup journey",
    "steps": [
      {
        "name": "page_view",
        "event_filter": {
          "event": "page_view",
          "properties": {"page": "/signup"}
        }
      },
      {
        "name": "form_submit",
        "event_filter": {"event": "form_submitted"}
      },
      {
        "name": "email_verify",
        "event_filter": {"event": "email_verified"}
      },
      {
        "name": "account_created",
        "event_filter": {"event": "account_created"}
      }
    ],
    "baseline_days": 7
  }'
```

### Event Ingestion

Events are the lifeblood of ArguxAI. Ingest events from your app:

```javascript
// JavaScript/TypeScript
const apiKey = "your-api-key";

async function trackEvent(event, properties = {}) {
  await fetch("http://localhost:8000/api/events", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": apiKey,
    },
    body: JSON.stringify({
      event,
      properties: {
        ...properties,
        timestamp: new Date().toISOString(),
        user_id: getCurrentUserId(), // Your user ID
        session_id: getSessionId(),
        url: window.location.href,
        user_agent: navigator.userAgent,
      },
    }),
  });
}

// Track events
trackEvent("page_view", { page: "/signup" });
trackEvent("form_submitted", { form_name: "signup" });
trackEvent("email_verified");
trackEvent("account_created", { plan: "free" });
```

```python
# Python
import requests
from datetime import datetime

API_KEY = "your-api-key"
BASE_URL = "http://localhost:8000"

def track_event(event: str, properties: dict = None, user_id: str = None):
    """Track an event"""
    payload = {
        "event": event,
        "properties": {
            **(properties or {}),
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id or "anonymous",
        },
    }
    
    response = requests.post(
        f"{BASE_URL}/api/events",
        json=payload,
        headers={"X-API-Key": API_KEY},
    )
    return response.json()

# Track events
track_event("page_view", {"page": "/signup"}, user_id="user_123")
track_event("form_submitted", {"form_name": "signup"})
track_event("email_verified", user_id="user_123")
track_event("account_created", {"plan": "free"}, user_id="user_123")
```

### AI Diagnosis

Once an anomaly is detected:

```bash
# Via Dashboard: Click "Run AI Diagnosis" on issue
# Via API:
curl -X POST http://localhost:8000/api/issues/{issue_id}/diagnose \
  -H "Authorization: Bearer $API_KEY"
```

**Response Example:**

```json
{
  "issue_id": "iss_abc123",
  "anomaly": {
    "funnel": "email_verification",
    "metric": "conversion_rate",
    "baseline": 0.85,
    "current": 0.45,
    "drop_percent": 47.1,
    "significance": "3.2σ (p<0.001)"
  },
  "diagnosis": {
    "root_cause": "Twilio SMS API timeout in US region",
    "confidence": 0.92,
    "evidence": [
      "Error logs show 342 Twilio timeout errors (15:00-15:45 UTC)",
      "Correlation with India region (+89% errors)",
      "API response time increased from 200ms to 5000ms",
      "Other SMS providers unaffected"
    ],
    "affected_users": 3421,
    "estimated_revenue_impact": 8400,
    "recommended_fix": "Implement fallback to Nexmo SMS provider"
  },
  "ai_generated_pr": {
    "title": "Fix: Implement SMS provider fallback for Twilio timeouts",
    "description": "Adds fallback SMS provider logic to handle provider timeouts gracefully...",
    "code_diff": "..."
  }
}
```

### Generating GitHub PRs

```bash
# Via Dashboard: Click "Generate PR" on diagnosed issue
# Via API:
curl -X POST http://localhost:8000/api/github/generate-pr-simple \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "issue_id": "iss_abc123",
    "target_file": "src/services/sms.ts",
    "branch_name": "fix/sms-provider-fallback"
  }'
```

**Generated PR Includes:**

✅ Complete, runnable code fix
✅ TypeScript/JavaScript test file
✅ Monitoring and alerts config
✅ Feature flag for gradual rollout
✅ Link to dashboard for review
✅ Estimated impact metrics

### Jira Integration

```bash
# Create Jira ticket from issue
curl -X POST http://localhost:8000/api/jira/create-ticket/iss_abc123 \
  -H "Authorization: Bearer $API_KEY"
```

**Creates Ticket With:**
- Issue title and description
- Root cause diagnosis
- Affected users count
- Estimated revenue impact
- Link to ArguxAI dashboard
- Link to generated PR
- Priority based on severity

### Figma Design Review

```bash
# Via Dashboard: Figma section → Paste URL → "Analyze"
# Via API:
curl -X POST http://localhost:8000/api/figma/review \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "figma_url": "https://www.figma.com/file/abc123/designs",
    "focus_area": "signup_flow"
  }'
```

**Analysis Returns:**

```json
{
  "design_url": "...",
  "analysis": {
    "cta_analysis": {
      "primary_button": {
        "size": "40px",
        "color": "#7C3AED",
        "contrast_ratio": 8.5,
        "feedback": "✓ Excellent visibility and accessibility"
      }
    },
    "form_clarity": {
      "score": 8.2,
      "issues": [
        "Email field label could be clearer",
        "Error message color needs higher contrast"
      ]
    },
    "trust_signals": {
      "findings": [
        "No security badges visible",
        "Missing privacy/terms links",
        "Consider adding testimonials"
      ]
    },
    "mobile_responsive": {
      "score": 7.8,
      "issues": ["CTA button too small on mobile"]
    },
    "estimated_conversion_impact": "+2.3%"
  }
}
```

---

## 📊 API Documentation

### Interactive API Docs

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Authentication

Include API key in headers:

```bash
curl -H "Authorization: Bearer your_api_key" http://localhost:8000/api/...
# or
curl -H "X-API-Key: your_api_key" http://localhost:8000/api/...
```

### Core Endpoints

#### Events

```bash
# Ingest event
POST /api/events
{
  "event": "string",
  "properties": {
    "user_id": "string",
    "timestamp": "2024-02-07T12:00:00Z",
    ...any custom properties
  }
}
→ 201 Created

# List event types
GET /api/events/types
→ ["page_view", "form_submitted", "email_verified", ...]

# Get events (with filters)
GET /api/events?event=page_view&limit=100&offset=0
```

#### Funnels

```bash
# Create funnel
POST /api/funnels
{
  "name": "string",
  "steps": [
    {
      "name": "step_name",
      "event_filter": {
        "event": "string",
        "properties": {...}
      }
    }
  ],
  "baseline_days": 7
}
→ 201 Created

# List funnels
GET /api/funnels

# Get funnel details
GET /api/funnels/{id}

# Get funnel metrics
GET /api/funnels/{id}/metrics?days=7
```

#### Issues & Anomalies

```bash
# Detect anomalies (manual trigger)
POST /api/issues/detect
→ Returns detected issues

# List issues
GET /api/issues?status=open&limit=50

# Get issue details
GET /api/issues/{id}

# Run AI diagnosis
POST /api/issues/{id}/diagnose
→ Returns root cause analysis

# Update issue status
PATCH /api/issues/{id}
{
  "status": "open|in_progress|resolved|false_alarm"
}
```

#### GitHub Integration

```bash
# Generate PR for issue
POST /api/github/generate-pr-simple
{
  "issue_id": "string",
  "target_file": "string",
  "branch_name": "string"
}
→ Returns PR details and URL

# List pull requests
GET /api/github/prs?status=open

# Get PR details
GET /api/github/prs/{pr_id}
```

#### Jira Integration

```bash
# Create Jira ticket
POST /api/jira/create-ticket/{issue_id}
→ Returns Jira ticket URL

# List tickets
GET /api/jira/tickets
```

#### Figma Integration

```bash
# Analyze Figma design
POST /api/figma/review
{
  "figma_url": "string",
  "focus_area": "string"
}
→ Returns UX analysis and recommendations
```

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   USER APPLICATIONS                      │
│         (Your web app, mobile app, backend)              │
└────────────────────┬────────────────────────────────────┘
                     │ Events
                     ▼
┌─────────────────────────────────────────────────────────┐
│              ARGUXAI FRONTEND (React/Vue)                │
│        - Dashboard, Funnels, Issues, Settings            │
└────────────────────┬────────────────────────────────────┘
                     │ REST API
                     ▼
┌─────────────────────────────────────────────────────────┐
│           ARGUXAI BACKEND (FastAPI/Python)              │
├─────────────────────────────────────────────────────────┤
│  API Layer:                                              │
│  - Events ingestion                                      │
│  - Funnel management                                     │
│  - Issue tracking                                        │
│  - PR generation                                         │
├─────────────────────────────────────────────────────────┤
│  Services:                                               │
│  - Anomaly Detection (Statistical)                       │
│  - Evidence Collection                                   │
│  - AI Diagnosis (DeepSeek)                               │
│  - Code Generation                                       │
│  - Integrations (GitHub, Jira, Figma)                    │
├─────────────────────────────────────────────────────────┤
│  Data Layer:                                             │
│  - SQLite (local) / Convex (cloud)                       │
│  - Redis (caching)                                       │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬──────────┐
        ▼            ▼            ▼          ▼
   ┌────────┐  ┌─────────┐  ┌────────┐  ┌──────────┐
   │ DeepSeek│  │ GitHub  │  │ Figma  │  │  Jira    │
   │   AI    │  │  API    │  │  API   │  │   API    │
   └────────┘  └─────────┘  └────────┘  └──────────┘
```

### Backend Structure

```
arguxai/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app
│   ├── config.py                    # Settings/env vars
│   ├── security.py                  # Auth, API keys
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py          # Shared dependencies
│   │   └── routes/
│   │       ├── events.py            # POST /api/events
│   │       ├── funnels.py           # CRUD funnels
│   │       ├── issues.py            # Issues/anomalies
│   │       ├── github.py            # PR generation
│   │       ├── jira.py              # Ticket creation
│   │       ├── figma.py             # Design analysis
│   │       └── health.py            # Health checks
│   │
│   ├── models/
│   │   ├── event.py                 # Event schema
│   │   ├── funnel.py                # Funnel schema
│   │   ├── issue.py                 # Issue schema
│   │   ├── pr.py                    # PR schema
│   │   └── response.py              # Response models
│   │
│   ├── services/
│   │   ├── anomaly_detector.py      # Statistical detection
│   │   ├── evidence_collector.py    # Log/error analysis
│   │   ├── ai_diagnosis.py          # DeepSeek integration
│   │   ├── pr_generator.py          # Code generation
│   │   ├── issue_manager.py         # CRUD operations
│   │   └── metrics.py               # Funnel metrics
│   │
│   ├── integrations/
│   │   ├── deepseek_client.py       # AI API
│   │   ├── github_client.py         # GitHub API
│   │   ├── jira_client.py           # Jira API
│   │   ├── figma_client.py          # Figma API
│   │   └── base_client.py           # Base class
│   │
│   ├── core/
│   │   ├── logging.py               # Logging setup
│   │   ├── errors.py                # Custom exceptions
│   │   └── constants.py             # Constants
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py                # SQLAlchemy models
│   │   ├── session.py               # DB session
│   │   └── migrations/              # Alembic migrations
│   │
│   └── utils/
│       ├── stats.py                 # Statistical functions
│       ├── validators.py            # Input validation
│       └── formatters.py            # Response formatting
│
├── frontend/
│   ├── index.html                   # Main HTML
│   ├── css/
│   │   ├── styles.css               # Global styles
│   │   └── components.css           # Component styles
│   └── js/
│       ├── app.js                   # Main app
│       ├── api-service.js           # API client
│       ├── router.js                # Client routing
│       ├── pages/
│       │   ├── dashboard.js
│       │   ├── funnels.js
│       │   ├── issues.js
│       │   └── settings.js
│       └── utils.js
│
├── tests/
│   ├── test_anomaly_detection.py
│   ├── test_github_integration.py
│   ├── test_ai_diagnosis.py
│   ├── test_event_ingestion.py
│   └── test_pr_generation.py
│
├── init_sqlite.py                   # Database initialization
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Backend container
├── docker-compose.yml               # Multi-container setup
├── .env.example                     # Example env vars
└── README.md                        # This file
```

### Data Flow

```
1. Event Ingestion
   User App → API /events → Queue → Event Store

2. Metric Aggregation (Every 5 minutes)
   Event Store → Aggregator → Funnel Metrics

3. Anomaly Detection (Continuous)
   Funnel Metrics → Statistical Analysis → Anomalies

4. AI Diagnosis (On Trigger)
   Anomaly + Evidence → DeepSeek API → Root Cause

5. PR Generation (On Request)
   Root Cause + Code Template → PR Generator → GitHub

6. Dashboard Updates (Real-time via WebSocket)
   Issues Table → WebSocket → Frontend → UI Update
```

---

## 🔧 Configuration & Tuning

### Anomaly Detection Sensitivity

```env
# Conservative (fewer false positives)
MIN_DROP_PERCENT=15.0
MIN_SAMPLE_SIZE=200
SIGMA_THRESHOLD=2.5
ALERT_COOLDOWN_MINUTES=10

# Aggressive (catches more anomalies)
MIN_DROP_PERCENT=10.0
MIN_SAMPLE_SIZE=50
SIGMA_THRESHOLD=2.0
ALERT_COOLDOWN_MINUTES=2
```

### AI Model Configuration

```env
# Faster responses, less accurate
DEEPSEEK_TEMPERATURE=0.5
DEEPSEEK_MAX_TOKENS=1000

# More accurate, slower, higher cost
DEEPSEEK_TEMPERATURE=0.9
DEEPSEEK_MAX_TOKENS=3000
```

### Database Performance

```env
# SQLite (development)
USE_SQLITE=true
SQLITE_DB_PATH=./arguxai.db

# Convex (production, recommended)
CONVEX_DEPLOYMENT_URL=https://...
CONVEX_DEPLOY_KEY=...

# Redis caching
REDIS_URL=redis://localhost:6379
REDIS_TTL=3600
```

---

## 🧪 Testing

### Run All Tests

```bash
cd tests

# Run all tests
python -m pytest

# Run specific test file
python test_anomaly_detection.py

# Run with coverage
pytest --cov=app tests/

# Run in verbose mode
pytest -v
```

### Test Files Overview

**test_system.py**
- End-to-end system test
- Creates funnel, ingest events, detect anomaly
- Verifies full pipeline

**test_github_integration.py**
- Tests GitHub API connectivity
- Verifies PR creation
- Tests authentication

**test_anomaly_detection.py**
- Statistical detection accuracy
- Tests sigma calculation
- Edge cases (small sample, high variance)

**test_ai_diagnosis.py**
- DeepSeek API integration
- Response parsing
- Error handling

**test_event_ingestion.py**
- Event payload validation
- Database storage
- Query filtering

**test_pr_generation.py**
- Code generation accuracy
- Test file creation
- GitHub API calls

### Example Test Run

```bash
$ pytest tests/test_system.py -v

test_system.py::test_create_funnel PASSED
test_system.py::test_ingest_events PASSED
test_system.py::test_detect_anomaly PASSED
test_system.py::test_run_diagnosis PASSED
test_system.py::test_generate_pr PASSED

======================== 5 passed in 8.23s ========================
```

---

## 🚨 Troubleshooting

### Common Issues & Solutions

#### 1. **Backend Won't Start**

**Error**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
# Ensure you're in project root
cd arguxai

# Reinstall dependencies
pip install -r requirements.txt

# Start with full path
python -m uvicorn app.main:app --reload
```

#### 2. **Database Issues**

**Error**: `table issues has no column named X`

**Solution**:
```bash
# Reset database (loses all data!)
rm arguxai.db
python init_sqlite.py

# For Convex:
npx convex dev --reset-database
```

#### 3. **API Key Errors**

**Error**: `401 Unauthorized` or `Invalid API Key`

**Solution**:
```bash
# Check .env file has API_KEY set
cat .env | grep API_KEY

# Test API key
curl -H "Authorization: Bearer your_api_key" http://localhost:8000/health
```

#### 4. **GitHub PR Creation Fails**

**Error**: `422 Unprocessable Entity`

**Causes & Fixes**:
```bash
# 1. Invalid GitHub token
# - Check token has 'repo' scope
# - Check token hasn't expired
# - Regenerate at https://github.com/settings/tokens

# 2. No write access
# - Verify you have write access to repository
# - Check permission in GitHub repo settings

# 3. Branch already exists
# - Add timestamp to branch name: fix/issue-2024-02-07-15-30

# 4. File path doesn't exist
# - Verify target file path is correct
# - Check file exists in repository

# Test GitHub connection
python -c "
from app.integrations.github_client import GitHubClient
client = GitHubClient()
repos = client.get_user_repos()
print(f'✓ GitHub connected. Found {len(repos)} repos')
"
```

#### 5. **DeepSeek API Errors**

**Error**: `401 Unauthorized - Invalid API key`

**Solution**:
```bash
# Get new key from https://platform.deepseek.com
# Update .env
DEEPSEEK_API_KEY=sk_new_key_here

# Test connection
python -c "
from app.integrations.deepseek_client import DeepSeekClient
client = DeepSeekClient()
response = client.diagnose(text='Test')
print('✓ DeepSeek configured')
"
```

**Error**: `429 Rate Limit Exceeded`

**Solution**:
```env
# Implement backoff in code (already done)
# Add exponential retry in deepseek_client.py
# Wait between requests: 1s → 2s → 4s

# Upgrade DeepSeek plan if rate limits too low
```

#### 6. **Frontend Can't Connect to API**

**Error**: `CORS error` or `Failed to fetch http://localhost:8000`

**Solution**:
```env
# Update CORS settings in .env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Check backend is running
curl http://localhost:8000/health
# Should return: {"status": "healthy"}

# Check frontend API URL
# In frontend/js/api-service.js:
const API_URL = 'http://localhost:8000';
```

#### 7. **High Memory Usage**

**Error**: Out of memory when processing large events

**Solution**:
```bash
# Increase available memory
docker update --memory 4g arguxai-backend

# Implement pagination in event queries
# Reduce RECENT_WINDOW_MINUTES in .env
# Clear old data: DELETE FROM events WHERE created_at < NOW() - 30 days
```

#### 8. **Slow Anomaly Detection**

**Error**: Takes >10 minutes to detect anomalies

**Solution**:
```env
# Reduce baseline window
BASELINE_WINDOW_HOURS=12  # Was 24

# Increase detection frequency
RECENT_WINDOW_MINUTES=10  # Was 30

# Optimize database
# Add indexes:
CREATE INDEX idx_events_funnel_created ON events(funnel_id, created_at);
```

#### 9. **Docker Issues**

**Error**: `cannot connect to Docker daemon`

**Solution**:
```bash
# Start Docker
systemctl start docker  # Linux
open /Applications/Docker.app  # macOS

# Verify Docker
docker ps

# If permission denied: add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

**Error**: `docker-compose: command not found`

**Solution**:
```bash
# Install Docker Compose v2
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose

chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

### Debug Mode

Enable verbose logging:

```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

Then check logs:

```bash
# Docker
docker-compose logs -f app

# Local
tail -f logs/arguxai.log
```

---

## 📈 Monitoring & Observability

### Health Checks

```bash
# Endpoint health
curl http://localhost:8000/health
# → {"status": "healthy", "timestamp": "2024-02-07T12:00:00Z"}

# Database connectivity
curl http://localhost:8000/health/db
# → {"database": "connected", "latency_ms": 2}

# External services
curl http://localhost:8000/health/integrations
# → {
#     "deepseek": "connected",
#     "github": "connected",
#     "figma": "not_configured",
#     "jira": "error"
#   }
```

### Metrics & Analytics

ArguxAI exposes Prometheus metrics:

```bash
# Endpoint
curl http://localhost:8000/metrics

# Metrics include:
# - requests_total (by endpoint, method, status)
# - request_duration_seconds
# - events_ingested_total
# - anomalies_detected_total
# - pr_created_total
# - deepseek_api_calls_total
```

### Logging

Logs are written to `logs/arguxai.log`:

```
2024-02-07 12:00:15 INFO     api.events        Event ingested: user_123, page_view
2024-02-07 12:05:23 WARNING  services.anomaly  Conversion drop detected in signup_flow
2024-02-07 12:05:45 INFO     ai_diagnosis      Running diagnosis for issue_123
2024-02-07 12:06:12 INFO     integrations.github PR created: #42
```

---

## 🔐 Security Considerations

### API Key Management

```bash
# Generate secure API key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Never commit .env to git
echo ".env" >> .gitignore
echo "logs/" >> .gitignore
echo "data/" >> .gitignore
```

### GitHub Token Security

- Use separate bot account for PR creation
- Use fine-grained tokens with minimal permissions
- Rotate tokens regularly
- Never log token in errors

### Data Privacy

- Events should not contain PII (passwords, tokens, SSN)
- Use data masking for sensitive fields
- Implement GDPR right-to-deletion
- Regular security audits

### Production Checklist

- [ ] Use HTTPS/TLS for all connections
- [ ] Enable rate limiting (already built-in)
- [ ] Set up WAF (Web Application Firewall)
- [ ] Use managed database (AWS RDS, etc.)
- [ ] Enable audit logging
- [ ] Regular backups
- [ ] Penetration testing
- [ ] OWASP Top 10 review

---

## 📚 Additional Resources

### Documentation
- [DeepSeek API Docs](https://platform.deepseek.com/docs)
- [GitHub API Docs](https://docs.github.com/en/rest)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Convex Database](https://docs.convex.dev/)

### Community
- GitHub Discussions
- Discord Community (if available)
- Stack Overflow tag: `#arguxai`

### Examples
- `examples/` directory with sample integrations
- Jupyter notebooks for analysis
- Postman collection for API testing

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests (`tests/test_your_feature.py`)
5. Update documentation
6. Commit with clear messages (`git commit -m 'Add: feature X'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests before committing
pytest tests/

# Format code
black app/ tests/
isort app/ tests/

# Lint
flake8 app/ tests/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **DeepSeek AI** for powerful language models
- **FastAPI** for the excellent Python web framework
- **Convex** for real-time database infrastructure
- **GitHub API** for seamless code integration
- Our amazing community contributors

---

## 📞 Support & Contact

### Getting Help


- **GitHub Issues**: [Report bugs](https://github.com/techiepookie/arguxai/issues)
- **Discussions**: [Ask questions](https://github.com/techiepookie/arguxai/discussions)
- **Email**: nikhilkumar1241@outlook.com

### Reporting Security Issues

Please report security vulnerabilities responsibly:
- Email: security@arguxai.dev
- Do not open public GitHub issues for security problems
- We'll respond within 48 hours

---

## 🚀 Roadmap

### Upcoming Features

- [ ] Webhook integrations (Segment, Amplitude, Mixpanel)
- [ ] Slack bot for incident alerts
- [ ] Custom LLM model support
- [ ] A/B test integration
- [ ] Advanced segmentation
- [ ] Mobile app (iOS/Android)
- [ ] Predictive anomaly detection
- [ ] Cost optimization suggestions

### In Development

- [ ] Multi-workspace support
- [ ] Team collaboration features
- [ ] Advanced RBAC
- [ ] Custom metrics builder

---

<div align="center">

**ArguxAI** — BEAT THE MATRIX.

[⭐ Star this repo](https://github.com/techiepookie/arguxai) if you find it helpful!

Built with ❤️ by the ArguxAI Team

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Status](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)
![Last Updated](https://img.shields.io/badge/last%20updated-2024--02--07-orange.svg)

</div>
