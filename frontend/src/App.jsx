import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE_URL = 'http://localhost:8000/api'

function App() {
  const [healthStatus, setHealthStatus] = useState(null)
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    checkApiHealth()
  }, [])

  const checkApiHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health/`)
      setHealthStatus(response.data)
      setError(null)
    } catch (err) {
      setError('Unable to connect to Django API')
      console.error('API health check failed:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Casino CRM</h1>
        <p>Django + React Web Application</p>
      </header>
      
      <main>
        <div className="status-card">
          <h2>API Status</h2>
          {loading ? (
            <p>Checking API connection...</p>
          ) : error ? (
            <div className="error">
              <p>❌ {error}</p>
              <p>Make sure Django server is running on port 8000</p>
            </div>
          ) : (
            <div className="success">
              <p>✅ {healthStatus?.message}</p>
              <p>Status: {healthStatus?.status}</p>
            </div>
          )}
        </div>
        
        <div className="info-card">
          <h2>Project Structure</h2>
          <ul>
            <li><strong>Backend:</strong> Django REST API with PostgreSQL</li>
            <li><strong>Frontend:</strong> React SPA with Vite</li>
            <li><strong>Database:</strong> PostgreSQL (via Docker)</li>
            <li><strong>API:</strong> Django REST Framework</li>
          </ul>
        </div>
        
        <div className="getting-started">
          <h2>Getting Started</h2>
          <ol>
            <li>Start PostgreSQL: <code>docker-compose up -d</code></li>
            <li>Run Django migrations: <code>cd backend && python manage.py migrate</code></li>
            <li>Start Django server: <code>python manage.py runserver</code></li>
            <li>Start React app: <code>cd frontend && npm run dev</code></li>
          </ol>
        </div>
      </main>
    </div>
  )
}

export default App
