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
import { getAgeBreakdown } from '../api/stats';

function AgeBreakdown() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['age_breakdown'],
    queryFn: getAgeBreakdown,
  });

  if (isLoading) return <div className="card chart-card">Loading age breakdown…</div>;
  if (error) return <div className="card chart-card">Error: {error.message}</div>;

  const chartData = data.items.map((it) => ({
    ageRange: it.age_range,
    count: it.count,
    pct: Number(it.pct_of_total.toFixed(2)),
  }));

  return (
    <div className="card chart-card">
      <h2>Age Breakdown</h2>
      <p className="chart-subtitle">Users by age range, all {data.total_users.toLocaleString()} users</p>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData} margin={{ top: 16, right: 16, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="ageRange" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip
            formatter={(value, name, item) => {
              if (name === 'count') {
                const pct = item?.payload?.pct;
                return [
                  `${Number(value).toLocaleString()}${pct != null ? ` (${pct}%)` : ''}`,
                  'users',
                ];
              }
              return [value, name];
            }}
          />
          <Bar dataKey="count" fill="var(--accent)" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default AgeBreakdown;
