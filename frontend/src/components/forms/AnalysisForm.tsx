"use client";

import { useState } from "react";
import { ResumeInputForm } from "./ResumeInputForm";
import { JobDescriptionForm } from "./JobDescriptionForm";
import { AnalyzeButton } from "./AnalyzeButton";
import { MatchPercentage } from "../results/MatchPercentage";
import { KeywordComparison } from "../results/KeywordComparison";
import { BulletSuggestions } from "../results/BulletSuggestions";
import { useAnalyzeResume } from "../../hooks/useAnalyzeResume";
import { sampleResume, sampleJobDescription } from "../../lib/sampleData";

export const AnalysisForm = () => {
  const [resumeText, setResumeText] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const { isLoading, result, error, analyze, reset } = useAnalyzeResume();

  const handleAnalyze = async () => {
    if (!resumeText.trim() || !jobDescription.trim()) {
      alert("Please fill in both the resume and job description fields.");
      return;
    }

    await analyze({
      resume_text: resumeText,
      job_description: jobDescription,
    });
  };

  const handleReset = () => {
    setResumeText("");
    setJobDescription("");
    reset();
  };

  const loadSampleData = () => {
    setResumeText(sampleResume);
    setJobDescription(sampleJobDescription);
    reset();
  };

  const canAnalyze =
    resumeText.trim().length >= 50 && jobDescription.trim().length >= 50;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 py-10 space-y-6">

        {/* Header */}
        <div className="text-center py-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-indigo-600 rounded-2xl shadow-lg mb-4">
            <span className="text-3xl">🎓</span>
          </div>
          <h1 className="text-5xl font-bold text-slate-900 mb-3">
            Vidya<span className="text-indigo-600">Mitra</span>
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto mb-6">
            AI-Powered Resume Evaluator &amp; Career Planner — analyze keyword matches,
            get improvement suggestions, and boost your interview chances.
          </p>
          <button
            onClick={loadSampleData}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-white border border-indigo-200 hover:bg-indigo-50 text-indigo-700 rounded-full text-sm font-medium shadow-sm transition-all hover:shadow-md"
          >
            📝 Try with Sample Data
          </button>
        </div>

        {/* Input Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-2xl shadow-md border border-slate-100 p-6">
            <ResumeInputForm
              value={resumeText}
              onChange={setResumeText}
              disabled={isLoading}
            />
          </div>
          <div className="bg-white rounded-2xl shadow-md border border-slate-100 p-6">
            <JobDescriptionForm
              value={jobDescription}
              onChange={setJobDescription}
              disabled={isLoading}
            />
          </div>
        </div>

        {/* Analyze + Reset */}
        <div className="bg-white rounded-2xl shadow-md border border-slate-100 p-6">
          <AnalyzeButton
            onClick={handleAnalyze}
            isLoading={isLoading}
            disabled={!canAnalyze}
          />
          {!canAnalyze && !isLoading && (
            <p className="text-sm text-slate-400 mt-3 text-center">
              Both fields need at least 50 characters to analyze
            </p>
          )}
          {(result || error) && (
            <div className="mt-4 flex justify-center">
              <button
                onClick={handleReset}
                className="px-5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-lg text-sm font-medium transition-colors"
              >
                🔄 Start Over
              </button>
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-5 rounded-2xl">
            <p className="font-semibold text-red-800 mb-1">⚠️ Analysis Error</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-slate-900 mb-1">Analysis Results</h2>
              <p className="text-slate-500 text-sm">Here&apos;s how your resume matches the job description</p>
            </div>

            <div className="bg-white rounded-2xl shadow-md border border-slate-100 p-6">
              <MatchPercentage percentage={result.match_percentage} />
            </div>

            <div className="bg-white rounded-2xl shadow-md border border-slate-100 p-6">
              <KeywordComparison
                matchedKeywords={result.matched_keywords}
                missingKeywords={result.missing_keywords}
              />
            </div>

            {result.suggestions && result.suggestions.length > 0 && (
              <div className="bg-white rounded-2xl shadow-md border border-slate-100 p-6">
                <BulletSuggestions suggestions={result.suggestions} />
              </div>
            )}

            {result.overall_feedback && (
              <div className="bg-indigo-50 rounded-2xl p-6 border border-indigo-100">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-indigo-600 text-xl">🎯</span>
                  <h3 className="text-lg font-semibold text-indigo-800">Overall Feedback</h3>
                </div>
                <p className="text-indigo-700 text-sm leading-relaxed">{result.overall_feedback}</p>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {result.strengths && result.strengths.length > 0 && (
                <div className="bg-green-50 rounded-2xl p-6 border border-green-100">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-green-600 text-xl">💪</span>
                    <h3 className="text-lg font-semibold text-green-800">Strengths</h3>
                  </div>
                  <ul className="space-y-2">
                    {result.strengths.map((strength, index) => (
                      <li key={index} className="text-green-700 text-sm flex items-start gap-2">
                        <span className="text-green-500 mt-0.5 shrink-0">✓</span>
                        <span>{strength}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {result.areas_for_improvement && result.areas_for_improvement.length > 0 && (
                <div className="bg-amber-50 rounded-2xl p-6 border border-amber-100">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-amber-600 text-xl">📈</span>
                    <h3 className="text-lg font-semibold text-amber-800">Areas to Improve</h3>
                  </div>
                  <ul className="space-y-2">
                    {result.areas_for_improvement.map((area, index) => (
                      <li key={index} className="text-amber-700 text-sm flex items-start gap-2">
                        <span className="text-amber-500 mt-0.5 shrink-0">→</span>
                        <span>{area}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalysisForm;
