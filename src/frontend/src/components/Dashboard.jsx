import { useQuery } from '@tanstack/react-query';
import { getSummary } from '../api/stats';
import KpiCard from './KpiCard';
import ScreenTimeHistogram from './ScreenTimeHistogram';
import AddictionBreakdown from './AddictionBreakdown';
import AgeBreakdown from './AgeBreakdown';
import ScreenTimeSleepScatter from './ScreenTimeSleepScatter';

function formatNumber(n, digits = 0) {
  if (n == null || Number.isNaN(n)) return '—';
  return n.toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['summary'],
    queryFn: getSummary,
  });

  const summaryProps = (value, unit, digits) => ({
    loading: isLoading,
    error,
    value: isLoading || error ? null : formatNumber(value, digits),
    unit,
  });

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>SmartReflect on Smartphone Use</h1>
        <p>Explore a dataset of smartphone use and overuse.</p>
      </header>

      <section className="kpi-row">
        <KpiCard label="Total users" {...summaryProps(data?.total_users, '', 0)} />
        <KpiCard
          label="Avg daily screen time"
          {...summaryProps(data?.avg_screen_time_hours, 'hrs', 2)}
        />
        <KpiCard label="Avg sleep" {...summaryProps(data?.avg_sleep_hours, 'hrs', 2)} />
        <KpiCard
          label="% addicted"
          {...summaryProps(data?.pct_addicted, '%', 1)}
          footnote={
            data
              ? `${(data.addicted_designation || []).join(' + ') || '—'} \u2022 ${formatNumber(
                  data.coverage_pct,
                  1,
                )}% coverage`
              : null
          }
        />
      </section>

      <section className="chart-grid">
        <ScreenTimeHistogram />
        <AddictionBreakdown />
        <AgeBreakdown />
        <ScreenTimeSleepScatter />
      </section>
    </div>
  );
}

export default Dashboard;
