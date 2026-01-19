import { useState, useEffect, useCallback } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Check, 
  AlertCircle, 
  ArrowLeft,
  ExternalLink,
  RefreshCw,
  Clock,
  CheckCircle2,
  XCircle
} from 'lucide-react'
import { Card, Button, Input } from '../components'
import { ClickIcon } from '../components/icons'
import { useTelegram } from '../hooks/useTelegram'
import { useAuth } from '../providers'
import { clickAPI, type ClickPaymentResponse, type ClickPaymentStatus } from '../lib/api'

const quickAmounts = [10000, 25000, 50000, 100000, 250000, 500000]

type Step = 'amount' | 'processing' | 'waiting' | 'success' | 'error'

export default function ClickDeposit() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { hapticFeedback, showAlert, openLink } = useTelegram()
  const { user, refetchUser } = useAuth()
  
  const [amount, setAmount] = useState('')
  const [step, setStep] = useState<Step>('amount')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [paymentId, setPaymentId] = useState<number | null>(null)
  const [paymentUrl, setPaymentUrl] = useState<string | null>(null)
  const [paymentStatus, setPaymentStatus] = useState<ClickPaymentStatus | null>(null)
  const [checkingStatus, setCheckingStatus] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string>('')

  const parsedAmount = parseInt(amount) || 0
  const minAmount = 1000

  // URL'dan amount va payment_id olish
  useEffect(() => {
    const urlAmount = searchParams.get('amount')
    const returnedPaymentId = searchParams.get('payment_id')
    
    if (urlAmount && parseInt(urlAmount) >= minAmount) {
      setAmount(urlAmount)
      // Agar summa to'g'ri bo'lsa, darhol to'lov sahifasiga o'tkazamiz
      // Foydalanuvchi summani ko'radi va "To'lash" tugmasini bosadi
    }
    
    if (returnedPaymentId) {
      setPaymentId(parseInt(returnedPaymentId))
      setStep('waiting')
    }
  }, [searchParams])

  // To'lov holatini tekshirish
  const checkPaymentStatus = useCallback(async () => {
    if (!paymentId) return
    
    setCheckingStatus(true)
    try {
      const status = await clickAPI.getPaymentStatus(paymentId)
      setPaymentStatus(status)
      
      if (status.success && status.status === 'completed') {
        setStep('success')
        hapticFeedback?.notification?.('success')
        // Balansni yangilash
        await refetchUser()
      } else if (status.status === 'cancelled' || status.status === 'error') {
        setStep('error')
        setErrorMessage("To'lov bekor qilindi yoki xatolik yuz berdi")
        hapticFeedback?.notification?.('error')
      }
    } catch (error) {
      console.error('Error checking payment status:', error)
    } finally {
      setCheckingStatus(false)
    }
  }, [paymentId, hapticFeedback, refetchUser])

  // Waiting stepda avtomatik tekshirish
  useEffect(() => {
    if (step === 'waiting' && paymentId) {
      // Dastlab tekshirish
      checkPaymentStatus()
      
      // Har 5 sekundda tekshirish
      const interval = setInterval(checkPaymentStatus, 5000)
      
      return () => clearInterval(interval)
    }
  }, [step, paymentId, checkPaymentStatus])

  // Click to'lov yaratish
  const createClickPayment = async () => {
    if (parsedAmount < minAmount) {
      showAlert?.(`Minimal to'lov miqdori ${minAmount.toLocaleString()} so'm`)
      return
    }

    setIsSubmitting(true)
    setStep('processing')
    
    try {
      const result: ClickPaymentResponse = await clickAPI.createPayment(parsedAmount)
      
      if (result.success && result.payment_url) {
        setPaymentId(result.payment_id!)
        setPaymentUrl(result.payment_url)
        setStep('waiting')
        
        hapticFeedback?.notification?.('success')
        
        // Click sahifasini ochish
        if (openLink) {
          openLink(result.payment_url)
        } else {
          window.open(result.payment_url, '_blank')
        }
      } else {
        setStep('error')
        setErrorMessage(result.error || "To'lov yaratishda xatolik")
        hapticFeedback?.notification?.('error')
      }
    } catch (error) {
      console.error('Error creating Click payment:', error)
      setStep('error')
      setErrorMessage("Serverga ulanishda xatolik")
      hapticFeedback?.notification?.('error')
    } finally {
      setIsSubmitting(false)
    }
  }

  // Steplar bo'yicha renderlar
  const renderAmountStep = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="space-y-6"
    >
      {/* Click Logo/Card */}
      <Card className="bg-[#00AEEF] text-white p-6 text-center">
        <div className="w-20 h-20 mx-auto mb-4 bg-white rounded-2xl flex items-center justify-center">
          <ClickIcon size={64} />
        </div>
        <h2 className="text-xl font-bold">Click orqali to'lov</h2>
        <p className="text-white/80 mt-2">Xavfsiz va tezkor to'lov</p>
      </Card>

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

      {/* Joriy balans */}
      <Card className="bg-tg-secondary-bg">
        <div className="flex justify-between items-center">
          <span className="text-tg-hint">Joriy balans:</span>
          <span className="font-bold text-tg-text">
            {(user?.balance || 0).toLocaleString()} so'm
          </span>
        </div>
      </Card>

      <Button
        fullWidth
        size="lg"
        disabled={parsedAmount < minAmount}
        loading={isSubmitting}
        onClick={createClickPayment}
        className="!bg-[#00AEEF] hover:!bg-[#0099D6]"
      >
        <div className="flex items-center justify-center gap-2">
          <ClickIcon size={24} />
          <span>Click orqali to'lash</span>
        </div>
      </Button>

      <Button
        fullWidth
        variant="secondary"
        onClick={() => navigate('/deposit')}
        icon={<ArrowLeft size={20} />}
      >
        Orqaga
      </Button>
    </motion.div>
  )

  const renderProcessingStep = () => (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="space-y-6"
    >
      <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-8 text-center">
        <div className="w-20 h-20 mx-auto rounded-full bg-white/20 flex items-center justify-center mb-4">
          <RefreshCw size={40} className="animate-spin" />
        </div>
        <h2 className="text-xl font-bold">To'lov tayyorlanmoqda...</h2>
        <p className="text-white/80 mt-2">Iltimos, kuting</p>
      </Card>
    </motion.div>
  )

  const renderWaitingStep = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="space-y-6"
    >
      <Card className="bg-gradient-to-r from-orange-400 to-orange-500 text-white p-6 text-center">
        <div className="w-16 h-16 mx-auto rounded-full bg-white/20 flex items-center justify-center mb-4">
          <Clock size={32} />
        </div>
        <h2 className="text-xl font-bold">To'lov kutilmoqda</h2>
        <p className="text-white/80 mt-2">#{paymentId}</p>
        <p className="text-3xl font-bold mt-4">{parsedAmount.toLocaleString()} so'm</p>
      </Card>

      {/* Click sahifasini qayta ochish */}
      {paymentUrl && (
        <Button
          fullWidth
          size="lg"
          onClick={() => {
            if (openLink) {
              openLink(paymentUrl)
            } else {
              window.open(paymentUrl, '_blank')
            }
          }}
          icon={<ExternalLink size={20} />}
        >
          Click sahifasini ochish
        </Button>
      )}

      {/* Holatni tekshirish */}
      <Button
        fullWidth
        variant="secondary"
        onClick={checkPaymentStatus}
        loading={checkingStatus}
        icon={<RefreshCw size={20} className={checkingStatus ? 'animate-spin' : ''} />}
      >
        Holatni tekshirish
      </Button>

      {/* Joriy holat */}
      {paymentStatus && (
        <Card className="bg-tg-secondary-bg">
          <div className="flex items-center gap-3">
            {paymentStatus.status === 'pending' && (
              <>
                <Clock size={20} className="text-orange-500" />
                <span className="text-tg-text">To'lov kutilmoqda...</span>
              </>
            )}
            {paymentStatus.status === 'preparing' && (
              <>
                <RefreshCw size={20} className="text-blue-500 animate-spin" />
                <span className="text-tg-text">To'lov jarayonda...</span>
              </>
            )}
            {paymentStatus.status === 'completed' && (
              <>
                <CheckCircle2 size={20} className="text-green-500" />
                <span className="text-tg-text">To'lov muvaffaqiyatli!</span>
              </>
            )}
            {(paymentStatus.status === 'cancelled' || paymentStatus.status === 'error') && (
              <>
                <XCircle size={20} className="text-red-500" />
                <span className="text-tg-text">To'lov bekor qilindi</span>
              </>
            )}
          </div>
        </Card>
      )}

      <div className="flex items-start gap-3 text-tg-hint text-sm bg-blue-50 p-4 rounded-xl">
        <AlertCircle size={18} className="text-blue-600 shrink-0 mt-0.5" />
        <div className="text-blue-800">
          <p className="font-medium mb-1">Qanday to'lash kerak:</p>
          <ol className="list-decimal list-inside space-y-1">
            <li>Click sahifasini oching</li>
            <li>Click ilovasida to'lovni tasdiqlang</li>
            <li>Bu yerga qaytib "Holatni tekshirish" tugmasini bosing</li>
          </ol>
        </div>
      </div>

      <Button
        fullWidth
        variant="ghost"
        onClick={() => navigate('/balance')}
      >
        Bekor qilish
      </Button>
    </motion.div>
  )

  const renderSuccessStep = () => (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="space-y-6"
    >
      <Card className="bg-gradient-to-r from-green-500 to-emerald-600 text-white p-8 text-center">
        <div className="w-20 h-20 mx-auto rounded-full bg-white/20 flex items-center justify-center mb-4">
          <Check size={40} />
        </div>
        <h2 className="text-2xl font-bold">To'lov muvaffaqiyatli!</h2>
        <p className="text-4xl font-bold mt-4">
          {(paymentStatus?.amount || parsedAmount).toLocaleString()} so'm
        </p>
        <p className="text-white/80 mt-2">balansingizga qo'shildi</p>
      </Card>

      <Card className="bg-tg-secondary-bg">
        <div className="flex justify-between items-center">
          <span className="text-tg-hint">Yangi balans:</span>
          <span className="font-bold text-green-600 text-xl">
            {(user?.balance || 0).toLocaleString()} so'm
          </span>
        </div>
      </Card>

      <Button
        fullWidth
        size="lg"
        onClick={() => navigate('/balance')}
        icon={<CheckCircle2 size={20} />}
      >
        Balansga o'tish
      </Button>
    </motion.div>
  )

  const renderErrorStep = () => (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="space-y-6"
    >
      <Card className="bg-gradient-to-r from-red-500 to-red-600 text-white p-8 text-center">
        <div className="w-20 h-20 mx-auto rounded-full bg-white/20 flex items-center justify-center mb-4">
          <XCircle size={40} />
        </div>
        <h2 className="text-2xl font-bold">Xatolik yuz berdi</h2>
        <p className="text-white/80 mt-2">{errorMessage}</p>
      </Card>

      <Button
        fullWidth
        size="lg"
        onClick={() => {
          setStep('amount')
          setPaymentId(null)
          setPaymentUrl(null)
          setPaymentStatus(null)
          setErrorMessage('')
        }}
        icon={<RefreshCw size={20} />}
      >
        Qayta urinish
      </Button>

      <Button
        fullWidth
        variant="secondary"
        onClick={() => navigate('/balance')}
      >
        Orqaga
      </Button>
    </motion.div>
  )

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-tg-text">Click to'lov</h1>
        <p className="text-tg-hint">Xavfsiz onlayn to'lov</p>
      </div>

      {step === 'amount' && renderAmountStep()}
      {step === 'processing' && renderProcessingStep()}
      {step === 'waiting' && renderWaitingStep()}
      {step === 'success' && renderSuccessStep()}
      {step === 'error' && renderErrorStep()}
    </div>
  )
}
