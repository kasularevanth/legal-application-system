// ============ src/services/api/auth.ts ============
import api from "./index";

export const authAPI = {
  login: (credentials: { username: string; password: string }) =>
    api.post("/auth/login/", credentials),

  register: (userData: any) => api.post("/auth/register/", userData),

  getProfile: () => api.get("/auth/profile/"),

  updateProfile: (data: any) => api.put("/auth/profile/", data),

  changePassword: (data: { old_password: string; new_password: string }) =>
    api.post("/auth/change-password/", data),
};
