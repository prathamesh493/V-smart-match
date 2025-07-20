# VSmart Backend

A backend service for parsing resumes, matching with job descriptions, and aggregating developer profiles from GitHub and LeetCode.

## Project Structure

```
vsmart-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # App entry point (FastAPI/Flask)
│   └── config.py               # Env vars, API keys (Gemini, etc.)
│
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── resume.py           # Resume upload → Gemini parsing → return data
│   │   ├── match.py            # Resume-JD matching logic
│   │   ├── profile.py          # GitHub & LeetCode data fetch
│   │   └── health.py           # Basic health check
│   └── schemas/
│       ├── resume.py           # Request/response models for resume
│       ├── match.py            # Job description + match response
│       └── profile.py          # GitHub/LeetCode profile models
│
├── services/
│   ├── gemini.py               # Gemini API wrapper for parsing & extraction
│   ├── matcher.py              # Matching logic (resume ↔ JD)
│   ├── github.py               # GitHub API integration
│   ├── leetcode.py             # LeetCode scraping/API
│   └── profile_aggregator.py   # Combine GitHub + LeetCode info
│
├── data/
│   ├── resumes/                # Temporary uploaded resumes
│   └── jd/                     # Static or example job descriptions
│
├── tests/
│   ├── test_resume.py
│   ├── test_match.py
│   └── test_profiles.py
│
├── requirements.txt            # Project dependencies
├── .env                        # API keys, config
└── README.md
```

## Setup and Installation

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file with the following variables:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   GITHUB_API_TOKEN=your_github_token
   ```

4. Run the application:
   ```bash
   python -m app.main
   ```

## API Endpoints

- `POST /api/resume/upload` - Upload and parse resume
- `POST /api/match` - Match resume with job description
- `GET /api/profile/{username}` - Get developer profile from GitHub and LeetCode
- `GET /api/health` - Health check endpoint

### MCQ Generation Endpoints
- `POST /api/mcq/generate` - Generate MCQ questions for skills assessment
- `POST /api/mcq/validate` - Validate question quality
- `POST /api/mcq/detect-duplicates` - Detect duplicate questions
- `GET /api/mcq/supported-skills` - Get list of supported skills
- `GET /api/mcq/batch-generate` - Generate questions for multiple skills

## Development

### Running Tests
```bash
pytest
```


## Observability & Monitoring

# 🚀 Instrumented Backend with OpenTelemetry, Jaeger, and Prometheus

This project provides a backend web service instrumented with OpenTelemetry. It includes a full local observability stack with:

- **Jaeger** — Distributed tracing UI
- **Prometheus** — Metrics storage and query UI
- **Otel Collector** — Telemetry pipeline and collector

---

## 🏗️ Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/) (comes baked into Docker Desktop)
- (Optional) Python 3.12+ and `pip` (if you want to run the backend locally, not in Docker)


2. **Start the full stack**

    ```
    docker-compose down  # clear any previous run
    docker-compose up --build
    ```

    *Wait ~30 seconds for all services to come up.*

3. **Access the services:**

    - **Backend API**: [http://localhost:8000](http://localhost:8000)
    - **Jaeger UI (tracing)**: [http://localhost:16686](http://localhost:16686)
    - **Prometheus UI (metrics)**: [http://localhost:9090](http://localhost:9090)


## Features

- Resume parsing using Google's Gemini AI
- Resume to Job Description matching
- Developer profile aggregation from GitHub and LeetCode
- **AI-powered MCQ generation engine** for skills assessment
- API for integrating with frontend applications

### MCQ Generation Engine

The AI-powered MCQ generation engine creates relevant multiple-choice questions for:
- **Technical skills**: Python, JavaScript, React, AWS, etc.
- **Soft skills**: Leadership, Communication, Teamwork, etc.
- **Different question types**: Technical, scenario-based, code-based
- **Multiple difficulty levels**: Beginner, intermediate, advanced
- **Multi-language support**: Generate questions in different languages

See [MCQ Generation Documentation](docs/MCQ_GENERATION.md) for detailed usage.