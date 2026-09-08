import AgentPanel from "./features/agents/AgentPanel";
import { useLoadAgents, useResetAgents } from "./features/agents/agents.hooks";
import { useAuth } from "./features/auth/auth.hooks";
import { useFleetSocket } from "./features/fleet/fleet.hooks";
import GraphView from "./features/graph/GraphView";
import { useLoadGraph, useResetGraph } from "./features/graph/graph.hooks";
import TaskPanel from "./features/tasks/TaskPanel";
import { useResetTasks } from "./features/tasks/tasks.hooks";

const SOCKET_COLOR = {
  connected: "#22c55e",
  connecting: "#f59e0b",
  disconnected: "#dc2626",
};

export default function Dashboard() {
  const { logout } = useAuth();

  const graph = useLoadGraph();
  const agents = useLoadAgents();
  const socketStatus = useFleetSocket();

  const resetGraph = useResetGraph();
  const resetAgents = useResetAgents();
  const resetTasks = useResetTasks();

  const handleReload = () => {
    graph.reload();
    agents.reload();
  };

  const handleLogout = () => {
    resetGraph();
    resetAgents();
    resetTasks();
    logout();
  };

  const loadError = graph.error || agents.error;

  return (
    <div style={{ display: "flex", height: "100vh", width: "100vw" }}>
      <div
        style={{
          flex: 1,
          minWidth: 0,
          overflow: "hidden",
          borderRight: "1px solid #e5e7eb",
        }}
      >
        <GraphView />
      </div>

      <div style={{ width: 320, flexShrink: 0, overflowY: "auto" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "0.75rem",
            borderBottom: "1px solid #e5e7eb",
          }}
        >
          <strong>Fleet Dispatch</strong>

          <span style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span
              title={`Live updates: ${socketStatus}`}
              style={{
                display: "inline-block",
                width: 8,
                height: 8,
                borderRadius: "50%",
                backgroundColor: SOCKET_COLOR[socketStatus],
              }}
            />
            <button onClick={handleReload} disabled={graph.loading || agents.loading}>
              {graph.loading || agents.loading ? "Loading..." : "Reload"}
            </button>
            <button onClick={handleLogout}>Log out</button>
          </span>
        </div>

        {loadError && (
          <p
            style={{
              color: "#dc2626",
              fontSize: "0.8rem",
              margin: 0,
              padding: "0.5rem 0.75rem",
            }}
          >
            {loadError}
          </p>
        )}

        <AgentPanel />
        <TaskPanel />
      </div>
    </div>
  );
}
