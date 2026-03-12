import axios from "axios";
import { AnalysisRequest, AnalysisResponse } from "../types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8002";

console.log(`[VidyaMitra] API URL: ${API_BASE_URL}`);

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 120000,
});

// Request interceptor — logs every outgoing API call
apiClient.interceptors.request.use((config) => {
  console.group(`[VidyaMitra] ▶ ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
  if (config.data) {
    const body = typeof config.data === "string" ? JSON.parse(config.data) : config.data;
    console.log("Resume length:", body.resume_text?.length ?? 0, "chars");
    console.log("Job desc length:", body.job_description?.length ?? 0, "chars");
  }
  console.log("Timeout:", config.timeout, "ms");
  console.groupEnd();
  return config;
});

// Response interceptor — logs every API response
apiClient.interceptors.response.use(
  (response) => {
    const data = response.data as Partial<AnalysisResponse>;
    console.group(`[VidyaMitra] ✅ ${response.status} ${response.config.url}`);
    console.log("Match %:", data.match_percentage);
    console.log("Matched keywords:", data.matched_keywords?.length ?? 0);
    console.log("Missing keywords:", data.missing_keywords?.length ?? 0);
    console.log("Suggestions:", data.suggestions?.length ?? 0);
    console.groupEnd();
    return response;
  },
  (error) => {
    console.group(`[VidyaMitra] ❌ API Error`);
    console.error("URL:", error.config?.url);
    console.error("Status:", error.response?.status);
    console.error("Message:", error.response?.data?.detail || error.message);
    console.groupEnd();
    return Promise.reject(error);
  }
);

export const analyzeResume = async (
  data: AnalysisRequest,
): Promise<AnalysisResponse> => {
  console.log("[VidyaMitra] 🚀 Starting resume analysis...");
  const start = Date.now();
  try {
    const response = await apiClient.post<AnalysisResponse>("/analyze", data);
    console.log(`[VidyaMitra] ⏱ Analysis completed in ${Date.now() - start}ms`);
    return response.data;
  } catch (error) {
    console.error(`[VidyaMitra] ⏱ Failed after ${Date.now() - start}ms`);
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message;
      throw new Error(`Analysis failed: ${message}`);
    }
    throw new Error("An unexpected error occurred during analysis");
  }
};

export const checkHealth = async (): Promise<{ status: string }> => {
  console.log("[VidyaMitra] 🏥 Checking backend health...");
  try {
    const response = await apiClient.get("/health");
    console.log("[VidyaMitra] ✅ Backend healthy:", response.data);
    return response.data;
  } catch {
    console.error("[VidyaMitra] ❌ Backend health check failed");
    throw new Error("Backend health check failed");
  }
};
