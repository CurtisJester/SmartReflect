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
import { getAddictionBreakdown } from '../api/stats';

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
    ...Object.fromEntries(
      Object.entries(it.age_counts).map(([ageRange, count]) => [
        ageRange,
        Number(((count / data.total_users) * 100).toFixed(2)),
      ]),
    ),
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
            formatter={(value, name, item) => {
              const level = item?.payload?.level;
              const ageCount =
                data.items.find((it) => it.level === level)?.age_counts?.[name] || 0;
              return [`${value}% (${ageCount.toLocaleString()})`, name];
            }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          {data.age_ranges.map((ageRange, index) => (
            <Bar
              key={ageRange}
              dataKey={ageRange}
              stackId="addiction-age"
              fill={AGE_COLORS[index % AGE_COLORS.length]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default AddictionBreakdown;
