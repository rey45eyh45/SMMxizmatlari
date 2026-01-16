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

  // LocalStorage dan telefon raqamni olish
  const getStoredPhone = (): string | null => {
    try {
      return localStorage.getItem('smm_user_phone')
    } catch {
      return null
    }
  }

  // Telefon raqamni saqlash
  const storePhone = (phone: string) => {
    try {
      localStorage.setItem('smm_user_phone', phone)
    } catch {
      console.log('Could not save phone to localStorage')
    }
  }

  // Telegram WebApp orqali kontakt so'rash
  const requestContact = async (): Promise<string | null> => {
    return new Promise((resolve) => {
      if (!tg || typeof tg.requestContact !== 'function') {
        console.log('requestContact not available')
        resolve(null)
        return
      }

      try {
        // @ts-ignore - Telegram WebApp types incomplete
        tg.requestContact((ok: boolean, response?: any) => {
          if (ok && response?.responseUnsafe?.contact?.phone_number) {
            const phone = response.responseUnsafe.contact.phone_number
            console.log('Got contact phone:', phone)
            storePhone(phone)
            resolve(phone)
          } else {
            console.log('Contact request failed or cancelled')
            resolve(null)
          }
        })
      } catch (err) {
        console.error('requestContact error:', err)
        resolve(null)
      }
    })
  }

  const authenticate = async () => {
    try {
      setIsLoading(true)
      setError(null)

      // 1. initData mavjud bo'lsa - HMAC bilan validate qilish (eng ishonchli)
      if (initData && initData.length > 0) {
        console.log('Authenticating with initData')
        setTelegramInitData(initData)

        try {
          const response = await authAPI.authenticate(initData)
          if (response.success && response.user) {
            setUser(response.user)
            setIsLoading(false)
            return
          }
        } catch (err) {
          console.log('initData auth failed, trying other methods')
        }
      }

      // 2. initDataUnsafe.user mavjud bo'lsa - user_id bo'yicha olish/yaratish
      if (tgUser?.id) {
        console.log('Using tgUser ID:', tgUser.id)
        
        try {
          // Avval mavjud userni olishga harakat
          const response = await userAPI.getById(tgUser.id)
          if (response.success && response.user) {
            setUser(response.user)
            setIsLoading(false)
            return
          }
        } catch {
          // User topilmadi - yangi yaratamiz
          console.log('User not found, creating new user')
        }

        // Yangi user yaratish
        try {
          const newUser = await userAPI.createOrGet({
            user_id: tgUser.id,
            username: tgUser.username || '',
            full_name: `${tgUser.first_name || ''} ${tgUser.last_name || ''}`.trim() || 'Foydalanuvchi'
          })
          if (newUser.success && newUser.user) {
            setUser(newUser.user)
            setIsLoading(false)
            return
          }
        } catch (err) {
          console.error('Failed to create user:', err)
        }
      }

      // 3. LocalStorage da saqlangan telefon raqam bo'lsa - u orqali topish
      const storedPhone = getStoredPhone()
      if (storedPhone) {
        console.log('Trying stored phone:', storedPhone)
        try {
          const response = await userAPI.getByPhone(storedPhone)
          if (response.success && response.user) {
            setUser(response.user)
            setIsLoading(false)
            return
          }
        } catch {
          console.log('Stored phone lookup failed')
        }
      }

      // 4. Telegram WebApp kontakt so'rash (faqat Mini App ichida ishlaydi)
      console.log('Requesting contact from Telegram...')
      const contactPhone = await requestContact()
      if (contactPhone) {
        try {
          const response = await userAPI.getByPhone(contactPhone)
          if (response.success && response.user) {
            setUser(response.user)
            setIsLoading(false)
            return
          }
        } catch {
          console.log('Contact phone lookup failed')
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
