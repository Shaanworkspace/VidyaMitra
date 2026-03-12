# Project Structure

```
ai-resume-analyzer-with-langchain/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Configuration
│   │   ├── models.py            # Pydantic models
│   │   ├── chains/
│   │   │   ├── __init__.py
│   │   │   ├── analyzer.py      # Main analysis chain
│   │   │   ├── suggester.py     # Suggestion generation
│   │   │   └── prompts.py       # Prompt templates
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── text_processor.py
│   │       └── embeddings.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Main page
│   │   ├── layout.tsx
│   │   └── api/
│   │       └── analyze/
│   │           └── route.ts     # API proxy
│   ├── components/
│   │   ├── ResumeInput.tsx
│   │   ├── JobDescriptionInput.tsx
│   │   ├── AnalysisResults.tsx
│   │   ├── MatchScore.tsx
│   │   ├── SuggestionCard.tsx
│   │   └── ui/                  # shadcn components
│   ├── lib/
│   │   ├── api-client.ts
│   │   └── utils.ts
│   ├── public/
│   ├── package.json
│   └── tsconfig.json
│
├── examples/
│   ├── sample_resume.txt
│   └── sample_job_description.txt
│
├── .gitignore
├── README.md
└── IMPLEMENTATION_PLAN.md
```
