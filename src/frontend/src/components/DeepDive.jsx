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
import { getLeastAddicted, getMostAddicted, getWeekendMaxxing } from '../api/stats';
import KpiCard from './KpiCard';

function formatNumber(n, digits = 0) {
  if (n == null || Number.isNaN(n)) return '—';
  return n.toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function formatRange(min, max, digits = 0) {
  if (min == null || max == null || Number.isNaN(min) || Number.isNaN(max)) return '—';
  return `${formatNumber(min, digits)}–${formatNumber(max, digits)}`;
}

function BreakdownChart({ title, subtitle, items }) {
  const chartData = items.map((item) => ({
    label: item.label,
    count: item.count,
    pct: Number(item.pct_of_cohort.toFixed(2)),
  }));

  return (
    <div className="card chart-card">
      <h2>{title}</h2>
      <p className="chart-subtitle">{subtitle}</p>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 16, right: 24, left: 16, bottom: 8 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis type="number" tick={{ fontSize: 11 }} tickFormatter={(v) => `${v}%`} />
          <YAxis dataKey="label" type="category" tick={{ fontSize: 12 }} width={80} />
          <Tooltip
            formatter={(value, _name, item) => {
              const count = item?.payload?.count;
              return [`${value}%${count != null ? ` (${count.toLocaleString()})` : ''}`, '% of cohort'];
            }}
          />
          <Bar dataKey="pct" fill="var(--accent)" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function DeepDiveSection({ title, subtitle, data, isLoading, error, cohortFootnote, cohortLabel, rangeLabel = 'Daily screen time range' }) {
  const kpiProps = (value, unit, digits) => ({
    loading: isLoading,
    error,
    value: isLoading || error ? null : formatNumber(value, digits),
    unit,
  });

  return (
    <>
      <header className="dashboard-header">
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </header>

      <section className="kpi-row">
        <KpiCard
          label="Cohort users"
          {...kpiProps(data?.cohort_users, '', 0)}
          footnote={
            data ? `${cohortFootnote} of ${formatNumber(data.total_users, 0)} users` : null
          }
        />
        <KpiCard
          label={rangeLabel}
          {...kpiProps(formatRange(data?.min_screen_time_hours, data?.max_screen_time_hours, 2), 'hrs')}
        />
        <KpiCard label="Avg sleep" {...kpiProps(data?.avg_sleep_hours, 'hrs', 2)} />
        <KpiCard
          label="Avg notifications"
          {...kpiProps(data?.avg_notifications_per_day, '/day', 1)}
        />
      </section>

      {error ? <section className="card">Error: {error.message}</section> : null}

      {!isLoading && !error && data ? (
        <section className="chart-grid">
          <BreakdownChart
            title="Addiction Level Breakdown"
            subtitle={`% of ${data.cohort_users.toLocaleString()} ${cohortLabel}`}
            items={data.addiction_breakdown}
          />
          <BreakdownChart
            title="Age Breakdown"
            subtitle={`Age ranges within ${data.cohort_users.toLocaleString()} ${cohortLabel}`}
            items={data.age_breakdown}
          />
        </section>
      ) : null}
    </>
  );
}

function DeepDive() {
  const mostAddicted = useQuery({
    queryKey: ['most_addicted'],
    queryFn: getMostAddicted,
  });
  const leastAddicted = useQuery({
    queryKey: ['least_addicted'],
    queryFn: getLeastAddicted,
  });
  const weekendMaxxing = useQuery({
    queryKey: ['weekend_maxxing'],
    queryFn: getWeekendMaxxing,
  });

  return (
    <div className="dashboard">
      <DeepDiveSection
        title="Most Addicted"
        subtitle="Stats and charts for users in the top 10th percentile of daily screen time."
        data={mostAddicted.data}
        isLoading={mostAddicted.isLoading}
        error={mostAddicted.error}
        cohortFootnote="Top 10%"
        cohortLabel="high screen-time users"
      />
      <hr className="section-divider" />
      <DeepDiveSection
        title="Least Addicted"
        subtitle="Stats and charts for users in the bottom 10th percentile of daily screen time."
        data={leastAddicted.data}
        isLoading={leastAddicted.isLoading}
        error={leastAddicted.error}
        cohortFootnote="Bottom 10%"
        cohortLabel="low screen-time users"
      />
      <hr className="section-divider" />
      <DeepDiveSection
        title="Weekend Maxxing"
        subtitle="Stats and charts for users in the top 10th percentile of weekend screen time."
        data={weekendMaxxing.data}
        isLoading={weekendMaxxing.isLoading}
        error={weekendMaxxing.error}
        cohortFootnote="Top 10%"
        cohortLabel="high weekend screen-time users"
        rangeLabel="Weekend screen time range"
      />
    </div>
  );
}

export default DeepDive;
