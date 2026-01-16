import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Check, Copy, AlertCircle } from 'lucide-react'
import { Card, Button, Input, Loading, ErrorState } from '../components'
import { paymentsAPI } from '../lib/api'
import { useTelegram } from '../hooks/useTelegram'

const quickAmounts = [10000, 25000, 50000, 100000, 250000, 500000]

export default function Deposit() {
  const navigate = useNavigate()
  const { hapticFeedback, showAlert } = useTelegram()
  
  const [amount, setAmount] = useState('')
  const [selectedMethod, setSelectedMethod] = useState<string | null>(null)
  const [step, setStep] = useState<'amount' | 'method' | 'confirm'>('amount')

  const { data: methods, isLoading, error, refetch } = useQuery({
    queryKey: ['payment-methods'],
    queryFn: paymentsAPI.getMethods
  })

  const createPaymentMutation = useMutation({
    mutationFn: () => paymentsAPI.create(parseInt(amount), selectedMethod!),
    onSuccess: (payment) => {
      hapticFeedback.notification('success')
      showAlert(`✅ To'lov #${payment.id} yaratildi! Admin tasdiqlashini kuting.`)
      navigate('/balance')
    },
    onError: (error: any) => {
      hapticFeedback.notification('error')
      showAlert(error.response?.data?.detail || 'Xatolik yuz berdi')
    }
  })

  if (isLoading) return <Loading />
  if (error) return <ErrorState onRetry={() => refetch()} />

  const currentMethod = methods?.find(m => m.id === selectedMethod)
  const parsedAmount = parseInt(amount) || 0
  const minAmount = methods?.[0]?.min_amount || 5000

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text.replace(/\s/g, ''))
    hapticFeedback.notification('success')
    showAlert('📋 Karta raqami nusxalandi!')
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-tg-text">Hisobni to'ldirish</h1>
        <p className="text-tg-hint">Tez va oson</p>
      </div>

      {/* Step 1: Amount */}
      {step === 'amount' && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-6"
        >
          <Input
            label="Miqdorni kiriting"
            placeholder={`Min: ${minAmount.toLocaleString()} so'm`}
            value={amount}
            onChange={setAmount}
            type="number"
            min={minAmount}
            suffix="so'm"
          />

          <div>
            <p className="text-sm text-tg-hint mb-3">Tezkor summa:</p>
            <div className="grid grid-cols-3 gap-2">
              {quickAmounts.map((amt) => (
                <button
                  key={amt}
                  onClick={() => {
                    hapticFeedback.selection()
                    setAmount(amt.toString())
                  }}
                  className={`
                    py-3 rounded-xl text-sm font-medium transition-all
                    ${amount === amt.toString() 
                      ? 'bg-tg-button text-tg-button-text' 
                      : 'bg-tg-secondary-bg text-tg-text'}
                  `}
                >
                  {amt.toLocaleString()}
                </button>
              ))}
            </div>
          </div>

          <Button
            fullWidth
            size="lg"
            disabled={parsedAmount < minAmount}
            onClick={() => {
              hapticFeedback.impact('medium')
              setStep('method')
            }}
          >
            Davom etish
          </Button>
        </motion.div>
      )}

      {/* Step 2: Payment Method */}
      {step === 'method' && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-4"
        >
          <Card className="bg-tg-button text-white text-center">
            <p className="text-white/80">To'lov miqdori</p>
            <p className="text-3xl font-bold">{parsedAmount.toLocaleString()} so'm</p>
          </Card>

          <p className="text-tg-text font-medium">To'lov usulini tanlang:</p>

          <div className="space-y-3">
            {methods?.map((method) => (
              <Card
                key={method.id}
                onClick={() => {
                  hapticFeedback.selection()
                  setSelectedMethod(method.id)
                }}
                className={`cursor-pointer transition-all ${
                  selectedMethod === method.id 
                    ? 'ring-2 ring-tg-button' 
                    : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-tg-text">{method.name}</p>
                    <p className="text-sm text-tg-hint">{method.card_number}</p>
                  </div>
                  {selectedMethod === method.id && (
                    <div className="w-6 h-6 rounded-full bg-tg-button flex items-center justify-center">
                      <Check size={14} className="text-white" />
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>

          <div className="flex gap-3">
            <Button
              variant="secondary"
              onClick={() => setStep('amount')}
              className="flex-1"
            >
              Orqaga
            </Button>
            <Button
              disabled={!selectedMethod}
              onClick={() => {
                hapticFeedback.impact('medium')
                setStep('confirm')
              }}
              className="flex-1"
            >
              Davom etish
            </Button>
          </div>
        </motion.div>
      )}

      {/* Step 3: Confirm */}
      {step === 'confirm' && currentMethod && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-4"
        >
          <Card className="bg-gradient-to-r from-green-500 to-emerald-600 text-white">
            <p className="text-white/80 text-center">To'lang va tasdiqlang</p>
            <p className="text-3xl font-bold text-center mt-2">
              {parsedAmount.toLocaleString()} so'm
            </p>
          </Card>

          <Card>
            <p className="text-tg-hint text-sm">Karta raqami:</p>
            <div className="flex items-center justify-between mt-2">
              <p className="text-xl font-mono font-bold text-tg-text">
                {currentMethod.card_number}
              </p>
              <button
                onClick={() => copyToClipboard(currentMethod.card_number)}
                className="p-2 rounded-lg bg-tg-secondary-bg"
              >
                <Copy size={20} className="text-tg-link" />
              </button>
            </div>
            <p className="text-tg-hint text-sm mt-2">
              {currentMethod.card_holder}
            </p>
          </Card>

          <div className="flex items-start gap-3 text-tg-hint text-sm bg-yellow-50 p-4 rounded-xl">
            <AlertCircle size={18} className="text-yellow-600 shrink-0 mt-0.5" />
            <p className="text-yellow-800">
              To'lovni amalga oshirgandan so'ng "Tasdiqlash" tugmasini bosing.
              Admin tekshirib, balansingizga qo'shadi (5-30 daqiqa).
            </p>
          </div>

          <div className="flex gap-3">
            <Button
              variant="secondary"
              onClick={() => setStep('method')}
              className="flex-1"
            >
              Orqaga
            </Button>
            <Button
              onClick={() => createPaymentMutation.mutate()}
              loading={createPaymentMutation.isPending}
              icon={<Check size={20} />}
              className="flex-1"
            >
              Tasdiqlash
            </Button>
          </div>
        </motion.div>
      )}
    </div>
  )
}
