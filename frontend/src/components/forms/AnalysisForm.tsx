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
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-gray-900">
          VidyaMitra Career Agent
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          AI-Powered Resume Evaluator, Trainer & Career Planner.
          Analyze keyword matches, get improvement suggestions, and
          boost your chances of landing interviews.
        </p>
        <div className="flex justify-center">
          <button
            onClick={loadSampleData}
            className="px-4 py-2 bg-blue-100 hover:bg-blue-200 text-blue-800 rounded-lg text-sm font-medium transition-colors"
          >
            📝 Try with Sample Data
          </button>
        </div>
      </div>

      {/* Input Section */}
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <ResumeInputForm
            value={resumeText}
            onChange={setResumeText}
            disabled={isLoading}
          />
          <JobDescriptionForm
            value={jobDescription}
            onChange={setJobDescription}
            disabled={isLoading}
          />
        </div>

        {/* Action Buttons */}
        <div className="mt-8 flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <AnalyzeButton
              onClick={handleAnalyze}
              isLoading={isLoading}
              disabled={!canAnalyze}
            />
            {!canAnalyze && (
              <p className="text-sm text-gray-500 mt-2 text-center">
                Please ensure both fields have at least 50 characters
              </p>
            )}
          </div>
          {(result || error) && (
            <button
              onClick={handleReset}
              className="px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors"
            >
              🔄 Reset
            </button>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-red-600 text-xl">❌</span>
            <h3 className="text-lg font-semibold text-red-800">
              Analysis Error
            </h3>
          </div>
          <p className="text-red-700">{error}</p>
          <button
            onClick={reset}
            className="mt-3 px-4 py-2 bg-red-100 hover:bg-red-200 text-red-800 rounded text-sm font-medium transition-colors"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Results Section */}
      {result && (
        <div className="space-y-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Analysis Results
            </h2>
            <p className="text-gray-600">
              Here&apos;s how your resume matches the job description
            </p>
          </div>

          {/* Match Percentage */}
          <MatchPercentage percentage={result.match_percentage} />

          {/* Keyword Analysis */}
          <div className="bg-white rounded-lg shadow-lg p-8">
            <KeywordComparison
              matchedKeywords={result.matched_keywords}
              missingKeywords={result.missing_keywords}
            />
          </div>

          {/* Bullet Suggestions */}
          <div className="bg-white rounded-lg shadow-lg p-8">
            <BulletSuggestions suggestions={result.suggestions} />
          </div>

          {/* Overall Feedback */}
          <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
            <div className="flex items-center space-x-2 mb-3">
              <span className="text-blue-600 text-xl">🎯</span>
              <h3 className="text-lg font-semibold text-blue-800">
                Overall Feedback
              </h3>
            </div>
            <p className="text-blue-700">{result.overall_feedback}</p>
          </div>

          {/* Strengths and Areas for Improvement */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Strengths */}
            {result.strengths && result.strengths.length > 0 && (
              <div className="bg-green-50 rounded-lg p-6 border border-green-200">
                <div className="flex items-center space-x-2 mb-3">
                  <span className="text-green-600 text-xl">💪</span>
                  <h3 className="text-lg font-semibold text-green-800">
                    Strengths
                  </h3>
                </div>
                <ul className="space-y-2">
                  {result.strengths.map((strength, index) => (
                    <li
                      key={index}
                      className="text-green-700 text-sm flex items-start space-x-2"
                    >
                      <span className="text-green-600 mt-0.5">•</span>
                      <span>{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Areas for Improvement */}
            {result.areas_for_improvement &&
              result.areas_for_improvement.length > 0 && (
                <div className="bg-yellow-50 rounded-lg p-6 border border-yellow-200">
                  <div className="flex items-center space-x-2 mb-3">
                    <span className="text-yellow-600 text-xl">🎯</span>
                    <h3 className="text-lg font-semibold text-yellow-800">
                      Areas for Improvement
                    </h3>
                  </div>
                  <ul className="space-y-2">
                    {result.areas_for_improvement.map((area, index) => (
                      <li
                        key={index}
                        className="text-yellow-700 text-sm flex items-start space-x-2"
                      >
                        <span className="text-yellow-600 mt-0.5">•</span>
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
  );
};

export default AnalysisForm;
