import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { getJsonReport, setAuthToken } from "../api/kubeauditApi";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import MetricCard from "../components/MetricCard";
import SectionCard from "../components/SectionCard";
import StatusBadge from "../components/StatusBadge";
import RecommendationStatusActions from "../components/RecommendationStatusActions";
import { formatDateTime } from "../utils/dateFormat";
import {
  getSelectedAuditId,
  SELECTION_CHANGED_EVENT,
  setSelectedAuditId,
} from "../utils/selection";

type FindingFilter = "ALL" | "FAIL" | "WARN" | "PASS";

export default function AuditDetailPage() {
  const params = useParams();

  const routeAuditId = params.auditId ? Number(params.auditId) : null;
  const initialAuditId = routeAuditId || getSelectedAuditId();

  const [recommendationStatusOverrides, setRecommendationStatusOverrides] =
  useState<Record<number, string>>({});
  const [auditId, setAuditId] = useState(initialAuditId);
  const [report, setReport] = useState<any>(null);
  const [selectedFinding, setSelectedFinding] = useState<any>(null);
  const [filter, setFilter] = useState<FindingFilter>("ALL");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function loadData(nextAuditId = auditId, keepFindingId?: number) {
    try {
      setIsLoading(true);
      setError("");
      setReport(null);
  
      if (!keepFindingId) {
        setSelectedFinding(null);
      }
  
      if (!nextAuditId) {
        setError("No hay una auditoría válida seleccionada.");
        return;
      }
  
      setAuthToken(localStorage.getItem("kubeaudit_token"));
      setSelectedAuditId(nextAuditId, false);
  
      const data = await getJsonReport(nextAuditId, 200, 100);
  
      setReport(data);
      setAuditId(nextAuditId);
  
      if (keepFindingId) {
        const refreshedFinding = (data.findings || []).find(
          (finding: any) => finding.finding_id === keepFindingId
        );
  
        setSelectedFinding(refreshedFinding || null);
      }
    } catch (err: any) {
      setReport(null);
      setError(
        err.response?.data?.detail ||
          "No se pudo cargar el detalle de auditoría."
      );
    } finally {
      setIsLoading(false);
    }
  }  

  useEffect(() => {
    loadData(initialAuditId);

    function handleSelectionChanged() {
      const nextAuditId = getSelectedAuditId();
      setAuditId(nextAuditId);
      loadData(nextAuditId);
    }

    window.addEventListener(SELECTION_CHANGED_EVENT, handleSelectionChanged);

    return () => {
      window.removeEventListener(SELECTION_CHANGED_EVENT, handleSelectionChanged);
    };
  }, []);

  const findings = report?.findings || [];
  const remediationItems =
    report?.remediation_plan?.items ||
    report?.remediation_plan?.recommendations ||
    [];

  const filteredFindings = useMemo(() => {
    if (filter === "ALL") {
      return findings;
    }

    return findings.filter((finding: any) => finding.result === filter);
  }, [findings, filter]);

  function getRecommendationForFinding(finding: any) {
    return (
      remediationItems.find(
        (item: any) => item.finding_id === finding.finding_id
      ) ||
      remediationItems.find(
        (item: any) => item.control_code === finding.control_code
      )
    );
  }

  function openFinding(finding: any) {
    setSelectedFinding(finding);
  }

  async function refreshAfterRecommendationChange() {
    await loadData(auditId, selectedFinding?.finding_id);
  }  

  function getRecommendationId(recommendation: any): number | null {
    return recommendation?.recommendation_id || recommendation?.id || null;
  }
  
  function getDisplayedRecommendationStatus(recommendation: any): string {
    const recommendationId = getRecommendationId(recommendation);
  
    if (recommendationId && recommendationStatusOverrides[recommendationId]) {
      return recommendationStatusOverrides[recommendationId];
    }
  
    return recommendation?.status || "PENDING";
  }
  
  function updateRecommendationStatusInView(
    recommendation: any,
    status: string
  ) {
    const recommendationId = getRecommendationId(recommendation);
  
    if (!recommendationId) {
      return;
    }
  
    setRecommendationStatusOverrides((current) => ({
      ...current,
      [recommendationId]: status,
    }));
  }
    
  const summary = report?.summary;
  const cluster = report?.cluster;

  const selectedRecommendation = selectedFinding
    ? getRecommendationForFinding(selectedFinding)
    : null;

  return (
    <div>
      <header className="page-header page-header-row">
        <div>
          <h1>Detalle de auditoría</h1>
          <p>
            Análisis técnico de hallazgos, evidencia y recomendaciones asociadas.
          </p>
        </div>

        <button className="secondary-button" onClick={() => loadData(auditId)}>
          Recargar
        </button>
      </header>

      {isLoading && <LoadingState message="Cargando detalle de auditoría..." />}

      {!isLoading && error && (
        <ErrorState message={error} onRetry={() => loadData(auditId)} />
      )}

      {!isLoading && !error && !report && (
        <EmptyState
          title="Detalle no disponible"
          description="Seleccioná una auditoría válida para consultar sus hallazgos."
          actionLabel="Reintentar"
          onAction={() => loadData(auditId)}
        />
      )}

      {!isLoading && !error && report && (
        <>
          <SectionCard title={`Auditoría #${report.audit_id}`}>
            <div className="audit-detail-grid">
              <div>
                <span>Clúster</span>
                <strong>{cluster?.name || `Cluster #${cluster?.cluster_id || "N/D"}`}</strong>
              </div>

              <div>
                <span>Cluster ID</span>
                <strong>{cluster?.cluster_id || "N/D"}</strong>
              </div>

              <div>
                <span>Generado en</span>
                <strong>{formatDateTime(report.generated_at)}</strong>
              </div>

              <div>
                <span>Ambiente</span>
                <strong>{cluster?.environment || "N/D"}</strong>
              </div>
            </div>
          </SectionCard>

          <div className="metric-grid">
            <MetricCard
              title="Cumplimiento"
              value={`${summary?.compliance_percentage ?? "N/D"}%`}
            />
            <MetricCard
              title="Total controles"
              value={summary?.total_controls ?? "N/D"}
            />
            <MetricCard
              title="PASS"
              value={summary?.passed_controls ?? "N/D"}
            />
            <MetricCard
              title="FAIL"
              value={summary?.failed_controls ?? "N/D"}
            />
            <MetricCard
              title="WARN"
              value={summary?.warning_controls ?? "N/D"}
            />
          </div>

          <SectionCard title="Hallazgos de auditoría">
            <div className="filter-row">
              <button
                className={filter === "ALL" ? "filter-button active" : "filter-button"}
                onClick={() => setFilter("ALL")}
              >
                Todos
              </button>

              <button
                className={filter === "FAIL" ? "filter-button active" : "filter-button"}
                onClick={() => setFilter("FAIL")}
              >
                FAIL
              </button>

              <button
                className={filter === "WARN" ? "filter-button active" : "filter-button"}
                onClick={() => setFilter("WARN")}
              >
                WARN
              </button>

              <button
                className={filter === "PASS" ? "filter-button active" : "filter-button"}
                onClick={() => setFilter("PASS")}
              >
                PASS
              </button>
            </div>

            {filteredFindings.length > 0 ? (
              <table>
                <thead>
                  <tr>
                    <th>Control</th>
                    <th>Título</th>
                    <th>Resultado</th>
                    <th>Detectado</th>
                    <th>Recomendación</th>
                    <th>Acción</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredFindings.map((finding: any) => {
                    const recommendation = getRecommendationForFinding(finding);

                    return (
                      <tr key={finding.finding_id}>
                        <td>{finding.control_code}</td>
                        <td>{finding.control_title}</td>
                        <td>
                          <StatusBadge value={finding.result} />
                        </td>
                        <td>{formatDateTime(finding.detected_at)}</td>
                        <td>
                          {recommendation ? (
                            <StatusBadge value={recommendation.priority || "PENDING"} />
                          ) : (
                            <span className="muted">Sin recomendación</span>
                          )}
                        </td>
                        <td>
                          <button
                            className="secondary-button"
                            onClick={() => openFinding(finding)}
                          >
                            Ver detalle
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            ) : (
              <EmptyState
                title="Sin hallazgos para este filtro"
                description="No hay controles que coincidan con el resultado seleccionado."
              />
            )}
          </SectionCard>

          {selectedFinding && (
            <SectionCard title={`Detalle del control ${selectedFinding.control_code}`}>
              <div className="detail-panel">
                <div className="detail-panel-header">
                  <div>
                    <h3>{selectedFinding.control_title}</h3>
                    <StatusBadge value={selectedFinding.result} />
                  </div>

                  <button
                    className="secondary-button"
                    onClick={() => setSelectedFinding(null)}
                  >
                    Cerrar detalle
                  </button>
                </div>

                <div className="audit-detail-grid">
                  <div>
                    <span>Finding ID</span>
                    <strong>{selectedFinding.finding_id}</strong>
                  </div>

                  <div>
                    <span>Resultado</span>
                    <strong>{selectedFinding.result}</strong>
                  </div>

                  <div>
                    <span>Detectado en</span>
                    <strong>{formatDateTime(selectedFinding.detected_at)}</strong>
                  </div>

                  <div>
                    <span>Hash de evidencia</span>
                    <strong className="evidence-hash">
                      {selectedFinding.evidence_hash || "N/D"}
                    </strong>
                  </div>
                </div>

                <h3>Detalle</h3>
                <p>{selectedFinding.detail || "Sin detalle adicional."}</p>

                <h3>Evidencia sanitizada</h3>
                {selectedFinding.evidence_sanitized ? (
                  <pre className="evidence-block">
                    {selectedFinding.evidence_sanitized}
                  </pre>
                ) : (
                  <EmptyState
                    title="Sin evidencia sanitizada"
                    description="Este hallazgo no tiene evidencia textual asociada."
                  />
                )}

                <h3>Recomendación asociada</h3>
                {selectedRecommendation ? (
                  <div className="recommendation-detail">
                    <div className="recommendation-header">
                      <strong>{selectedRecommendation.control_code}</strong>
                      <StatusBadge value={selectedRecommendation.priority} />
                      <StatusBadge value={selectedRecommendation.source} />
                      <StatusBadge value={getDisplayedRecommendationStatus(selectedRecommendation)} />
                    </div>
                  
                    <h4>{selectedRecommendation.title}</h4>
                    <p>
                      {selectedRecommendation.recommendation_text ||
                        selectedRecommendation.description ||
                        "Sin texto de recomendación disponible."}
                    </p>
                  
                    <RecommendationStatusActions
                      recommendation={{
                        ...selectedRecommendation,
                        status: getDisplayedRecommendationStatus(selectedRecommendation),
                      }}
                      onChanged={(nextStatus) =>
                        updateRecommendationStatusInView(selectedRecommendation, nextStatus)
                      }
                    />
                  </div>
                ) : (
                  <EmptyState
                    title="Sin recomendación asociada"
                    description="Este hallazgo no tiene una recomendación pendiente en el plan actual."
                  />
                )}
              </div>
            </SectionCard>
          )}
        </>
      )}
    </div>
  );
}
