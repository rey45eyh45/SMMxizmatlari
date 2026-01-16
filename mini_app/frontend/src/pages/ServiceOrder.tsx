import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Check, AlertCircle, Info } from 'lucide-react'
import { Button, Input, Card, Loading, ErrorState } from '../components'
import { servicesAPI, ordersAPI } from '../lib/api'
import { useAuthStore } from '../store'
import { useTelegram } from '../hooks/useTelegram'

export default function ServiceOrder() {
  const { serviceId } = useParams<{ serviceId: string }>()
  const navigate = useNavigate()
  const { hapticFeedback, showAlert, mainButton } = useTelegram()
  const { user, updateBalance } = useAuthStore()

  const [link, setLink] = useState('')
  const [quantity, setQuantity] = useState('')

  const { data: service, isLoading, error, refetch } = useQuery({
    queryKey: ['service', serviceId],
    queryFn: () => servicesAPI.getService(serviceId!),
    enabled: !!serviceId
  })

  const createOrderMutation = useMutation({
    mutationFn: () => ordersAPI.create(serviceId!, link, parseInt(quantity)),
    onSuccess: (order) => {
      hapticFeedback.notification('success')
      updateBalance(user!.balance - order.price)
      showAlert(`✅ Buyurtma #${order.id} yaratildi!`)
      navigate('/orders')
    },
    onError: (error: any) => {
      hapticFeedback.notification('error')
      showAlert(error.response?.data?.detail || 'Xatolik yuz berdi')
    }
  })

  if (isLoading) return <Loading />
  if (error || !service) return <ErrorState onRetry={() => refetch()} />

  const qty = parseInt(quantity) || 0
  const totalPrice = Math.max(100, Math.floor((qty / 1000) * service.price_per_1000))
  const balance = user?.balance || 0
  const canOrder = 
    link.length > 0 && 
    qty >= service.min_quantity && 
    qty <= service.max_quantity && 
    balance >= totalPrice

  const handleOrder = () => {
    if (!canOrder) return
    hapticFeedback.impact('medium')
    createOrderMutation.mutate()
  }

  return (
    <div className="space-y-6">
      {/* Service Info */}
      <Card>
        <h1 className="text-xl font-bold text-tg-text">{service.name}</h1>
        <p className="text-tg-hint mt-1">{service.description}</p>
        
        <div className="grid grid-cols-2 gap-4 mt-4">
          <div className="bg-tg-bg rounded-xl p-3">
            <p className="text-tg-hint text-xs">Narx</p>
            <p className="text-tg-text font-semibold">
              {service.price_per_1000.toLocaleString()} so'm
            </p>
            <p className="text-tg-hint text-xs">1000 ta uchun</p>
          </div>
          <div className="bg-tg-bg rounded-xl p-3">
            <p className="text-tg-hint text-xs">Kafolat</p>
            <p className="text-tg-text font-semibold">{service.guarantee}</p>
            <p className="text-tg-hint text-xs">Tezlik: {service.speed}</p>
          </div>
        </div>
      </Card>

      {/* Order Form */}
      <div className="space-y-4">
        <Input
          label="Havola (Link)"
          placeholder="https://t.me/..."
          value={link}
          onChange={setLink}
          type="url"
          hint="Kanal yoki guruh havolasini kiriting"
        />

        <Input
          label="Miqdor"
          placeholder={`Min: ${service.min_quantity.toLocaleString()}`}
          value={quantity}
          onChange={setQuantity}
          type="number"
          min={service.min_quantity}
          max={service.max_quantity}
          hint={`Min: ${service.min_quantity.toLocaleString()} | Max: ${service.max_quantity.toLocaleString()}`}
        />
      </div>

      {/* Price Summary */}
      <Card className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-tg-hint">Miqdor:</span>
          <span className="text-tg-text font-medium">{qty.toLocaleString()} ta</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-tg-hint">Narx:</span>
          <span className="text-tg-text font-medium">{service.price_per_1000.toLocaleString()} so'm / 1000</span>
        </div>
        <div className="border-t border-tg-bg pt-3">
          <div className="flex justify-between items-center">
            <span className="text-tg-text font-semibold">Jami:</span>
            <span className="text-xl font-bold text-tg-button">
              {totalPrice.toLocaleString()} so'm
            </span>
          </div>
        </div>
        
        {balance < totalPrice && qty > 0 && (
          <div className="flex items-center gap-2 text-red-500 text-sm">
            <AlertCircle size={16} />
            <span>Balans yetarli emas. Kerak: {(totalPrice - balance).toLocaleString()} so'm</span>
          </div>
        )}
      </Card>

      {/* Info */}
      <div className="flex items-start gap-3 text-tg-hint text-sm">
        <Info size={18} className="shrink-0 mt-0.5" />
        <p>
          Buyurtma yaratilgandan so'ng, xizmat avtomatik ravishda bajariladi.
          Odatda 1-24 soat ichida tugaydi.
        </p>
      </div>

      {/* Order Button */}
      <Button
        fullWidth
        size="lg"
        onClick={handleOrder}
        disabled={!canOrder}
        loading={createOrderMutation.isPending}
        icon={<Check size={20} />}
      >
        Buyurtma berish
      </Button>
    </div>
  )
}
