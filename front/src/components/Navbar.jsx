import { Link } from 'react-router-dom'
import LogoutButton from './LogoutButton'
import { useEffect } from 'react'
import { useState } from 'react'

export default function Navbar() {
    const VITE_API_AUTH = import.meta.env.VITE_API_AUTH_URL;
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        const verifyToken = async () => {
            const token = localStorage.getItem("token");
            if (!token) {
                setIsAuthenticated(false);
                return;
            }
            try {
                const response = await fetch(`${VITE_API_AUTH}/verifyToken`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem("token")}`,
                },
                });
                if (response.ok) {
                    setIsAuthenticated(true);
                } else {
                    setIsAuthenticated(false);
                }
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };
        verifyToken();
    }, []);
    
    return (
        <nav class="container">
            <ul>
                <li><Link to="/">Home</Link></li>
                 {isAuthenticated ? (
                    <li><Link to="/dashboard">Dashboard</Link></li>
                ) : (
                    <>
                    <li><Link to="/login">Connexion</Link></li>
                    <li><Link to="/register">Inscription</Link></li>
                    </>
                )}
                <li><Link to="/contacts">Contacts</Link></li>
                {isAuthenticated && <li><LogoutButton /></li>}
            </ul>
        </nav>
    )
}