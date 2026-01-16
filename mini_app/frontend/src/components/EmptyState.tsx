import { PackageOpen } from 'lucide-react'

interface EmptyStateProps {
  title?: string
  description?: string
  icon?: React.ReactNode
}

export default function EmptyState({ 
  title = "Ma'lumot topilmadi",
  description,
  icon
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-4">
      <div className="w-16 h-16 rounded-full bg-tg-secondary-bg flex items-center justify-center">
        {icon || <PackageOpen className="text-tg-hint" size={32} />}
      </div>
      <div className="text-center">
        <p className="text-tg-text font-medium">{title}</p>
        {description && (
          <p className="text-tg-hint text-sm mt-1">{description}</p>
        )}
      </div>
    </div>
  )
}
