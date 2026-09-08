import apiClient from "../../lib/apiClient";

export function fetchAgents() {
  return apiClient.get("agents/").then((res) => res.data);
}

export function sendAgentLocation(agentId, { lat, lng }) {
  return apiClient
    .post(`agents/${agentId}/location/`, { lat, lng })
    .then((res) => res.data);
}
