import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getExploreRows } from '../api/stats';

const columnLabels = {
  transaction_id: 'Transaction',
  user_id: 'User',
  age: 'Age',
  gender: 'Gender',
  daily_screen_time_hours: 'Daily screen time',
  social_media_hours: 'Social media',
  gaming_hours: 'Gaming',
  work_study_hours: 'Work/study',
  sleep_hours: 'Sleep',
  notifications_per_day: 'Notifications',
  app_opens_per_day: 'App opens',
  weekend_screen_time: 'Weekend screen time',
  stress_level: 'Stress',
  academic_work_impact: 'Academic/work impact',
  addiction_level: 'Addiction level',
  addicted_label: 'Addicted',
};

const defaultColumns = [
  'user_id',
  'age',
  'gender',
  'daily_screen_time_hours',
  'sleep_hours',
  'notifications_per_day',
  'stress_level',
  'addiction_level',
];

const filterGroups = [
  { key: 'gender', label: 'Gender', options: ['Female', 'Male', 'Other'] },
  { key: 'stress_level', label: 'Stress', options: ['Low', 'Medium', 'High'] },
  { key: 'academic_work_impact', label: 'Academic/work impact', options: ['No', 'Yes'] },
  { key: 'addiction_level', label: 'Addiction level', options: ['None', 'Mild', 'Moderate', 'Severe'] },
  { key: 'addicted_label', label: 'Addicted', options: ['0', '1'] },
];

function formatCell(value) {
  if (value == null) return '—';
  if (typeof value === 'number' && !Number.isInteger(value)) return value.toFixed(2);
  return String(value);
}

function Explore() {
  const [filters, setFilters] = useState({ limit: 100 });
  const [visibleColumns, setVisibleColumns] = useState(defaultColumns);
  const { data, isLoading, error } = useQuery({
    queryKey: ['explore', filters],
    queryFn: () => getExploreRows(filters),
  });

  const availableColumns = data?.columns || Object.keys(columnLabels);
  const rows = data?.rows || [];
  const activeFilterCount = useMemo(
    () => Object.entries(filters).filter(([key, value]) => key !== 'limit' && value).length,
    [filters],
  );

  const toggleFilter = (key, value) => {
    setFilters((current) => ({
      ...current,
      [key]: current[key] === value ? '' : value,
    }));
  };

  const toggleColumn = (column) => {
    setVisibleColumns((current) =>
      current.includes(column) ? current.filter((item) => item !== column) : [...current, column],
    );
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Explore</h1>
        <p>Browse the smartphone usage dataset with live filter chips and mutable column display.</p>
      </header>

      <section className="card explore-panel">
        <div className="explore-panel-header">
          <h2>Filters</h2>
          <button className="chip" type="button" onClick={() => setFilters({ limit: filters.limit })}>
            Clear filters{activeFilterCount ? ` (${activeFilterCount})` : ''}
          </button>
        </div>
        {filterGroups.map((group) => (
          <div className="filter-group" key={group.key}>
            <div className="filter-label">{group.label}</div>
            <div className="chip-row">
              {group.options.map((option) => (
                <button
                  className={filters[group.key] === option ? 'chip active' : 'chip'}
                  key={option}
                  type="button"
                  onClick={() => toggleFilter(group.key, option)}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>
        ))}
      </section>

      <section className="card explore-panel">
        <div className="explore-panel-header">
          <h2>Columns</h2>
          <span>{visibleColumns.length} visible</span>
        </div>
        <div className="chip-row">
          {availableColumns.map((column) => (
            <button
              className={visibleColumns.includes(column) ? 'chip active' : 'chip'}
              key={column}
              type="button"
              onClick={() => toggleColumn(column)}
            >
              {columnLabels[column] || column}
            </button>
          ))}
        </div>
      </section>

      <section className="card explore-table-card">
        <div className="explore-panel-header">
          <h2>Data</h2>
          <span>
            {isLoading ? 'Loading…' : `${rows.length.toLocaleString()} of ${(data?.total || 0).toLocaleString()} rows`}
          </span>
        </div>
        {error ? <div className="kpi-error">{error.message}</div> : null}
        {!error ? (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  {visibleColumns.map((column) => (
                    <th key={column}>{columnLabels[column] || column}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr>
                    <td colSpan={visibleColumns.length || 1}>Loading…</td>
                  </tr>
                ) : rows.length ? (
                  rows.map((row) => (
                    <tr key={row.transaction_id}>
                      {visibleColumns.map((column) => (
                        <td key={column}>{formatCell(row[column])}</td>
                      ))}
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={visibleColumns.length || 1}>No rows match the selected filters.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        ) : null}
      </section>
    </div>
  );
}

export default Explore;
