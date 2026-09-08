import { useLoginForm } from "./auth.hooks";

export default function LoginPage() {
  const { username, setUsername, password, setPassword, error, loading, submit } =
    useLoginForm();

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <form
        onSubmit={submit}
        style={{ display: "flex", flexDirection: "column", gap: "0.6rem", width: 260 }}
      >
        <h1 style={{ fontSize: "1.2rem", marginBottom: "0.5rem" }}>
          Fleet Dispatch Login
        </h1>

        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          autoComplete="username"
          autoFocus
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
        />

        {error && (
          <p style={{ color: "#dc2626", fontSize: "0.85rem", margin: 0 }}>{error}</p>
        )}

        <button type="submit" disabled={loading || !username || !password}>
          {loading ? "Logging in..." : "Log in"}
        </button>
      </form>
    </div>
  );
}
