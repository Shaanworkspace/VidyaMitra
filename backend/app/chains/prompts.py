"""Prompt templates for resume analysis."""

from langchain_core.prompts import PromptTemplate

# Keyword extraction prompt
KEYWORD_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["text", "context"],
    template="""Extract the most important keywords and skills from the following {context}.
Focus on technical skills, tools, frameworks, soft skills, and domain-specific terms.

{context}:
{text}

Return a comma-separated list of keywords (maximum 30 keywords):
""",
)

# Match analysis prompt
MATCH_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=[
        "resume_keywords",
        "job_keywords",
        "resume_text",
        "job_description",
    ],
    template="""Analyze how well this resume matches the job description.

Job Description Keywords: {job_keywords}
Resume Keywords: {resume_keywords}

Full Job Description:
{job_description}

Full Resume:
{resume_text}

Provide a detailed analysis including:
1. Match percentage (0-100)
2. Matched keywords (found in both)
3. Missing important keywords (in JD but not resume)
4. Key strengths of the candidate
5. Areas that need improvement

Format your response as JSON with keys: 
- match_percentage: integer (0-100)
- matched_keywords: array of strings
- missing_keywords: array of strings  
- strengths: array of strings (each strength as separate item)
- improvements: array of strings (each improvement as separate item)

Example format:
{{
  "match_percentage": 75,
  "matched_keywords": ["Python", "AWS", "Docker"],
  "missing_keywords": ["Kubernetes", "React"],
  "strengths": ["Strong Python experience", "Cloud infrastructure knowledge"],
  "improvements": ["Add Kubernetes experience", "Include frontend skills"]
}}
""",
)

# Bullet point improvement prompt
BULLET_IMPROVEMENT_PROMPT = PromptTemplate(
    input_variables=["bullet_points", "job_description", "missing_keywords"],
    template="""Improve these resume bullet points to better match the job description.
Focus on incorporating missing keywords naturally and adding quantifiable results.

Job Description Context:
{job_description}

Missing Keywords to Incorporate: {missing_keywords}

Current Bullet Points:
{bullet_points}

For each bullet point, provide:
1. The original text
2. An improved version that:
   - Incorporates relevant missing keywords naturally
   - Adds specific metrics/numbers where possible
   - Uses strong action verbs
   - Demonstrates impact and results
3. A brief explanation of the improvements

Format as JSON array with objects containing: original, improved, reason
""",
)
