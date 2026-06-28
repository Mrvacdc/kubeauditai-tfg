import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  getAuditSummary,
  getClusterHistory,
  setAuthToken,
} from "../api/kubeauditApi";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import MetricCard from "../components/MetricCard";
import SectionCard from "../components/SectionCard";
import StatusBadge from "../components/StatusBadge";
import {
  getSelectedAuditId,
  getSelectedClusterId,
  SELECTION_CHANGED_EVENT,
  setSelectedAuditId,
} from "../utils/selection";

export default function DashboardPage() {
  const [summary, setSummary] = useState<any>(null);
  const [history, setHistory] = useState<any>(null);
  const [error, setError] = useState("");
  const [emptyMessage, setEmptyMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  async function loadData() {
    try {
      setIsLoading(true);
      setError("");
      setEmptyMessage("");
      setSummary(null);
      setHistory(null);

      setAuthToken(localStorage.getItem("kubeaudit_token"));

      const clusterId = getSelectedClusterId();
      const selectedAuditId = getSelectedAuditId();

      const historyData = await getClusterHistory(clusterId);
      const audits = historyData.audits || [];

      setHistory(historyData);

      if (audits.length === 0) {
        setSelectedAuditId(0, false);
        setEmptyMessage(
          "No se encontraron auditorías para el clúster seleccionado. Verificá el ID del clúster o registrá una auditoría."
        );
        return;
      }

      const availableAuditIds = audits.map((audit: any) => audit.audit_id);

      const auditId = availableAuditIds.includes(selectedAuditId)
        ? selectedAuditId
        : availableAuditIds[0];

      if (!auditId) {
        setSelectedAuditId(0, false);
        setEmptyMessage(
          "No hay una auditoría válida seleccionada para este clúster."
        );
        return;
      }

      if (auditId !== selectedAuditId) {
        setSelectedAuditId(auditId, false);
      }

      const summaryData = await getAuditSummary(auditId);
      setSummary(summaryData);
    } catch (err: any) {
      setSummary(null);
      setHistory(null);
      setError(
        err.response?.data?.detail ||
          "No se pudo cargar el dashboard. Revisá el backend, la sesión o el clúster seleccionado."
      );
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

  const historyChartData =
    history?.audits
      ?.slice()
      .reverse()
      .map((audit: any) => ({
        audit: `#${audit.audit_id}`,
        cumplimiento: audit.compliance_percentage,
      })) || [];

  const hasHistoryChartData = historyChartData.length >= 2;

  const recommendationData = summary?.recommendations_by_status || [];
  const hasRecommendationData = recommendationData.some(
    (item: any) => Number(item.count) > 0
  );

  const topFailedControls = summary?.top_failed_controls || [];
  const canViewDetail = Boolean(summary) && getSelectedAuditId() > 0;

  return (
    <div>
      <header className="page-header page-header-row">
        <div>
          <h1>Dashboard de cumplimiento</h1>
          <p>
            Vista general de auditorías CIS Kubernetes para el clúster y auditoría seleccionados.
          </p>
        </div>
        <div className="action-row">
          {canViewDetail && (
            <button
              className="secondary-button"
              onClick={() => navigate(`/audits/${getSelectedAuditId()}`)}
            >
              Ver detalle
            </button>
          )}

          <button className="secondary-button" onClick={loadData}>
            Recargar
          </button>
        </div>
      </header>

      {isLoading && <LoadingState message="Cargando dashboard de cumplimiento..." />}

      {!isLoading && error && <ErrorState message={error} onRetry={loadData} />}

      {!isLoading && !error && emptyMessage && (
        <EmptyState
          title="Clúster no disponible o sin auditorías"
          description={emptyMessage}
          actionLabel="Reintentar"
          onAction={loadData}
        />
      )}

      {!isLoading && !error && !emptyMessage && !summary && (
        <EmptyState
          title="No hay datos de auditoría"
          description="Seleccioná una auditoría válida desde la barra superior para visualizar el dashboard."
          actionLabel="Reintentar"
          onAction={loadData}
        />
      )}

      {!isLoading && !error && !emptyMessage && summary && (
        <>
          <div className="metric-grid">
            <MetricCard
              title="Cumplimiento actual"
              value={`${summary.compliance_percentage}%`}
              subtitle={`Auditoría #${getSelectedAuditId()}`}
            />
            <MetricCard title="Total controles" value={summary.total_controls} />
            <MetricCard title="PASS" value={summary.passed_controls} />
            <MetricCard title="FAIL" value={summary.failed_controls} />
            <MetricCard title="WARN" value={summary.warning_controls} />
          </div>

          <div className="two-columns">
            <SectionCard title="Evolución del cumplimiento">
              {hasHistoryChartData ? (
                <ResponsiveContainer width="100%" height={280}>
                  <LineChart data={historyChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="audit" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="cumplimiento"
                      stroke="#2563eb"
                      strokeWidth={3}
                      dot={{ r: 5 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <EmptyState
                  title="Sin historial disponible"
                  description="Todavía no hay suficientes auditorías para graficar la evolución."
                />
              )}
            </SectionCard>

            <SectionCard title="Recomendaciones por estado">
              {hasRecommendationData ? (
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={recommendationData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#2563eb" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <EmptyState
                  title="Sin recomendaciones"
                  description="No hay recomendaciones generadas para esta auditoría."
                />
              )}
            </SectionCard>
          </div>

          <SectionCard title="Hallazgos críticos">
            {topFailedControls.length > 0 ? (
              <table>
                <thead>
                  <tr>
                    <th>Control</th>
                    <th>Título</th>
                    <th>Resultado</th>
                    <th>Cantidad</th>
                  </tr>
                </thead>
                <tbody>
                  {topFailedControls.map((item: any) => (
                    <tr key={item.control_code}>
                      <td>{item.control_code}</td>
                      <td>{item.title}</td>
                      <td>
                        <StatusBadge value={item.result} />
                      </td>
                      <td>{item.count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <EmptyState
                title="Sin hallazgos críticos"
                description="La auditoría seleccionada no tiene controles FAIL o WARN destacados."
              />
            )}
          </SectionCard>
        </>
      )}
    </div>
  );
}
