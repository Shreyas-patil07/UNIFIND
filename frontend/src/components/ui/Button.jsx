import { cn } from '../../utils/cn'

const buttonVariants = {
  default: 'bg-primary text-white hover:bg-primary-hover',
  outline: 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50',
  ghost: 'hover:bg-slate-100 text-slate-700',
}

const buttonSizes = {
  default: 'px-6 py-3',
  sm: 'px-4 py-2 text-sm',
  lg: 'px-8 py-4 text-lg',
}

export function Button({
  children,
  className,
  variant = 'default',
  size = 'default',
  disabled,
  ...props
}) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center rounded-xl font-medium transition-all duration-200 active:scale-95 disabled:opacity-60 disabled:cursor-not-allowed',
        buttonVariants[variant],
        buttonSizes[size],
        className
      )}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  )
}
