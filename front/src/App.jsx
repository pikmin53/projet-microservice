import Header from './components/Header'
import Footer from './components/Footer'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Login from './pages/Login'
import SignUp from './pages/SignUp'
import Dashboard from './pages/Dashboard'
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
          <Route path="/signup" element={<SignUp />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </main>
      < Footer />
    </>
  )
}

export default App
