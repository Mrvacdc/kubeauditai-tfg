type EmptyStateProps = {
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
};

export default function EmptyState({
  title,
  description,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="empty-state">
      <div className="empty-icon">∅</div>
      <h3>{title}</h3>
      {description && <p>{description}</p>}
      {actionLabel && onAction && (
        <button className="secondary-button" onClick={onAction}>
          {actionLabel}
        </button>
      )}
    </div>
  );
}
