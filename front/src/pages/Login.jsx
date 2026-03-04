import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLocation } from 'react-router-dom'


export default function Login() {
  const location = useLocation()
  const message = location.state?.error

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const VITE_API_AUTH = import.meta.env.VITE_API_AUTH_URL;
  console.log("URL d'authentification appelée :", `${VITE_API_AUTH}/token`)

  
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await fetch(`${VITE_API_AUTH}/token`, {

        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      })
      console.log("Réponse du serveur:", response)

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
      {message && <p className="error" style={{color:"red"}}>{message}</p>}
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