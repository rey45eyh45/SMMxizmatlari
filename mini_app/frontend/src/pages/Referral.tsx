import { motion } from 'framer-motion'
import { Copy, Users, Gift, Share2 } from 'lucide-react'
import { Card, Loading } from '../components'
import { useTelegram } from '../hooks/useTelegram'
import { useAuth } from '../providers'

export default function Referral() {
  const { hapticFeedback, showAlert, tg } = useTelegram()
  const { user, isLoading } = useAuth()
  
  const referralLink = user ? `https://t.me/SmmXizmatlari_bot?start=ref${user.user_id}` : ''
  const referralCount = user?.referral_count || 0
  const referralEarnings = user?.referral_earnings || 0

  if (isLoading) {
    return <Loading />
  }

  const copyLink = () => {
    if (referralLink) {
      navigator.clipboard.writeText(referralLink)
      hapticFeedback?.notification?.('success')
      showAlert?.('📋 Havola nusxalandi!')
    }
  }

  const shareLink = () => {
    if (referralLink && tg) {
      tg.openTelegramLink(`https://t.me/share/url?url=${encodeURIComponent(referralLink)}&text=${encodeURIComponent('📱 Eng arzon SMM xizmatlari! Ro\'yxatdan o\'ting va bonus oling!')}`)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-tg-text">Referal dasturi</h1>
        <p className="text-tg-hint">Do'stlaringizni taklif qiling va pul ishlang!</p>
      </div>

      {/* Stats Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-2 gap-3"
      >
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
              <Users size={20} />
            </div>
            <div>
              <p className="text-white/80 text-sm">Referallar</p>
              <p className="text-2xl font-bold">{referralCount}</p>
            </div>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-green-500 to-emerald-600 text-white">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
              <Gift size={20} />
            </div>
            <div>
              <p className="text-white/80 text-sm">Daromad</p>
              <p className="text-2xl font-bold">
                {referralEarnings.toLocaleString()}
              </p>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Referral Link */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card>
          <p className="text-tg-text font-medium mb-3">Sizning havolangiz:</p>
          
          <div className="bg-tg-bg rounded-xl p-3 flex items-center gap-2">
            <p className="flex-1 text-sm text-tg-text truncate font-mono">
              {referralLink}
            </p>
            <button
              onClick={copyLink}
              className="p-2 rounded-lg bg-tg-secondary-bg shrink-0"
            >
              <Copy size={18} className="text-tg-link" />
            </button>
          </div>

          <button
            onClick={shareLink}
            className="w-full mt-3 py-3 rounded-xl bg-tg-button text-tg-button-text font-medium flex items-center justify-center gap-2"
          >
            <Share2 size={18} />
            Ulashish
          </button>
        </Card>
      </motion.div>

      {/* How it works */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h2 className="text-lg font-semibold text-tg-text mb-3">Qanday ishlaydi?</h2>
        
        <div className="space-y-3">
          {[
            { step: 1, text: "Havolangizni do'stlaringizga yuboring" },
            { step: 2, text: "Do'stingiz ro'yxatdan o'tadi" },
            { step: 3, text: "Siz va do'stingiz bonus olasiz! 🎉" }
          ].map((item, index) => (
            <motion.div
              key={item.step}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + index * 0.1 }}
            >
              <Card className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-tg-button text-tg-button-text font-bold flex items-center justify-center">
                  {item.step}
                </div>
                <p className="text-tg-text">{item.text}</p>
              </Card>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Bonus info */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card className="bg-gradient-to-r from-purple-500 to-pink-500 text-white">
          <div className="text-center">
            <p className="text-white/80">Har bir referal uchun</p>
            <p className="text-3xl font-bold mt-1">1,000 so'm</p>
            <p className="text-white/80 text-sm mt-1">bonus oling!</p>
          </div>
        </Card>
      </motion.div>
    </div>
  )
}
