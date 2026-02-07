# ArguxAI Dashboard - Frontend Setup

## Quick Start

### 1. Start Backend API
```bash
# From ai-ux-flow directory
.\venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Serve Frontend
```bash
# From frontend directory
python -m http.server 8080
```

### 3. Open Browser
Navigate to: `http://localhost:8080`

## Features

### ✅ Dashboard
- Real-time metrics from backend
- Total events, sessions, funnels, issues
- Global conversion rate

### ✨ Funnels (NEW!)
- **Manual Funnel Creation**: Build funnels step-by-step
- **AI Funnel Generation**: 
  - Describe your funnel in natural language
  - Click "Enhance Prompt" to improve your description
  - Click "Generate Funnel" to create complete funnel structure
  - Preview and edit before saving
- View all funnels in a table
- Edit and delete funnels

### 📊 Other Pages
- **Issues**: Detected anomalies (connected to backend)
- **GitHub**: PR generation (placeholder)
- **Figma**: Design review (placeholder)
- **Reports**: Analytics (placeholder)
- **Settings**: API key management

## API Endpoints Used

- `GET /api/dashboard/metrics` - Dashboard stats
- `GET /api/funnels` - List funnels
- `POST /api/funnels` - Create funnel
- `POST /api/funnels/enhance-prompt` - AI prompt enhancement
- `POST /api/funnels/generate-ai` - AI funnel generation
- `DELETE /api/funnels/{id}` - Delete funnel
- `POST /api/issues/detect` - Detect anomalies

## Technology Stack

- **Frontend**: Vanilla JS, HTML5, CSS3
- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **AI**: DeepSeek API for funnel generation

## Rebranding

All references to "SynapseFlow" have been replaced with "ArguxAI" throughout the application.
