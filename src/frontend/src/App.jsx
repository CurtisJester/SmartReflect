// frontend/src/App.jsx
import { useEffect, useState } from 'react';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch data from your FastAPI route
    fetch('http://localhost:8000/get_one')  // Change to your route
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(error => {
        setError(error.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h1>FastAPI Data</h1>
      <pre style={{ 
        background: '#f4f4f4', 
        padding: '15px', 
        borderRadius: '5px',
        overflow: 'auto' 
      }}>
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}

export default App;