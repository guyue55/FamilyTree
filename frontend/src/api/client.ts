import axios from 'axios'

const base = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE) || '/api/v1'

const client = axios.create({
  baseURL: base,
  timeout: 15000
})

if ((typeof import.meta !== 'undefined' && import.meta.env?.DEV)) {
  console.log('API base URL:', base)
}

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default client
