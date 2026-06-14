import { cn } from '#/lib/utils'

interface BadgeProps {
    variant?: 'active' | 'on_leave' | 'inactive' | 'ok' | 'error'
    children: React.ReactNode
    className?: string
}

export function Badge({ variant = 'active', children, className }: BadgeProps) {
    return (
    <span
        className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        {
            'bg-green-100 text-green-800': variant === 'active' || variant === 'ok',
            'bg-yellow-100 text-yellow-800': variant === 'on_leave',
            'bg-red-100 text-red-800': variant === 'inactive' || variant === 'error',
        },
        className
        )}
    >
        {children}
    </span>
    )
}