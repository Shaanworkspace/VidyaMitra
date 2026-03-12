"use client";

import { useState } from "react";
import { BulletSuggestion } from "../../types";

interface BulletSuggestionsProps {
  suggestions: BulletSuggestion[];
}

export const BulletSuggestions = ({ suggestions }: BulletSuggestionsProps) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const copyToClipboard = async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  if (suggestions.length === 0) {
    return (
      <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
        <h3 className="text-xl font-semibold text-gray-800 mb-2">
          Bullet Point Suggestions
        </h3>
        <p className="text-gray-600">
          No specific bullet point improvements available at this time.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold text-gray-800">
        Bullet Point Improvements
      </h3>

      <div className="space-y-6">
        {suggestions.map((suggestion, index) => (
          <div
            key={index}
            className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm"
          >
            <div className="space-y-4">
              {/* Original */}
              <div className="bg-red-50 p-4 rounded-lg border-l-4 border-red-400">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold text-red-800 mb-2">
                      ❌ Original
                    </h4>
                    <p className="text-red-700 text-sm">
                      {suggestion.original}
                    </p>
                  </div>
                </div>
              </div>

              {/* Improved */}
              <div className="bg-green-50 p-4 rounded-lg border-l-4 border-green-400">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold text-green-800 mb-2">
                      ✅ Improved
                    </h4>
                    <p className="text-green-700 text-sm">
                      {suggestion.improved}
                    </p>
                  </div>
                  <button
                    onClick={() => copyToClipboard(suggestion.improved, index)}
                    className="ml-3 px-3 py-1 bg-green-100 hover:bg-green-200 text-green-800 rounded text-xs font-medium transition-colors"
                  >
                    {copiedIndex === index ? "✓ Copied" : "📋 Copy"}
                  </button>
                </div>
              </div>

              {/* Reason */}
              <div className="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-400">
                <h4 className="text-sm font-semibold text-blue-800 mb-2">
                  💡 Why This Works
                </h4>
                <p className="text-blue-700 text-sm">{suggestion.reason}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Usage Tips */}
      <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
        <div className="flex items-center space-x-2 mb-2">
          <span className="text-yellow-600 text-lg">💡</span>
          <h4 className="text-md font-semibold text-yellow-800">Usage Tips</h4>
        </div>
        <ul className="text-yellow-700 text-sm space-y-1">
          <li>
            • Use the &ldquo;Copy&rdquo; button to easily add improved bullet
            points to your resume
          </li>
          <li>
            • Focus on quantifiable achievements and specific technologies
          </li>
          <li>
            • Tailor the language to match the job description&apos;s tone
          </li>
          <li>• Consider the industry context when implementing suggestions</li>
        </ul>
      </div>
    </div>
  );
};
