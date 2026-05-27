import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api";
const DEFAULT_TENANT_ID = "00000000-0000-0000-0000-000000000001";

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
    "X-Tenant-ID": DEFAULT_TENANT_ID,
  },
  timeout: 30000,
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || "An error occurred";
    return Promise.reject(new Error(message));
  }
);

// Intake
export const submitIntake = (data: object) =>
  apiClient.post("/v1/intake", data).then((r) => r.data);

export const getIntakeStatus = (companyId: string) =>
  apiClient.get(`/v1/intake/${companyId}`).then((r) => r.data);

// Intelligence
export const getIntelligence = (companyId: string) =>
  apiClient.get(`/v1/intelligence/${companyId}`).then((r) => r.data);

// Positioning
export const getPositioning = (companyId: string) =>
  apiClient.get(`/v1/positioning/${companyId}`).then((r) => r.data);

export const approvePositioning = (companyId: string) =>
  apiClient.put(`/v1/positioning/${companyId}/approve`).then((r) => r.data);

// ICP
export const getICPs = (companyId: string) =>
  apiClient.get(`/v1/icp/${companyId}`).then((r) => r.data);

// Target Discovery
export const getTargetCompanies = (companyId: string) =>
  apiClient.get(`/v1/targets/${companyId}/companies`).then((r) => r.data);

export const getTargetContacts = (companyId: string) =>
  apiClient.get(`/v1/targets/${companyId}/contacts`).then((r) => r.data);

// Campaign Context
export const getCampaignContext = (companyId: string) =>
  apiClient.get(`/v1/campaign/${companyId}`).then((r) => r.data);

// Workflow
export const getWorkflowStatus = (runId: string) =>
  apiClient.get(`/v1/workflow/${runId}`).then((r) => r.data);
