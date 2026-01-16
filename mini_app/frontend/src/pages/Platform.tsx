import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { ServiceCard, Loading, ErrorState } from '../components'
import { servicesAPI } from '../lib/api'
import { useTelegram } from '../hooks/useTelegram'

const platformColors: Record<string, string> = {
  telegram: '#0088cc',
  instagram: '#E1306C',
  youtube: '#FF0000',
  tiktok: '#000000'
}

export default function Platform() {
  const { platformId } = useParams<{ platformId: string }>()
  const navigate = useNavigate()
  const { hapticFeedback } = useTelegram()

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['platform', platformId],
    queryFn: () => servicesAPI.getPlatformServices(platformId!),
    enabled: !!platformId
  })

  if (isLoading) return <Loading />
  if (error || !data) return <ErrorState onRetry={() => refetch()} />

  const { platform, categories, services } = data
  const color = platformColors[platformId!] || '#0088cc'

  // Group services by category
  const servicesByCategory: Record<string, typeof services> = {}
  services.forEach(service => {
    const cat = service.category
    if (!servicesByCategory[cat]) {
      servicesByCategory[cat] = []
    }
    servicesByCategory[cat].push(service)
  })

  const formatPrice = (price: number) => {
    return `${price.toLocaleString()} so'm / 1000`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <div 
          className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl"
          style={{ backgroundColor: `${color}15` }}
        >
          {platform.emoji}
        </div>
        <div>
          <h1 className="text-2xl font-bold text-tg-text">{platform.name}</h1>
          <p className="text-tg-hint">{services.length} ta xizmat</p>
        </div>
      </div>

      {/* Categories */}
      {categories.length > 0 && (
        <div className="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4 scrollbar-hide">
          {categories.map((cat) => (
            <button
              key={cat.id}
              className="shrink-0 px-4 py-2 rounded-full bg-tg-secondary-bg text-sm font-medium text-tg-text whitespace-nowrap"
            >
              {cat.emoji} {cat.name}
            </button>
          ))}
        </div>
      )}

      {/* Services by Category */}
      {Object.entries(servicesByCategory).map(([category, categoryServices], catIndex) => (
        <motion.div
          key={category}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: catIndex * 0.1 }}
        >
          <h2 className="text-lg font-semibold text-tg-text mb-3 capitalize">
            {categories.find(c => c.id === category)?.name || category}
          </h2>
          
          <div className="space-y-3">
            {categoryServices.map((service, index) => (
              <motion.div
                key={service.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: catIndex * 0.1 + index * 0.05 }}
              >
                <ServiceCard
                  emoji={platform.emoji}
                  name={service.name}
                  description={service.description}
                  price={formatPrice(service.price_per_1000)}
                  color={color}
                  onClick={() => {
                    hapticFeedback.selection()
                    navigate(`/order/${service.id}`)
                  }}
                />
              </motion.div>
            ))}
          </div>
        </motion.div>
      ))}
    </div>
  )
}
