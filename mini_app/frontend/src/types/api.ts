// API Response Types

export interface User {
  user_id: number
  username?: string
  full_name?: string
  balance: number
  referral_count: number
  referral_earnings: number
  is_banned: boolean
  created_at?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: {
    user_id: number
    username?: string
    full_name?: string
    balance: number
    is_premium?: boolean
  }
}

export interface Platform {
  id: string
  name: string
  emoji: string
  color: string
}

export interface ServiceCategory {
  id: string
  name: string
  emoji: string
  services_count: number
}

export interface Service {
  id: string
  name: string
  description: string
  price_per_1000: number
  min_quantity: number
  max_quantity: number
  guarantee: string
  speed: string
  panel: string
  panel_service_id?: number
  category: string
  platform: string
}

export interface Order {
  id: number
  service_type: string
  service_name?: string
  link: string
  quantity: number
  price: number
  status: string
  created_at: string
  api_order_id?: number
  panel_name?: string
}

export interface Payment {
  id: number
  amount: number
  method: string
  status: string
  created_at: string
  card_number?: string
  card_holder?: string
}

export interface PaymentMethod {
  id: string
  name: string
  card_number: string
  card_holder: string
  min_amount: number
}

export interface ReferralStats {
  referral_count: number
  referral_earnings: number
  referral_link: string
  referrals: ReferralUser[]
}

export interface ReferralUser {
  user_id: number
  username?: string
  full_name?: string
  created_at: string
}

export interface SMSPlatform {
  code: string
  name: string
  emoji: string
}

export interface SMSCountry {
  code: string
  name: string
  flag: string
}

export interface SMSPrice {
  provider: string
  provider_name: string
  price_rub: number
  price_uzs: number
  available: number
}

export interface SMSOrder {
  success: boolean
  order_id: string
  phone_number: string
  provider: string
  platform: string
  country: string
  price: number
  status: string
  code?: string
}

export interface PremiumPlan {
  months: number
  price: number
  original_price?: number
  discount_percent?: number
  popular?: boolean
  best_value?: boolean
  features: string[]
}

export interface PremiumStatus {
  is_premium: boolean
  plan_type?: string
  start_date?: string
  end_date?: string
  days_left?: number
}

export interface Settings {
  usd_rate: number
  rub_rate: number
  min_deposit: number
  referral_bonus: number
}
