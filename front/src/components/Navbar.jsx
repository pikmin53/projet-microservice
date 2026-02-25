import { Link } from 'react-router-dom'
export default function Navbar() {
    return (
        <nav class="container">
            <ul>
                <li><Link to="/">Home</Link></li>
                <li><Link to="/login">Connexion</Link></li>
                <li><Link to="/signup">Inscription</Link></li>
                <li><Link to="/dashboard">Dashboard</Link></li>
            </ul>
        </nav>
    )
}