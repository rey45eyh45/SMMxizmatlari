import { motion } from 'framer-motion'
import { ChevronRight } from 'lucide-react'

interface PlatformCardProps {
  emoji: string
  name: string
  servicesCount?: number
  onClick?: () => void
  color: string
}

export default function PlatformCard({
  emoji,
  name,
  servicesCount,
  onClick,
  color
}: PlatformCardProps) {
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
        className="w-14 h-14 rounded-2xl flex items-center justify-center text-3xl shrink-0"
        style={{ backgroundColor: `${color}15` }}
      >
        {emoji}
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
