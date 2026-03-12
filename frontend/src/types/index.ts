export interface BulletSuggestion {
  original: string;
  improved: string;
  reason: string;
}

export interface AnalysisResponse {
  match_percentage: number;
  matched_keywords: string[];
  missing_keywords: string[];
  suggestions: BulletSuggestion[];
  strengths: string[];
  areas_for_improvement: string[];
  overall_feedback: string;
  processing_time?: number;
}

export interface AnalysisRequest {
  resume_text: string;
  job_description: string;
}

export interface AnalysisState {
  isLoading: boolean;
  result: AnalysisResponse | null;
  error: string | null;
}
