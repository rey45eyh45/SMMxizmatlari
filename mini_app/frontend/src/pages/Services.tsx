import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { PlatformCard } from '../components'
import { useTelegram } from '../hooks/useTelegram'
import { mockPlatforms } from '../lib/mockData'

export default function Services() {
  const navigate = useNavigate()
  const { hapticFeedback } = useTelegram()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-tg-text">Xizmatlar</h1>
        <p className="text-tg-hint mt-1">Platformani tanlang</p>
      </div>

      <div className="space-y-3">
        {mockPlatforms.map((platform, index) => (
          <motion.div
            key={platform.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <PlatformCard
              id={platform.id}
              emoji={platform.emoji}
              name={platform.name}
              color={platform.color}
              onClick={() => {
                hapticFeedback?.selection?.()
                navigate(`/platform/${platform.id}`)
              }}
            />
          </motion.div>
        ))}

        {/* Virtual Numbers - Special */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
        >
          <PlatformCard
            id="sms"
            emoji="📱"
            name="Virtual Raqamlar"
            color="#4CAF50"
            onClick={() => {
              hapticFeedback?.selection?.()
              navigate('/sms')
            }}
          />
        </motion.div>
      </div>
    </div>
  )
}
