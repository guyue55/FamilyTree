import client from './client'

export async function login(username: string, password: string) {
  const res = await client.post('/auth/login', { username, password })
  return res.data
}

export async function register(user: {
  username: string
  email: string
  password: string
  confirm_password: string
  first_name?: string
  last_name?: string
}) {
  const res = await client.post('/auth/register', user)
  return res.data
}

export async function ensureAuthToken() {
  const token = localStorage.getItem('access_token')
  if (token) return token
  const devUser = {
    username: 'devuser',
    email: 'devuser@example.com',
    password: 'DevUser_12345!',
    confirm_password: 'DevUser_12345!',
    first_name: 'Dev',
    last_name: 'User'
  }
  try {
    const loginResp = await login(devUser.username, devUser.password)
    if (loginResp && loginResp.access_token) {
      localStorage.setItem('access_token', loginResp.access_token)
      return loginResp.access_token
    }
  } catch {
    // Ignore login error
  }
  try {
    await register(devUser)
    const loginResp = await login(devUser.username, devUser.password)
    if (loginResp && loginResp.access_token) {
      localStorage.setItem('access_token', loginResp.access_token)
      return loginResp.access_token
    }
  } catch {
    // Ignore register/login error
  }
  return null
}
