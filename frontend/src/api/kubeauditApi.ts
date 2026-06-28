import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("kubeaudit_token");
      delete api.defaults.headers.common.Authorization;

      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
}

export async function login(email: string, password: string) {
  const response = await api.post("/auth/login", {
    email,
    password,
  });

  return response.data;
}

export async function getAuditSummary(auditId: number) {
  const response = await api.get(`/dashboard/audits/${auditId}/summary`);
  return response.data;
}

export async function getCluster(clusterId: number) {
  const response = await api.get(`/clusters/${clusterId}`);
  return response.data;
}

export async function getClusterHistory(clusterId: number) {
  const response = await api.get(`/dashboard/clusters/${clusterId}/history`);
  return response.data;
}

export async function getControlComparison(baseAuditId: number, targetAuditId: number) {
  const response = await api.get(
    `/dashboard/audits/compare-controls?base_audit_id=${baseAuditId}&target_audit_id=${targetAuditId}`
  );
  return response.data;
}

export async function getRemediationPlan(auditId: number) {
  const response = await api.get(
    `/dashboard/audits/${auditId}/remediation-plan?limit=10`
  );
  return response.data;
}

export async function getExecutiveSummary(auditId: number) {
  const response = await api.get(`/reports/audits/${auditId}/executive-summary`);
  return response.data;
}

export async function getMarkdownReport(auditId: number) {
  const response = await api.get(`/reports/audits/${auditId}/markdown`, {
    responseType: "text",
  });

  return response.data;
}

export async function getJsonReport(
  auditId: number,
  findingLimit = 200,
  remediationLimit = 100
) {
  const response = await api.get(`/reports/audits/${auditId}/json`, {
    params: {
      finding_limit: findingLimit,
      remediation_limit: remediationLimit,
    },
  });

  return response.data;
}

export type RecommendationStatus = "PENDING" | "APPLIED" | "DISMISSED";

export async function updateRecommendationStatus(
  recommendationId: number,
  status: RecommendationStatus
) {
  const response = await api.patch(
    `/recommendations/${recommendationId}/status`,
    {
      status,
    }
  );

  return response.data;
}

export async function getAuditLogs(params?: {
  limit?: number;
  action?: string;
  entity_type?: string;
  entity_id?: number;
}) {
  const response = await api.get("/audit-logs", {
    params: {
      limit: params?.limit || 50,
      action: params?.action || undefined,
      entity_type: params?.entity_type || undefined,
      entity_id: params?.entity_id || undefined,
    },
  });

  return response.data;
}

export async function importKubeBenchJson(clusterId: number, file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/audits/upload", formData, {
    params: {
      cluster_id: clusterId,
    },
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
}

export async function runKubeBenchAudit(clusterId: number) {
  const response = await api.post("/audits/run-kube-bench", null, {
    params: {
      cluster_id: clusterId,
    },
  });

  return response.data;
}