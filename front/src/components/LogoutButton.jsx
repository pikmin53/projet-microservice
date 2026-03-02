export default function LogoutButton() {
    const handleLogout = () => {
        localStorage.removeItem("token")
        window.location.href = "/login"
    }

    return (
        <button onClick={handleLogout}>Déconnexion</button>
    )
}