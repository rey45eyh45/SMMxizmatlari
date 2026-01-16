interface InputProps {
  label?: string
  placeholder?: string
  value: string | number
  onChange: (value: string) => void
  type?: 'text' | 'number' | 'url' | 'tel'
  error?: string
  hint?: string
  disabled?: boolean
  min?: number
  max?: number
  prefix?: string
  suffix?: string
  className?: string
}

export default function Input({
  label,
  placeholder,
  value,
  onChange,
  type = 'text',
  error,
  hint,
  disabled = false,
  min,
  max,
  prefix,
  suffix,
  className = ''
}: InputProps) {
  return (
    <div className={`space-y-1.5 ${className}`}>
      {label && (
        <label className="block text-sm font-medium text-tg-text">
          {label}
        </label>
      )}
      
      <div className="relative">
        {prefix && (
          <span className="absolute left-4 top-1/2 -translate-y-1/2 text-tg-hint">
            {prefix}
          </span>
        )}
        
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
          min={min}
          max={max}
          className={`
            w-full px-4 py-3 rounded-xl bg-tg-secondary-bg text-tg-text
            placeholder:text-tg-hint focus:outline-none focus:ring-2
            focus:ring-tg-button/50 transition-all
            disabled:opacity-50 disabled:cursor-not-allowed
            ${prefix ? 'pl-10' : ''}
            ${suffix ? 'pr-16' : ''}
            ${error ? 'ring-2 ring-red-500' : ''}
          `}
        />
        
        {suffix && (
          <span className="absolute right-4 top-1/2 -translate-y-1/2 text-tg-hint text-sm">
            {suffix}
          </span>
        )}
      </div>
      
      {error && (
        <p className="text-sm text-red-500">{error}</p>
      )}
      
      {hint && !error && (
        <p className="text-sm text-tg-hint">{hint}</p>
      )}
    </div>
  )
}
