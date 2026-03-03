import { Link } from 'react-router-dom'
import LogoutButton from './LogoutButton'
export default function Navbar() {
    return (
        <nav class="container">
            <ul>
                <li><Link to="/">Home</Link></li>
                <li><Link to="/login">Connexion</Link></li>
                <li><Link to="/register">Inscription</Link></li>
                <li><Link to="/dashboard">Dashboard</Link></li>
                <li><Link to="/contacts">Contacts</Link></li>
                <li><LogoutButton /></li>
            </ul>
        </nav>
    )
}