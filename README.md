# ArguxAI - AI-Powered Conversion Funnel Monitoring

ArguxAI is an intelligent system that automatically detects conversion drops in your user funnels, diagnoses root causes using AI, and generates code fixes via GitHub pull requests.

## 🚀 Features

- **Real-time Anomaly Detection**: Statistical analysis of conversion metrics with sigma-based significance testing
- **AI-Powered Diagnosis**: DeepSeek AI analyzes conversion drops and identifies root causes
- **Automated Code Fixes**: Generates GitHub PRs with AI-suggested fixes
- **Figma Design Review**: AI analysis of design files for UX issues
- **Jira Integration**: Automatic ticket creation for detected issues
- **Interactive Dashboard**: Real-time metrics and funnel visualization

## 📋 Prerequisites

- Python 3.10+
- Node.js 16+ (for Convex)
- GitHub account with repository access
- Jira account (optional)
- Figma access token (optional)
- DeepSeek API key

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-ux-flow
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# API Configuration
API_KEY=your_api_key_here
ENVIRONMENT=development

# Convex Database
CONVEX_DEPLOYMENT_URL=your_convex_url
CONVEX_DEPLOY_KEY=your_convex_key

# DeepSeek AI Provider
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL_CHAT=deepseek-chat
DEEPSEEK_MODEL_VISION=deepseek-vl

# GitHub Integration
GITHUB_TOKEN=your_github_token
GITHUB_DEFAULT_REPO=owner/repo

# Figma Integration (optional)
FIGMA_ACCESS_TOKEN=your_figma_token

# Jira Integration (optional)
JIRA_DOMAIN=your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_jira_token
JIRA_PROJECT_KEY=YOUR_PROJECT_KEY

# Anomaly Detection Configuration
MIN_DROP_PERCENT=12.0
MIN_SAMPLE_SIZE=100
SIGMA_THRESHOLD=2.0
ALERT_COOLDOWN_MINUTES=5

# Demo Mode
DEMO_MODE=false
```

### 4. Initialize Database

```bash
python init_sqlite.py
```

### 5. Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 6. Access the Frontend

Open `frontend/index.html` in your browser or serve it with a local server:

```bash
cd frontend
python -m http.server 8080
```

Then navigate to `http://localhost:8080`

## 📖 Usage Guide

### Dashboard

The dashboard provides an overview of:
- Active issues count
- Conversion rate trends
- Recent anomalies
- System health status

### Funnel Management

1. **Create a Funnel**: Define conversion steps (e.g., page_view → login → purchase)
2. **AI-Enhanced Prompts**: Use AI to generate funnel definitions from natural language
3. **Monitor Metrics**: Track conversion rates for each step

### Issue Detection & Resolution

1. **Automatic Detection**: System continuously monitors for conversion drops
2. **AI Diagnosis**: Click "Run AI Diagnosis" to analyze root causes
3. **Generate PR**: Create automated GitHub pull requests with fixes
4. **Create Jira Ticket**: Track issues in your project management system

### GitHub Integration

#### Setup

1. Create a GitHub Personal Access Token with `repo` scope
2. Add token to `.env` file
3. Ensure you have write access to the target repository

#### Generating PRs

1. Navigate to Issues page
2. Select an issue with AI diagnosis
3. Click "Generate GitHub PR"
4. System will:
   - Fetch the target file
   - Generate AI-powered fix
   - Create a new branch
   - Commit changes
   - Create pull request

### Figma Integration

1. Get Figma access token from [Figma Settings](https://www.figma.com/settings)
2. Add token to `.env`
3. Navigate to Figma page
4. Enter Figma file URL
5. Click "Analyze Design"
6. Review AI-generated UX feedback

### Jira Integration

1. Create Jira API token from [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Configure Jira settings in `.env`
3. Click "Create Jira Ticket" on any diagnosed issue
4. Ticket will be created with full context and evidence

## 🏗️ Architecture

### Backend (Python/FastAPI)

```
app/
├── api/routes/          # API endpoints
├── core/                # Core utilities (logging, security)
├── integrations/        # External service clients
├── models/              # Pydantic data models
├── services/            # Business logic
└── utils/               # Helper functions
```

### Frontend (Vanilla JS)

```
frontend/
├── css/                 # Stylesheets
├── js/
│   ├── pages/          # Page-specific logic
│   ├── api-service.js  # API client
│   ├── router.js       # Client-side routing
│   └── utils.js        # Utility functions
└── index.html          # Main HTML file
```

### Key Components

- **Anomaly Detector**: Statistical analysis using Z-scores
- **Evidence Collector**: Gathers error logs, user behavior data
- **AI Diagnosis Service**: DeepSeek integration for root cause analysis
- **PR Generator**: Automated code fix generation
- **Issue Manager**: Lifecycle management for detected issues

## 🧪 Testing

### Run All Tests

```bash
# Move to tests directory
cd tests

# Run specific test
python test_system.py
python test_github_write.py
python test_figma_fixed.py
```

### Test Files

- `test_system.py`: End-to-end system test
- `test_github_write.py`: GitHub API access verification
- `test_figma_fixed.py`: Figma integration test
- `test_event_tracking.py`: Event ingestion test
- `test_pr_generation.py`: PR generation test

## 📊 API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

#### Events
- `POST /api/events` - Ingest user events
- `GET /api/events/types` - List event types

#### Issues
- `GET /api/issues` - List all issues
- `GET /api/issues/{id}` - Get issue details
- `POST /api/issues/detect` - Trigger anomaly detection
- `POST /api/issues/{id}/diagnose` - Run AI diagnosis

#### GitHub
- `POST /api/github/generate-pr-simple` - Generate PR for issue
- `GET /api/github/prs` - List pull requests

#### Jira
- `POST /api/jira/create-ticket/{issue_id}` - Create Jira ticket

#### Figma
- `POST /api/figma/review` - Analyze Figma design

## 🔧 Configuration

### Anomaly Detection Tuning

Adjust sensitivity in `.env`:

```env
MIN_DROP_PERCENT=12.0      # Minimum drop to trigger alert
MIN_SAMPLE_SIZE=100        # Minimum sessions required
SIGMA_THRESHOLD=2.0        # Statistical significance (2σ = 95%)
```

### AI Model Configuration

```env
DEEPSEEK_MODEL_CHAT=deepseek-chat        # For text analysis
DEEPSEEK_MODEL_VISION=deepseek-vl        # For image analysis
```

## 🐛 Troubleshooting

### GitHub PR Creation Fails

**Error**: `422 Unprocessable Entity`

**Solutions**:
1. Verify GitHub token has `repo` scope
2. Check you have write access to repository
3. Ensure branch doesn't already exist
4. Verify file path is correct

### Figma Analysis Errors

**Error**: `413 Request Entity Too Large`

**Solution**: Images are automatically compressed to <1MB

**Error**: `400 Invalid Request Format`

**Solution**: System uses text-based analysis instead of vision API

### Database Issues

**Error**: `table issues has no column named X`

**Solution**: Reinitialize database:
```bash
rm arguxai.db
python init_sqlite.py
```

### Rate Limiting

**Error**: `429 Too Many Requests`

**Solution**: System includes automatic rate limiting and retry logic

## 📝 Development

### Adding New Integrations

1. Create client in `app/integrations/`
2. Add models in `app/models/`
3. Create service in `app/services/`
4. Add API routes in `app/api/routes/`
5. Update frontend in `frontend/js/pages/`

### Code Style

- Python: Follow PEP 8
- JavaScript: Use ES6+ features
- Use type hints in Python
- Add docstrings to all functions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

- DeepSeek AI for powerful language models
- FastAPI for excellent Python web framework
- Convex for real-time database
- GitHub API for seamless integration

## 📞 Support

For issues and questions:
- GitHub Issues: [Your Repo Issues]
- Email: [Your Email]
- Documentation: [Your Docs URL]

---

**Built with ❤️ by the ArguxAI Team**
