import type { ReportNarrative as ReportNarrativeType } from "@/types/api";

interface ReportNarrativeProps {
  narrative: ReportNarrativeType;
}

export default function ReportNarrative({ narrative }: ReportNarrativeProps) {
  const sections: Array<{ title: string; body: string }> = [
    { title: "Executive Summary", body: narrative.executive_summary },
    { title: "Traffic & Acquisition", body: narrative.traffic_and_acquisition },
    { title: "Ad Performance", body: narrative.ad_performance },
    { title: "Notable Changes", body: narrative.notable_changes },
    { title: "Recommendations", body: narrative.recommendations },
  ];

  return (
    <div className="space-y-6">
      {sections.map((section) => (
        <section key={section.title}>
          <h2 className="text-lg font-semibold text-gray-800 mb-1">{section.title}</h2>
          <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap">{section.body}</p>
        </section>
      ))}
    </div>
  );
}
