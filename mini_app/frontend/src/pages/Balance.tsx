import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Plus, History, TrendingUp, CreditCard } from 'lucide-react'
import { Card, Button, Loading, ErrorState } from '../components'
import { userAPI, paymentsAPI } from '../lib/api'
import { useTelegram } from '../hooks/useTelegram'
import { useAuthStore } from '../store'

export default function Balance() {
  const navigate = useNavigate()
  const { hapticFeedback } = useTelegram()
  const { user } = useAuthStore()

  const { data: payments, isLoading, error, refetch } = useQuery({
    queryKey: ['my-payments'],
    queryFn: () => paymentsAPI.getMyPayments(10)
  })

  const balance = user?.balance || 0

  if (error) return <ErrorState onRetry={() => refetch()} />

  return (
    <div className="space-y-6">
      {/* Balance Card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        <Card className="bg-gradient-to-r from-tg-button to-blue-600 text-white p-6 text-center">
          <p className="text-white/80">Balansingiz</p>
          <p className="text-4xl font-bold mt-2">
            {balance.toLocaleString()}
            <span className="text-xl ml-2">so'm</span>
          </p>
          
          <Button
            variant="secondary"
            fullWidth
            className="mt-6 bg-white text-tg-button hover:bg-white/90"
            icon={<Plus size={20} />}
            onClick={() => {
              hapticFeedback.impact('medium')
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
                {payments?.reduce((sum, p) => 
                  p.status === 'tasdiqlandi' ? sum + p.amount : sum, 0
                ).toLocaleString() || 0} so'm
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
              <p className="text-tg-text font-semibold">{payments?.length || 0} ta</p>
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

        {isLoading ? (
          <Loading />
        ) : payments?.length === 0 ? (
          <Card className="text-center py-8">
            <p className="text-tg-hint">To'lovlar tarixi bo'sh</p>
          </Card>
        ) : (
          <div className="space-y-2">
            {payments?.map((payment, index) => {
              const statusColors: Record<string, string> = {
                'kutilmoqda': '#F59E0B',
                'tasdiqlandi': '#10B981',
                'rad etildi': '#EF4444'
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
                        {payment.status}
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
