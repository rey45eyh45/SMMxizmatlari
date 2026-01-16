import { NavLink, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Home, Grid3X3, ShoppingBag, Wallet, User } from 'lucide-react'
import { useTelegram } from '../hooks/useTelegram'

const navItems = [
  { path: '/', icon: Home, label: 'Bosh sahifa' },
  { path: '/services', icon: Grid3X3, label: 'Xizmatlar' },
  { path: '/orders', icon: ShoppingBag, label: 'Buyurtmalar' },
  { path: '/balance', icon: Wallet, label: 'Hisob' },
]

export default function BottomNav() {
  const location = useLocation()
  const { hapticFeedback } = useTelegram()

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-tg-bg border-t border-tg-secondary-bg safe-bottom z-50">
      <div className="flex items-center justify-around h-16 max-w-lg mx-auto">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path
          const Icon = item.icon
          
          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => hapticFeedback.selection()}
              className="flex flex-col items-center justify-center w-full h-full relative"
            >
              <motion.div
                whileTap={{ scale: 0.9 }}
                className={`flex flex-col items-center ${
                  isActive ? 'text-tg-button' : 'text-tg-hint'
                }`}
              >
                <Icon size={22} strokeWidth={isActive ? 2.5 : 2} />
                <span className="text-[10px] mt-1 font-medium">{item.label}</span>
              </motion.div>
              
              {isActive && (
                <motion.div
                  layoutId="nav-indicator"
                  className="absolute -top-[1px] left-1/2 -translate-x-1/2 w-8 h-0.5 bg-tg-button rounded-full"
                  initial={false}
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                />
              )}
            </NavLink>
          )
        })}
      </div>
    </nav>
  )
}
