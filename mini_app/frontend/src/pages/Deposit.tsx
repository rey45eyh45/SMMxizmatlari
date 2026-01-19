import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Check, Copy, AlertCircle, Camera, Send, Upload, X, Image, ChevronRight } from 'lucide-react'
import { Card, Button, Input } from '../components'
import { ClickIcon } from '../components/icons'
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
  const { hapticFeedback, showAlert } = useTelegram()
  const { user } = useAuth()
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  const [amount, setAmount] = useState('')
  const [selectedMethod, setSelectedMethod] = useState<string | null>(null)
  const [step, setStep] = useState<'amount' | 'method' | 'confirm' | 'receipt'>('amount')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [methods, setMethods] = useState<PaymentMethod[]>([])
  const [paymentId, setPaymentId] = useState<number | null>(null)
  const [receiptImage, setReceiptImage] = useState<File | null>(null)
  const [receiptPreview, setReceiptPreview] = useState<string | null>(null)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')

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

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // Check file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        showAlert?.('❌ Rasm hajmi 10MB dan katta')
        return
      }
      
      setReceiptImage(file)
      setReceiptPreview(URL.createObjectURL(file))
      hapticFeedback?.selection?.()
    }
  }

  const clearImage = () => {
    setReceiptImage(null)
    setReceiptPreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const sendReceipt = async () => {
    console.log('sendReceipt called', { receiptImage, paymentId, user_id: user?.user_id })
    
    if (!receiptImage) {
      showAlert?.('❌ Iltimos, chek rasmini tanlang')
      return
    }
    
    if (!paymentId) {
      showAlert?.('❌ To\'lov ID topilmadi')
      return
    }
    
    if (!user?.user_id) {
      showAlert?.('❌ Foydalanuvchi aniqlanmadi')
      return
    }
    
    setUploadStatus('uploading')
    setIsSubmitting(true)
    
    try {
      const formData = new FormData()
      formData.append('receipt', receiptImage)
      formData.append('payment_id', paymentId.toString())
      formData.append('user_id', user.user_id.toString())
      formData.append('amount', parsedAmount.toString())
      formData.append('full_name', user.full_name || 'Foydalanuvchi')
      
      console.log('Sending receipt...', { paymentId, amount: parsedAmount })
      
      const response = await fetch('/api/payment/upload-receipt', {
        method: 'POST',
        body: formData
      })
      
      console.log('Response status:', response.status)
      
      // Check if response is ok
      const text = await response.text()
      console.log('Response text:', text)
      
      let data
      try {
        data = JSON.parse(text)
      } catch (e) {
        console.error('Failed to parse JSON:', text)
        throw new Error('Server error: ' + (text || 'No response'))
      }
      
      console.log('Response data:', data)
      
      if (data.success) {
        setUploadStatus('success')
        hapticFeedback?.notification?.('success')
        
        // 2 sekunddan keyin Balance sahifasiga o'tish
        setTimeout(() => {
          navigate('/balance')
        }, 2000)
      } else {
        setUploadStatus('error')
        showAlert?.('❌ ' + (data.error || 'Xatolik yuz berdi'))
      }
    } catch (error) {
      console.error('Error uploading receipt:', error)
      setUploadStatus('error')
      showAlert?.('❌ Chekni yuborishda xatolik: ' + (error as Error).message)
    } finally {
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
          {/* Click - Tezkor to'lov banneri */}
          <Card
            onClick={() => {
              hapticFeedback?.selection?.()
              // Agar summa kiritilgan bo'lsa, URL'ga qo'shib yuboramiz
              if (parsedAmount >= minAmount) {
                navigate(`/deposit/click?amount=${parsedAmount}`)
              } else {
                navigate('/deposit/click')
              }
            }}
            className="cursor-pointer bg-[#00AEEF] text-white p-4"
          >
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-white rounded-xl flex items-center justify-center shrink-0">
                <ClickIcon size={48} />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <p className="font-bold text-lg">Click to'lov</p>
                  <span className="px-2 py-0.5 bg-white/20 text-white text-xs font-medium rounded-full">
                    Tez ⚡
                  </span>
                </div>
                <p className="text-white/80 text-sm">Avtomatik - 1 daqiqada</p>
              </div>
              <ChevronRight size={24} className="text-white/80" />
            </div>
          </Card>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-tg-bg text-tg-hint">yoki karta o'tkazma</span>
            </div>
          </div>

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
            Karta o'tkazmasi bilan to'lash
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
          {/* Success Message */}
          {uploadStatus === 'success' ? (
            <Card className="bg-gradient-to-r from-green-500 to-emerald-600 text-white text-center py-8">
              <div className="w-20 h-20 mx-auto rounded-full bg-white/20 flex items-center justify-center mb-4">
                <Check size={40} />
              </div>
              <p className="text-2xl font-bold">Chek yuborildi!</p>
              <p className="text-white/80 mt-2">Admin tez orada tekshiradi</p>
              <p className="text-white/60 text-sm mt-4">Balans sahifasiga o'tmoqda...</p>
            </Card>
          ) : (
            <>
              <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white text-center py-6">
                <div className="w-16 h-16 mx-auto rounded-full bg-white/20 flex items-center justify-center mb-4">
                  <Camera size={32} />
                </div>
                <p className="text-xl font-bold">Chek yuborish</p>
                <p className="text-white/80 mt-2">To'lov #{paymentId}</p>
                <p className="text-white/60 text-sm mt-1">{parsedAmount.toLocaleString()} so'm</p>
              </Card>

              {/* Image Upload Area */}
              <Card>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleImageSelect}
                  accept="image/*"
                  className="hidden"
                />
                
                {receiptPreview ? (
                  <div className="relative">
                    <img 
                      src={receiptPreview} 
                      alt="Receipt" 
                      className="w-full rounded-lg max-h-64 object-contain bg-gray-100"
                    />
                    <button
                      onClick={clearImage}
                      className="absolute top-2 right-2 p-2 rounded-full bg-red-500 text-white shadow-lg"
                    >
                      <X size={20} />
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full py-12 border-2 border-dashed border-tg-hint/30 rounded-xl flex flex-col items-center justify-center gap-3 transition-colors hover:border-tg-button hover:bg-tg-button/5"
                  >
                    <div className="w-16 h-16 rounded-full bg-tg-button/10 flex items-center justify-center">
                      <Image size={32} className="text-tg-button" />
                    </div>
                    <div className="text-center">
                      <p className="text-tg-text font-medium">Chek rasmini tanlang</p>
                      <p className="text-tg-hint text-sm mt-1">Bosing yoki faylni torting</p>
                    </div>
                  </button>
                )}
              </Card>

              <div className="flex items-start gap-3 text-tg-hint text-sm bg-blue-50 p-4 rounded-xl">
                <AlertCircle size={18} className="text-blue-600 shrink-0 mt-0.5" />
                <div className="text-blue-800">
                  <p className="font-medium mb-1">Muhim!</p>
                  <p>Chekda to'lov miqdori va sana ko'rinishi kerak. Admin 5-30 daqiqa ichida tekshiradi.</p>
                </div>
              </div>

              <Button
                fullWidth
                size="lg"
                onClick={sendReceipt}
                disabled={!receiptImage}
                loading={isSubmitting}
                icon={<Send size={20} />}
              >
                {isSubmitting ? 'Yuborilmoqda...' : 'Chekni yuborish'}
              </Button>

              {!receiptImage && (
                <Button
                  fullWidth
                  variant="secondary"
                  onClick={() => fileInputRef.current?.click()}
                  icon={<Upload size={20} />}
                >
                  Rasm tanlash
                </Button>
              )}

              <Button
                fullWidth
                variant="ghost"
                onClick={() => navigate('/balance')}
              >
                Keyinroq yuboraman
              </Button>
            </>
          )}
        </motion.div>
      )}
    </div>
  )
}
