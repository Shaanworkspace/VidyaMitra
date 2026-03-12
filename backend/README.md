# Resume Analyzer Backend

## Setup Instructions

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

4. **Run the server:**
```bash
uvicorn app.main:app --reload
# Or simply: python -m app.main
```

## API Endpoints

### POST /analyze
Analyze a resume against a job description.

**Request Body:**
```json
{
  "resume_text": "Your resume content...",
  "job_description": "Job description content..."
}
```

**Response:**
```json
{
  "match_percentage": 85.0,
  "matched_keywords": ["Python", "Machine Learning"],
  "missing_keywords": ["TensorFlow", "PyTorch"],
  "suggestions": [
    {
      "original": "Worked on ML projects",
      "improved": "Developed 3 TensorFlow models achieving 95% accuracy",
      "reason": "Adds specific framework and quantifiable results"
    }
  ],
  "strengths": ["Strong Python skills", "Relevant experience"],
  "areas_for_improvement": ["Add specific ML frameworks"],
  "overall_feedback": "Your resume shows a good match..."
}
```

### GET /health
Health check endpoint.

## Testing

Run tests with:
```bash
pytest
```
