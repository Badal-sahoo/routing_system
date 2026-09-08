import { useState } from "react";

import { useAgents } from "../agents/agents.hooks";
import { useNodeLabels, useNodes } from "../graph/graph.hooks";
import { formatEta, useTaskActions, useTasks } from "./tasks.hooks";

export default function TaskPanel() {
  const nodes = useNodes();
  const nodeLabels = useNodeLabels();
  const agents = useAgents();
  const tasks = useTasks();
  const { error, reload, create, dispatch, dispatchingId } = useTaskActions();

  const [originId, setOriginId] = useState("");
  const [destinationId, setDestinationId] = useState("");

  const handleCreate = async (event) => {
    event.preventDefault();
    if (!originId || !destinationId) return;

    const result = await create(originId, destinationId);
    if (result === "created" || result === "stale") {
      setOriginId("");
      setDestinationId("");
    }
  };

  return (
    <div style={{ padding: "0.75rem" }}>
      <h2 style={{ fontSize: "1rem", marginBottom: "0.5rem" }}>
        Tasks <span style={{ opacity: 0.5, fontWeight: 400 }}>({tasks.length})</span>
      </h2>

      <form
        onSubmit={handleCreate}
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "0.4rem",
          marginBottom: "0.75rem",
        }}
      >
        <select value={originId} onChange={(event) => setOriginId(event.target.value)}>
          <option value="">Origin</option>
          {nodes.map((node) => (
            <option key={node.id} value={node.id}>
              {node.label}
            </option>
          ))}
        </select>

        <select
          value={destinationId}
          onChange={(event) => setDestinationId(event.target.value)}
        >
          <option value="">Destination</option>
          {nodes.map((node) => (
            <option key={node.id} value={node.id}>
              {node.label}
            </option>
          ))}
        </select>

        <button type="submit" disabled={!originId || !destinationId}>
          Create
        </button>
        <button type="button" onClick={reload}>
          Refresh
        </button>
      </form>

      {error && (
        <p style={{ color: "#dc2626", fontSize: "0.8rem", margin: "0 0 0.5rem" }}>
          {error}
        </p>
      )}

      {tasks.length === 0 && <p style={{ opacity: 0.6 }}>No tasks yet.</p>}

      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {tasks.map((task) => {
          const rider = agents.find((agent) => agent.id === task.assigned_agent_fk);
          const eta = formatEta(task);

          return (
            <li
              key={task.id}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                gap: "0.5rem",
                padding: "0.4rem 0",
                borderBottom: "1px solid #e5e7eb",
              }}
            >
              <span style={{ fontSize: "0.85rem" }}>
                <span style={{ opacity: 0.5 }}>#{task.id}</span>{" "}
                {nodeLabels[task.origin_node_fk] ?? task.origin_node_fk} &rarr;{" "}
                {nodeLabels[task.destination_node_fk] ?? task.destination_node_fk}
                <br />
                <em style={{ opacity: 0.7 }}>{task.status}</em>
                {rider && <span style={{ opacity: 0.7 }}> · {rider.name}</span>}
                {eta && (
                  <span
                    title={`${task.pickup_eta_minutes} min to the pickup, then ${task.delivery_eta_minutes} min to the drop-off`}
                    style={{ opacity: 0.7 }}
                  >
                    {" "}
                    · {eta}
                  </span>
                )}
              </span>

              <button
                disabled={task.status !== "pending" || dispatchingId === task.id}
                onClick={() => dispatch(task.id)}
              >
                {dispatchingId === task.id ? "Dispatching..." : "Dispatch"}
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
