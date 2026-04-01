import { Button } from 'antd'
import { Navigate, useNavigate } from 'react-router-dom'
import { AUTH_TOKEN_KEY } from '../constants/auth'

export default function HomePage() {
  const navigate = useNavigate()
  const token = localStorage.getItem(AUTH_TOKEN_KEY)

  if (!token) {
    return <Navigate to="/login" replace />
  }

  const logout = () => {
    localStorage.clear()
    navigate('/login', { replace: true })
  }

  return (
    <div style={{ minHeight: '100vh', position: 'relative', padding: 24 }}>
      <div style={{ position: 'absolute', top: 24, right: 24 }}>
        <Button onClick={logout}>Выйти</Button>
      </div>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100%',
        }}
      >
        <span style={{ fontSize: 18 }}>Привет</span>
      </div>
    </div>
  )
}
