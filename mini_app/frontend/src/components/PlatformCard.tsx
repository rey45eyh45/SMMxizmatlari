import { motion } from 'framer-motion'
import { ChevronRight } from 'lucide-react'
import { getPlatformIcon } from './icons/PlatformIcons'

interface PlatformCardProps {
  id?: string
  emoji: string
  name: string
  servicesCount?: number
  onClick?: () => void
  color: string
}

export default function PlatformCard({
  id,
  emoji,
  name,
  servicesCount,
  onClick,
  color
}: PlatformCardProps) {
  // Try to get SVG icon, fallback to emoji
  const IconComponent = id ? getPlatformIcon(id) : null

  return (
    <motion.button
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="w-full bg-tg-secondary-bg rounded-2xl p-4 flex items-center gap-4 relative overflow-hidden"
    >
      {/* Background accent */}
      <div 
        className="absolute inset-0 opacity-5"
        style={{ 
          background: `linear-gradient(135deg, ${color} 0%, transparent 50%)`
        }}
      />
      
      <div 
        className="w-14 h-14 rounded-2xl flex items-center justify-center shrink-0"
        style={{ backgroundColor: IconComponent ? 'transparent' : `${color}15` }}
      >
        {IconComponent ? (
          <IconComponent size={48} />
        ) : (
          <span className="text-3xl">{emoji}</span>
        )}
      </div>
      
      <div className="flex-1 text-left">
        <h3 className="font-semibold text-tg-text text-lg">{name}</h3>
        {servicesCount !== undefined && (
          <p className="text-sm text-tg-hint mt-0.5">
            {servicesCount} ta xizmat
          </p>
        )}
      </div>
      
      <ChevronRight className="text-tg-hint shrink-0" size={20} />
    </motion.button>
  )
}
