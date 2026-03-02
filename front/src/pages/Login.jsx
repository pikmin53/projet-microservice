  import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const BASE = import.meta.env.VITE_API_URL;
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    try {
        const response = await fetch(`${BASE}/auth/login`, {

        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      })

      const data = await response.json()
      localStorage.setItem("token", data.access_token)

      if (response.ok) {
        navigate('/dashboard')
      } else {
        setError('Identifiants incorrects')
      }
    } catch (err) {
      setError('Erreur de connexion: ' + err.message)
    }
  }

  return (
    <div className="container">
      <h2>Connexion</h2>
      <form onSubmit={handleSubmit}>
        <input 
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
        />
        <input 
          type="password" 
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Mot de passe"
        />
        {error && <p className="error" style={{color:"red"}}>{error}</p>}
        <button type="submit">Se connecter</button>
      </form>
    </div>
  )
}