// Mock data for development/demo mode

export const mockPlatforms = [
  { id: 'telegram', name: 'Telegram', emoji: '📱', color: '#0088cc' },
  { id: 'instagram', name: 'Instagram', emoji: '📸', color: '#E1306C' },
  { id: 'youtube', name: 'YouTube', emoji: '📺', color: '#FF0000' },
  { id: 'tiktok', name: 'TikTok', emoji: '🎵', color: '#000000' },
]

export const mockCategories: Record<string, any[]> = {
  telegram: [
    { id: 'members', name: "A'zolar", emoji: '👥', services_count: 15 },
    { id: 'views', name: "Ko'rishlar", emoji: '👁', services_count: 20 },
    { id: 'reactions', name: 'Reaksiyalar', emoji: '❤️', services_count: 10 },
  ],
  instagram: [
    { id: 'followers', name: 'Obunachilar', emoji: '👥', services_count: 25 },
    { id: 'likes', name: 'Layklar', emoji: '❤️', services_count: 18 },
    { id: 'views', name: "Ko'rishlar", emoji: '👁', services_count: 12 },
    { id: 'comments', name: 'Izohlar', emoji: '💬', services_count: 8 },
  ],
  youtube: [
    { id: 'subscribers', name: 'Obunachilar', emoji: '👥', services_count: 10 },
    { id: 'views', name: "Ko'rishlar", emoji: '👁', services_count: 15 },
    { id: 'likes', name: 'Layklar', emoji: '👍', services_count: 8 },
  ],
  tiktok: [
    { id: 'followers', name: 'Obunachilar', emoji: '👥', services_count: 12 },
    { id: 'likes', name: 'Layklar', emoji: '❤️', services_count: 10 },
    { id: 'views', name: "Ko'rishlar", emoji: '👁', services_count: 14 },
  ],
}

export const mockServices: Record<string, any[]> = {
  'telegram-members': [
    { id: '1', name: "Telegram a'zolar - Real", description: "Haqiqiy foydalanuvchilar", price_per_1000: 15000, min_quantity: 100, max_quantity: 100000, guarantee: "30 kun", speed: "10K/kun", panel: "Panel 1", category: 'members', platform: 'telegram' },
    { id: '2', name: "Telegram a'zolar - Premium", description: "Premium sifat", price_per_1000: 25000, min_quantity: 50, max_quantity: 50000, guarantee: "60 kun", speed: "5K/kun", panel: "Panel 2", category: 'members', platform: 'telegram' },
  ],
  'telegram-views': [
    { id: '3', name: "Telegram ko'rishlar - Tez", description: "Tezkor yetkazish", price_per_1000: 5000, min_quantity: 100, max_quantity: 1000000, guarantee: "Yo'q", speed: "100K/kun", panel: "Panel 1", category: 'views', platform: 'telegram' },
    { id: '4', name: "Telegram ko'rishlar - Real", description: "Haqiqiy ko'rishlar", price_per_1000: 8000, min_quantity: 100, max_quantity: 500000, guarantee: "Yo'q", speed: "50K/kun", panel: "Panel 1", category: 'views', platform: 'telegram' },
  ],
  'telegram-reactions': [
    { id: '5', name: "Telegram reaksiyalar - Mix", description: "Turli reaksiyalar", price_per_1000: 10000, min_quantity: 50, max_quantity: 100000, guarantee: "Yo'q", speed: "20K/kun", panel: "Panel 1", category: 'reactions', platform: 'telegram' },
  ],
  'instagram-followers': [
    { id: '6', name: 'Instagram obunachilar - Mix', description: "Aralash obunachilar", price_per_1000: 20000, min_quantity: 100, max_quantity: 100000, guarantee: "30 kun", speed: "10K/kun", panel: "Panel 1", category: 'followers', platform: 'instagram' },
    { id: '7', name: 'Instagram obunachilar - Real', description: "Haqiqiy obunachilar", price_per_1000: 35000, min_quantity: 50, max_quantity: 50000, guarantee: "60 kun", speed: "5K/kun", panel: "Panel 2", category: 'followers', platform: 'instagram' },
  ],
  'instagram-likes': [
    { id: '8', name: 'Instagram layklar - Tez', description: "Tezkor layklar", price_per_1000: 8000, min_quantity: 50, max_quantity: 50000, guarantee: "Yo'q", speed: "50K/kun", panel: "Panel 1", category: 'likes', platform: 'instagram' },
  ],
  'instagram-views': [
    { id: '9', name: "Instagram ko'rishlar", description: "Video ko'rishlar", price_per_1000: 3000, min_quantity: 100, max_quantity: 1000000, guarantee: "Yo'q", speed: "100K/kun", panel: "Panel 1", category: 'views', platform: 'instagram' },
  ],
  'instagram-comments': [
    { id: '10', name: 'Instagram izohlar', description: "Custom izohlar", price_per_1000: 50000, min_quantity: 10, max_quantity: 10000, guarantee: "Yo'q", speed: "1K/kun", panel: "Panel 1", category: 'comments', platform: 'instagram' },
  ],
  'youtube-subscribers': [
    { id: '11', name: 'YouTube obunachilar', description: "Kanal obunachilar", price_per_1000: 50000, min_quantity: 100, max_quantity: 10000, guarantee: "30 kun", speed: "1K/kun", panel: "Panel 1", category: 'subscribers', platform: 'youtube' },
  ],
  'youtube-views': [
    { id: '12', name: "YouTube ko'rishlar", description: "Video ko'rishlar", price_per_1000: 15000, min_quantity: 1000, max_quantity: 1000000, guarantee: "Yo'q", speed: "50K/kun", panel: "Panel 1", category: 'views', platform: 'youtube' },
  ],
  'youtube-likes': [
    { id: '13', name: 'YouTube layklar', description: "Video layklar", price_per_1000: 20000, min_quantity: 50, max_quantity: 50000, guarantee: "30 kun", speed: "5K/kun", panel: "Panel 1", category: 'likes', platform: 'youtube' },
  ],
  'tiktok-followers': [
    { id: '14', name: 'TikTok obunachilar', description: "Profil obunachilar", price_per_1000: 18000, min_quantity: 100, max_quantity: 100000, guarantee: "30 kun", speed: "10K/kun", panel: "Panel 1", category: 'followers', platform: 'tiktok' },
  ],
  'tiktok-likes': [
    { id: '15', name: 'TikTok layklar', description: "Video layklar", price_per_1000: 6000, min_quantity: 100, max_quantity: 100000, guarantee: "Yo'q", speed: "50K/kun", panel: "Panel 1", category: 'likes', platform: 'tiktok' },
  ],
  'tiktok-views': [
    { id: '16', name: "TikTok ko'rishlar", description: "Video ko'rishlar", price_per_1000: 2000, min_quantity: 1000, max_quantity: 10000000, guarantee: "Yo'q", speed: "1M/kun", panel: "Panel 1", category: 'views', platform: 'tiktok' },
  ],
}

export const mockUser = {
  user_id: 123456789,
  username: 'demo_user',
  full_name: 'Demo User',
  balance: 50000,
  referral_count: 5,
  referral_earnings: 10000,
  is_banned: false,
  created_at: new Date().toISOString()
}

export const mockOrders = [
  {
    id: 1001,
    service_type: 'smm',
    service_name: "Telegram a'zolar - Real",
    quantity: 1000,
    price: 15000,
    status: 'completed',
    link: 'https://t.me/example',
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: 1002,
    service_type: 'smm',
    service_name: 'Instagram layklar - Tez',
    quantity: 500,
    price: 4000,
    status: 'processing',
    link: 'https://instagram.com/p/example',
    created_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: 1003,
    service_type: 'smm',
    service_name: "YouTube ko'rishlar",
    quantity: 10000,
    price: 150000,
    status: 'pending',
    link: 'https://youtube.com/watch?v=example',
    created_at: new Date().toISOString(),
  }
]

export const mockReferralStats = {
  referral_count: 15,
  referral_earnings: 25000,
  referral_link: 'https://t.me/SmmXizmatlari_bot?start=ABC123',
  referrals: []
}

export const mockPayments = [
  {
    id: 1,
    amount: 50000,
    method: 'payme',
    status: 'completed',
    created_at: new Date(Date.now() - 172800000).toISOString(),
  },
  {
    id: 2,
    amount: 100000,
    method: 'click',
    status: 'completed', 
    created_at: new Date(Date.now() - 86400000).toISOString(),
  }
]

export const mockSMSPlatforms = [
  { code: 'tg', name: 'Telegram', emoji: '📱' },
  { code: 'wa', name: 'WhatsApp', emoji: '📲' },
  { code: 'ig', name: 'Instagram', emoji: '📸' },
  { code: 'go', name: 'Google', emoji: '🔍' },
]

export const mockSMSCountries = [
  { code: 'ru', name: 'Rossiya', flag: '🇷🇺' },
  { code: 'uz', name: "O'zbekiston", flag: '🇺🇿' },
  { code: 'kz', name: "Qozog'iston", flag: '🇰🇿' },
  { code: 'ua', name: 'Ukraina', flag: '🇺🇦' },
]

