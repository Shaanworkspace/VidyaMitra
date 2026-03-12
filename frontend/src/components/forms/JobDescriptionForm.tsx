"use client";

interface JobDescriptionFormProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export const JobDescriptionForm = ({
  value,
  onChange,
  disabled = false,
}: JobDescriptionFormProps) => {
  return (
    <div className="space-y-4">
      <div>
        <label
          htmlFor="job-description"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Job Description
        </label>
        <textarea
          id="job-description"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          className="w-full h-64 p-4 border-2 border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors disabled:opacity-50 disabled:bg-gray-50"
          placeholder="Paste the job description here..."
        />
      </div>

      <div className="flex items-center space-x-2">
        <span className="text-xs text-gray-500">
          💡 Include requirements, responsibilities, and preferred
          qualifications for best results
        </span>
      </div>
    </div>
  );
};
