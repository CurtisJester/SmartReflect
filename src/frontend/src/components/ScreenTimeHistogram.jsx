import { useQuery } from '@tanstack/react-query';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import { getScreenTimeHistogram } from '../api/stats';

function ScreenTimeHistogram() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['screen_time_histogram', 10],
    queryFn: () => getScreenTimeHistogram(10),
  });

  if (isLoading) return <div className="card chart-card">Loading histogram…</div>;
  if (error) return <div className="card chart-card">Error: {error.message}</div>;

  const chartData = data.bins.map((b) => ({
    label: `${b.bin_start.toFixed(1)}–${b.bin_end.toFixed(1)}`,
    count: b.count,
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
          <Tooltip />
          <Bar dataKey="count" fill="var(--accent)" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ScreenTimeHistogram;
