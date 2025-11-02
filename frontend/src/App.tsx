import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Assets from './pages/Assets'
import Login from './pages/Login'
import Disaster from './pages/Disaster'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        {/* /disaster는 인증 없이 접근 가능하도록 변경 */}
        <Route element={<Layout />}>
          <Route path="/disaster" element={<Disaster />} />
        </Route>
        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route path="/" element={<Home />} />
            <Route path="/assets" element={<Assets />} />
          </Route>
        </Route>
      </Routes>
    </Router>
  )
}

export default App




