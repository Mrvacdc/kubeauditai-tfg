import { BrowserRouter, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import RequireAuth from "./components/RequireAuth";
import AuditDetailPage from "./pages/AuditDetailPage";
import AuditsPage from "./pages/AuditsPage";
import AuditLogsPage from "./pages/AuditLogsPage";
import ClustersPage from "./pages/ClustersPage";
import CompareControlsPage from "./pages/CompareControlsPage";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import RemediationPage from "./pages/RemediationPage";
import ReportsPage from "./pages/ReportsPage";
import "./styles/global.css";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route
          element={
            <RequireAuth>
              <Layout />
            </RequireAuth>
          }
        >
          <Route path="/" element={<DashboardPage />} />
          <Route path="/clusters" element={<ClustersPage />} />
          <Route path="/audits" element={<AuditsPage />} />
          <Route path="/audits/:auditId" element={<AuditDetailPage />} />
          <Route path="/audit-detail" element={<AuditDetailPage />} />
          <Route path="/compare-controls" element={<CompareControlsPage />} />
          <Route path="/remediation" element={<RemediationPage />} />
          <Route path="/audit-logs" element={<AuditLogsPage />} />
          <Route path="/reports" element={<ReportsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
