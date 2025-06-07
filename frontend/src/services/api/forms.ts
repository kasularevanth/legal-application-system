// ============ src/services/api/forms.ts ============
import api from "./index";

export const formsAPI = {
  getTemplates: () => api.get("/forms/templates/"),

  getTemplate: (id: number) => api.get(`/forms/templates/${id}/`),

  getUserApplications: () => api.get("/forms/applications/"),

  getApplication: (id: number) => api.get(`/forms/applications/${id}/`),

  createApplication: (data: any) => api.post("/forms/applications/", data),

  updateApplication: (id: number, data: any) =>
    api.put(`/forms/applications/${id}/`, data),

  deleteApplication: (id: number) => api.delete(`/forms/applications/${id}/`),

  submitApplication: (id: number) =>
    api.post(`/forms/applications/${id}/submit/`),

  downloadApplication: (id: number) =>
    api.get(`/forms/applications/${id}/download/`, {
      responseType: "blob",
    }),
};
