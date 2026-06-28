import {
  BarChart3,
  ClipboardList,
  FileSearch,
  FileText,
  History,
  Home,
  Server,
  ShieldCheck,
  Wrench,
} from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";
import Topbar from "./Topbar";

export default function Layout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <ShieldCheck size={34} />
          <div>
            <h1>KubeAuditAI</h1>
            <p>CIS Kubernetes</p>
          </div>
        </div>

        <nav className="sidebar-nav">
          <NavLink to="/">
            <Home size={20} />
            Dashboard
          </NavLink>

          <NavLink to="/clusters">
            <Server size={20} />
            Clústeres
          </NavLink>

          <NavLink to="/audits">
            <ClipboardList size={20} />
            Auditorías
          </NavLink>

          <NavLink to="/audit-detail">
            <FileSearch size={20} />
            Detalle
          </NavLink>

          <NavLink to="/compare-controls">
            <BarChart3 size={20} />
            Comparación
          </NavLink>

          <NavLink to="/remediation">
            <Wrench size={20} />
            Remediación
          </NavLink>

          <NavLink to="/audit-logs">
            <History size={20} />
            Audit Logs
          </NavLink>

          <NavLink to="/reports">
            <FileText size={20} />
            Reportes
          </NavLink>
        </nav>

        <div className="sidebar-user">
          <div className="avatar">A</div>
          <div>
            <strong>Analyst User</strong>
            <span>Security Analyst</span>
          </div>
        </div>
      </aside>

      <div className="content-shell">
        <Topbar />

        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
