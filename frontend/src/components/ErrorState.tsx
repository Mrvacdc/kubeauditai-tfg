type ErrorStateProps = {
  message: string;
  onRetry?: () => void;
};

export default function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="error-state">
      <div>
        <strong>No se pudo cargar la información</strong>
        <p>{message}</p>
      </div>

      {onRetry && (
        <button className="secondary-button" onClick={onRetry}>
          Reintentar
        </button>
      )}
    </div>
  );
}
