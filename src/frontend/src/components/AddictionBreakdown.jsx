import { useQuery } from '@tanstack/react-query';
import {
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import { getAddictionBreakdown } from '../api/stats';

const ADDICTED_COLOR = 'var(--accent)';
const NON_ADDICTED_COLOR = 'var(--accent-border)';

function AddictionBreakdown() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['addiction_breakdown'],
    queryFn: getAddictionBreakdown,
  });

  if (isLoading) return <div className="card chart-card">Loading breakdown…</div>;
  if (error) return <div className="card chart-card">Error: {error.message}</div>;

  const chartData = data.items.map((it) => ({
    level: it.level,
    pct: Number(it.pct_of_total.toFixed(2)),
    count: it.count,
    addicted: it.is_addicted_designation,
  }));

  const designation = (data.addicted_designation || []).join(' or ');
  const coverage = data.coverage_pct.toFixed(1);

  return (
    <div className="card chart-card">
      <h2>Addiction Level Breakdown</h2>
      <p className="chart-subtitle">
        % of all {data.total_users.toLocaleString()} users · {coverage}% coverage ·{' '}
        <strong>{designation}</strong> classifies as addicted
      </p>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 16, right: 24, left: 16, bottom: 8 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis
            type="number"
            tick={{ fontSize: 11 }}
            tickFormatter={(v) => `${v}%`}
            domain={[0, 'auto']}
          />
          <YAxis dataKey="level" type="category" tick={{ fontSize: 12 }} width={80} />
          <Tooltip
            formatter={(value, _name, item) => {
              const count = item?.payload?.count;
              return [`${value}%${count != null ? ` (${count.toLocaleString()})` : ''}`, '% of total'];
            }}
          />
          <Bar dataKey="pct">
            {chartData.map((entry) => (
              <Cell
                key={entry.level}
                fill={entry.addicted ? ADDICTED_COLOR : NON_ADDICTED_COLOR}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default AddictionBreakdown;
