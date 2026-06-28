export function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return "N/D";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "N/D";
  }

  return new Intl.DateTimeFormat("es-AR", {
    timeZone: "America/Argentina/Buenos_Aires",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  })
    .format(date)
    .replace(",", "");
}
