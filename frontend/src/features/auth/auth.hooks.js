import { useCallback, useState, useSyncExternalStore } from "react";

import { getErrorMessage } from "../../lib/apiError";
import * as tokenStorage from "../../lib/tokenStorage";
import { login } from "./auth.api";

export function useAuth() {
  const accessToken = useSyncExternalStore(
    tokenStorage.subscribe,
    tokenStorage.getAccessToken,
    () => null
  );

  return {
    accessToken,
    isAuthenticated: Boolean(accessToken),
    logout: tokenStorage.clearTokens,
  };
}

export function useLoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = useCallback(
    async (event) => {
      event.preventDefault();
      setError("");
      setLoading(true);
      try {
        const tokens = await login(username, password);
        tokenStorage.setTokens(tokens);
      } catch (requestError) {
        setError(
          requestError.response?.status === 401
            ? "Invalid username or password."
            : getErrorMessage(requestError, "Could not reach the server.")
        );
      } finally {
        setLoading(false);
      }
    },
    [username, password]
  );

  return { username, setUsername, password, setPassword, error, loading, submit };
}
