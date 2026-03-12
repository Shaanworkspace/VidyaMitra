"use client";

interface AnalyzeButtonProps {
  onClick: () => void;
  isLoading: boolean;
  disabled?: boolean;
}

export const AnalyzeButton = ({
  onClick,
  isLoading,
  disabled = false,
}: AnalyzeButtonProps) => {
  const isDisabled = disabled || isLoading;

  return (
    <button
      onClick={onClick}
      disabled={isDisabled}
      className={`
        w-full px-6 py-4 rounded-xl font-semibold text-lg transition-all duration-200
        flex items-center justify-center space-x-2
        ${
          isDisabled
            ? "bg-slate-200 text-slate-400 cursor-not-allowed"
            : "bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
        }
      `}
    >
      {isLoading ? (
        <>
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
          <span>Analyzing Resume...</span>
        </>
      ) : (
        <>
          <span>🚀</span>
          <span>Analyze Resume</span>
        </>
      )}
    </button>
  );
};
