import { useEffect, useState } from "react";
import { getCluster, getClusterHistory, setAuthToken } from "../api/kubeauditApi";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import MetricCard from "../components/MetricCard";
import SectionCard from "../components/SectionCard";
import {
  getSelectedClusterId,
  SELECTION_CHANGED_EVENT,
} from "../utils/selection";

export default function ClustersPage() {
  const [cluster, setCluster] = useState<any>(null);
  const [history, setHistory] = useState<any>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function loadData() {
    try {
      setIsLoading(true);
      setError("");
      setAuthToken(localStorage.getItem("kubeaudit_token"));

      const clusterId = getSelectedClusterId();

      const [clusterResponse, historyResponse] = await Promise.all([
        getCluster(clusterId),
        getClusterHistory(clusterId),
      ]);

      setCluster(clusterResponse);
      setHistory(historyResponse);
    } catch (err: any) {
      setCluster(null);
      setHistory(null);
      setError(err.response?.data?.detail || "No se pudo cargar el clúster.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadData();

    window.addEventListener(SELECTION_CHANGED_EVENT, loadData);

    return () => {
      window.removeEventListener(SELECTION_CHANGED_EVENT, loadData);
    };
  }, []);

  const audits = history?.audits || [];
  const latestAudit = audits[0];
  const clusterId = getSelectedClusterId();

  const clusterName =
    cluster?.name ||
    history?.cluster_name ||
    history?.name ||
    null;

  const hasAudits = audits.length > 0;
  const hasClusterIdentity = Boolean(cluster?.id || clusterName) || hasAudits;

  return (
    <div>
      <header className="page-header page-header-row">
        <div>
          <h1>Clústeres</h1>
          <p>Detalle del clúster seleccionado desde la barra superior.</p>
        </div>

        <button className="secondary-button" onClick={loadData}>
          Recargar
        </button>
      </header>

      {isLoading && <LoadingState message="Cargando información del clúster..." />}

      {!isLoading && error && <ErrorState message={error} onRetry={loadData} />}

      {!isLoading && !error && !cluster && !history && (
        <EmptyState
          title="Clúster no disponible"
          description="Ingresá un cluster_id válido en la barra superior y presioná Aplicar."
        />
      )}

      {!isLoading && !error && history && (
        <>
          <div className="metric-grid">
            <MetricCard title="Cluster ID" value={clusterId} />
            <MetricCard
              title="Nombre"
              value={clusterName || "No disponible"}
            />
            <MetricCard title="Auditorías" value={audits.length} />
            <MetricCard
              title="Último cumplimiento"
              value={latestAudit ? `${latestAudit.compliance_percentage}%` : "N/D"}
            />
          </div>

          <SectionCard title="Detalle del clúster">
            {hasClusterIdentity ? (
              <div className="cluster-detail">
                <div>
                  <span>Nombre</span>
                  <strong>{clusterName || `Cluster #${clusterId}`}</strong>
                </div>

                <div>
                  <span>Estado</span>
                  <strong className={hasAudits ? "status-ok" : "status-warning"}>
                    {hasAudits ? "Con auditorías registradas" : "Registrado sin auditorías"}
                  </strong>
                </div>

                <div>
                  <span>Última auditoría</span>
                  <strong>{latestAudit ? `#${latestAudit.audit_id}` : "N/D"}</strong>
                </div>

                <div>
                  <span>API Server</span>
                  <strong>{cluster?.api_server || "N/D"}</strong>
                </div>

                <div>
                  <span>Namespace objetivo</span>
                  <strong>{cluster?.namespace_target || "N/D"}</strong>
                </div>

                <div>
                  <span>Fuente</span>
                  <strong>kube-bench / CIS Kubernetes</strong>
                </div>
              </div>
            ) : (
              <EmptyState
                title="Clúster no disponible"
                description="No se pudo confirmar la existencia del clúster seleccionado. Verificá el ID ingresado o registrá el clúster."
              />
            )}
          </SectionCard>
        </>
      )}
    </div>
  );
}
