import { useEffect, useMemo, useState } from "react";
import { getAuditLogs, setAuthToken } from "../api/kubeauditApi";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import MetricCard from "../components/MetricCard";
import SectionCard from "../components/SectionCard";
import StatusBadge from "../components/StatusBadge";
import { formatDateTime } from "../utils/dateFormat";

type AuditLogFilters = {
  limit: number;
  action: string;
  entity_type: string;
  entity_id: string;
};

function extractValue(detail: string, key: string): string | null {
  const regex = new RegExp(`${key}=([^;]+)`);
  const match = detail.match(regex);
  return match?.[1]?.trim() || null;
}

function extractStatusChange(detail: string) {
  const match = detail.match(/changed from ([A-Z_]+) to ([A-Z_]+)/);

  if (!match) {
    return null;
  }

  return {
    from: match[1],
    to: match[2],
  };
}

function parseLogDetail(detail: string | null | undefined) {
  const safeDetail = detail || "";

  return {
    statusChange: extractStatusChange(safeDetail),
    recommendationId: extractValue(safeDetail, "recommendation_id"),
    findingId: extractValue(safeDetail, "finding_id"),
    source: extractValue(safeDetail, "source"),
    priority: extractValue(safeDetail, "priority"),
    control: extractValue(safeDetail, "control"),
    result: extractValue(safeDetail, "result"),
    controlTitle: extractValue(safeDetail, "control_title"),
  };
}

function renderActionLabel(action: string | null | undefined) {
  if (!action) {
    return "N/D";
  }

  if (action === "RECOMMENDATION_STATUS_UPDATED") {
    return "Estado de recomendación";
  }

  if (action === "LOGIN_SUCCESS") {
    return "Inicio de sesión";
  }

  return action;
}

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [filters, setFilters] = useState<AuditLogFilters>({
    limit: 50,
    action: "",
    entity_type: "",
    entity_id: "",
  });

  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function loadLogs() {
    try {
      setIsLoading(true);
      setError("");

      setAuthToken(localStorage.getItem("kubeaudit_token"));

      const response = await getAuditLogs({
        limit: filters.limit,
        action: filters.action || undefined,
        entity_type: filters.entity_type || undefined,
        entity_id: filters.entity_id ? Number(filters.entity_id) : undefined,
      });

      setLogs(response.items || []);
    } catch (err: any) {
      setLogs([]);
      setError(
        err.response?.data?.detail ||
          "No se pudieron cargar los audit logs."
      );
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadLogs();
  }, []);

  const totalRecommendationChanges = useMemo(
    () =>
      logs.filter(
        (log) => log.action === "RECOMMENDATION_STATUS_UPDATED"
      ).length,
    [logs]
  );

  const totalLoginEvents = useMemo(
    () => logs.filter((log) => log.action === "LOGIN_SUCCESS").length,
    [logs]
  );

  function updateFilter<K extends keyof AuditLogFilters>(
    key: K,
    value: AuditLogFilters[K]
  ) {
    setFilters((current) => ({
      ...current,
      [key]: value,
    }));
  }

  function clearFilters() {
    setFilters({
      limit: 50,
      action: "",
      entity_type: "",
      entity_id: "",
    });
  }

  return (
    <div>
      <header className="page-header page-header-row">
        <div>
          <h1>Audit Logs</h1>
          <p>
            Bitácora de trazabilidad para acciones de usuarios, recomendaciones y cambios operativos.
          </p>
        </div>

        <button className="secondary-button" onClick={loadLogs}>
          Recargar
        </button>
      </header>

      <div className="metric-grid">
        <MetricCard title="Eventos listados" value={logs.length} />
        <MetricCard title="Cambios de recomendación" value={totalRecommendationChanges} />
        <MetricCard title="Logins exitosos" value={totalLoginEvents} />
      </div>

      <SectionCard title="Filtros">
        <div className="audit-log-filters">
          <div>
            <label>Acción</label>
            <input
              value={filters.action}
              onChange={(event) => updateFilter("action", event.target.value)}
              placeholder="Ej: status, login"
            />
          </div>

          <div>
            <label>Entidad</label>
            <select
              value={filters.entity_type}
              onChange={(event) =>
                updateFilter("entity_type", event.target.value)
              }
            >
              <option value="">Todas</option>
              <option value="Recommendation">Recommendation</option>
              <option value="Audit">Audit</option>
              <option value="Cluster">Cluster</option>
              <option value="Finding">Finding</option>
            </select>
          </div>

          <div>
            <label>ID entidad</label>
            <input
              type="number"
              value={filters.entity_id}
              onChange={(event) => updateFilter("entity_id", event.target.value)}
              placeholder="Ej: 146"
            />
          </div>

          <div>
            <label>Límite</label>
            <select
              value={filters.limit}
              onChange={(event) =>
                updateFilter("limit", Number(event.target.value))
              }
            >
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
              <option value={200}>200</option>
            </select>
          </div>

          <div className="action-row">
            <button className="secondary-button" onClick={loadLogs}>
              Aplicar
            </button>

            <button className="secondary-button" onClick={clearFilters}>
              Limpiar
            </button>
          </div>
        </div>
      </SectionCard>

      {isLoading && <LoadingState message="Cargando audit logs..." />}

      {!isLoading && error && <ErrorState message={error} onRetry={loadLogs} />}

      {!isLoading && !error && logs.length === 0 && (
        <EmptyState
          title="Sin audit logs"
          description="No se encontraron eventos para los filtros seleccionados."
          actionLabel="Recargar"
          onAction={loadLogs}
        />
      )}

      {!isLoading && !error && logs.length > 0 && (
        <SectionCard title="Eventos registrados">
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Usuario</th>
                <th>Acción</th>
                <th>Entidad</th>
                <th>IP</th>
                <th>Detalle</th>
              </tr>
            </thead>

            <tbody>
              {logs.map((log) => {
                const parsed = parseLogDetail(log.detail);

                return (
                  <tr key={log.id}>
                    <td>{formatDateTime(log.created_at)}</td>

                    <td>
                      <strong>Usuario #{log.user_id || "N/D"}</strong>
                    </td>

                    <td>
                      <div className="audit-log-action">
                        <StatusBadge value={log.action || "N/D"} />
                        <span>{renderActionLabel(log.action)}</span>
                      </div>
                    </td>

                    <td>
                      <div className="audit-log-entity">
                        <strong>{log.entity_type || "N/D"}</strong>
                        <span>ID: {log.entity_id || "N/D"}</span>
                      </div>
                    </td>

                    <td>{log.ip_address || "N/D"}</td>

                    <td>
                      <div className="audit-log-detail-card">
                        {parsed.statusChange && (
                          <div className="status-flow">
                            <StatusBadge value={parsed.statusChange.from} />
                            <span>→</span>
                            <StatusBadge value={parsed.statusChange.to} />
                          </div>
                        )}

                        <div className="audit-log-tags">
                          {parsed.control && (
                            <span>Control {parsed.control}</span>
                          )}

                          {parsed.result && (
                            <StatusBadge value={parsed.result} />
                          )}

                          {parsed.priority && (
                            <StatusBadge value={parsed.priority} />
                          )}

                          {parsed.source && (
                            <StatusBadge value={parsed.source} />
                          )}
                        </div>

                        {parsed.controlTitle && (
                          <p>{parsed.controlTitle}</p>
                        )}

                        {!parsed.controlTitle && (
                          <p>{log.detail || "Sin detalle"}</p>
                        )}

                        {(parsed.recommendationId || parsed.findingId) && (
                          <small>
                            Recomendación: {parsed.recommendationId || "N/D"} ·
                            Finding: {parsed.findingId || "N/D"}
                          </small>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </SectionCard>
      )}
    </div>
  );
}
