import { useNavigate } from 'react-router-dom'
import { useState, useEffect, useCallback } from 'react'
import { motion } from 'framer-motion'
import { Plus, History, TrendingUp, CreditCard, RefreshCw } from 'lucide-react'
import { Card, Button, Loading } from '../components'
import { useTelegram } from '../hooks/useTelegram'
import { useAuth } from '../providers'
import type { Payment } from '../types'

export default function Balance() {
  const navigate = useNavigate()
  const { hapticFeedback } = useTelegram()
  const { user, isLoading: authLoading, refetchUser } = useAuth()
  const [payments, setPayments] = useState<Payment[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)

  // Balansni serverdan yangilash - AuthProvider orqali
  const refreshBalance = useCallback(async () => {
    if (!user?.user_id) return
    
    try {
      setIsRefreshing(true)
      await refetchUser()
    } catch (error) {
      console.error('Error refreshing balance:', error)
    } finally {
      setIsRefreshing(false)
    }
  }, [user?.user_id, refetchUser])

  // Sahifa ochilganda balansni yangilash
  useEffect(() => {
    if (user?.user_id) {
      refreshBalance()
    }
  }, [user?.user_id])

  useEffect(() => {
    const fetchPayments = async () => {
      if (!user?.user_id) return
      
      try {
        setIsLoading(true)
        const response = await fetch(`/api/user/${user.user_id}/payments`)
        const data = await response.json()
        if (Array.isArray(data)) {
          setPayments(data)
        }
      } catch (error) {
        console.error('Error fetching payments:', error)
      } finally {
        setIsLoading(false)
      }
    }
    fetchPayments()
  }, [user?.user_id])

  if (authLoading || isLoading) {
    return <Loading />
  }

  return (
    <div className="space-y-6">
      {/* Balance Card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        <Card className="bg-gradient-to-r from-tg-button to-blue-600 text-white p-6 text-center relative">
          {/* Yangilash tugmasi */}
          <button
            onClick={() => {
              hapticFeedback?.impact?.('light')
              refreshBalance()
            }}
            className={`absolute top-4 right-4 p-2 rounded-full bg-white/20 hover:bg-white/30 transition-all ${isRefreshing ? 'animate-spin' : ''}`}
            disabled={isRefreshing}
          >
            <RefreshCw size={18} />
          </button>
          
          <p className="text-white/80">Balansingiz</p>
          <p className="text-4xl font-bold mt-2">
            {(user?.balance || 0).toLocaleString()}
            <span className="text-xl ml-2">so'm</span>
          </p>
          
          <Button
            variant="primary"
            fullWidth
            className="mt-6 !bg-white !text-blue-600 hover:!bg-gray-100 font-semibold"
            icon={<Plus size={20} />}
            onClick={() => {
              hapticFeedback?.impact?.('medium')
              navigate('/deposit')
            }}
          >
            Hisobni to'ldirish
          </Button>
        </Card>
      </motion.div>

      {/* Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-2 gap-3"
      >
        <Card>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-green-100 flex items-center justify-center">
              <TrendingUp className="text-green-600" size={20} />
            </div>
            <div>
              <p className="text-tg-hint text-sm">Jami kirim</p>
              <p className="text-tg-text font-semibold">
                {payments.reduce((sum, p) => 
                  p.status === 'completed' ? sum + p.amount : sum, 0
                ).toLocaleString()} so'm
              </p>
            </div>
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
              <CreditCard className="text-blue-600" size={20} />
            </div>
            <div>
              <p className="text-tg-hint text-sm">To'lovlar</p>
              <p className="text-tg-text font-semibold">{payments.length} ta</p>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Recent Payments */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className="flex items-center gap-2 mb-4">
          <History size={20} className="text-tg-hint" />
          <h2 className="text-lg font-semibold text-tg-text">To'lovlar tarixi</h2>
        </div>

        {payments.length === 0 ? (
          <Card className="text-center py-8">
            <p className="text-tg-hint">To'lovlar tarixi bo'sh</p>
          </Card>
        ) : (
          <div className="space-y-2">
            {payments.map((payment, index) => {
              const statusColors: Record<string, string> = {
                'pending': '#F59E0B',
                'completed': '#10B981',
                'failed': '#EF4444'
              }
              const statusLabels: Record<string, string> = {
                'pending': 'Kutilmoqda',
                'completed': 'Tasdiqlandi',
                'failed': 'Rad etildi'
              }
              
              return (
                <motion.div
                  key={payment.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 + index * 0.05 }}
                >
                  <Card className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-tg-text">
                        +{payment.amount.toLocaleString()} so'm
                      </p>
                      <p className="text-sm text-tg-hint">{payment.method}</p>
                    </div>
                    <div className="text-right">
                      <span 
                        className="text-sm font-medium"
                        style={{ color: statusColors[payment.status] || '#999' }}
                      >
                        {statusLabels[payment.status] || payment.status}
                      </span>
                      {payment.created_at && (
                        <p className="text-xs text-tg-hint">
                          {new Date(payment.created_at).toLocaleDateString('uz-UZ')}
                        </p>
                      )}
                    </div>
                  </Card>
                </motion.div>
              )
            })}
          </div>
        )}
      </motion.div>
    </div>
  )
}
