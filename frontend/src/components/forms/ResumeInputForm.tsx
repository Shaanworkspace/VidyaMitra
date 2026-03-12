"use client";

import { useState } from "react";

interface ResumeInputFormProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export const ResumeInputForm = ({
  value,
  onChange,
  disabled = false,
}: ResumeInputFormProps) => {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === "text/plain" || file.name.endsWith(".txt")) {
        const reader = new FileReader();
        reader.onload = (event) => onChange(event.target?.result as string);
        reader.readAsText(file);
      }
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => onChange(event.target?.result as string);
      reader.readAsText(file);
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <span className="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-indigo-100 text-indigo-700 text-sm font-bold">
          1
        </span>
        <label htmlFor="resume-text" className="text-base font-semibold text-slate-800">
          Your Resume
        </label>
      </div>

      <div
        className={`relative rounded-xl border-2 transition-all ${
          dragActive
            ? "border-indigo-400 bg-indigo-50"
            : "border-slate-200 hover:border-indigo-300"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <textarea
          id="resume-text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          style={{ color: '#1e293b', backgroundColor: '#ffffff' }}
          className="w-full h-64 p-4 rounded-xl border-0 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-400 disabled:opacity-50 disabled:cursor-not-allowed text-sm leading-relaxed"
          placeholder="Paste the full text of your resume here...

Include your work experience, education, skills, and achievements."
        />
        {dragActive && (
          <div className="absolute inset-0 flex items-center justify-center bg-indigo-50/95 rounded-xl">
            <div className="text-center">
              <p className="text-2xl mb-1">📄</p>
              <p className="text-indigo-600 font-semibold">Drop your .txt file here</p>
            </div>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between">
        <label className="cursor-pointer">
          <input
            type="file"
            accept=".txt,.text"
            onChange={handleFileUpload}
            disabled={disabled}
            className="hidden"
          />
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-lg text-xs font-medium transition-colors border border-slate-200 cursor-pointer">
            📁 Upload .txt file
          </span>
        </label>
        <span className="text-xs text-slate-400">
          {value.length > 0 ? `${value.length} characters` : "Drag & drop or paste text"}
        </span>
      </div>
    </div>
  );
};
