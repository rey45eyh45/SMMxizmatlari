import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft } from 'lucide-react'
import { ServiceCard } from '../components'
import { useTelegram } from '../hooks/useTelegram'
import { mockPlatforms, mockCategories, mockServices } from '../lib/mockData'

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

  const platform = mockPlatforms.find(p => p.id === platformId)
  const categories = mockCategories[platformId || ''] || []
  const color = platformColors[platformId!] || '#0088cc'

  if (!platform) {
    return (
      <div className="text-center py-10">
        <p className="text-tg-hint">Platforma topilmadi</p>
      </div>
    )
  }

  const formatPrice = (price: number) => {
    return `${price.toLocaleString()} so'm / 1000`
  }

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-tg-link"
      >
        <ArrowLeft size={20} />
        <span>Orqaga</span>
      </button>

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
          <p className="text-tg-hint">{categories.length} ta kategoriya</p>
        </div>
      </div>

      {/* Categories with Services */}
      {categories.map((category, catIndex) => {
        const categoryServices = mockServices[`${platformId}-${category.id}`] || []
        
        return (
          <motion.div
            key={category.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: catIndex * 0.1 }}
          >
            <h2 className="text-lg font-semibold text-tg-text mb-3">
              {category.emoji} {category.name}
            </h2>
            
            <div className="space-y-3">
              {categoryServices.length > 0 ? (
                categoryServices.map((service, index) => (
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
                        hapticFeedback?.selection?.()
                        navigate(`/order/${service.id}`)
                      }}
                    />
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-4 bg-tg-secondary-bg rounded-xl">
                  <p className="text-tg-hint">Xizmatlar mavjud emas</p>
                </div>
              )}
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}
