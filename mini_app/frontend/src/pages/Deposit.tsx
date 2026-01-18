import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Check, Copy, AlertCircle, Camera, Send } from 'lucide-react'
import { Card, Button, Input } from '../components'
import { useTelegram } from '../hooks/useTelegram'
import { useAuth } from '../providers'

const quickAmounts = [10000, 25000, 50000, 100000, 250000, 500000]

interface PaymentMethod {
  id: string
  name: string
  card_number: string
  card_holder: string
  min_amount: number
}

export default function Deposit() {
  const navigate = useNavigate()
  const { hapticFeedback, showAlert, tg } = useTelegram()
  const { user } = useAuth()
  
  const [amount, setAmount] = useState('')
  const [selectedMethod, setSelectedMethod] = useState<string | null>(null)
  const [step, setStep] = useState<'amount' | 'method' | 'confirm' | 'receipt'>('amount')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [methods, setMethods] = useState<PaymentMethod[]>([])
  const [paymentId, setPaymentId] = useState<number | null>(null)

  useEffect(() => {
    // Fetch payment methods
    fetch('/api/payment/methods')
      .then(res => res.json())
      .then(data => {
        if (data.success && data.methods) {
          setMethods(data.methods)
        }
      })
      .catch(err => console.error('Error fetching methods:', err))
  }, [])

  const currentMethod = methods.find(m => m.id === selectedMethod)
  const parsedAmount = parseInt(amount) || 0
  const minAmount = methods[0]?.min_amount || 5000

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text.replace(/\s/g, ''))
    hapticFeedback?.notification?.('success')
    showAlert?.('📋 Karta raqami nusxalandi!')
  }

  const handleConfirm = async () => {
    if (!user?.user_id || !selectedMethod) return
    
    setIsSubmitting(true)
    
    try {
      const response = await fetch('/api/payment/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.user_id,
          amount: parsedAmount,
          method: selectedMethod
        })
      })
      
      const data = await response.json()
      
      if (data.success) {
        setPaymentId(data.payment_id)
        hapticFeedback?.notification?.('success')
        setStep('receipt')
      } else {
        showAlert?.('❌ Xatolik: ' + (data.error || 'Noma\'lum xatolik'))
      }
    } catch (error) {
      console.error('Error creating payment:', error)
      showAlert?.('❌ Xatolik yuz berdi')
    } finally {
      setIsSubmitting(false)
    }
  }

  const sendReceiptToBot = () => {
    // Botga o'tib chek yuborish
    if (tg) {
      tg.openTelegramLink(`https://t.me/SmmXizmatlari_bot?start=receipt_${paymentId}`)
    }
  }
      setIsSubmitting(false)
    }
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
                    hapticFeedback?.selection?.()
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
              hapticFeedback?.impact?.('medium')
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
                  hapticFeedback?.selection?.()
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
                hapticFeedback?.impact?.('medium')
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
              onClick={handleConfirm}
              loading={isSubmitting}
              icon={<Check size={20} />}
              className="flex-1"
            >
              To'ladim
            </Button>
          </div>
        </motion.div>
      )}

      {/* Step 4: Send Receipt */}
      {step === 'receipt' && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-4"
        >
          <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white text-center py-6">
            <div className="w-16 h-16 mx-auto rounded-full bg-white/20 flex items-center justify-center mb-4">
              <Camera size={32} />
            </div>
            <p className="text-xl font-bold">Chek yuborish</p>
            <p className="text-white/80 mt-2">To'lov #{paymentId}</p>
          </Card>

          <Card>
            <div className="text-center space-y-3">
              <p className="text-tg-text font-medium">
                To'lov chekini (skrinshot) botga yuboring
              </p>
              <p className="text-tg-hint text-sm">
                Admin chekni tekshirib, balansingizga {parsedAmount.toLocaleString()} so'm qo'shadi
              </p>
            </div>
          </Card>

          <div className="flex items-start gap-3 text-tg-hint text-sm bg-blue-50 p-4 rounded-xl">
            <AlertCircle size={18} className="text-blue-600 shrink-0 mt-0.5" />
            <div className="text-blue-800">
              <p className="font-medium mb-1">Muhim!</p>
              <p>Chekda to'lov miqdori va sana ko'rinishi kerak. Admin 5-30 daqiqa ichida tasdiqlaydi.</p>
            </div>
          </div>

          <Button
            fullWidth
            size="lg"
            onClick={sendReceiptToBot}
            icon={<Send size={20} />}
          >
            Botga o'tib chek yuborish
          </Button>

          <Button
            fullWidth
            variant="ghost"
            onClick={() => navigate('/balance')}
          >
            Keyinroq yuboraman
          </Button>
        </motion.div>
      )}
    </div>
  )
}
