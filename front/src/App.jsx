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
      <Navbar />
      < Header />
      <main class="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/contacts" element={<Contacts />} />
        </Routes>
      </main>
      < Footer />
    </>
  )
}

export default App
