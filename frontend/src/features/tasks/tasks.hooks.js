import { useCallback, useEffect, useMemo, useState } from "react";
import { create } from "zustand";

import { getErrorMessage } from "../../lib/apiError";
import { TASK_REFRESH_DELAY_MS } from "../../lib/config";
import { refreshAgents } from "../agents/agents.hooks";
import { refreshGraph } from "../graph/graph.hooks";
import { createTask, dispatchTask, fetchTasks } from "./tasks.api";

function isStaleNodeError(error) {
  const data = error?.response?.data;
  return Boolean(data?.origin_node_fk || data?.destination_node_fk);
}

const useTasksStore = create((set) => ({
  tasks: [],
  setTasks: (tasks) => set({ tasks }),

  upsertTask: (task) =>
    set((state) => {
      const exists = state.tasks.some((existing) => existing.id === task.id);
      if (!exists) {
        return { tasks: [...state.tasks, task] };
      }
      return {
        tasks: state.tasks.map((existing) =>
          existing.id === task.id ? task : existing
        ),
      };
    }),

  reset: () => set({ tasks: [] }),
}));

export const useTasks = () => useTasksStore((state) => state.tasks);
export const useResetTasks = () => useTasksStore((state) => state.reset);
export const useUpsertTask = () => useTasksStore((state) => state.upsertTask);

const ACTIVE_STATUSES = ["assigned", "in_progress"];

export function useTasksByAgent() {
  const tasks = useTasks();
  return useMemo(() => {
    const byAgent = {};
    tasks.forEach((task) => {
      if (task.assigned_agent_fk && ACTIVE_STATUSES.includes(task.status)) {
        byAgent[task.assigned_agent_fk] = task;
      }
    });
    return byAgent;
  }, [tasks]);
}

export function formatEta(task) {
  return task.total_eta_minutes == null ? null : `~${task.total_eta_minutes} min`;
}

export function useTaskActions() {
  const setTasks = useTasksStore((state) => state.setTasks);
  const upsertTask = useTasksStore((state) => state.upsertTask);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [dispatchingId, setDispatchingId] = useState(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setTasks(await fetchTasks());
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Could not load tasks."));
    } finally {
      setLoading(false);
    }
  }, [setTasks]);

  useEffect(() => {
    reload();
  }, [reload]);

  const create = useCallback(
    async (originNodeId, destinationNodeId) => {
      setError("");
      try {
        const task = await createTask(
          Number(originNodeId),
          Number(destinationNodeId)
        );
        upsertTask(task);
        return "created";
      } catch (requestError) {
        if (isStaleNodeError(requestError)) {
          await Promise.all([
            refreshGraph().catch(() => {}),
            fetchTasks().then(setTasks).catch(() => {}),
          ]);
          setError("That place no longer exists. The list has been updated — pick again.");
          return "stale";
        }
        setError(getErrorMessage(requestError, "Could not create the task."));
        return "failed";
      }
    },
    [upsertTask, setTasks]
  );

  const dispatch = useCallback(
    async (taskId) => {
      setError("");
      setDispatchingId(taskId);
      try {
        await dispatchTask(taskId);
        await new Promise((resolve) => setTimeout(resolve, TASK_REFRESH_DELAY_MS));
        await Promise.all([
          fetchTasks().then(setTasks),
          refreshAgents().catch(() => {}),
        ]);
      } catch (requestError) {
        setError(getErrorMessage(requestError, "Could not dispatch the task."));
      } finally {
        setDispatchingId(null);
      }
    },
    [setTasks]
  );

  return { loading, error, reload, create, dispatch, dispatchingId };
}
