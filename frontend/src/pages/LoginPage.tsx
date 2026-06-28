import { ShieldCheck } from "lucide-react";
import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { login, setAuthToken } from "../api/kubeauditApi";

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    try {
      setLoading(true);
      setError("");

      const data = await login(email, password);

      localStorage.setItem("kubeaudit_token", data.access_token);
      localStorage.setItem("selected_cluster_id", "1");
      localStorage.setItem("selected_audit_id", "3");

      setAuthToken(data.access_token);

      navigate("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "No se pudo iniciar sesión.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <section className="login-card">
        <div className="login-brand">
          <ShieldCheck size={42} />
          <div>
            <h1>KubeAuditAI</h1>
            <p>Auditoría continua CIS Kubernetes</p>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>

          <label>
            Contraseña
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>

          {error && <div className="error-box">{error}</div>}

          <button type="submit" disabled={loading}>
            {loading ? "Ingresando..." : "Ingresar"}
          </button>
        </form>
      </section>

      <section className="login-aside">
        <h2>Hardening visible, medible y trazable</h2>
        <p>
          KubeAuditAI centraliza auditorías CIS Kubernetes, recomendaciones de
          remediación y evolución histórica del cumplimiento.
        </p>
      </section>
    </div>
  );
}
