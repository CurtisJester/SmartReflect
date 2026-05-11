function KpiCard({ label, value, unit, loading, error, footnote }) {
  let display;
  if (loading) display = '…';
  else if (error) display = '—';
  else display = value;

  return (
    <div className="card kpi-card">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">
        {display}
        {unit && !loading && !error ? <span className="kpi-unit"> {unit}</span> : null}
      </div>
      {error ? (
        <div className="kpi-error">error</div>
      ) : footnote && !loading ? (
        <div className="kpi-footnote">{footnote}</div>
      ) : null}
    </div>
  );
}

export default KpiCard;
