export const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/";

export const WS_URL = import.meta.env.VITE_WS_URL || "ws://127.0.0.1:8000/ws/fleet/";

export const WS_RECONNECT_DELAY_MS = Number(
  import.meta.env.VITE_WS_RECONNECT_DELAY_MS || 2000
);

export const TASK_REFRESH_DELAY_MS = Number(
  import.meta.env.VITE_TASK_REFRESH_DELAY_MS || 1000
);
