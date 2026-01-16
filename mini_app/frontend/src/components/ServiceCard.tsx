import { motion } from 'framer-motion'
import { LucideIcon } from 'lucide-react'

interface ServiceCardProps {
  emoji: string
  name: string
  description?: string
  price?: string
  onClick?: () => void
  color?: string
  icon?: LucideIcon
  badge?: string
}

export default function ServiceCard({
  emoji,
  name,
  description,
  price,
  onClick,
  color = '#0088cc',
  icon: Icon,
  badge
}: ServiceCardProps) {
  return (
    <motion.button
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="w-full bg-tg-secondary-bg rounded-2xl p-4 text-left relative overflow-hidden"
    >
      {/* Background gradient */}
      <div 
        className="absolute top-0 right-0 w-24 h-24 rounded-full opacity-10 blur-2xl"
        style={{ backgroundColor: color }}
      />
      
      {/* Badge */}
      {badge && (
        <div className="absolute top-2 right-2 bg-yellow-400 text-yellow-900 text-[10px] font-bold px-2 py-0.5 rounded-full">
          {badge}
        </div>
      )}
      
      <div className="flex items-start gap-3 relative z-10">
        <div 
          className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl"
          style={{ backgroundColor: `${color}20` }}
        >
          {Icon ? <Icon size={24} style={{ color }} /> : emoji}
        </div>
        
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-tg-text truncate">{name}</h3>
          {description && (
            <p className="text-sm text-tg-hint mt-0.5 line-clamp-2">{description}</p>
          )}
          {price && (
            <p className="text-sm font-semibold mt-1" style={{ color }}>
              {price}
            </p>
          )}
        </div>
      </div>
    </motion.button>
  )
}
