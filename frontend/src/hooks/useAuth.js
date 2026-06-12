import { useState, useEffect, useCallback } from 'react'
import { login as apiLogin, logout as apiLogout, getMe } from '../api/auth'

export function useAuth() {
  const [accessToken, setAccessToken] = useState(() => localStorage.getItem('access_token'))
  const [refreshToken, setRefreshToken] = useState(() => localStorage.getItem('refresh_token'))
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(() => !!localStorage.getItem('access_token'))

  useEffect(() => {
    if (!accessToken) {
      return
    }
    getMe(accessToken)
      .then(setUser)
      .catch(() => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        setAccessToken(null)
        setRefreshToken(null)
      })
      .finally(() => setLoading(false))
  }, [accessToken])

  const login = useCallback(async (username, password) => {
    const data = await apiLogin(username, password)
    localStorage.setItem('access_token', data.access_token)
    if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token)
    setAccessToken(data.access_token)
    setRefreshToken(data.refresh_token || null)
    const me = await getMe(data.access_token)
    setUser(me)
  }, [])

  const logout = useCallback(async () => {
    try {
      await apiLogout(refreshToken)
    } catch {
      // best-effort
    }
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setAccessToken(null)
    setRefreshToken(null)
    setUser(null)
  }, [refreshToken])

  return {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!accessToken,
  }
}
