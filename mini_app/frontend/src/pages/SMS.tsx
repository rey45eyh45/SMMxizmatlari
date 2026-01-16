import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { Phone, Copy, RefreshCw, X, Check, Loader } from 'lucide-react'
import { Card, Button, Loading, ErrorState } from '../components'
import { smsAPI } from '../lib/api'
import { useTelegram } from '../hooks/useTelegram'
import type { SMSPlatform, SMSCountry } from '../types'

export default function SMS() {
  const { hapticFeedback, showAlert } = useTelegram()
  
  const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null)
  const [selectedCountry, setSelectedCountry] = useState<string>('ru')
  const [activeOrder, setActiveOrder] = useState<{
    orderId: string
    phone: string
    provider: string
    code?: string
  } | null>(null)

  // Platforms
  const { data: platforms, isLoading: platformsLoading } = useQuery({
    queryKey: ['sms-platforms'],
    queryFn: smsAPI.getPlatforms
  })

  // Countries
  const { data: countries } = useQuery({
    queryKey: ['sms-countries'],
    queryFn: smsAPI.getCountries
  })

  // Prices
  const { data: prices, isLoading: pricesLoading, refetch: refetchPrices } = useQuery({
    queryKey: ['sms-prices', selectedPlatform, selectedCountry],
    queryFn: () => smsAPI.getPrices(selectedPlatform!, selectedCountry),
    enabled: !!selectedPlatform
  })

  // Buy mutation
  const buyMutation = useMutation({
    mutationFn: () => smsAPI.buy(selectedPlatform!, selectedCountry),
    onSuccess: (data) => {
      hapticFeedback.notification('success')
      setActiveOrder({
        orderId: data.order_id,
        phone: data.phone_number,
        provider: data.provider
      })
    },
    onError: (error: any) => {
      hapticFeedback.notification('error')
      showAlert(error.response?.data?.detail || 'Xatolik yuz berdi')
    }
  })

  // Check code
  const checkCodeMutation = useMutation({
    mutationFn: () => smsAPI.checkCode(activeOrder!.provider, activeOrder!.orderId),
    onSuccess: (data) => {
      if (data.code) {
        hapticFeedback.notification('success')
        setActiveOrder(prev => prev ? { ...prev, code: data.code } : null)
      }
    }
  })

  // Cancel
  const cancelMutation = useMutation({
    mutationFn: () => smsAPI.cancel(activeOrder!.provider, activeOrder!.orderId),
    onSuccess: () => {
      hapticFeedback.notification('success')
      showAlert('Buyurtma bekor qilindi')
      setActiveOrder(null)
    }
  })

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    hapticFeedback.notification('success')
    showAlert('📋 Nusxalandi!')
  }

  if (platformsLoading) return <Loading />

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-tg-text">Virtual Raqamlar</h1>
        <p className="text-tg-hint">SMS qabul qilish - arzon narxlarda!</p>
      </div>

      {/* Active Order */}
      <AnimatePresence>
        {activeOrder && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
          >
            <Card className="bg-gradient-to-r from-green-500 to-emerald-600 text-white">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">Faol buyurtma</h3>
                <button
                  onClick={() => cancelMutation.mutate()}
                  className="p-1 rounded-lg bg-white/20"
                >
                  <X size={18} />
                </button>
              </div>

              <div className="flex items-center justify-between bg-white/10 rounded-xl p-4">
                <div className="flex items-center gap-3">
                  <Phone size={24} />
                  <span className="text-xl font-mono font-bold">{activeOrder.phone}</span>
                </div>
                <button
                  onClick={() => copyToClipboard(activeOrder.phone)}
                  className="p-2 rounded-lg bg-white/20"
                >
                  <Copy size={18} />
                </button>
              </div>

              {activeOrder.code ? (
                <div className="mt-4 bg-white/10 rounded-xl p-4 text-center">
                  <p className="text-white/80 text-sm">SMS Kod:</p>
                  <div className="flex items-center justify-center gap-2 mt-1">
                    <span className="text-3xl font-mono font-bold">{activeOrder.code}</span>
                    <button
                      onClick={() => copyToClipboard(activeOrder.code!)}
                      className="p-2 rounded-lg bg-white/20"
                    >
                      <Copy size={18} />
                    </button>
                  </div>
                </div>
              ) : (
                <Button
                  fullWidth
                  variant="secondary"
                  className="mt-4 bg-white text-green-600"
                  onClick={() => checkCodeMutation.mutate()}
                  loading={checkCodeMutation.isPending}
                  icon={<RefreshCw size={18} />}
                >
                  SMS tekshirish
                </Button>
              )}
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Country Select */}
      <div>
        <p className="text-sm text-tg-hint mb-2">Davlat:</p>
        <div className="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4 scrollbar-hide">
          {countries?.map((country) => (
            <button
              key={country.code}
              onClick={() => {
                hapticFeedback.selection()
                setSelectedCountry(country.code)
              }}
              className={`
                shrink-0 px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap
                ${selectedCountry === country.code 
                  ? 'bg-tg-button text-tg-button-text' 
                  : 'bg-tg-secondary-bg text-tg-text'}
              `}
            >
              {country.flag} {country.name}
            </button>
          ))}
        </div>
      </div>

      {/* Platform Select */}
      <div>
        <p className="text-sm text-tg-hint mb-3">Platforma:</p>
        <div className="grid grid-cols-2 gap-3">
          {platforms?.map((platform) => (
            <motion.button
              key={platform.code}
              whileTap={{ scale: 0.98 }}
              onClick={() => {
                hapticFeedback.selection()
                setSelectedPlatform(platform.code)
              }}
              className={`
                p-4 rounded-2xl text-left transition-all
                ${selectedPlatform === platform.code 
                  ? 'bg-tg-button text-tg-button-text ring-2 ring-tg-button ring-offset-2' 
                  : 'bg-tg-secondary-bg text-tg-text'}
              `}
            >
              <span className="text-2xl">{platform.emoji}</span>
              <p className="font-medium mt-2">{platform.name}</p>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Prices */}
      {selectedPlatform && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm text-tg-hint">Narxlar:</p>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => refetchPrices()}
              icon={<RefreshCw size={14} />}
            >
              Yangilash
            </Button>
          </div>

          {pricesLoading ? (
            <Loading />
          ) : prices?.length === 0 ? (
            <Card className="text-center py-6">
              <p className="text-tg-hint">Raqam mavjud emas</p>
            </Card>
          ) : (
            <div className="space-y-2">
              {prices?.map((price, index) => (
                <Card 
                  key={index}
                  className="flex items-center justify-between"
                >
                  <div>
                    <p className="font-medium text-tg-text">{price.provider_name}</p>
                    <p className="text-sm text-tg-hint">{price.available} ta mavjud</p>
                  </div>
                  <Button
                    size="sm"
                    onClick={() => buyMutation.mutate()}
                    loading={buyMutation.isPending}
                    disabled={activeOrder !== null}
                  >
                    {price.price_uzs.toLocaleString()} so'm
                  </Button>
                </Card>
              ))}
            </div>
          )}
        </motion.div>
      )}
    </div>
  )
}
