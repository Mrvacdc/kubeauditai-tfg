type LoadingStateProps = {
  message?: string;
};

export default function LoadingState({
  message = "Cargando información...",
}: LoadingStateProps) {
  return (
    <div className="loading-state">
      <div className="spinner" />
      <p>{message}</p>
    </div>
  );
}
