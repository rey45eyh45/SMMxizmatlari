import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, Settings } from '../types'

interface AuthState {
  token: string | null
  user: User | null
  isAuthenticated: boolean
  setAuth: (token: string, user: User) => void
  logout: () => void
  updateBalance: (balance: number) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      setAuth: (token, user) => set({ token, user, isAuthenticated: true }),
      logout: () => set({ token: null, user: null, isAuthenticated: false }),
      updateBalance: (balance) => set((state) => ({
        user: state.user ? { ...state.user, balance } : null
      }))
    }),
    {
      name: 'auth-storage'
    }
  )
)

interface AppState {
  settings: Settings | null
  isLoading: boolean
  setSettings: (settings: Settings) => void
  setLoading: (loading: boolean) => void
}

export const useAppStore = create<AppState>((set) => ({
  settings: null,
  isLoading: false,
  setSettings: (settings) => set({ settings }),
  setLoading: (isLoading) => set({ isLoading })
}))

interface CartItem {
  serviceId: string
  serviceName: string
  link: string
  quantity: number
  price: number
}

interface CartState {
  items: CartItem[]
  addItem: (item: CartItem) => void
  removeItem: (serviceId: string) => void
  clearCart: () => void
  getTotal: () => number
}

export const useCartStore = create<CartState>((set, get) => ({
  items: [],
  addItem: (item) => set((state) => ({
    items: [...state.items.filter(i => i.serviceId !== item.serviceId), item]
  })),
  removeItem: (serviceId) => set((state) => ({
    items: state.items.filter(i => i.serviceId !== serviceId)
  })),
  clearCart: () => set({ items: [] }),
  getTotal: () => get().items.reduce((sum, item) => sum + item.price, 0)
}))
