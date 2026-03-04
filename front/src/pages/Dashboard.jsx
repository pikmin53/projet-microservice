import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

// Ne fonctionne pas 
export default function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const navigate = useNavigate()
  const VITE_API_GATEWAY = import.meta.env.VITE_API_GATEWAY_URL;
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
        }

        const response = await fetch(`${VITE_API_GATEWAY}/models/data`, {

        method: 'GET',
        headers: headers
      })

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }
      const result = await response.json()
      setData(result)
      console.log("Données reçues du serveur:", result)
      }
      catch (err) {
        setError('Erreur de connexion: ' + err.message)
        console.error('Erreur de connexion: ' + err.message)
      }
    }
    
    fetchData()
  }, [])

  return (
    <div className="container">
      <h2>Dashboard</h2>
      <p>Page de tableau de bord</p>
      {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
      {error && <p className="error" style={{color:"red"}}>{error}</p>}
    </div>
  )
}