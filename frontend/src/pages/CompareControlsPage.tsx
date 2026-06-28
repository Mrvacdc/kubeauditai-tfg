import { useEffect, useState } from "react";
import {
  getClusterHistory,
  getControlComparison,
  setAuthToken,
} from "../api/kubeauditApi";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import MetricCard from "../components/MetricCard";
import SectionCard from "../components/SectionCard";
import StatusBadge from "../components/StatusBadge";
import {
  getBaseAuditId,
  getSelectedAuditId,
  getSelectedClusterId,
  getTargetAuditId,
  SELECTION_CHANGED_EVENT,
  setBaseAuditId as persistBaseAuditId,
  setTargetAuditId as persistTargetAuditId,
} from "../utils/selection";

export default function CompareControlsPage() {
  const [data, setData] = useState<any>(null);
  const [audits, setAudits] = useState<any[]>([]);
  const [baseAuditId, setBaseAuditIdState] = useState(getBaseAuditId());
  const [targetAuditId, setTargetAuditIdState] = useState(getTargetAuditId());
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function loadInitialData() {
    try {
      setIsLoading(true);
      setError("");
      setAuthToken(localStorage.getItem("kubeaudit_token"));

      const clusterId = getSelectedClusterId();
      const history = await getClusterHistory(clusterId);
      const auditList = history.audits || [];

      setAudits(auditList);

      const auditIds = auditList.map((audit: any) => audit.audit_id);
      if (auditIds.length === 0) {
        setData(null);
        setError(
          "No se encontraron auditorías para el clúster seleccionado. Verificá el ID del clúster o registrá una auditoría."
        );
        return;
      }
      
      if (auditIds.length === 1) {
        setData(null);
        setError(
          "El clúster seleccionado tiene una sola auditoría. Se necesitan al menos dos auditorías para comparar."
        );
        return;
      }

      const storedBaseAuditId = getBaseAuditId();
      const storedTargetAuditId = getTargetAuditId();
      const selectedAuditId = getSelectedAuditId();

      const nextTargetAuditId = auditIds.includes(storedTargetAuditId)
        ? storedTargetAuditId
        : auditIds.includes(selectedAuditId)
          ? selectedAuditId
          : auditIds[0];

      const nextBaseAuditId =
        auditIds.includes(storedBaseAuditId) && storedBaseAuditId !== nextTargetAuditId
          ? storedBaseAuditId
          : auditIds.find((auditId: number) => auditId !== nextTargetAuditId);

      if (!nextBaseAuditId || !nextTargetAuditId || nextBaseAuditId === nextTargetAuditId) {
        setData(null);
        setError("No hay una combinación válida de auditorías para comparar.");
        return;
      }

      setBaseAuditIdState(nextBaseAuditId);
      setTargetAuditIdState(nextTargetAuditId);

      persistBaseAuditId(nextBaseAuditId, false);
      persistTargetAuditId(nextTargetAuditId, false);

      const comparison = await getControlComparison(nextBaseAuditId, nextTargetAuditId);
      setData(comparison);
    } catch (err: any) {
      setData(null);
      setError(err.response?.data?.detail || "No se pudo cargar la comparación.");
    } finally {
      setIsLoading(false);
    }
  }

  async function loadComparison(baseId = baseAuditId, targetId = targetAuditId) {
    try {
      setIsLoading(true);
      setError("");

      if (baseId === targetId) {
        setData(null);
        setError("La auditoría base y la auditoría objetivo deben ser distintas.");
        return;
      }

      setAuthToken(localStorage.getItem("kubeaudit_token"));

      const response = await getControlComparison(baseId, targetId);
      setData(response);
    } catch (err: any) {
      setData(null);
      setError(err.response?.data?.detail || "No se pudo cargar la comparación.");
    } finally {
      setIsLoading(false);
    }
  }

  function changeBaseAuditId(value: string) {
    const nextAuditId = Number(value);

    setBaseAuditIdState(nextAuditId);
    persistBaseAuditId(nextAuditId, false);
  }

  function changeTargetAuditId(value: string) {
    const nextAuditId = Number(value);

    setTargetAuditIdState(nextAuditId);
    persistTargetAuditId(nextAuditId, false);
  }

  useEffect(() => {
    loadInitialData();

    window.addEventListener(SELECTION_CHANGED_EVENT, loadInitialData);

    return () => {
      window.removeEventListener(SELECTION_CHANGED_EVENT, loadInitialData);
    };
  }, []);

  return (
    <div>
      <header className="page-header page-header-row">
        <div>
          <h1>Comparación avanzada</h1>
          <p>Evolución control por control entre auditorías del clúster seleccionado.</p>
        </div>

        <button className="secondary-button" onClick={loadInitialData}>
          Recargar
        </button>
      </header>

      <SectionCard title="Seleccionar auditorías">
        {audits.length > 0 ? (
          <div className="comparison-toolbar">
            <label>
              Auditoría base
              <select
                value={baseAuditId}
                onChange={(event) => changeBaseAuditId(event.target.value)}
              >
                {audits.map((audit: any) => (
                  <option key={audit.audit_id} value={audit.audit_id}>
                    Auditoría #{audit.audit_id} · {audit.compliance_percentage}%
                  </option>
                ))}
              </select>
            </label>

            <label>
              Auditoría objetivo
              <select
                value={targetAuditId}
                onChange={(event) => changeTargetAuditId(event.target.value)}
              >
                {audits.map((audit: any) => (
                  <option key={audit.audit_id} value={audit.audit_id}>
                    Auditoría #{audit.audit_id} · {audit.compliance_percentage}%
                  </option>
                ))}
              </select>
            </label>

            <button onClick={() => loadComparison(baseAuditId, targetAuditId)}>
              Comparar
            </button>
          </div>
        ) : (
          <EmptyState
            title="Cluster no disponible o sin auditorías"
            description="No se encontraron auditorías para el clúster seleccionado. Verificá el ID ingresado en la barra superior."
          />
        )}
      </SectionCard>

      {isLoading && <LoadingState message="Calculando comparación avanzada..." />}

      {!isLoading && error && <ErrorState message={error} onRetry={loadInitialData} />}

      {!isLoading && !error && !data && (
        <EmptyState
          title="No hay comparación disponible"
          description="Seleccioná dos auditorías distintas para comparar su evolución."
        />
      )}

      {!isLoading && !error && data && (
        <>
          <div className="metric-grid">
            <MetricCard title="Comparados" value={data.summary.total_controls_compared} />
            <MetricCard title="Resueltos" value={data.summary.resolved_count} />
            <MetricCard title="Regresiones" value={data.summary.regression_count} />
            <MetricCard title="Nuevos hallazgos" value={data.summary.new_finding_count} />
            <MetricCard title="Nuevos PASS" value={data.summary.newly_evaluated_passed_count} />
          </div>

          <SectionCard title="Controles resueltos">
            <ControlTable items={data.resolved_controls} />
          </SectionCard>

          <SectionCard title="Regresiones">
            <ControlTable items={data.regressions} />
          </SectionCard>

          <SectionCard title="Nuevos hallazgos">
            <ControlTable items={data.new_findings.slice(0, 20)} />
          </SectionCard>
        </>
      )}
    </div>
  );
}

function ControlTable({ items }: { items: any[] }) {
  if (!items || items.length === 0) {
    return (
      <EmptyState
        title="Sin registros en esta categoría"
        description="No se encontraron controles para este grupo de comparación."
      />
    );
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Control</th>
          <th>Título</th>
          <th>Base</th>
          <th>Target</th>
          <th>Transición</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={`${item.control_code}-${item.transition}`}>
            <td>{item.control_code}</td>
            <td>{item.control_title}</td>
            <td>
              <StatusBadge value={item.base_result} />
            </td>
            <td>
              <StatusBadge value={item.target_result} />
            </td>
            <td>{item.transition}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
