// Platform SVG Icons - Original brand icons

export const TelegramIcon = ({ size = 24, className = '' }: { size?: number; className?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0z" fill="#0088CC"/>
    <path d="M17.562 7.2l-2.08 10.493c-.153.692-.574.865-1.163.54l-3.213-2.37-1.55 1.493c-.172.171-.315.315-.646.315l.23-3.285 5.97-5.391c.26-.23-.057-.358-.402-.128l-7.38 4.647-3.176-1c-.69-.217-.703-.69.145-1.024l12.415-4.78c.576-.208 1.08.141.85 1.49z" fill="#fff"/>
  </svg>
)

export const InstagramIcon = ({ size = 24, className = '' }: { size?: number; className?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <defs>
      <linearGradient id="instagram-gradient" x1="0%" y1="100%" x2="100%" y2="0%">
        <stop offset="0%" stopColor="#FFDC80"/>
        <stop offset="25%" stopColor="#FCAF45"/>
        <stop offset="50%" stopColor="#F77737"/>
        <stop offset="75%" stopColor="#F56040"/>
        <stop offset="100%" stopColor="#C13584"/>
      </linearGradient>
      <linearGradient id="instagram-gradient-2" x1="0%" y1="100%" x2="100%" y2="0%">
        <stop offset="0%" stopColor="#FFDC80"/>
        <stop offset="50%" stopColor="#E1306C"/>
        <stop offset="100%" stopColor="#833AB4"/>
      </linearGradient>
    </defs>
    <rect width="24" height="24" rx="6" fill="url(#instagram-gradient-2)"/>
    <circle cx="12" cy="12" r="4" stroke="#fff" strokeWidth="2" fill="none"/>
    <circle cx="17.5" cy="6.5" r="1.5" fill="#fff"/>
  </svg>
)

export const YouTubeIcon = ({ size = 24, className = '' }: { size?: number; className?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814z" fill="#FF0000"/>
    <path d="M9.545 15.568V8.432L15.818 12l-6.273 3.568z" fill="#fff"/>
  </svg>
)

export const TikTokIcon = ({ size = 24, className = '' }: { size?: number; className?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <rect width="24" height="24" rx="6" fill="#000"/>
    <path d="M17.067 9.53v2.594a5.55 5.55 0 0 1-3.243-1.034v4.706a4.298 4.298 0 0 1-4.296 4.297 4.255 4.255 0 0 1-2.526-.824 4.298 4.298 0 0 0 7.122-3.233v-4.706c.932.715 2.087 1.134 3.243 1.034V9.53a3.85 3.85 0 0 1-.3-.049z" fill="#25F4EE"/>
    <path d="M16.767 9.481v2.594a5.55 5.55 0 0 1-3.243-1.034v4.706a4.298 4.298 0 0 1-7.122 3.233 4.298 4.298 0 0 0 7.822-2.449v-4.706a5.55 5.55 0 0 0 3.243 1.034V9.53c-.239.008-.474-.007-.7-.049z" fill="#FE2C55"/>
    <path d="M13.524 15.796v-4.706a5.55 5.55 0 0 0 3.243 1.034V9.53a3.554 3.554 0 0 1-1.943-1.37 3.554 3.554 0 0 1-1.3-2.553H11.08v10.147a2.297 2.297 0 0 1-4.078 1.456 2.297 2.297 0 0 1 2.526-3.717v-2.646a4.298 4.298 0 0 0-3.526 6.43 4.298 4.298 0 0 0 7.522-3.481z" fill="#fff"/>
  </svg>
)

export const FacebookIcon = ({ size = 24, className = '' }: { size?: number; className?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <circle cx="12" cy="12" r="12" fill="#1877F2"/>
    <path d="M16.671 15.469l.524-3.418h-3.282v-2.219c0-.935.458-1.847 1.927-1.847h1.492V5.035s-1.354-.231-2.65-.231c-2.703 0-4.47 1.638-4.47 4.604v2.605H7.078v3.418h3.134v8.267a12.39 12.39 0 003.858 0v-8.229h2.601z" fill="#fff"/>
  </svg>
)

export const TwitterIcon = ({ size = 24, className = '' }: { size?: number; className?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <rect width="24" height="24" rx="6" fill="#000"/>
    <path d="M13.323 10.775L18.542 5h-1.236l-4.532 5.015L9.13 5H5l5.476 7.584L5 18.25h1.237l4.787-5.298 3.846 5.298H19l-5.677-7.475zm-1.695 1.875l-.555-.755-4.417-6.01h1.902l3.564 4.851.555.756 4.632 6.303h-1.901l-3.78-5.145z" fill="#fff"/>
  </svg>
)

export const SpotifyIcon = ({ size = 24, className = '' }: { size?: number; className?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <circle cx="12" cy="12" r="12" fill="#1DB954"/>
    <path d="M16.94 16.15a.75.75 0 0 1-1.03.25c-2.82-1.72-6.37-2.11-10.55-1.16a.75.75 0 1 1-.34-1.46c4.58-1.05 8.5-.6 11.67 1.34.36.22.47.68.25 1.03zm1.25-2.75a.94.94 0 0 1-1.29.31c-3.23-1.98-8.15-2.56-11.96-1.4a.94.94 0 1 1-.54-1.8c4.35-1.32 9.77-.68 13.48 1.6.44.27.58.85.31 1.29zm.11-2.87c-3.88-2.3-10.27-2.52-13.97-1.39a1.12 1.12 0 1 1-.65-2.15c4.23-1.29 11.26-1.04 15.7 1.61a1.12 1.12 0 0 1-1.08 1.93z" fill="#fff"/>
  </svg>
)

export const DiscordIcon = ({ size = 24, className = '' }: { size?: number; className?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <rect width="24" height="24" rx="6" fill="#5865F2"/>
    <path d="M18.59 6.28a14.27 14.27 0 0 0-3.52-1.09.05.05 0 0 0-.06.03c-.15.27-.32.62-.44.9a13.18 13.18 0 0 0-3.95 0 9.1 9.1 0 0 0-.45-.9.05.05 0 0 0-.06-.03 14.23 14.23 0 0 0-3.52 1.09.05.05 0 0 0-.02.02c-2.24 3.35-2.86 6.61-2.56 9.83a.06.06 0 0 0 .02.04 14.37 14.37 0 0 0 4.33 2.19.05.05 0 0 0 .06-.02c.33-.45.63-.93.89-1.43a.05.05 0 0 0-.03-.07 9.47 9.47 0 0 1-1.35-.65.05.05 0 0 1 0-.09c.09-.07.18-.14.27-.21a.05.05 0 0 1 .05 0c2.83 1.29 5.89 1.29 8.68 0a.05.05 0 0 1 .05 0c.09.07.18.14.27.21a.05.05 0 0 1 0 .09c-.43.25-.88.47-1.35.65a.05.05 0 0 0-.03.07c.26.5.56.98.89 1.43a.05.05 0 0 0 .06.02 14.33 14.33 0 0 0 4.34-2.19.05.05 0 0 0 .02-.04c.36-3.71-.6-6.93-2.54-9.79a.04.04 0 0 0-.02-.03zM9.24 14.08c-.85 0-1.55-.78-1.55-1.74s.69-1.74 1.55-1.74c.87 0 1.57.79 1.55 1.74 0 .96-.69 1.74-1.55 1.74zm5.73 0c-.85 0-1.55-.78-1.55-1.74s.69-1.74 1.55-1.74c.87 0 1.57.79 1.55 1.74 0 .96-.68 1.74-1.55 1.74z" fill="#fff"/>
  </svg>
)

export const ThreadsIcon = ({ size = 24, className = '' }: { size?: number; className?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <rect width="24" height="24" rx="6" fill="#000"/>
    <path d="M16.14 11.37c-.08-.04-.16-.07-.24-.1a5.76 5.76 0 0 0-.12-1.23c-.33-1.45-1.24-2.5-2.64-3.02a5.3 5.3 0 0 0-2.74-.15c-1.23.27-2.19.97-2.82 2.03a4.9 4.9 0 0 0-.63 2.8c.08 1.33.62 2.44 1.62 3.3.83.71 1.82 1.1 2.93 1.1.33 0 .66-.03 1-.1 1.23-.27 2.19-.97 2.82-2.03.26-.43.44-.9.54-1.4.08.04.16.07.24.1.66.29 1.07.74 1.22 1.35.24.98-.08 2.12-1.13 2.8-.86.57-1.86.8-2.93.72-1.4-.1-2.56-.66-3.44-1.68-.86-.99-1.26-2.18-1.2-3.54.07-1.37.56-2.55 1.48-3.52.96-1.01 2.13-1.54 3.5-1.59 1.16-.04 2.2.31 3.12 1.05.4.32.73.7 1 1.13l1.24-.87A5.99 5.99 0 0 0 17.1 5.8c-1.18-.74-2.49-1.04-3.91-.9-1.75.18-3.23.94-4.4 2.27-1.1 1.25-1.63 2.73-1.59 4.43.04 1.65.58 3.08 1.63 4.28 1.13 1.29 2.58 2.02 4.35 2.15.27.02.54.03.8.03 1.26 0 2.43-.32 3.48-.98 1.57-1 2.2-2.63 1.9-4.33-.24-1.38-1.11-2.38-2.22-3.38zm-2.05.18c.62.27 1.03.68 1.22 1.23.24.68.07 1.46-.45 1.98-.41.4-.93.6-1.53.6-.17 0-.35-.02-.53-.05-.8-.18-1.36-.72-1.6-1.53-.2-.68-.04-1.39.43-1.92.45-.5 1.07-.77 1.81-.7.24.03.46.12.65.39z" fill="#fff"/>
  </svg>
)

// SMS / Virtual Numbers icon
export const SMSIcon = ({ size = 24, className = '' }: { size?: number; className?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <rect width="24" height="24" rx="6" fill="#4CAF50"/>
    <path d="M17 3H7C5.9 3 5 3.9 5 5V17L9 13H17C18.1 13 19 12.1 19 11V5C19 3.9 18.1 3 17 3ZM17 11H8.17L7 12.17V5H17V11Z" fill="#fff"/>
    <circle cx="9" cy="8" r="1" fill="#fff"/>
    <circle cx="12" cy="8" r="1" fill="#fff"/>
    <circle cx="15" cy="8" r="1" fill="#fff"/>
  </svg>
)

// Platform icon mapping
export const PlatformIconMap: Record<string, React.ComponentType<{ size?: number; className?: string }>> = {
  telegram: TelegramIcon,
  instagram: InstagramIcon,
  youtube: YouTubeIcon,
  tiktok: TikTokIcon,
  facebook: FacebookIcon,
  twitter: TwitterIcon,
  x: TwitterIcon,
  spotify: SpotifyIcon,
  discord: DiscordIcon,
  threads: ThreadsIcon,
  sms: SMSIcon,
  'virtual-numbers': SMSIcon,
}

// Get platform icon by ID
export const getPlatformIcon = (platformId: string) => {
  return PlatformIconMap[platformId.toLowerCase()] || null
}
