import { Users, UserCheck, UserMinus, Clock } from 'lucide-react'
import { Badge } from './badge'
import { cn } from '#/lib/utils'
import type { Employee } from './employee-table'

interface ProviderStatus {
    atlas: string
    beacon: string
    cobalt: string
}

interface MetricsCardsProps {
    employees: Employee[]
    providers: ProviderStatus
    partial: boolean
}

function StatCard({
    label,
    value,
    icon: Icon,
    className,
    }: {
    label: string
    value: number
    icon: React.ElementType
    className?: string
    }) {
    return (
        <div className="bg-white rounded-lg border border-gray-200 p-5 flex items-center gap-4">
        <div className={cn('p-2 rounded-lg', className)}>
            <Icon className="w-5 h-5" />
        </div>
        <div>
            <p className="text-2xl font-semibold text-gray-900">{value.toLocaleString()}</p>
            <p className="text-sm text-gray-500">{label}</p>
        </div>
        </div>
    )
}

export function MetricsCards({ employees, providers, partial }: MetricsCardsProps) {
    const active = employees.filter(e => e.status === 'active').length
    const onLeave = employees.filter(e => e.status === 'on_leave').length
    const inactive = employees.filter(e => e.status === 'inactive').length

    return (
        <div className="space-y-4">
        {/* Provider status bar */}
        {partial && (
            <div className="flex items-center gap-2 bg-yellow-50 border border-yellow-200 rounded-lg px-4 py-3 text-sm text-yellow-800">
            <Clock className="w-4 h-4 shrink-0" />
            <span>Partial data — one or more providers are unavailable. Showing available results.</span>
            </div>
        )}

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <StatCard
            label="Total employees"
            value={employees.length}
            icon={Users}
            className="bg-blue-50 text-blue-600"
            />
            <StatCard
            label="Active"
            value={active}
            icon={UserCheck}
            className="bg-green-50 text-green-600"
            />
            <StatCard
            label="On leave"
            value={onLeave}
            icon={Clock}
            className="bg-yellow-50 text-yellow-600"
            />
            <StatCard
            label="Inactive"
            value={inactive}
            icon={UserMinus}
            className="bg-red-50 text-red-600"
            />
        </div>

        {/* Provider status indicators */}
        <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs text-gray-500 font-medium">Providers:</span>
            {Object.entries(providers).map(([name, status]) => (
            <Badge key={name} variant={status as 'ok' | 'error'}>
                {name} — {status}
            </Badge>
            ))}
        </div>
        </div>
    )
}