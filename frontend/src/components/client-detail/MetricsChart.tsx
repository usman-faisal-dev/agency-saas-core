interface MetricsChartProps {
  metricName: string;
  dataPoints?: Array<{ date: string; value: number }>;
}

export default function MetricsChart({ metricName, dataPoints = [] }: MetricsChartProps) {
  return (
    <div className="border rounded-lg p-4">
      <h3 className="text-sm font-semibold text-gray-700 mb-2">{metricName}</h3>
      {dataPoints.length === 0 ? (
        <p className="text-xs text-gray-400">No data available</p>
      ) : (
        <div className="h-40 flex items-end gap-1">
          {dataPoints.map((dp, i) => (
            <div
              key={i}
              className="flex-1 bg-blue-400 rounded-t"
              style={{ height: `${Math.min(dp.value, 100)}%` }}
              title={`${dp.date}: ${dp.value}`}
            />
          ))}
        </div>
      )}
    </div>
  );
}
