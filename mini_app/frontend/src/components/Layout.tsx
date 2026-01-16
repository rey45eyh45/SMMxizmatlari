import { ReactNode, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import BottomNav from './BottomNav'
import { useTelegram } from '../hooks/useTelegram'
import { useAuthStore } from '../store'
import { authAPI, settingsAPI } from '../lib/api'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const { tg, initData, backButton, isInTelegram } = useTelegram()
  const { isAuthenticated, setAuth } = useAuthStore()

  // Authenticate on mount
  useEffect(() => {
    async function authenticate() {
      if (initData && !isAuthenticated) {
        try {
          const response = await authAPI.authenticate(initData)
          setAuth(response.access_token, {
            user_id: response.user.user_id,
            username: response.user.username,
            full_name: response.user.full_name,
            balance: response.user.balance,
            referral_count: 0,
            referral_earnings: 0,
            is_banned: false
          })
        } catch (error) {
          console.error('Auth error:', error)
        }
      }
    }
    authenticate()
  }, [initData, isAuthenticated, setAuth])

  // Handle back button
  useEffect(() => {
    if (location.pathname !== '/') {
      backButton.show(() => {
        navigate(-1)
      })
    } else {
      backButton.hide()
    }

    return () => {
      backButton.hide()
    }
  }, [location.pathname, backButton, navigate])

  return (
    <div className="min-h-screen bg-tg-bg pb-20">
      <AnimatePresence mode="wait">
        <motion.main
          key={location.pathname}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
          className="px-4 py-4"
        >
          {children}
        </motion.main>
      </AnimatePresence>
      <BottomNav />
    </div>
  )
}
