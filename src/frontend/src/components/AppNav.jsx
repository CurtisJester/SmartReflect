const navItems = [
  { path: '/', label: 'Dashboard' },
  { path: '/deep-dive', label: 'Deep Dive' },
  { path: '/explore', label: 'Explore' },
];

function AppNav({ currentPath, onNavigate }) {
  return (
    <nav className="app-nav">
      <a
        className="app-brand"
        href="/"
        onClick={(event) => {
          event.preventDefault();
          onNavigate('/');
        }}
      >
        SmartReflect
      </a>
      <div className="nav-links">
        {navItems.map((item) => (
          <a
            key={item.path}
            className={currentPath === item.path ? 'nav-link active' : 'nav-link'}
            href={item.path}
            onClick={(event) => {
              event.preventDefault();
              onNavigate(item.path);
            }}
          >
            {item.label}
          </a>
        ))}
      </div>
    </nav>
  );
}

export default AppNav;
