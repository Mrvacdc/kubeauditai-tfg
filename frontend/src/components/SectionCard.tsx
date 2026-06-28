import type { ReactNode } from "react";

type SectionCardProps = {
  title: string;
  children: ReactNode;
};

export default function SectionCard({ title, children }: SectionCardProps) {
  return (
    <section className="section-card">
      <h2>{title}</h2>
      {children}
    </section>
  );
}
