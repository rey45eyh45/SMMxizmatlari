interface CardProps {
  children: React.ReactNode
  className?: string
  onClick?: () => void
}

export default function Card({ children, className = '', onClick }: CardProps) {
  return (
    <div 
      onClick={onClick}
      className={`
        bg-tg-secondary-bg rounded-2xl p-4
        ${onClick ? 'cursor-pointer active:opacity-80 transition-opacity' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  )
}
