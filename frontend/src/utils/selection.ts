export const SELECTION_CHANGED_EVENT = "kubeaudit-selection-changed";

export function emitSelectionChanged() {
  window.dispatchEvent(new Event(SELECTION_CHANGED_EVENT));
}

export function getSelectedClusterId(): number {
  return Number(localStorage.getItem("selected_cluster_id") || "1");
}

export function setSelectedClusterId(clusterId: number, emit = true) {
  localStorage.setItem("selected_cluster_id", String(clusterId));

  if (emit) {
    emitSelectionChanged();
  }
}

export function getSelectedAuditId(): number {
  return Number(localStorage.getItem("selected_audit_id") || "3");
}

export function setSelectedAuditId(auditId: number, emit = true) {
  localStorage.setItem("selected_audit_id", String(auditId));

  if (emit) {
    emitSelectionChanged();
  }
}

export function getBaseAuditId(): number {
  return Number(localStorage.getItem("base_audit_id") || "1");
}

export function setBaseAuditId(auditId: number, emit = true) {
  localStorage.setItem("base_audit_id", String(auditId));

  if (emit) {
    emitSelectionChanged();
  }
}

export function getTargetAuditId(): number {
  return Number(localStorage.getItem("target_audit_id") || getSelectedAuditId());
}

export function setTargetAuditId(auditId: number, emit = true) {
  localStorage.setItem("target_audit_id", String(auditId));

  if (emit) {
    emitSelectionChanged();
  }
}
