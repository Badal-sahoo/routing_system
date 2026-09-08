import { useNodeLabels } from "../graph/graph.hooks";
import { useTasksByAgent } from "../tasks/tasks.hooks";
import { AGENT_STATUS_COLOR, formatLiveLocation, useAgents } from "./agents.hooks";

export default function AgentPanel() {
  const agents = useAgents();
  const nodeLabels = useNodeLabels();
  const tasksByAgent = useTasksByAgent();

  return (
    <div style={{ padding: "0.75rem" }}>
      <h2 style={{ fontSize: "1rem", marginBottom: "0.5rem" }}>
        Agents <span style={{ opacity: 0.5, fontWeight: 400 }}>({agents.length})</span>
      </h2>

      {agents.length === 0 && <p style={{ opacity: 0.6 }}>No agents yet.</p>}

      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {agents.map((agent) => {
          const location = formatLiveLocation(agent.live_location);
          const place =
            agent.current_node_fk == null
              ? "no node"
              : nodeLabels[agent.current_node_fk] ?? `place #${agent.current_node_fk}`;
          const currentTask = tasksByAgent[agent.id];

          return (
            <li
              key={agent.id}
              style={{
                padding: "0.4rem 0",
                borderBottom: "1px solid #e5e7eb",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  gap: "0.5rem",
                }}
              >
                <span>
                  <span
                    style={{
                      display: "inline-block",
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      backgroundColor:
                        AGENT_STATUS_COLOR[agent.status] ?? AGENT_STATUS_COLOR.offline,
                      marginRight: 8,
                    }}
                  />
                  {agent.name}
                </span>
                <span style={{ fontSize: "0.8rem", opacity: 0.7 }}>{agent.status}</span>
              </div>

              <div
                style={{
                  fontSize: "0.75rem",
                  opacity: 0.6,
                  marginLeft: 16,
                  marginTop: 2,
                }}
              >
                {place}
                {location && ` · ${location}`}
              </div>

              {currentTask && (
                <div
                  style={{
                    fontSize: "0.75rem",
                    marginLeft: 16,
                    marginTop: 2,
                    color: AGENT_STATUS_COLOR.busy,
                  }}
                >
                  on Task #{currentTask.id}
                  {currentTask.total_eta_minutes != null &&
                    ` · ~${currentTask.total_eta_minutes} min`}
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
