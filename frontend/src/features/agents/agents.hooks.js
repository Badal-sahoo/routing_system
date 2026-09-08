import { useCallback, useEffect, useState } from "react";
import { create } from "zustand";

import { getErrorMessage } from "../../lib/apiError";
import { fetchAgents } from "./agents.api";

export const AGENT_STATUS_COLOR = {
  available: "#22c55e",
  busy: "#f59e0b",
  offline: "#6b7280",
};

const useAgentsStore = create((set) => ({
  agents: [],
  setAgents: (agents) => set({ agents }),

  patchAgentLocation: (message) =>
    set((state) => {
      const { agent_id: agentId, ...location } = message;
      return {
        agents: state.agents.map((agent) =>
          agent.id === agentId ? { ...agent, live_location: location } : agent
        ),
      };
    }),

  upsertAgent: (agent) =>
    set((state) => {
      const exists = state.agents.some((existing) => existing.id === agent.id);
      if (!exists) {
        return { agents: [...state.agents, agent] };
      }
      return {
        agents: state.agents.map((existing) =>
          existing.id === agent.id ? { ...existing, ...agent } : existing
        ),
      };
    }),

  reset: () => set({ agents: [] }),
}));

export async function refreshAgents() {
  const agents = await fetchAgents();
  useAgentsStore.getState().setAgents(agents);
}

export const useAgents = () => useAgentsStore((state) => state.agents);
export const usePatchAgentLocation = () =>
  useAgentsStore((state) => state.patchAgentLocation);
export const useUpsertAgent = () => useAgentsStore((state) => state.upsertAgent);
export const useResetAgents = () => useAgentsStore((state) => state.reset);

export function useLoadAgents() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const reload = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      await refreshAgents();
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Could not load agents."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  return { loading, error, reload };
}

export function formatLiveLocation(liveLocation) {
  if (!liveLocation) return null;
  const lat = Number(liveLocation.lat).toFixed(4);
  const lng = Number(liveLocation.lng).toFixed(4);
  return `${lat}, ${lng}`;
}
