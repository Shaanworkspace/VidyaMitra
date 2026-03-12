import { useState } from "react";
import { analyzeResume } from "../lib/api";
import { AnalysisRequest, AnalysisState } from "../types";

export const useAnalyzeResume = () => {
  const [state, setState] = useState<AnalysisState>({
    isLoading: false,
    result: null,
    error: null,
  });

  const analyze = async (data: AnalysisRequest) => {
    setState({
      isLoading: true,
      result: null,
      error: null,
    });

    try {
      const result = await analyzeResume(data);
      setState({
        isLoading: false,
        result,
        error: null,
      });
    } catch (error) {
      setState({
        isLoading: false,
        result: null,
        error:
          error instanceof Error
            ? error.message
            : "An unexpected error occurred",
      });
    }
  };

  const reset = () => {
    setState({
      isLoading: false,
      result: null,
      error: null,
    });
  };

  return {
    ...state,
    analyze,
    reset,
  };
};
