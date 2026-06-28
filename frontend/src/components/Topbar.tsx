import { Bell, LogOut, UserCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  getClusterHistory,
  setAuthToken,
} from "../api/kubeauditApi";
import {
  getSelectedAuditId,
  getSelectedClusterId,
  SELECTION_CHANGED_EVENT,
  setSelectedAuditId,
  setSelectedClusterId,
} from "../utils/selection";

export default function Topbar() {
  const navigate = useNavigate();

  const [clusterInput, setClusterInput] = useState(String(getSelectedClusterId()));
  const [auditId, setAuditId] = useState(getSelectedAuditId());
  const [audits, setAudits] = useState<any[]>([]);
  const [selectorError, setSelectorError] = useState("");

  async function loadAuditsForCluster(clusterId: number) {
    try {
      setSelectorError("");
      setAuthToken(localStorage.getItem("kubeaudit_token"));

      const history = await getClusterHistory(clusterId);
      const auditList = history.audits || [];

      setAudits(auditList);

      if (auditList.length === 0) {
        setAuditId(0);
        setSelectedAuditId(0, false);
        setSelectorError(
          "Cluster no disponible o sin auditorías registradas"
        );
        return;
      }      

      const availableAuditIds = auditList.map((audit: any) => audit.audit_id);
      const currentAuditId = getSelectedAuditId();

      const nextAuditId = availableAuditIds.includes(currentAuditId)
        ? currentAuditId
        : availableAuditIds[0];

      setAuditId(nextAuditId);
      setSelectedAuditId(nextAuditId, false);
    } catch {
      setAudits([]);
      setAuditId(0);
      setSelectedAuditId(0, false);
      setSelectorError("Cluster no disponible");  
    }
  }

  function applyCluster() {
    const nextClusterId = Number(clusterInput);

    if (!nextClusterId || Number.isNaN(nextClusterId)) {
      setSelectorError("Cluster inválido");
      return;
    }

    setSelectedClusterId(nextClusterId, false);

    loadAuditsForCluster(nextClusterId).then(() => {
      window.dispatchEvent(new Event(SELECTION_CHANGED_EVENT));
    });
  }

  function handleAuditChange(value: string) {
    const nextAuditId = Number(value);

    if (!nextAuditId) {
      return;
    }

    setAuditId(nextAuditId);
    setSelectedAuditId(nextAuditId);
  }

  function logout() {
    localStorage.removeItem("kubeaudit_token");
    setAuthToken(null);
    navigate("/login");
  }

  useEffect(() => {
    loadAuditsForCluster(getSelectedClusterId());
  
    function refreshFromStorage() {
      const clusterId = getSelectedClusterId();
  
      setClusterInput(String(clusterId));
      setAuditId(getSelectedAuditId());
  
      loadAuditsForCluster(clusterId);
    }
  
    window.addEventListener(SELECTION_CHANGED_EVENT, refreshFromStorage);
  
    return () => {
      window.removeEventListener(SELECTION_CHANGED_EVENT, refreshFromStorage);
    };
  }, []);

  return (
    <header className="topbar">
      <div className="topbar-selectors">
        <div className="selector-field">
          <label>Cluster</label>
          <div className="cluster-selector">
            <input
              type="number"
              value={clusterInput}
              onChange={(event) => setClusterInput(event.target.value)}
            />
            <button className="secondary-button" onClick={applyCluster}>
              Aplicar
            </button>
          </div>
        </div>

        <div className="selector-field">
          <label>Auditoría activa</label>
          <select
            value={auditId}
            onChange={(event) => handleAuditChange(event.target.value)}
            disabled={audits.length === 0}
          >
            {audits.length === 0 ? (
              <option value={0}>Sin auditorías disponibles</option>
            ) : (
              audits.map((audit: any) => (
                <option key={audit.audit_id} value={audit.audit_id}>
                  Auditoría #{audit.audit_id} · {audit.compliance_percentage}%
                </option>
              ))
            )}
          </select>
        </div>

        {selectorError && <span className="selector-error">{selectorError}</span>}
      </div>

      <div className="topbar-actions">
        <button className="icon-button" title="Notificaciones">
          <Bell size={20} />
        </button>

        <div className="topbar-user">
          <UserCircle size={30} />
          <div>
            <strong>Analyst User</strong>
            <span>Security Analyst</span>
          </div>
        </div>

        <button className="logout-button" onClick={logout}>
          <LogOut size={18} />
          Salir
        </button>
      </div>
    </header>
  );
}
