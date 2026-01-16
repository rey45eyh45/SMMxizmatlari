import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { PlatformCard, Loading, ErrorState } from '../components'
import { servicesAPI } from '../lib/api'
import { useTelegram } from '../hooks/useTelegram'

const platformColors: Record<string, string> = {
  telegram: '#0088cc',
  instagram: '#E1306C',
  youtube: '#FF0000',
  tiktok: '#000000',
  sms: '#4CAF50'
}

export default function Services() {
  const navigate = useNavigate()
  const { hapticFeedback } = useTelegram()

  const { data: platforms, isLoading, error, refetch } = useQuery({
    queryKey: ['platforms'],
    queryFn: servicesAPI.getPlatforms
  })

  if (isLoading) return <Loading />
  if (error) return <ErrorState onRetry={() => refetch()} />

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-tg-text">Xizmatlar</h1>
        <p className="text-tg-hint mt-1">Platformani tanlang</p>
      </div>

      <div className="space-y-3">
        {platforms?.map((platform, index) => (
          <motion.div
            key={platform.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <PlatformCard
              emoji={platform.emoji}
              name={platform.name}
              color={platformColors[platform.id] || '#0088cc'}
              onClick={() => {
                hapticFeedback.selection()
                navigate(`/services/${platform.id}`)
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
            emoji="📱"
            name="Virtual Raqamlar"
            color="#4CAF50"
            onClick={() => {
              hapticFeedback.selection()
              navigate('/sms')
            }}
          />
        </motion.div>
      </div>
    </div>
  )
}
