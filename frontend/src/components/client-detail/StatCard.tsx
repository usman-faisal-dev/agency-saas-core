interface StatCardProps {
  label: string;
  value: string | number;
  delta?: string;
}

export default function StatCard({ label, value, delta }: StatCardProps) {
  return (
    <div className="border rounded-lg p-4 flex flex-col gap-1">
      <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">{label}</span>
      <span className="text-2xl font-bold text-gray-900">{value}</span>
      {delta && (
        <span className={`text-xs font-medium ${delta.startsWith("-") ? "text-red-600" : "text-green-600"}`}>
          {delta}
        </span>
      )}
    </div>
  );
}
