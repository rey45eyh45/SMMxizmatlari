import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { authAPI, setTelegramInitData, userAPI } from '../lib/api'
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

  // URL dan user_id olish
  const getUserIdFromUrl = (): number | null => {
    try {
      const params = new URLSearchParams(window.location.search)
      const userId = params.get('user_id')
      if (userId) {
        return parseInt(userId)
      }
      // Telegram startParam ham tekshiramiz
      // @ts-ignore - Telegram WebApp types incomplete
      const startParam = tg?.initDataUnsafe?.start_param
      if (startParam) {
        const match = startParam.match(/user_(\d+)/)
        if (match) {
          return parseInt(match[1])
        }
      }
    } catch {
      return null
    }
    return null
  }

  // LocalStorage dan user_id olish
  const getStoredUserId = (): number | null => {
    try {
      const stored = localStorage.getItem('smm_user_id')
      return stored ? parseInt(stored) : null
    } catch {
      return null
    }
  }

  // User ID ni saqlash
  const storeUserId = (userId: number) => {
    try {
      localStorage.setItem('smm_user_id', userId.toString())
    } catch {
      console.log('Could not save userId to localStorage')
    }
  }

  const authenticate = async () => {
    try {
      setIsLoading(true)
      setError(null)

      // 1. initData mavjud bo'lsa - HMAC bilan validate qilish (Open tugmasi)
      if (initData && initData.length > 0) {
        console.log('Authenticating with initData')
        setTelegramInitData(initData)

        try {
          const response = await authAPI.authenticate(initData)
          if (response.success && response.user) {
            setUser(response.user)
            storeUserId(response.user.user_id)
            setIsLoading(false)
            return
          }
        } catch (err) {
          console.log('initData auth failed, trying other methods')
        }
      }

      // 2. URL dan user_id olish (Mini App ochish tugmasi)
      const urlUserId = getUserIdFromUrl()
      if (urlUserId) {
        console.log('Using URL user_id:', urlUserId)
        try {
          const response = await userAPI.getById(urlUserId)
          if (response.success && response.user) {
            setUser(response.user)
            storeUserId(response.user.user_id)
            setIsLoading(false)
            return
          }
        } catch {
          console.log('URL user_id lookup failed')
        }
      }

      // 3. initDataUnsafe.user mavjud bo'lsa - user_id bo'yicha olish
      if (tgUser?.id) {
        console.log('Using tgUser ID:', tgUser.id)
        
        try {
          const response = await userAPI.getById(tgUser.id)
          if (response.success && response.user) {
            setUser(response.user)
            storeUserId(response.user.user_id)
            setIsLoading(false)
            return
          }
        } catch {
          console.log('User not found by tgUser.id')
        }
      }

      // 4. LocalStorage da saqlangan user_id bo'lsa
      const storedUserId = getStoredUserId()
      if (storedUserId) {
        console.log('Trying stored userId:', storedUserId)
        try {
          const response = await userAPI.getById(storedUserId)
          if (response.success && response.user) {
            setUser(response.user)
            setIsLoading(false)
            return
          }
        } catch {
          console.log('Stored userId lookup failed')
          localStorage.removeItem('smm_user_id')
        }
      }

      // 5. Hech narsa ishlamasa - foydalanuvchi botda ro'yxatdan o'tmagan
      console.log('No user data available')
      setError('Foydalanuvchi topilmadi. Iltimos, avval botda /start bosing.')
      
    } catch (err: any) {
      console.error('Auth error:', err)
      setError(err.message || 'Autentifikatsiya xatosi')
    } finally {
      setIsLoading(false)
    }
  }

  const refetchUser = async () => {
    await authenticate()
  }

  useEffect(() => {
    if (tg) {
      tg.ready()
      tg.expand()
      authenticate()
    } else {
      // Browser test
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
