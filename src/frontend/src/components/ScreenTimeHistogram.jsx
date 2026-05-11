import { useQuery } from '@tanstack/react-query';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import { getScreenTimeHistogram } from '../api/stats';

const AGE_COLORS = [
  '#a98bdc',
  '#5182ec',
  '#afc97f',
  '#059669',
  '#ca8a04',
  '#ea580c',
  '#dc2626',
  '#be185d',
];

function ScreenTimeHistogram() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['screen_time_histogram'],
    queryFn: getScreenTimeHistogram,
  });

  if (isLoading) return <div className="card chart-card">Loading histogram…</div>;
  if (error) return <div className="card chart-card">Error: {error.message}</div>;

  const chartData = data.bins.map((b) => ({
    label: `${b.bin_start}-${b.bin_end}hrs`,
    count: b.count,
    ...b.age_counts,
  }));

  return (
    <div className="card chart-card">
      <h2>Daily Screen Time Distribution</h2>
      <p className="chart-subtitle">Hours per day, all users</p>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData} margin={{ top: 16, right: 16, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="label" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip
            formatter={(value, name, item) => {
              const total = item?.payload?.count || 0;
              const pct = total ? ((Number(value) / total) * 100).toFixed(1) : '0.0';
              return [`${Number(value).toLocaleString()} (${pct}%)`, name];
            }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          {data.age_ranges.map((ageRange, index) => (
            <Bar
              key={ageRange}
              dataKey={ageRange}
              stackId="screen-time-age"
              fill={AGE_COLORS[index % AGE_COLORS.length]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ScreenTimeHistogram;
