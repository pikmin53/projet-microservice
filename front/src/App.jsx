import Header from './components/Header'
import Footer from './components/Footer'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Contacts from './pages/Contacts'
import { Routes, Route } from 'react-router-dom'

function App() {
  return (
    <>
      <main class="container">
        <Routes>
          <Route path="/" element={<><Navbar /><Header /><Home /></>} />
          <Route path="/login" element={<><Navbar /><Header /><Login /></>} />
          <Route path="/register" element={<><Navbar /><Header /><Register /></>} />
          <Route path="/dashboard" element={<><Navbar /><Header /><Dashboard /></>} />
          <Route path="/contacts" element={<><Navbar /><Header /><Contacts /></>} />
        </Routes>
      </main>
      < Footer />
    </>
  )
}

export default App
