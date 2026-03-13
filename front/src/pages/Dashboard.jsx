import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import MetricsChart from '../components/MetricsChart'

const METRIC_NAMES = ['cpu', 'ram', 'accuracy', 'vitesse_exec']

export default function Dashboard() {
  const [data, setData] = useState({
    cpu: [],
    ram : [],
    accuracy : [],
    vitesse_exec : [],
  })
  const [user, setUser] = useState(null)
  const [error, setError] = useState(null)
  const navigate = useNavigate()
  const VITE_API_GATEWAY = import.meta.env.VITE_API_GATEWAY_URL ;
  const VITE_API_AUTH = import.meta.env.VITE_API_AUTH_URL;

  useEffect(() => {
    const fetchData = async () => {
      try {
        const headers = {
          'Authorization': `Bearer ${localStorage.getItem("token")}`,
        }

        const auth = await fetch(`${VITE_API_AUTH}/verifyToken`, {
          method: 'GET',
          headers: headers
        })

        if (!auth.ok) {
          navigate('/login',{ state: { error: 'Session expirée, veuillez vous reconnecter.' } })
          return
        }
        const response = await fetch(`${VITE_API_GATEWAY}/models/data`, {

        method: 'GET',
        headers: headers
        })

        if (!response.ok) {
          throw new Error(`Erreur HTTP: ${response.status}`);
        }
        const result = await response.json()
        setUser(result.user.user)
        const resultData = result.message || {}
        setError(null)
        setData(prevData => {
          const newData = { ...prevData }
          for (const key of METRIC_NAMES) {
            const incoming = resultData[key]

            if (Array.isArray(incoming)) {
              newData[key] = incoming
              continue
            }

            if (incoming !== undefined && incoming !== null) {
              newData[key] = [...prevData[key], incoming]
            }
          }
          return newData
        })
      }
      catch (err) {
        setError({ message: 'Erreur de connexion: ' + err.message })
        console.error('Erreur de connexion: ' + err.message)
      }
    }
    
    fetchData()
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [navigate, VITE_API_AUTH, VITE_API_GATEWAY])

  return (
    <div>
      <h2>Dashboard</h2>
      {error?.message && <p style={{ color: 'red' }}>{error.message}</p>}
      <article>
        <h2>Métriques utilisateur</h2>
        <MetricsChart
          data={data.accuracy}
          title="Accuracy"
          unit=""
        />
        <MetricsChart
          data={data.vitesse_exec}
          title="Vitesse d'exécution"
          unit="img/s"
        />
      </article>
      {user && user.statut === 'admin' && <div>
        <article>
          <h2>Métriques admin</h2>
          <MetricsChart
          data={data.cpu}
          title="CPU"
          unit="%"
        />
          <MetricsChart
            data={data.ram}
            title="RAM"
            unit="Mb"
          />
        </article>
      </div>}
    </div>
  )
}