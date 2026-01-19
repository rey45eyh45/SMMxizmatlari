/**
 * Click to'lov tizimi SVG ikonkasi
 * Rasmiy Click logosi
 */

interface ClickIconProps {
  size?: number
  className?: string
}

export function ClickIcon({ size = 32, className = '' }: ClickIconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Click logo - ko'k va oq rangda */}
      <rect width="48" height="48" rx="12" fill="#00AEEF" />
      <path
        d="M13 24C13 18.477 17.477 14 23 14H25C30.523 14 35 18.477 35 24C35 29.523 30.523 34 25 34H23C17.477 34 13 29.523 13 24Z"
        fill="white"
      />
      <path
        d="M23.5 19C20.462 19 18 21.462 18 24.5C18 27.538 20.462 30 23.5 30C25.898 30 27.943 28.41 28.707 26.25H25.5C25.033 26.708 24.395 27 23.688 27C22.308 27 21.188 25.88 21.188 24.5C21.188 23.12 22.308 22 23.688 22C24.395 22 25.033 22.292 25.5 22.75H28.707C27.943 20.59 25.898 19 23.5 19Z"
        fill="#00AEEF"
      />
      <circle cx="31" cy="24" r="2.5" fill="#00AEEF" />
    </svg>
  )
}

/**
 * Click logo - faqat yozuv
 */
export function ClickLogo({ size = 80, className = '' }: ClickIconProps) {
  return (
    <svg
      width={size}
      height={size * 0.4}
      viewBox="0 0 200 80"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* CLICK yozuvi */}
      <text
        x="50%"
        y="55"
        textAnchor="middle"
        fill="#00AEEF"
        fontSize="48"
        fontWeight="bold"
        fontFamily="Arial, sans-serif"
      >
        CLICK
      </text>
    </svg>
  )
}

/**
 * Payme ikonkasi
 */
export function PaymeIcon({ size = 32, className = '' }: ClickIconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <rect width="48" height="48" rx="12" fill="#00CCCC" />
      <path
        d="M10 28V20H13.5C15.433 20 17 21.567 17 23.5V24.5C17 26.433 15.433 28 13.5 28H10ZM12.5 22V26H13.5C14.328 26 15 25.328 15 24.5V23.5C15 22.672 14.328 22 13.5 22H12.5Z"
        fill="white"
      />
      <path
        d="M19 28V20H22C23.657 20 25 21.343 25 23C25 24.657 23.657 26 22 26H21.5V28H19ZM21.5 22V24H22C22.552 24 23 23.552 23 23C23 22.448 22.552 22 22 22H21.5Z"
        fill="white"
      />
      <path
        d="M27 28V22H25V20H31V22H29V28H27Z"
        fill="white"
      />
      <circle cx="35" cy="24" r="4" stroke="white" strokeWidth="2" fill="none" />
    </svg>
  )
}

/**
 * Uzum Bank ikonkasi
 */
export function UzumIcon({ size = 32, className = '' }: ClickIconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <rect width="48" height="48" rx="12" fill="#7B2D8E" />
      <path
        d="M24 14C18.477 14 14 18.477 14 24C14 29.523 18.477 34 24 34C29.523 34 34 29.523 34 24C34 18.477 29.523 14 24 14ZM24 30C20.686 30 18 27.314 18 24C18 20.686 20.686 18 24 18C27.314 18 30 20.686 30 24C30 27.314 27.314 30 24 30Z"
        fill="white"
      />
      <circle cx="24" cy="24" r="3" fill="white" />
    </svg>
  )
}

export default ClickIcon
