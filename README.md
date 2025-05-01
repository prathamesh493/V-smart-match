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

## Development

### Running Tests
```bash
pytest
```

## Features

- Resume parsing using Google's Gemini AI
- Resume to Job Description matching
- Developer profile aggregation from GitHub and LeetCode
- API for integrating with frontend applications