"use client";

interface MatchPercentageProps {
  percentage: number;
}

export const MatchPercentage = ({ percentage }: MatchPercentageProps) => {
  const getColorClass = (percent: number) => {
    if (percent >= 80) return "text-green-600";
    if (percent >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  const getBackgroundColor = (percent: number) => {
    if (percent >= 80) return "bg-green-100";
    if (percent >= 60) return "bg-yellow-100";
    return "bg-red-100";
  };

  const getBorderColor = (percent: number) => {
    if (percent >= 80) return "border-green-200";
    if (percent >= 60) return "border-yellow-200";
    return "border-red-200";
  };

  const getProgressColor = (percent: number) => {
    if (percent >= 80) return "stroke-green-600";
    if (percent >= 60) return "stroke-yellow-600";
    return "stroke-red-600";
  };

  // SVG circle parameters
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div
      className={`p-6 rounded-lg border-2 ${getBackgroundColor(percentage)} ${getBorderColor(percentage)}`}
    >
      <div className="flex items-center justify-center space-x-6">
        <div className="relative">
          <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 100 100">
            {/* Background circle */}
            <circle
              cx="50"
              cy="50"
              r={radius}
              stroke="currentColor"
              strokeWidth="8"
              fill="transparent"
              className="text-gray-200"
            />
            {/* Progress circle */}
            <circle
              cx="50"
              cy="50"
              r={radius}
              stroke="currentColor"
              strokeWidth="8"
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className={`${getProgressColor(percentage)} transition-all duration-1000 ease-in-out`}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={`text-2xl font-bold ${getColorClass(percentage)}`}>
              {percentage}%
            </span>
          </div>
        </div>

        <div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">
            Resume Match Score
          </h3>
          <p className="text-sm text-gray-600">
            {percentage >= 80 &&
              "Excellent match! Your resume aligns well with the job requirements."}
            {percentage >= 60 &&
              percentage < 80 &&
              "Good match! Consider incorporating more relevant keywords."}
            {percentage < 60 &&
              "Needs improvement. Focus on highlighting relevant skills and experience."}
          </p>
        </div>
      </div>
    </div>
  );
};
