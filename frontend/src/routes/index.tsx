import { createFileRoute } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { EmployeeTable, type Employee } from '#/components/ui/employee-table'
import { MetricsCards } from '#/components/ui/metrics-cards'
import { Search } from 'lucide-react'

const PROXY_URL = 'http://localhost:8000'

interface EmployeeResponse {
  data: Employee[]
  meta: {
    providers: { atlas: string; beacon: string; cobalt: string }
    partial: boolean
    total: number
    page: number
    page_size: number
    pages: number
  }
}

export const Route = createFileRoute('/')({ component: EmployeeDashboard })

function EmployeeDashboard() {
  const [response, setResponse] = useState<EmployeeResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')

  useEffect(() => {
    async function fetchEmployees() {
      try {
        setIsLoading(true)
        const res = await fetch(`${PROXY_URL}/employees?page=1&page_size=1200`)
        if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`)
        const data: EmployeeResponse = await res.json()
        setResponse(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setIsLoading(false)
      }
    }
    fetchEmployees()
  }, [])

  const filtered = response?.data.filter(emp => {
    if (!search) return true
    const q = search.toLowerCase()
    const fullName = `${emp.first_name} ${emp.last_name}`.toLowerCase()
    return (
      fullName.includes(q) ||
      emp.email.toLowerCase().includes(q) ||
      emp.department.toLowerCase().includes(q) ||
      emp.job_title.toLowerCase().includes(q)
    )
  }) ?? []

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">

        {/* Header */}
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Employee Directory</h1>
          <p className="text-sm text-gray-500 mt-1">
            Employee data aggregated from HR providers: Atlas, Beacon and Cobalt
          </p>
        </div>

        {/* Error state */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-800">
            Could not load employee data: {error}
          </div>
        )}

        {/* Metrics */}
        {response && (
          <MetricsCards
            employees={filtered}
            providers={response.meta.providers}
            partial={response.meta.partial}
          />
        )}

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search by name, email, department or role..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Table */}
        <EmployeeTable data={filtered} isLoading={isLoading} />

      </div>
    </div>
  )
}