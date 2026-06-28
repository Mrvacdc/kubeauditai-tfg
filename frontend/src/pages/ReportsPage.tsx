import { useEffect, useState } from "react";
import {
  getExecutiveSummary,
  getMarkdownReport,
  setAuthToken,
} from "../api/kubeauditApi";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import MetricCard from "../components/MetricCard";
import SectionCard from "../components/SectionCard";
import {
  getSelectedAuditId,
  SELECTION_CHANGED_EVENT,
} from "../utils/selection";

export default function ReportsPage() {
  const [summary, setSummary] = useState<any>(null);
  const [markdown, setMarkdown] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function loadData() {
    try {
      setIsLoading(true);
      setError("");
      setAuthToken(localStorage.getItem("kubeaudit_token"));

      const auditId = getSelectedAuditId();

      const [executiveSummary, markdownReport] = await Promise.all([
        getExecutiveSummary(auditId),
        getMarkdownReport(auditId),
      ]);

      setSummary(executiveSummary);
      setMarkdown(markdownReport || "");
    } catch (err: any) {
      setSummary(null);
      setMarkdown("");
      setError(err.response?.data?.detail || "No se pudieron cargar los reportes.");
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

  function downloadMarkdown() {
    const auditId = getSelectedAuditId();
    const blob = new Blob([markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);

    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `kubeaudit-audit-${auditId}.md`;
    anchor.click();

    URL.revokeObjectURL(url);
  }

  return (
    <div>
      <header className="page-header page-header-row">
        <div>
          <h1>Reportes</h1>
          <p>Resumen ejecutivo y exportación Markdown para la auditoría seleccionada.</p>
        </div>

        <button className="secondary-button" onClick={loadData}>
          Recargar
        </button>
      </header>

      {isLoading && <LoadingState message="Generando vista de reportes..." />}

      {!isLoading && error && <ErrorState message={error} onRetry={loadData} />}

      {!isLoading && !error && !summary && (
        <EmptyState
          title="No hay reporte disponible"
          description="Seleccioná una auditoría válida para generar el resumen ejecutivo."
        />
      )}

      {!isLoading && !error && summary && (
        <>
          <div className="metric-grid">
            <MetricCard title="Auditoría" value={`#${getSelectedAuditId()}`} />
            <MetricCard title="Cumplimiento" value={`${summary.compliance_percentage}%`} />
            <MetricCard title="Controles" value={summary.total_controls} />
            <MetricCard title="FAIL" value={summary.failed_controls} />
            <MetricCard title="Pendientes HIGH" value={summary.high_pending_recommendations} />
          </div>

          <SectionCard title="Resumen ejecutivo">
            <p>{summary.summary}</p>

            {summary.notes?.length > 0 ? (
              <ul>
                {summary.notes.map((note: string) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            ) : (
              <EmptyState
                title="Sin notas ejecutivas"
                description="El reporte no contiene observaciones adicionales."
              />
            )}
          </SectionCard>

          <SectionCard title="Reporte Markdown">
            {markdown ? (
              <>
                <button onClick={downloadMarkdown}>Descargar Markdown</button>
                <pre className="markdown-preview">{markdown.slice(0, 5000)}</pre>
              </>
            ) : (
              <EmptyState
                title="Markdown no disponible"
                description="No se generó contenido Markdown para esta auditoría."
              />
            )}
          </SectionCard>
        </>
      )}
    </div>
  );
}
