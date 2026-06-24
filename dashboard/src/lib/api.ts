/** API client for the Orbit Sentinel backend */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export const api = {
  // Dashboard
  getDashboardOverview: () =>
    apiFetch<import("./types").DashboardOverview>("/api/v1/dashboard/overview"),

  // Analyses
  getAnalyses: (params?: { status?: string; limit?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.set("status", params.status);
    if (params?.limit) searchParams.set("limit", String(params.limit));
    const qs = searchParams.toString();
    return apiFetch<import("./types").AnalysisResponse[]>(
      `/api/v1/analyses${qs ? `?${qs}` : ""}`
    );
  },

  getAnalysis: (id: string) =>
    apiFetch<import("./types").AnalysisDetail>(`/api/v1/analyses/${id}`),

  createAnalysis: (data: { project_id: number; mr_iid: number; project_name?: string }) =>
    apiFetch<import("./types").AnalysisResponse>("/api/v1/analyses", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Settings
  getSettings: () =>
    apiFetch<Record<string, unknown>>("/api/v1/settings"),

  // Health
  getHealth: () => apiFetch<{ status: string }>("/health"),
};
