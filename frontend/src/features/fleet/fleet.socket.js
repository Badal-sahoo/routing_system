import { WS_RECONNECT_DELAY_MS, WS_URL } from "../../lib/config";

export function connectFleetSocket({ onMessage, onStatusChange }) {
  let socket = null;
  let reconnectTimer = null;
  let closedByCaller = false;

  const open = () => {
    onStatusChange?.("connecting");
    socket = new WebSocket(WS_URL);

    socket.onopen = () => onStatusChange?.("connected");

    socket.onmessage = (event) => {
      try {
        onMessage(JSON.parse(event.data));
      } catch {
        return;
      }
    };

    socket.onclose = () => {
      onStatusChange?.("disconnected");
      if (!closedByCaller) {
        reconnectTimer = setTimeout(open, WS_RECONNECT_DELAY_MS);
      }
    };

    socket.onerror = () => socket?.close();
  };

  open();

  return () => {
    closedByCaller = true;
    clearTimeout(reconnectTimer);
    socket?.close();
  };
}
