import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '../store'
import type { 
  AuthResponse, 
  User, 
  Platform, 
  Service, 
  ServiceCategory,
  Order, 
  Payment, 
  PaymentMethod,
  ReferralStats,
  SMSPlatform,
  SMSCountry,
  SMSPrice,
  SMSOrder,
  PremiumPlan,
  PremiumStatus,
  Settings
} from '../types'

const API_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - add auth token
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
    }
    return Promise.reject(error)
  }
)

// ==================== AUTH ====================

export const authAPI = {
  authenticate: async (initData: string): Promise<AuthResponse> => {
    const { data } = await api.post<AuthResponse>('/auth/telegram', { init_data: initData })
    return data
  },
  
  verify: async (token: string): Promise<{ valid: boolean; user_id: number }> => {
    const { data } = await api.post('/auth/verify', { token })
    return data
  }
}

// ==================== USER ====================

export const userAPI = {
  getMe: async (): Promise<User> => {
    const { data } = await api.get<User>('/user/me')
    return data
  },
  
  getBalance: async (): Promise<{ balance: number; formatted: string }> => {
    const { data } = await api.get('/user/balance')
    return data
  },
  
  getReferralStats: async (): Promise<ReferralStats> => {
    const { data } = await api.get<ReferralStats>('/user/referral')
    return data
  },
  
  getOrders: async (limit = 20): Promise<Order[]> => {
    const { data } = await api.get<Order[]>('/user/orders', { params: { limit } })
    return data
  },
  
  getPayments: async (limit = 20): Promise<Payment[]> => {
    const { data } = await api.get<Payment[]>('/user/payments', { params: { limit } })
    return data
  },
  
  getPremiumStatus: async (): Promise<PremiumStatus> => {
    const { data } = await api.get<PremiumStatus>('/user/premium')
    return data
  }
}

// ==================== SERVICES ====================

export const servicesAPI = {
  getPlatforms: async (): Promise<Platform[]> => {
    const { data } = await api.get<Platform[]>('/services/platforms')
    return data
  },
  
  getPlatformServices: async (platformId: string): Promise<{
    platform: Platform
    categories: ServiceCategory[]
    services: Service[]
  }> => {
    const { data } = await api.get(`/services/platform/${platformId}`)
    return data
  },
  
  getCategoryServices: async (platformId: string, categoryId: string): Promise<Service[]> => {
    const { data } = await api.get<Service[]>(`/services/platform/${platformId}/category/${categoryId}`)
    return data
  },
  
  getService: async (serviceId: string): Promise<Service> => {
    const { data } = await api.get<Service>(`/services/service/${serviceId}`)
    return data
  },
  
  getPremiumPlans: async (): Promise<PremiumPlan[]> => {
    const { data } = await api.get<PremiumPlan[]>('/services/premium/plans')
    return data
  }
}

// ==================== ORDERS ====================

export const ordersAPI = {
  create: async (serviceId: string, link: string, quantity: number): Promise<Order> => {
    const { data } = await api.post<Order>('/orders/create', {
      service_id: serviceId,
      link,
      quantity
    })
    return data
  },
  
  getMyOrders: async (limit = 20): Promise<Order[]> => {
    const { data } = await api.get<Order[]>('/orders/my', { params: { limit } })
    return data
  },
  
  getOrder: async (orderId: number): Promise<Order> => {
    const { data } = await api.get<Order>(`/orders/${orderId}`)
    return data
  },
  
  getOrderStatus: async (orderId: number): Promise<{
    order_id: number
    status: string
    charge?: number
    start_count?: number
    remains?: number
  }> => {
    const { data } = await api.get(`/orders/${orderId}/status`)
    return data
  }
}

// ==================== PAYMENTS ====================

export const paymentsAPI = {
  getMethods: async (): Promise<PaymentMethod[]> => {
    const { data } = await api.get<PaymentMethod[]>('/payments/methods')
    return data
  },
  
  create: async (amount: number, method: string): Promise<Payment> => {
    const { data } = await api.post<Payment>('/payments/create', { amount, method })
    return data
  },
  
  getMyPayments: async (limit = 20): Promise<Payment[]> => {
    const { data } = await api.get<Payment[]>('/payments/my', { params: { limit } })
    return data
  },
  
  getPayment: async (paymentId: number): Promise<Payment> => {
    const { data } = await api.get<Payment>(`/payments/${paymentId}`)
    return data
  }
}

// ==================== SMS ====================

export const smsAPI = {
  getPlatforms: async (): Promise<SMSPlatform[]> => {
    const { data } = await api.get<SMSPlatform[]>('/sms/platforms')
    return data
  },
  
  getCountries: async (): Promise<SMSCountry[]> => {
    const { data } = await api.get<SMSCountry[]>('/sms/countries')
    return data
  },
  
  getPrices: async (platform: string, country: string): Promise<SMSPrice[]> => {
    const { data } = await api.get<SMSPrice[]>(`/sms/prices/${platform}/${country}`)
    return data
  },
  
  buy: async (platform: string, country: string): Promise<SMSOrder> => {
    const { data } = await api.post<SMSOrder>('/sms/buy', { platform, country })
    return data
  },
  
  checkCode: async (provider: string, orderId: string): Promise<{
    order_id: string
    status: string
    code?: string
  }> => {
    const { data } = await api.get(`/sms/check/${provider}/${orderId}`)
    return data
  },
  
  cancel: async (provider: string, orderId: string): Promise<{ cancelled: boolean }> => {
    const { data } = await api.post(`/sms/cancel/${provider}/${orderId}`)
    return data
  }
}

// ==================== SETTINGS ====================

export const settingsAPI = {
  getPublic: async (): Promise<Settings> => {
    const { data } = await api.get<Settings>('/settings')
    return data
  }
}

export default api
