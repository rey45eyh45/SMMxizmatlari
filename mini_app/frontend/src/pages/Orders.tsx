import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Clock, CheckCircle, XCircle, Loader, RefreshCw } from 'lucide-react'
import { Card, EmptyState, Button, Loading } from '../components'
import { useAuth } from '../providers'
import type { Order } from '../types'

const statusConfig: Record<string, { icon: typeof Clock; color: string; label: string }> = {
  pending: { icon: Clock, color: '#F59E0B', label: 'Kutilmoqda' },
  processing: { icon: Loader, color: '#3B82F6', label: 'Bajarilmoqda' },
  'in progress': { icon: Loader, color: '#3B82F6', label: 'Bajarilmoqda' },
  completed: { icon: CheckCircle, color: '#10B981', label: 'Tugallandi' },
  partial: { icon: CheckCircle, color: '#F59E0B', label: 'Qisman' },
  canceled: { icon: XCircle, color: '#EF4444', label: 'Bekor qilindi' },
  refunded: { icon: XCircle, color: '#8B5CF6', label: 'Qaytarildi' }
}

export default function Orders() {
  const { user } = useAuth()
  const [orders, setOrders] = useState<Order[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const fetchOrders = async () => {
    if (!user?.user_id) return
    
    try {
      setIsLoading(true)
      const response = await fetch(`/api/orders/${user.user_id}`)
      const data = await response.json()
      if (data.success && data.orders) {
        setOrders(data.orders)
      }
    } catch (error) {
      console.error('Error fetching orders:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchOrders()
  }, [user?.user_id])

  if (isLoading) {
    return <Loading />
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-tg-text">Buyurtmalarim</h1>
          <p className="text-tg-hint">{orders.length} ta buyurtma</p>
        </div>
        <Button variant="ghost" onClick={fetchOrders} icon={<RefreshCw size={18} />}>
          Yangilash
        </Button>
      </div>

      {orders.length === 0 ? (
        <EmptyState
          title="Buyurtmalar yo'q"
          description="Birinchi buyurtmangizni bering!"
        />
      ) : (
        <div className="space-y-3">
          {orders.map((order, index) => {
            const status = statusConfig[order.status.toLowerCase()] || statusConfig.pending
            const StatusIcon = status.icon

            return (
              <motion.div
                key={order.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card>
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-tg-hint text-sm">#{order.id}</span>
                        <div 
                          className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
                          style={{ 
                            backgroundColor: `${status.color}20`,
                            color: status.color
                          }}
                        >
                          <StatusIcon size={12} />
                          {status.label}
                        </div>
                      </div>
                      
                      <h3 className="font-semibold text-tg-text mt-1 truncate">
                        {order.service_name || order.service_type}
                      </h3>
                      
                      <p className="text-sm text-tg-hint mt-1 truncate">
                        {order.link}
                      </p>
                      
                      <div className="flex items-center gap-4 mt-2 text-sm">
                        <span className="text-tg-hint">
                          {order.quantity.toLocaleString()} ta
                        </span>
                        <span className="font-medium text-tg-text">
                          {order.price.toLocaleString()} so'm
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {order.created_at && (
                    <p className="text-xs text-tg-hint mt-3">
                      {new Date(order.created_at).toLocaleString('uz-UZ')}
                    </p>
                  )}
                </Card>
              </motion.div>
            )
          })}
        </div>
      )}
    </div>
  )
}
