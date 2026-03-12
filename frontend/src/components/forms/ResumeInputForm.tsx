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
        reader.onload = (event) => {
          const text = event.target?.result as string;
          onChange(text);
        };
        reader.readAsText(file);
      }
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const text = event.target?.result as string;
        onChange(text);
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <label
          htmlFor="resume-text"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Resume Content
        </label>
        <div
          className={`relative ${
            dragActive ? "border-blue-500 bg-blue-50" : "border-gray-300"
          } border-2 border-dashed rounded-lg transition-colors`}
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
            className="w-full h-64 p-4 border-0 resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent rounded-lg bg-transparent"
            placeholder="Paste your resume text here, or drag and drop a .txt file..."
          />
          {dragActive && (
            <div className="absolute inset-0 flex items-center justify-center bg-blue-50 bg-opacity-90 rounded-lg">
              <p className="text-blue-600 font-medium">
                Drop your resume file here
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <label className="flex items-center cursor-pointer">
          <input
            type="file"
            accept=".txt,.text"
            onChange={handleFileUpload}
            disabled={disabled}
            className="hidden"
          />
          <div className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium text-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
            📁 Upload Text File
          </div>
        </label>
        <span className="text-xs text-gray-500">Supports .txt files</span>
      </div>
    </div>
  );
};
