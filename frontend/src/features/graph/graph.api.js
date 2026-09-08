import apiClient from "../../lib/apiClient";

export function fetchNodes() {
  return apiClient.get("nodes/").then((res) => res.data);
}

export function fetchEdges() {
  return apiClient.get("edges/").then((res) => res.data);
}
