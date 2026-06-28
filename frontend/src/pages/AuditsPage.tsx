import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  getClusterHistory,
  importKubeBenchJson,
  runKubeBenchAudit,
  setAuthToken,
} from "../api/kubeauditApi";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";
import FeedbackBanner from "../components/FeedbackBanner";
import LoadingState from "../components/LoadingState";
import MetricCard from "../components/MetricCard";
import SectionCard from "../components/SectionCard";
import StatusBadge from "../components/StatusBadge";
import { formatDateTime } from "../utils/dateFormat";
import {
  emitSelectionChanged,
  getSelectedClusterId,
  SELECTION_CHANGED_EVENT,
  setBaseAuditId,
  setSelectedAuditId,
  setTargetAuditId,
} from "../utils/selection";

function getAuditIdFromResponse(response: any): number | null {
  return (
    response?.audit_id ||
    response?.id ||
    response?.audit?.audit_id ||
    response?.audit?.id ||
    response?.data?.audit_id ||
    null
  );
}

export default function AuditsPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const [history, setHistory] = useState<any>(null);
  const [audits, setAudits] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [isRunning, setIsRunning] = useState(false);

  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [lastCreatedAuditId, setLastCreatedAuditId] = useState<number | null>(null);

  async function loadData() {
    try {
      setIsLoading(true);
      setError("");

      setAuthToken(localStorage.getItem("kubeaudit_token"));

      const clusterId = getSelectedClusterId();
      const response = await getClusterHistory(clusterId);

      setHistory(response);
      setAudits(response.audits || []);
    } catch (err: any) {
      setHistory(null);
      setAudits([]);
      setError(
        err.response?.data?.detail ||
          "No se pudieron cargar las auditorías del clúster seleccionado."
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

  useEffect(() => {
    if (!successMessage) {
      return;
    }
  
    const timer = window.setTimeout(() => {
      setSuccessMessage("");
    }, 9000);
  
    return () => {
      window.clearTimeout(timer);
    };
  }, [successMessage]);
  
  const latestAudit = audits[0];

  const completedCount = useMemo(
    () => audits.filter((audit) => audit.status === "completed").length,
    [audits]
  );

  const failedCount = useMemo(
    () => audits.filter((audit) => audit.status === "failed").length,
    [audits]
  );

  function selectAudit(auditId: number) {
    setSelectedAuditId(auditId);
    setSuccessMessage(`Auditoría #${auditId} seleccionada como activa.`);
  }

  function goToDetail(auditId: number) {
    setSelectedAuditId(auditId);
    navigate(`/audits/${auditId}`);
  }

  function prepareComparison(auditId: number) {
    const currentAuditIds = audits.map((audit) => audit.audit_id);

    if (currentAuditIds.length < 2) {
      setError("Se necesitan al menos dos auditorías para preparar una comparación.");
      return;
    }

    const baseAuditId =
      currentAuditIds.find((id) => id !== auditId) || currentAuditIds[0];

    setBaseAuditId(baseAuditId, false);
    setTargetAuditId(auditId, false);
    emitSelectionChanged();

    navigate("/compare-controls");
  }

  async function handleImport() {
    if (!selectedFile) {
      setError("Seleccioná un archivo JSON de kube-bench antes de importar.");
      return;
    }

    try {
      setIsImporting(true);
      setError("");
      setSuccessMessage("");
      setAuthToken(localStorage.getItem("kubeaudit_token"));

      const clusterId = getSelectedClusterId();
      const response = await importKubeBenchJson(clusterId, selectedFile);

      const newAuditId = getAuditIdFromResponse(response);

      await loadData();

      if (newAuditId) {
        setSelectedAuditId(newAuditId);
        setLastCreatedAuditId(newAuditId);
        setSuccessMessage(`Auditoría #${newAuditId} importada correctamente.`);
      } else {
        setLastCreatedAuditId(null);
        setSuccessMessage("Archivo importado correctamente. Recargá el listado si no ves la nueva auditoría.");
      }

      setSelectedFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "No se pudo importar el JSON. Verificá que el archivo sea válido y que el endpoint exista."
      );
    } finally {
      setIsImporting(false);
    }
  }

  async function handleRunKubeBench() {
    try {
      setIsRunning(true);
      setError("");
      setSuccessMessage("");
      setAuthToken(localStorage.getItem("kubeaudit_token"));

      const clusterId = getSelectedClusterId();
      const response = await runKubeBenchAudit(clusterId);

      const newAuditId = getAuditIdFromResponse(response);

      await loadData();

      if (newAuditId) {
        setSelectedAuditId(newAuditId);
        setLastCreatedAuditId(newAuditId);
        setSuccessMessage(
          `Auditoría #${newAuditId} ejecutada correctamente. Las recomendaciones generadas por IA con DeepSeek se procesan en segundo plano y pueden tardar aproximadamente entre 15 y 30 minutos en estar disponibles. Luego podrás visualizarlas en la sección Remediación, en el Dashboard o en el detalle de la auditoría.`
        );
      } else {
        setLastCreatedAuditId(null);
        setSuccessMessage(
          "Ejecución solicitada correctamente. Las recomendaciones generadas por IA con DeepSeek se procesan en segundo plano y pueden tardar aproximadamente entre 15 y 30 minutos en estar disponibles. Recargá el listado para ver el resultado."
        );
      }
    } catch (err: any) {
      if (err.response?.status === 504) {
        setError("");
        setSuccessMessage(
          "La ejecución de kube-bench superó el tiempo de espera de la interfaz, pero puede continuar procesándose en el backend. Revisá el historial de auditorías en unos minutos. Si la auditoría fue registrada, las recomendaciones generadas por IA con DeepSeek podrán tardar aproximadamente entre 15 y 30 minutos en estar disponibles."
        );

        try {
          await loadData();
        } catch {
          // No bloquea la experiencia de usuario si la recarga falla.
        }

        return;
      }

      setError(
        err.response?.data?.detail ||
          "No se pudo ejecutar kube-bench desde la interfaz. Verificá el endpoint backend y la conexión al clúster."
      );
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <div>
      <header className="page-header page-header-row">
        <div>
          <h1>Auditorías</h1>
          <p>
            Importación, ejecución y consulta de auditorías CIS Kubernetes para el clúster seleccionado.
          </p>
        </div>

        <div className="action-row">
          <button className="secondary-button" onClick={loadData}>
            Recargar
          </button>
        </div>
      </header>

      <div className="metric-grid">
        <MetricCard title="Auditorías" value={audits.length} />
        <MetricCard title="Completadas" value={completedCount} />
        <MetricCard title="Fallidas" value={failedCount} />
        <MetricCard
          title="Último cumplimiento"
          value={latestAudit ? `${latestAudit.compliance_percentage}%` : "N/D"}
        />
      </div>

      <SectionCard title="Nueva auditoría">
        <div className="audit-actions-grid">
          <div className="audit-action-card">
            <h3>Importar JSON kube-bench</h3>
            <p>
              Cargá un resultado previamente generado por kube-bench para registrarlo como auditoría histórica.
            </p>

            <input
              ref={fileInputRef}
              type="file"
              accept=".json,application/json"
              onChange={(event) =>
                setSelectedFile(event.target.files?.[0] || null)
              }
            />

            {selectedFile && (
              <small className="muted">
                Archivo seleccionado: {selectedFile.name}
              </small>
            )}

            <button
              className="primary-button"
              disabled={isImporting || isRunning}
              onClick={handleImport}
            >
              {isImporting ? "Importando..." : "Importar JSON"}
            </button>
          </div>

          <div className="audit-action-card">
            <h3>Ejecutar kube-bench</h3>
            <p>
              Lanza una auditoría CIS Kubernetes sobre el clúster seleccionado y guarda el resultado en KubeAuditAI.
              Al finalizar, las recomendaciones con IA se generarán en segundo plano mediante DeepSeek.
            </p>

            <button
              className="primary-button"
              disabled={isRunning || isImporting}
              onClick={handleRunKubeBench}
            >
              {isRunning ? "Ejecutando kube-bench..." : "Ejecutar kube-bench"}
            </button>

            <small className="muted">
              La ejecución de kube-bench puede demorar varios minutos. Las recomendaciones generadas por IA con DeepSeek se procesan luego en segundo plano y pueden tardar aproximadamente entre 15 y 30 minutos en visualizarse.
            </small>
          </div>
        </div>
      </SectionCard>

      {(isLoading || isImporting || isRunning) && (
        <LoadingState
          message={
            isRunning
              ? "Ejecutando auditoría kube-bench. Luego se generarán recomendaciones con IA en segundo plano..."
              : isImporting
                ? "Importando auditoría..."
                : "Cargando auditorías..."
          }
        />
      )}

      {error && <ErrorState message={error} onRetry={loadData} />}

      {successMessage && (
        <FeedbackBanner
          variant="success"
          message={successMessage}
          actionLabel={lastCreatedAuditId ? "Ver detalle" : undefined}
          onAction={
            lastCreatedAuditId
              ? () => goToDetail(lastCreatedAuditId)
              : undefined
          }
          onClose={() => setSuccessMessage("")}
        />
      )}

      {!isLoading && !error && audits.length === 0 && (
        <EmptyState
          title="Sin auditorías registradas"
          description="Todavía no hay auditorías para este clúster. Podés importar un JSON o ejecutar kube-bench desde esta pantalla."
          actionLabel="Recargar"
          onAction={loadData}
        />
      )}

      {!isLoading && audits.length > 0 && (
        <SectionCard title="Historial de auditorías">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Fecha</th>
                <th>Estado</th>
                <th>Cumplimiento</th>
                <th>PASS</th>
                <th>FAIL</th>
                <th>WARN</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>
              {audits.map((audit) => (
                <tr key={audit.audit_id}>
                  <td>#{audit.audit_id}</td>
                  <td>{formatDateTime(audit.created_at || audit.started_at)}</td>
                  <td>
                    <StatusBadge value={audit.status || "N/D"} />
                  </td>
                  <td>{audit.compliance_percentage ?? "N/D"}%</td>
                  <td>{audit.passed_controls ?? audit.passed ?? "N/D"}</td>
                  <td>{audit.failed_controls ?? audit.failed ?? "N/D"}</td>
                  <td>{audit.warning_controls ?? audit.warning ?? "N/D"}</td>
                  <td>
                    <div className="action-row">
                      <button
                        className="secondary-button"
                        onClick={() => selectAudit(audit.audit_id)}
                      >
                        Usar
                      </button>

                      <button
                        className="secondary-button"
                        onClick={() => goToDetail(audit.audit_id)}
                      >
                        Detalle
                      </button>

                      <button
                        className="secondary-button"
                        onClick={() => prepareComparison(audit.audit_id)}
                      >
                        Comparar
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </SectionCard>
      )}
    </div>
  );
}
