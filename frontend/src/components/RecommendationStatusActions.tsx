import { useState } from "react";
import {
  RecommendationStatus,
  updateRecommendationStatus,
} from "../api/kubeauditApi";
import StatusBadge from "./StatusBadge";

type RecommendationStatusActionsProps = {
  recommendation: any;
  onChanged?: (status: RecommendationStatus) => Promise<void> | void;
};

function getRecommendationId(recommendation: any): number | null {
  return (
    recommendation?.recommendation_id ||
    recommendation?.id ||
    null
  );
}

function getCurrentStatus(recommendation: any): RecommendationStatus {
  const status = String(recommendation?.status || "PENDING").toUpperCase();

  if (status === "APPLIED" || status === "DISMISSED" || status === "PENDING") {
    return status;
  }

  return "PENDING";
}

export default function RecommendationStatusActions({
  recommendation,
  onChanged,
}: RecommendationStatusActionsProps) {
  const [isUpdating, setIsUpdating] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const recommendationId = getRecommendationId(recommendation);
  const currentStatus = getCurrentStatus(recommendation);

  async function changeStatus(nextStatus: RecommendationStatus) {
    if (!recommendationId) {
      setError("No se encontró el ID de la recomendación.");
      return;
    }

    if (nextStatus === currentStatus) {
      return;
    }

    try {
      setIsUpdating(true);
      setMessage("");
      setError("");

      await updateRecommendationStatus(recommendationId, nextStatus);

      setMessage(`Estado actualizado a ${nextStatus}.`);

      if (onChanged) {
        await onChanged(nextStatus);
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "No se pudo actualizar el estado de la recomendación."
      );
    } finally {
      setIsUpdating(false);
    }
  }

  if (!recommendation) {
    return null;
  }

  return (
    <div className="recommendation-actions">
      <div className="recommendation-current-status">
        <span>Estado actual</span>
        <StatusBadge value={currentStatus} />
      </div>

      <div className="action-row">
        <button
          className="secondary-button"
          disabled={isUpdating || currentStatus === "APPLIED"}
          onClick={() => changeStatus("APPLIED")}
        >
          Marcar aplicada
        </button>

        <button
          className="secondary-button"
          disabled={isUpdating || currentStatus === "DISMISSED"}
          onClick={() => changeStatus("DISMISSED")}
        >
          Descartar
        </button>

        <button
          className="secondary-button"
          disabled={isUpdating || currentStatus === "PENDING"}
          onClick={() => changeStatus("PENDING")}
        >
          Reabrir
        </button>
      </div>

      {isUpdating && <p className="muted">Actualizando recomendación...</p>}
      {message && <p className="success-message">{message}</p>}
      {error && <p className="inline-error">{error}</p>}
    </div>
  );
}
