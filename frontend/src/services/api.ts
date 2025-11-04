import axios from 'axios'

// 상대 경로 사용 (현재 도메인의 /api로 자동 프록시)
// 프로덕션에서는 절대 경로를 사용하지 않고 상대 경로만 사용
// baseURL은 빈 문자열로 설정하여 절대 경로를 사용하도록 함
const getBaseURL = () => {
  const envUrl = import.meta.env.VITE_API_BASE_URL
  if (envUrl && (envUrl.startsWith('http://') || envUrl.startsWith('https://'))) {
    // 절대 URL이면 상대 경로로 변환
    try {
      const url = new URL(envUrl)
      return url.pathname || ''
    } catch {
      return ''
    }
  }
  // 환경 변수가 없거나 '/api'로 시작하면 빈 문자열 반환 (절대 경로 사용)
  return ''
}

export const api = axios.create({
  baseURL: getBaseURL(),
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api




