import { useQuery } from '@tanstack/react-query';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import { getScatterSample } from '../api/stats';

function ScreenTimeSleepScatter() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['scatter_sample', 1000],
    queryFn: () => getScatterSample(1000),
  });

  if (isLoading) return <div className="card chart-card chart-wide">Loading scatter…</div>;
  if (error) return <div className="card chart-card chart-wide">Error: {error.message}</div>;

  return (
    <div className="card chart-card chart-wide">
      <h2>Screen Time vs. Sleep</h2>
      <p className="chart-subtitle">
        Random sample of {data.points.length} users — {data.x_label} (x) vs. {data.y_label} (y)
      </p>
      <ResponsiveContainer width="100%" height={320}>
        <ScatterChart margin={{ top: 16, right: 24, left: 0, bottom: 16 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis
            type="number"
            dataKey="x"
            name="screen time (hrs)"
            tick={{ fontSize: 11 }}
            label={{ value: 'Screen time (hrs)', position: 'insideBottom', offset: -8, fontSize: 12 }}
          />
          <YAxis
            type="number"
            dataKey="y"
            name="sleep (hrs)"
            tick={{ fontSize: 11 }}
            label={{ value: 'Sleep (hrs)', angle: -90, position: 'insideLeft', fontSize: 12 }}
          />
          <ZAxis range={[20, 20]} />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} />
          <Scatter data={data.points} fill="var(--accent)" fillOpacity={0.5} />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ScreenTimeSleepScatter;
