type StatusBadgeProps = {
  value: string | number | null | undefined;
};

function getBadgeClass(value: string) {
  const normalized = value.toUpperCase();

  if (normalized === "PASS" || normalized === "COMPLETED" || normalized === "FINALIZADA") {
    return "badge badge-success";
  }

  if (normalized === "FAIL" || normalized === "FAILED" || normalized === "ERROR" || normalized === "HIGH") {
    return "badge badge-danger";
  }

  if (normalized === "WARN" || normalized === "WARNING" || normalized === "MEDIUM") {
    return "badge badge-warning";
  }

  if (normalized === "LOW") {
    return "badge badge-info";
  }

  if (normalized === "PENDING") {
    return "badge badge-info";
  }

  if (normalized === "APPLIED") {
    return "badge badge-success";
  }

  if (normalized === "DISMISSED") {
    return "badge badge-neutral";
  }

  if (normalized === "DEEPSEEK") {
    return "badge badge-info";
  }

  if (normalized === "RULE_ENGINE") {
    return "badge badge-neutral";
  }

  return "badge badge-neutral";
}

export default function StatusBadge({ value }: StatusBadgeProps) {
  const label = value === null || value === undefined ? "N/D" : String(value);

  return <span className={getBadgeClass(label)}>{label}</span>;
}
