import { Loader2 } from 'lucide-react'

interface LoadingProps {
  text?: string
  fullScreen?: boolean
}

export default function Loading({ text = 'Yuklanmoqda...', fullScreen = false }: LoadingProps) {
  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-tg-bg flex items-center justify-center z-50">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="animate-spin text-tg-button" size={40} />
          <p className="text-tg-hint">{text}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center justify-center py-12 gap-4">
      <Loader2 className="animate-spin text-tg-button" size={32} />
      <p className="text-tg-hint text-sm">{text}</p>
    </div>
  )
}
