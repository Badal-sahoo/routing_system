import { useCallback, useEffect, useMemo, useState } from "react";
import { create } from "zustand";

import { getErrorMessage } from "../../lib/apiError";
import { fetchEdges, fetchNodes } from "./graph.api";

const useGraphStore = create((set) => ({
  nodes: [],
  edges: [],
  setGraph: ({ nodes, edges }) => set({ nodes, edges }),
  reset: () => set({ nodes: [], edges: [] }),
}));

export async function refreshGraph() {
  const [nodes, edges] = await Promise.all([fetchNodes(), fetchEdges()]);
  useGraphStore.getState().setGraph({ nodes, edges });
}

export const useNodes = () => useGraphStore((state) => state.nodes);
export const useEdges = () => useGraphStore((state) => state.edges);
export const useResetGraph = () => useGraphStore((state) => state.reset);

export function useNodeLabels() {
  const nodes = useNodes();
  return useMemo(() => {
    const labels = {};
    nodes.forEach((node) => {
      labels[node.id] = node.label;
    });
    return labels;
  }, [nodes]);
}

export function useLoadGraph() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const reload = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      await refreshGraph();
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Could not load the graph."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  return { loading, error, reload };
}
