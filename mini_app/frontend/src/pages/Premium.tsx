import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Crown, Star, Sparkles } from 'lucide-react'
import { Card, Loading } from '../components'
import { useTelegram } from '../hooks/useTelegram'
import { useAuth } from '../providers'

interface PremiumPlan {
  months: number
  price: number
  original_price: number
  discount_percent: number
  popular: boolean
  best_value: boolean
}

interface PremiumStatus {
  is_premium: boolean
  days_left: number
  expires_at?: string
}

export default function Premium() {
  const { hapticFeedback, showAlert, tg } = useTelegram()
  const { user } = useAuth()
  const [plans, setPlans] = useState<PremiumPlan[]>([])
  const [status, setStatus] = useState<PremiumStatus>({ is_premium: false, days_left: 0 })
  const [isLoading, setIsLoading] = useState(true)
  const [requesting, setRequesting] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true)
        
        // Fetch plans
        const plansRes = await fetch('/api/premium/plans')
        const plansData = await plansRes.json()
        if (plansData.success) {
          setPlans(plansData.plans)
        }
        
        // Fetch status
        if (user?.user_id) {
          const statusRes = await fetch(`/api/premium/${user.user_id}`)
          const statusData = await statusRes.json()
          if (statusData.success) {
            setStatus(statusData)
          }
        }
      } catch (error) {
        console.error('Error fetching premium data:', error)
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchData()
  }, [user?.user_id])

  const handleSelectPlan = async (months: number, price: number) => {
    hapticFeedback?.impact?.('medium')
    
    if (!user?.user_id) {
      showAlert?.('Xatolik: Foydalanuvchi aniqlanmadi')
      return
    }
    
    // Check balance
    if ((user.balance || 0) < price) {
      showAlert?.(`Balans yetarli emas! Kerakli: ${price.toLocaleString()} so'm`)
      return
    }
    
    setRequesting(true)
    
    try {
      const response = await fetch('/api/premium/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.user_id,
          months,
          price
        })
      })
      
      const data = await response.json()
      
      if (data.success) {
        hapticFeedback?.notification?.('success')
        showAlert?.(`✅ So'rov yuborildi!\n\n${months} oylik Premium - ${price.toLocaleString()} so'm\n\nAdmin 24 soat ichida faollashtiradi.`)
      } else {
        showAlert?.('Xatolik yuz berdi')
      }
    } catch (error) {
      console.error('Error requesting premium:', error)
      showAlert?.('Xatolik yuz berdi')
    } finally {
      setRequesting(false)
    }
  }

  if (isLoading) {
    return <Loading />
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
              onClick={() => !requesting && handleSelectPlan(plan.months, plan.price)}
              className={`cursor-pointer transition-all ${
                plan.popular || plan.best_value 
                  ? 'ring-2 ring-yellow-400' 
                  : ''
              } ${requesting ? 'opacity-50' : ''}`}
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
                  {plan.original_price && plan.discount_percent > 0 && (
                    <p className="text-sm text-tg-hint line-through">
                      {plan.original_price.toLocaleString()} so'm
                    </p>
                  )}
                </div>
                
                <div className="text-right">
                  <p className="text-xl font-bold text-tg-button">
                    {plan.price.toLocaleString()} so'm
                  </p>
                  {plan.discount_percent > 0 && (
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

      {/* Balance info */}
      <Card className="bg-tg-secondary-bg">
        <p className="text-tg-hint text-sm text-center">
          💰 Balansingiz: <span className="font-semibold text-tg-text">{(user?.balance || 0).toLocaleString()} so'm</span>
        </p>
      </Card>

      {/* Note */}
      <p className="text-center text-tg-hint text-sm">
        ⏱ Obuna 24 soat ichida admin tomonidan faollashtiriladi
      </p>
    </div>
  )
}
