import { useEffect, useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from './components/Dashboard';
import AppNav from './components/AppNav';
import DeepDive from './components/DeepDive';
import Explore from './components/Explore';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const routes = {
  '/': Dashboard,
  '/deep-dive': DeepDive,
  '/explore': Explore,
};

function App() {
  const [path, setPath] = useState(window.location.pathname);
  const ActivePage = routes[path] || Dashboard;

  useEffect(() => {
    const onPopState = () => setPath(window.location.pathname);
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  const navigate = (nextPath) => {
    if (nextPath === path) return;
    window.history.pushState({}, '', nextPath);
    setPath(nextPath);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <AppNav currentPath={path} onNavigate={navigate} />
      <ActivePage />
    </QueryClientProvider>
  );
}

export default App;