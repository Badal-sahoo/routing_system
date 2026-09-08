import apiClient from "../../lib/apiClient";

export function fetchTasks() {
  return apiClient.get("tasks/").then((res) => res.data);
}

export function createTask(originNodeId, destinationNodeId) {
  return apiClient
    .post("tasks/", {
      origin_node_fk: originNodeId,
      destination_node_fk: destinationNodeId,
    })
    .then((res) => res.data);
}

export function dispatchTask(taskId) {
  return apiClient.post(`tasks/${taskId}/dispatch/`).then((res) => res.data);
}
