import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from 'react'
import { authAPI, setTelegramInitData, userAPI } from '../lib/api'
import { useTelegram } from '../hooks/useTelegram'
import type { User } from '../types'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  isDemo: boolean
  error: string | null
  refetchUser: () => Promise<void>
  requestPhoneAuth: () => void
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  isDemo: false,
  error: null,
  refetchUser: async () => {},
  requestPhoneAuth: () => {},
})

export function useAuth() {
  return useContext(AuthContext)
}

interface AuthProviderProps {
  children: ReactNode
}

// LocalStorage dan saqlangan user_id ni olish
const getSavedUserId = (): number | null => {
  try {
    const saved = localStorage.getItem('tg_user_id')
    return saved ? parseInt(saved, 10) : null
  } catch {
    return null
  }
}

// LocalStorage ga user_id ni saqlash
const saveUserId = (userId: number) => {
  try {
    localStorage.setItem('tg_user_id', userId.toString())
  } catch {
    // Ignore storage errors
  }
}

export function AuthProvider({ children }: AuthProviderProps) {
  const { tg, initData, user: tgUser } = useTelegram()
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isDemo, setIsDemo] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Botga yo'naltirish - foydalanuvchi /start bosib qaytadi
  const requestPhoneAuth = useCallback(() => {
    if (tg) {
      // Botga yo'naltirish - u yerda /start bosib, keyin "Open" orqali qaytadi
      tg.openTelegramLink('https://t.me/ideal_smm_uz_bot?start=miniapp')
    }
  }, [tg])

  // User ID bo'yicha foydalanuvchini olish
  const fetchUserById = async (userId: number) => {
    try {
      setIsLoading(true)
      const response = await userAPI.getById(userId)
      if (response.success && response.user) {
        setUser(response.user)
        setIsDemo(false)
        saveUserId(userId)
      }
    } catch (err) {
      console.error('Failed to fetch user:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const authenticate = async () => {
    try {
      setIsLoading(true)
      setError(null)

      // 1. Avval initData orqali autentifikatsiya qilishga harakat
      if (initData && initData.length > 0) {
        console.log('Authenticating with initData')
        setTelegramInitData(initData)

        const response = await authAPI.authenticate(initData)
        
        if (response.success && response.user) {
          setUser(response.user)
          setIsDemo(false)
          saveUserId(response.user.user_id)
          setIsLoading(false)
          return
        }
      }

      // 2. initDataUnsafe dan user ma'lumotlarini olish
      if (tgUser?.id) {
        console.log('Using tgUser ID:', tgUser.id)
        saveUserId(tgUser.id)
        
        try {
          const response = await userAPI.getById(tgUser.id)
          if (response.success && response.user) {
            setUser(response.user)
            setIsDemo(false)
            setIsLoading(false)
            return
          }
        } catch {
          // User not found, continue
        }
      }

      // 3. LocalStorage dan saqlangan user_id ni tekshirish
      const savedUserId = getSavedUserId()
      if (savedUserId) {
        console.log('Using saved user ID:', savedUserId)
        try {
          const response = await userAPI.getById(savedUserId)
          if (response.success && response.user) {
            setUser(response.user)
            setIsDemo(false)
            setIsLoading(false)
            return
          }
        } catch {
          // Saved user not found, continue
        }
      }

      // 4. CloudStorage dan user_id ni o'qish
      if (tg?.CloudStorage) {
        tg.CloudStorage.getItem('user_id', async (err: Error | null, value: string | null) => {
          if (!err && value) {
            const userId = parseInt(value, 10)
            console.log('Using CloudStorage user ID:', userId)
            saveUserId(userId)
            await fetchUserById(userId)
            return
          }
        })
      }

      // 5. Hech biri ishlamasa - Demo mode
      console.log('No authentication method available - using demo mode')
      setIsDemo(true)
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
    } catch (err: any) {
      console.error('Auth error:', err)
      setError(err.message || 'Authentication failed')
      
      // Fallback to demo mode
      setIsDemo(true)
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
      tg.expand() // Mini App ni to'liq ochish
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
        isDemo,
        error,
        refetchUser,
        requestPhoneAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
