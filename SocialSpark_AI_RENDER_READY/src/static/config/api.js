const API_BASE_URL = '/api'

export const apiConfig = {
  baseURL: API_BASE_URL,
  endpoints: {
    auth: {
      login: '/auth/login',
      register: '/auth/register',
      logout: '/auth/logout'
    },
    user: {
      profile: '/user/profile',
      update: '/user/update'
    },
    content: {
      list: '/content',
      create: '/content',
      update: '/content',
      delete: '/content'
    },
    generate: {
      content: '/generate/content'
    },
    analytics: {
      dashboard: '/analytics/dashboard'
    }
  }
}

export default apiConfig

