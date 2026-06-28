import { useEffect, useState } from "react";
import { getRemediationPlan, setAuthToken } from "../api/kubeauditApi";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import MetricCard from "../components/MetricCard";
import SectionCard from "../components/SectionCard";
import StatusBadge from "../components/StatusBadge";
import {
  getSelectedAuditId,
  SELECTION_CHANGED_EVENT,
} from "../utils/selection";

export default function RemediationPage() {
  const [plan, setPlan] = useState<any>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function loadData() {
    try {
      setIsLoading(true);
      setError("");
      setAuthToken(localStorage.getItem("kubeaudit_token"));

      const auditId = getSelectedAuditId();
      const response = await getRemediationPlan(auditId);

      setPlan(response);
    } catch (err: any) {
      setPlan(null);
      setError(err.response?.data?.detail || "No se pudo cargar el plan.");
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

  const items = plan?.items || [];
  const summary = plan?.summary || [];

  return (
    <div>
      <header className="page-header page-header-row">
        <div>
          <h1>Plan de remediación</h1>
          <p>Recomendaciones pendientes para la auditoría seleccionada.</p>
        </div>

        <button className="secondary-button" onClick={loadData}>
          Recargar
        </button>
      </header>

      {isLoading && <LoadingState message="Cargando plan de remediación..." />}

      {!isLoading && error && <ErrorState message={error} onRetry={loadData} />}

      {!isLoading && !error && !plan && (
        <EmptyState
          title="No hay plan de remediación"
          description="Seleccioná una auditoría válida para consultar sus recomendaciones."
        />
      )}

      {!isLoading && !error && plan && (
        <>
          <div className="metric-grid">
            <MetricCard title="Auditoría" value={`#${getSelectedAuditId()}`} />
            <MetricCard title="Pendientes" value={plan.total_pending} />
            {summary.map((item: any) => (
              <MetricCard
                key={`${item.priority}-${item.source}`}
                title={`${item.priority} / ${item.source}`}
                value={item.count}
              />
            ))}
          </div>

          <SectionCard title="Recomendaciones principales">
            {items.length > 0 ? (
              <div className="recommendation-list">
                {items.map((item: any) => (
                  <article className="recommendation-card" key={item.recommendation_id}>
                    <div className="recommendation-header">
                      <strong>{item.control_code}</strong>
                      <StatusBadge value={item.priority} />
                      <StatusBadge value={item.source} />
                    </div>
                    <h3>{item.title}</h3>
                    <p className="muted">{item.control_title}</p>
                    <p>{item.recommendation_text}</p>
                  </article>
                ))}
              </div>
            ) : (
              <EmptyState
                title="Sin recomendaciones pendientes"
                description="No hay recomendaciones pendientes para la auditoría seleccionada."
              />
            )}
          </SectionCard>
        </>
      )}
    </div>
  );
}
