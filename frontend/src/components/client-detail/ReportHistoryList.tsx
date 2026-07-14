import Link from "next/link";
import type { Report } from "@/types/api";

interface ReportHistoryListProps {
  reports: Report[];
  clientId: string;
}

export default function ReportHistoryList({ reports, clientId }: ReportHistoryListProps) {
  if (reports.length === 0) {
    return <p className="text-sm text-gray-400">No reports generated yet.</p>;
  }

  return (
    <ul className="divide-y">
      {reports.map((report) => (
        <li key={report.id} className="py-3">
          <Link
            href={`/clients/${clientId}/reports/${report.id}`}
            className="text-sm font-medium text-blue-600 hover:underline"
          >
            Report — {report.start_date} to {report.end_date}
          </Link>
          <span className="ml-2 text-xs text-gray-500 capitalize">{report.status}</span>
        </li>
      ))}
    </ul>
  );
}
