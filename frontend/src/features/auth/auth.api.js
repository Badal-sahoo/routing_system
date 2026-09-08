import axios from "axios";

import { API_URL } from "../../lib/config";

const authClient = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

export function login(username, password) {
  return authClient.post("token/", { username, password }).then((res) => res.data);
}

export function refreshAccessToken(refresh) {
  return authClient.post("token/refresh/", { refresh }).then((res) => res.data);
}
