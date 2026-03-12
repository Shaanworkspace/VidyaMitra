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
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <span className="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-purple-100 text-purple-700 text-sm font-bold">
          2
        </span>
        <label htmlFor="job-description" className="text-base font-semibold text-slate-800">
          Job Description
        </label>
      </div>

      <textarea
        id="job-description"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        style={{ color: '#1e293b', backgroundColor: '#ffffff' }}
        className="w-full h-64 p-4 rounded-xl border-2 border-slate-200 hover:border-purple-300 resize-none focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm leading-relaxed"
        placeholder="Paste the job description here...

Include requirements, responsibilities, and qualifications for best results."
      />

      <div className="flex items-center justify-between">
        <span className="text-xs text-slate-500">
          💡 Include all skills and requirements from the job posting
        </span>
        <span className="text-xs text-slate-400">
          {value.length > 0 ? `${value.length} characters` : ""}
        </span>
      </div>
    </div>
  );
};
