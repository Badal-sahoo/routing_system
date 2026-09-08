import { useCallback, useEffect, useState } from "react";

import { usePatchAgentLocation, useUpsertAgent } from "../agents/agents.hooks";
import { useUpsertTask } from "../tasks/tasks.hooks";
import { connectFleetSocket } from "./fleet.socket";

export function useFleetSocket() {
  const patchAgentLocation = usePatchAgentLocation();
  const upsertAgent = useUpsertAgent();
  const upsertTask = useUpsertTask();
  const [status, setStatus] = useState("connecting");

  const handleMessage = useCallback(
    (message) => {
      switch (message.kind) {
        case "gps":
          patchAgentLocation(message);
          break;
        case "agent":
          upsertAgent(message.agent);
          break;
        case "task":
          upsertTask(message.task);
          break;
        default:
          break;
      }
    },
    [patchAgentLocation, upsertAgent, upsertTask]
  );

  useEffect(() => {
    return connectFleetSocket({
      onMessage: handleMessage,
      onStatusChange: setStatus,
    });
  }, [handleMessage]);

  return status;
}
