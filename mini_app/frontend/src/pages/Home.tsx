import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Wallet, 
  Users, 
  ShoppingBag, 
  Crown, 
  ChevronRight,
  Sparkles,
  User
} from 'lucide-react'
import { useTelegram } from '../hooks/useTelegram'
import { useAuth } from '../providers'
import { PlatformCard, Card, Loading } from '../components'
import { mockPlatforms } from '../lib/mockData'

export default function Home() {
  const navigate = useNavigate()
  const { hapticFeedback, user: tgUser } = useTelegram()
  const { user, isLoading, error } = useAuth()

  if (isLoading) {
    return <Loading />
  }

  // Agar xatolik bo'lsa
  if (error || !user) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] p-4">
        <div className="w-20 h-20 rounded-full bg-red-500/10 flex items-center justify-center mb-4">
          <User size={40} className="text-red-500" />
        </div>
        <h2 className="text-xl font-bold text-tg-text mb-2">Xatolik</h2>
        <p className="text-tg-hint text-center">
          {error || "Foydalanuvchi aniqlanmadi. Iltimos, Mini App ni qayta oching."}
        </p>
      </div>
    )
  }

  const displayName = user.full_name || tgUser?.first_name || 'Foydalanuvchi'
  const balance = user.balance || 0
  const photoUrl = tgUser?.photo_url

  const handleNavigation = (path: string) => {
    hapticFeedback?.selection?.()
    navigate(path)
  }

  return (
    <div className="space-y-6">
      {/* Header with Profile */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-4 py-2"
      >
        {/* Profile Photo */}
        <div className="w-14 h-14 rounded-full bg-gradient-to-r from-tg-button to-blue-500 flex items-center justify-center overflow-hidden shrink-0">
          {photoUrl ? (
            <img 
              src={photoUrl} 
              alt={displayName}
              className="w-full h-full object-cover"
            />
          ) : (
            <User size={28} className="text-white" />
          )}
        </div>
        
        {/* Greeting */}
        <div className="flex-1">
          <h1 className="text-xl font-bold text-tg-text">
            Salom, {displayName}! 👋
          </h1>
          <p className="text-tg-hint text-sm">
            SMM xizmatlari sizga yaqin
          </p>
        </div>
      </motion.div>

      {/* Balance Card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
      >
        <Card 
          onClick={() => handleNavigation('/balance')}
          className="bg-gradient-to-r from-tg-button to-blue-600 text-white p-5"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/80 text-sm">Balansingiz</p>
              <p className="text-3xl font-bold mt-1">
                {balance.toLocaleString()} <span className="text-lg">so'm</span>
              </p>
            </div>
            <div className="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center">
              <Wallet size={28} />
            </div>
          </div>
          <div className="flex items-center gap-2 mt-4 text-white/80 text-sm">
            <span>To'ldirish uchun bosing</span>
            <ChevronRight size={16} />
          </div>
        </Card>
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-4 gap-3"
      >
        {[
          { icon: ShoppingBag, label: 'Buyurtmalar', path: '/orders', color: '#0088cc' },
          { icon: Users, label: 'Referal', path: '/referral', color: '#10B981' },
          { icon: Crown, label: 'Premium', path: '/premium', color: '#F59E0B' },
          { icon: Sparkles, label: 'SMS', path: '/sms', color: '#8B5CF6' },
        ].map((item, index) => (
          <motion.button
            key={item.path}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleNavigation(item.path)}
            className="flex flex-col items-center gap-2 p-3 rounded-2xl bg-tg-secondary-bg"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 + index * 0.05 }}
          >
            <div 
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ backgroundColor: `${item.color}20` }}
            >
              <item.icon size={20} style={{ color: item.color }} />
            </div>
            <span className="text-xs font-medium text-tg-text">{item.label}</span>
          </motion.button>
        ))}
      </motion.div>

      {/* Platforms */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-tg-text">Platformalar</h2>
          <button 
            onClick={() => handleNavigation('/services')}
            className="text-sm text-tg-link font-medium"
          >
            Barchasi
          </button>
        </div>
        
        <div className="space-y-3">
          {mockPlatforms.map((platform, index) => (
            <motion.div
              key={platform.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + index * 0.1 }}
            >
              <PlatformCard
                emoji={platform.emoji}
                name={platform.name}
                color={platform.color}
                onClick={() => handleNavigation(`/platform/${platform.id}`)}
              />
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Virtual Numbers Banner */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <Card 
          onClick={() => handleNavigation('/sms')}
          className="bg-gradient-to-r from-purple-500 to-pink-500 text-white"
        >
          <div className="flex items-center gap-4">
            <div className="text-4xl">📱</div>
            <div className="flex-1">
              <h3 className="font-semibold text-lg">Virtual Raqamlar</h3>
              <p className="text-white/80 text-sm mt-0.5">
                SMS qabul qilish - arzon narxlarda!
              </p>
            </div>
            <ChevronRight size={20} />
          </div>
        </Card>
      </motion.div>
    </div>
  )
}
