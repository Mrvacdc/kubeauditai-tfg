type FeedbackBannerProps = {
  variant?: "success" | "info" | "warning";
  message: string;
  actionLabel?: string;
  onAction?: () => void;
  onClose?: () => void;
};

export default function FeedbackBanner({
  variant = "success",
  message,
  actionLabel,
  onAction,
  onClose,
}: FeedbackBannerProps) {
  return (
    <div className={`feedback-banner feedback-${variant}`}>
      <div>
        <strong>{message}</strong>
      </div>

      <div className="action-row">
        {actionLabel && onAction && (
          <button className="secondary-button" onClick={onAction}>
            {actionLabel}
          </button>
        )}

        {onClose && (
          <button className="secondary-button" onClick={onClose}>
            Cerrar
          </button>
        )}
      </div>
    </div>
  );
}
