import { motion } from 'framer-motion'
import { Crown, Star, Sparkles } from 'lucide-react'
import { Card } from '../components'
import { useTelegram } from '../hooks/useTelegram'

// Mock premium plans
const mockPlans = [
  { months: 1, price: 100000, original_price: 120000, discount_percent: 17, popular: false, best_value: false },
  { months: 3, price: 270000, original_price: 360000, discount_percent: 25, popular: true, best_value: false },
  { months: 6, price: 480000, original_price: 720000, discount_percent: 33, popular: false, best_value: true },
  { months: 12, price: 850000, original_price: 1440000, discount_percent: 41, popular: false, best_value: false },
]

// Mock premium status
const mockPremiumStatus = {
  is_premium: false,
  days_left: 0
}

export default function Premium() {
  const { hapticFeedback, showAlert, tg } = useTelegram()

  const plans = mockPlans
  const status = mockPremiumStatus

  const handleSelectPlan = (months: number, price: number) => {
    hapticFeedback.impact('medium')
    
    // Open bot chat with premium command
    if (tg) {
      tg.openTelegramLink(`https://t.me/idealsmm_bot?start=premium_${months}`)
    } else {
      showAlert(`Premium ${months} oylik - ${price.toLocaleString()} so'm. Botda davom eting.`)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center py-4">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="w-20 h-20 mx-auto rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 flex items-center justify-center mb-4"
        >
          <Crown size={40} className="text-white" />
        </motion.div>
        <h1 className="text-2xl font-bold text-tg-text">Telegram Premium</h1>
        <p className="text-tg-hint mt-1">Arzon narxlarda obuna bo'ling!</p>
      </div>

      {/* Current Status */}
      {status.is_premium && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white">
            <div className="flex items-center gap-3">
              <Sparkles size={24} />
              <div>
                <p className="font-semibold">Premium faol!</p>
                <p className="text-white/80 text-sm">
                  {status.days_left} kun qoldi
                </p>
              </div>
            </div>
          </Card>
        </motion.div>
      )}

      {/* Features */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card>
          <h2 className="font-semibold text-tg-text mb-4">Premium afzalliklari:</h2>
          <div className="space-y-3">
            {[
              "✅ Premium emoji va stikerlar",
              "✅ 4GB gacha fayl yuklash",
              "✅ Tezlashtirilgan yuklab olish",
              "✅ Reklama yo'q",
              "✅ Eksklyuziv reaksiyalar",
              "✅ Premium badge"
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 + index * 0.05 }}
                className="flex items-center gap-2"
              >
                <span className="text-tg-text">{feature}</span>
              </motion.div>
            ))}
          </div>
        </Card>
      </motion.div>

      {/* Plans */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="space-y-3"
      >
        <h2 className="font-semibold text-tg-text">Tariflar:</h2>
        
        {plans.map((plan, index) => (
          <motion.div
            key={plan.months}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 + index * 0.1 }}
          >
            <Card
              onClick={() => handleSelectPlan(plan.months, plan.price)}
              className={`cursor-pointer transition-all ${
                plan.popular || plan.best_value 
                  ? 'ring-2 ring-yellow-400' 
                  : ''
              }`}
            >
              {(plan.popular || plan.best_value) && (
                <div className="flex items-center gap-1 text-yellow-600 text-xs font-bold mb-2">
                  <Star size={12} fill="currentColor" />
                  {plan.best_value ? 'ENG FOYDALI' : 'MASHHUR'}
                </div>
              )}
              
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold text-tg-text text-lg">
                    {plan.months} oylik
                  </p>
                  {plan.original_price && plan.discount_percent && plan.discount_percent > 0 && (
                    <p className="text-sm text-tg-hint line-through">
                      {plan.original_price.toLocaleString()} so'm
                    </p>
                  )}
                </div>
                
                <div className="text-right">
                  <p className="text-xl font-bold text-tg-button">
                    {plan.price.toLocaleString()} so'm
                  </p>
                  {plan.discount_percent && plan.discount_percent > 0 && (
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                      -{plan.discount_percent}%
                    </span>
                  )}
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </motion.div>

      {/* Note */}
      <p className="text-center text-tg-hint text-sm">
        Obuna 24 soat ichida faollashtiriladi
      </p>
    </div>
  )
}
