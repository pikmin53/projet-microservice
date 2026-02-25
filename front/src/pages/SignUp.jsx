import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function SignUp() {

  const [name, setName] = useState('')
  const [firstName, setFirstName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    try {
      const response = await fetch('http://api:8000/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, firstName, email, password }),
      })

      if (response.ok) {
        navigate('/login')
      } else {
        setError('Erreur lors de l\'inscription')
      }
    } catch (err) {
      setError('Erreur de connexion: ' + err.message)
    }
  }

  return (
    <div className="container">
      <h2>Inscription</h2>
      <form onSubmit={handleSubmit}>
        <input 
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Nom"
        />
        <input 
          type="text"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          placeholder="Prénom"
        />
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
        <input 
          type="password" 
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          placeholder="Confirmer le mot de passe"
        />
        {error && <p className="error" style={{color:"red"}}>{error}</p>}
        <button type="submit">S'inscrire</button>
      </form>
    </div>
  )
}