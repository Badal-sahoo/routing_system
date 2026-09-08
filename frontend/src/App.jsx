import Dashboard from "./Dashboard";
import LoginPage from "./features/auth/LoginPage";
import { useAuth } from "./features/auth/auth.hooks";

export default function App() {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Dashboard /> : <LoginPage />;
}
