import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getExploreRows, getExploreExport } from '../api/stats';

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

function ChevronIcon() {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="4,6 8,10 12,6" />
    </svg>
  );
}

function SortIndicator({ column, sort }) {
  return (
    <span className="sort-arrows" aria-hidden="true">
      <span className={sort.column === column && sort.dir === 'asc' ? 'sort-arrow active' : 'sort-arrow'}>▲</span>
      <span className={sort.column === column && sort.dir === 'desc' ? 'sort-arrow active' : 'sort-arrow'}>▼</span>
    </span>
  );
}

const PAGE_SIZE_OPTIONS = [10, 25, 50, 100, 250];

function Explore() {
  const [filters, setFilters] = useState({});
  const [visibleColumns, setVisibleColumns] = useState(defaultColumns);
  const [sort, setSort] = useState({ column: null, dir: null });
  const [filtersOpen, setFiltersOpen] = useState(true);
  const [columnsOpen, setColumnsOpen] = useState(true);
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(100);

  const offset = page * pageSize;

  const { data, isLoading, error } = useQuery({
    queryKey: ['explore', filters, sort, page, pageSize],
    queryFn: () =>
      getExploreRows({
        ...filters,
        limit: pageSize,
        offset,
        ...(sort.column ? { sort_by: sort.column, sort_dir: sort.dir } : {}),
      }),
  });

  const availableColumns = data?.columns || Object.keys(columnLabels);
  const rows = data?.rows || [];
  const total = data?.total || 0;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const activeFilterCount = useMemo(
    () => Object.values(filters).filter(Boolean).length,
    [filters],
  );

  const toggleFilter = (key, value) => {
    setPage(0);
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

  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const exportFilters = {
        ...filters,
        ...(sort.column ? { sort_by: sort.column, sort_dir: sort.dir } : {}),
      };
      const { rows: allRows } = await getExploreExport(exportFilters);
      const header = visibleColumns.map((col) => columnLabels[col] || col);
      const body = allRows.map((row) =>
        visibleColumns.map((col) => {
          const val = formatCell(row[col]);
          return /[,"\n]/.test(val) ? `"${val.replace(/"/g, '""')}"` : val;
        }),
      );
      const csv = [header, ...body].map((r) => r.join(',')).join('\n');
      const name = window.prompt('Filename:', 'explore.csv');
      if (!name) return;
      const a = document.createElement('a');
      a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
      a.download = name.endsWith('.csv') ? name : `${name}.csv`;
      a.click();
    } finally {
      setIsExporting(false);
    }
  };

  const handleSort = (column) => {
    setPage(0);
    setSort((current) => {
      if (current.column !== column) return { column, dir: 'asc' };
      if (current.dir === 'asc') return { column, dir: 'desc' };
      return { column: null, dir: null };
    });
  };

  const rowCountLabel = useMemo(() => {
    if (isLoading) return 'Loading…';
    if (!rows.length) return '0 rows';
    const from = (offset + 1).toLocaleString();
    const to = (offset + rows.length).toLocaleString();
    return `${from}–${to} of ${total.toLocaleString()} rows`;
  }, [isLoading, rows.length, offset, total, pageSize]);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Explore</h1>
        <p>Browse the smartphone usage dataset with live filter chips and mutable column display.</p>
      </header>

      <section className="card explore-panel">
        <div className="explore-panel-header">
          <h2>Filters</h2>
          <div className="explore-panel-header-right">
            <button className="chip" type="button" onClick={() => { setPage(0); setFilters({}); }}>
              Clear filters{activeFilterCount ? ` (${activeFilterCount})` : ''}
            </button>
            <button
              className={`drawer-toggle${filtersOpen ? ' open' : ''}`}
              type="button"
              onClick={() => setFiltersOpen((o) => !o)}
              aria-label={filtersOpen ? 'Collapse filters' : 'Expand filters'}
            >
              <ChevronIcon />
            </button>
          </div>
        </div>
        <div className={`drawer-body${filtersOpen ? '' : ' closed'}`}>
          <div className="drawer-body-inner">
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
          </div>
        </div>
      </section>

      <section className="card explore-panel">
        <div className="explore-panel-header">
          <h2>Columns</h2>
          <div className="explore-panel-header-right">
            <span>{visibleColumns.length} visible</span>
            <button
              className={`drawer-toggle${columnsOpen ? ' open' : ''}`}
              type="button"
              onClick={() => setColumnsOpen((o) => !o)}
              aria-label={columnsOpen ? 'Collapse columns' : 'Expand columns'}
            >
              <ChevronIcon />
            </button>
          </div>
        </div>
        <div className={`drawer-body${columnsOpen ? '' : ' closed'}`}>
          <div className="drawer-body-inner">
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
          </div>
        </div>
      </section>

      <section className="card explore-table-card">
        <div className="explore-panel-header">
          <h2>Data</h2>
          <div className="explore-panel-header-right">
            <span>{rowCountLabel}</span>
            <select
              className="page-size-select"
              value={pageSize}
              onChange={(e) => { setPage(0); setPageSize(Number(e.target.value)); }}
            >
              {PAGE_SIZE_OPTIONS.map((n) => (
                <option key={n} value={n}>{n} per page</option>
              ))}
            </select>
            <button
              className="chip"
              type="button"
              onClick={handleExport}
              disabled={isExporting || isLoading || !!error}
            >
              {isExporting ? 'Exporting…' : 'Export CSV'}
            </button>
          </div>
        </div>
        {error ? <div className="kpi-error">{error.message}</div> : null}
        {!error ? (
          <>
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    {visibleColumns.map((column) => (
                      <th key={column} className="sortable-th" onClick={() => handleSort(column)}>
                        {columnLabels[column] || column}
                        <SortIndicator column={column} sort={sort} />
                      </th>
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
            <div className="table-pager">
              <button
                className="chip"
                type="button"
                onClick={() => setPage((p) => p - 1)}
                disabled={page === 0 || isLoading}
              >
                ← Prev
              </button>
              <span>Page {page + 1} of {totalPages}</span>
              <button
                className="chip"
                type="button"
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= totalPages - 1 || isLoading}
              >
                Next →
              </button>
            </div>
          </>
        ) : null}
      </section>
    </div>
  );
}

export default Explore;
