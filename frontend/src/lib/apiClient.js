import axios from "axios";

import { API_URL } from "./config";
import * as tokenStorage from "./tokenStorage";
import { refreshAccessToken } from "../features/auth/auth.api";

const apiClient = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

apiClient.interceptors.request.use((config) => {
  const accessToken = tokenStorage.getAccessToken();
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

let refreshPromise = null;

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;
    const refreshToken = tokenStorage.getRefreshToken();

    if (status !== 401 || originalRequest?._retried || !refreshToken) {
      if (status === 401 && !refreshToken) {
        tokenStorage.clearTokens();
      }
      return Promise.reject(error);
    }

    originalRequest._retried = true;

    try {
      if (!refreshPromise) {
        refreshPromise = refreshAccessToken(refreshToken).finally(() => {
          refreshPromise = null;
        });
      }

      const { access } = await refreshPromise;
      tokenStorage.setTokens({ access });

      originalRequest.headers.Authorization = `Bearer ${access}`;
      return apiClient(originalRequest);
    } catch (refreshError) {
      tokenStorage.clearTokens();
      return Promise.reject(refreshError);
    }
  }
);

export default apiClient;
