import { AlertCircle, RefreshCcw } from 'lucide-react'
import Button from './Button'

interface ErrorStateProps {
  message?: string
  onRetry?: () => void
}

export default function ErrorState({ 
  message = "Xatolik yuz berdi", 
  onRetry 
}: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-4">
      <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center">
        <AlertCircle className="text-red-500" size={32} />
      </div>
      <p className="text-tg-text text-center">{message}</p>
      {onRetry && (
        <Button 
          variant="secondary" 
          onClick={onRetry}
          icon={<RefreshCcw size={18} />}
        >
          Qayta urinish
        </Button>
      )}
    </div>
  )
}
