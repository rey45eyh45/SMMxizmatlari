import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { authAPI, setTelegramInitData } from '../lib/api'
import { useTelegram } from '../hooks/useTelegram'
import type { User } from '../types'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  error: string | null
  refetchUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  error: null,
  refetchUser: async () => {},
})

export function useAuth() {
  return useContext(AuthContext)
}

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const { tg, initData, user: tgUser } = useTelegram()
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const authenticate = async () => {
    try {
      setIsLoading(true)
      setError(null)

      // Telegram WebApp ichida ishlayotganini tekshirish
      if (!initData) {
        console.log('No Telegram init data - using demo mode')
        // Demo mode - mock user
        setUser({
          user_id: tgUser?.id || 123456789,
          username: tgUser?.username || 'demo_user',
          full_name: tgUser?.first_name || 'Demo User',
          balance: 50000,
          referral_count: 5,
          referral_earnings: 10000,
          is_banned: false,
          created_at: new Date().toISOString()
        })
        setIsLoading(false)
        return
      }

      // Set init data for all future API requests
      setTelegramInitData(initData)

      // Authenticate with backend
      const response = await authAPI.authenticate(initData)
      
      if (response.success && response.user) {
        setUser(response.user)
      } else {
        throw new Error('Authentication failed')
      }
    } catch (err: any) {
      console.error('Auth error:', err)
      setError(err.message || 'Authentication failed')
      
      // Fallback to demo mode on error
      setUser({
        user_id: tgUser?.id || 123456789,
        username: tgUser?.username || 'demo_user',
        full_name: tgUser?.first_name || 'Demo User',
        balance: 50000,
        referral_count: 5,
        referral_earnings: 10000,
        is_banned: false,
        created_at: new Date().toISOString()
      })
    } finally {
      setIsLoading(false)
    }
  }

  const refetchUser = async () => {
    await authenticate()
  }

  useEffect(() => {
    // Telegram WebApp tayyor bo'lganda autentifikatsiya qilish
    if (tg) {
      tg.ready()
      authenticate()
    } else {
      // Browser'da test qilish uchun
      authenticate()
    }
  }, [tg])

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        error,
        refetchUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
