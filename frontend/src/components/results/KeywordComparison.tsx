"use client";

interface KeywordComparisonProps {
  matchedKeywords: string[];
  missingKeywords: string[];
}

export const KeywordComparison = ({
  matchedKeywords,
  missingKeywords,
}: KeywordComparisonProps) => {
  return (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold text-gray-800">Keyword Analysis</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Matched Keywords */}
        <div className="bg-green-50 p-6 rounded-lg border border-green-200">
          <div className="flex items-center space-x-2 mb-4">
            <span className="text-green-600 text-xl">✅</span>
            <h4 className="text-lg font-semibold text-green-800">
              Matched Keywords ({matchedKeywords.length})
            </h4>
          </div>
          {matchedKeywords.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {matchedKeywords.map((keyword, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium border border-green-300"
                >
                  {keyword}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-green-600 text-sm">No matched keywords found</p>
          )}
        </div>

        {/* Missing Keywords */}
        <div className="bg-red-50 p-6 rounded-lg border border-red-200">
          <div className="flex items-center space-x-2 mb-4">
            <span className="text-red-600 text-xl">❌</span>
            <h4 className="text-lg font-semibold text-red-800">
              Missing Keywords ({missingKeywords.length})
            </h4>
          </div>
          {missingKeywords.length > 0 ? (
            <>
              <div className="flex flex-wrap gap-2 mb-3">
                {missingKeywords.map((keyword, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium border border-red-300"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
              <p className="text-red-600 text-xs">
                💡 Consider incorporating these keywords into your resume
              </p>
            </>
          ) : (
            <p className="text-red-600 text-sm">
              Great! No missing keywords detected
            </p>
          )}
        </div>
      </div>

      {/* Summary */}
      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
        <div className="flex items-center space-x-2 mb-2">
          <span className="text-blue-600 text-lg">📊</span>
          <h4 className="text-md font-semibold text-blue-800">Summary</h4>
        </div>
        <p className="text-blue-700 text-sm">
          Your resume contains <strong>{matchedKeywords.length}</strong>{" "}
          relevant keywords and is missing{" "}
          <strong>{missingKeywords.length}</strong> important terms from the job
          description.
          {missingKeywords.length > 0 && (
            <span className="block mt-1">
              Focus on naturally incorporating the missing keywords to improve
              your match score.
            </span>
          )}
        </p>
      </div>
    </div>
  );
};
