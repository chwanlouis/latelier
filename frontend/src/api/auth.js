const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export async function login(username, password) {
  const body = new URLSearchParams({ username, password })
  const res = await fetch(`${API_BASE}/api/v1/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail || 'Login failed')
  }
  return res.json()
}

export async function logout(refreshToken) {
  const params = refreshToken ? `?refresh_token=${encodeURIComponent(refreshToken)}` : ''
  await fetch(`${API_BASE}/api/v1/auth/logout${params}`, { method: 'POST' })
}

export async function getMe(accessToken) {
  const authHeader = 'Bearer ' + accessToken
  const res = await fetch(`${API_BASE}/api/v1/auth/me`, {
    headers: { Authorization: authHeader },
  })
  if (!res.ok) throw new Error('Unauthorized')
  return res.json()
}
