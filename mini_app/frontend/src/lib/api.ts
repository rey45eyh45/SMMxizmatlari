import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import type { 
  User, 
  Platform, 
  Service, 
  ServiceCategory,
  Order, 
  Payment, 
  ReferralStats,
  SMSPlatform,
  SMSCountry,
} from '../types'

// API URL - production'da same origin, local'da localhost:8000
const API_URL = import.meta.env.VITE_API_URL || ''

// Telegram WebApp init data
let telegramInitData = ''

export function setTelegramInitData(initData: string) {
  telegramInitData = initData
}

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - add Telegram init data to all requests
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (telegramInitData) {
    config.headers['X-Telegram-Init-Data'] = telegramInitData
  }
  return config
})

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// ==================== AUTH ====================

export const authAPI = {
  authenticate: async (initData: string): Promise<{
    success: boolean
    user: User
  }> => {
    const { data } = await api.post('/api/auth', { init_data: initData })
    return data
  }
}

// ==================== USER ====================

export const userAPI = {
  getMe: async (): Promise<User> => {
    const { data } = await api.get('/api/user/me')
    return data
  },
  
  getById: async (userId: number): Promise<{ success: boolean; user: User }> => {
    const { data } = await api.get(`/api/user/${userId}`)
    return data
  },
  
  createOrGet: async (userData: { user_id: number; username: string; full_name: string }): Promise<{ success: boolean; user: User }> => {
    const { data } = await api.post('/api/user/create', userData)
    return data
  },
  
  getBalance: async (): Promise<{ balance: number }> => {
    const { data } = await api.get('/api/user/balance')
    return data
  },
  
  getReferralStats: async (): Promise<ReferralStats> => {
    const { data } = await api.get('/api/referral/stats')
    return data
  }
}

// ==================== ORDERS ====================

export const ordersAPI = {
  getMyOrders: async (): Promise<{ orders: Order[] }> => {
    const { data } = await api.get('/api/orders')
    return data
  },
  
  create: async (serviceId: string, link: string, quantity: number): Promise<Order> => {
    const { data } = await api.post('/api/orders/create', {
      service_id: serviceId,
      link,
      quantity
    })
    return data
  }
}

// ==================== PAYMENTS ====================

export const paymentsAPI = {
  getMyPayments: async (): Promise<{ payments: Payment[] }> => {
    const { data } = await api.get('/api/payments')
    return data
  },
  
  getMethods: async (): Promise<{
    id: string
    name: string
    card_number: string
    card_holder: string
    min_amount: number
  }[]> => {
    // Mock payment methods - backend'da qo'shilishi kerak
    return [
      { id: 'uzcard', name: 'UzCard', card_number: '8600 1234 5678 9012', card_holder: 'IDEAL SMM', min_amount: 5000 },
      { id: 'humo', name: 'Humo', card_number: '9860 1234 5678 9012', card_holder: 'IDEAL SMM', min_amount: 5000 },
    ]
  },
  
  create: async (amount: number, method: string): Promise<Payment> => {
    const { data } = await api.post('/api/payments/create', { amount, method })
    return data
  }
}

// ==================== PLATFORMS & SERVICES ====================

export const servicesAPI = {
  getPlatforms: async (): Promise<{ platforms: Platform[] }> => {
    const { data } = await api.get('/api/platforms')
    return data
  },
  
  getCategories: async (platformId: string): Promise<{ categories: ServiceCategory[] }> => {
    const { data } = await api.get(`/api/platforms/${platformId}/categories`)
    return data
  },
  
  getServices: async (platformId: string, categoryId: string): Promise<{ services: Service[] }> => {
    const { data } = await api.get(`/api/services/${platformId}/${categoryId}`)
    return data
  },
  
  getService: async (serviceId: string): Promise<Service> => {
    const { data } = await api.get(`/api/service/${serviceId}`)
    return data
  }
}

// ==================== SMS ====================

export const smsAPI = {
  getPlatforms: async (): Promise<SMSPlatform[]> => {
    // Mock - backend'da qo'shilishi kerak
    return [
      { code: 'tg', name: 'Telegram', emoji: '📱' },
      { code: 'wa', name: 'WhatsApp', emoji: '📲' },
      { code: 'ig', name: 'Instagram', emoji: '📸' },
      { code: 'go', name: 'Google', emoji: '🔍' },
    ]
  },
  
  getCountries: async (): Promise<SMSCountry[]> => {
    return [
      { code: 'ru', name: 'Rossiya', flag: '🇷🇺' },
      { code: 'uz', name: "O'zbekiston", flag: '🇺🇿' },
      { code: 'kz', name: "Qozog'iston", flag: '🇰🇿' },
      { code: 'ua', name: 'Ukraina', flag: '🇺🇦' },
    ]
  },
  
  getPrices: async (_platform: string, _country: string): Promise<any[]> => {
    // Mock prices
    return [
      { provider_name: '5sim', available: 245, price_uzs: 15000 },
      { provider_name: 'SMS-Activate', available: 189, price_uzs: 18000 },
    ]
  },
  
  buy: async (platform: string, country: string): Promise<any> => {
    const { data } = await api.post('/api/sms/buy', { platform, country })
    return data
  }
}

// ==================== SETTINGS ====================

export const settingsAPI = {
  getPublic: async (): Promise<any> => {
    const { data } = await api.get('/api/settings')
    return data
  }
}

export default api
