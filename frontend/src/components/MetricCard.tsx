type MetricCardProps = {
  title: string;
  value: string | number;
  subtitle?: string;
};

export default function MetricCard({ title, value, subtitle }: MetricCardProps) {
  return (
    <div className="metric-card">
      <p className="metric-title">{title}</p>
      <p className="metric-value">{value}</p>
      {subtitle && <p className="metric-subtitle">{subtitle}</p>}
    </div>
  );
}
