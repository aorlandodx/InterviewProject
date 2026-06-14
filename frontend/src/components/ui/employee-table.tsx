import {
    useReactTable,
    getCoreRowModel,
    getPaginationRowModel,
    getSortedRowModel,
    flexRender,
    type ColumnDef,
    type SortingState,
} from '@tanstack/react-table'
import { useState } from 'react'
import { ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react'
import { Badge } from './badge'
import { cn } from '#/lib/utils'

export interface Employee {
    id: string
    first_name: string
    last_name: string
    email: string
    job_title: string
    department: string
    status: 'active' | 'on_leave' | 'inactive'
    annual_salary: number
    currency: string
    hire_date: string
    source: string
    source_ids: {
        atlas?: string
        beacon?: number
        cobalt?: string
    }
}

const statusLabel: Record<string, string> = {
    active: 'Active',
    on_leave: 'On leave',
    inactive: 'Inactive',
}

const sourceColors: Record<string, string> = {
    atlas: 'bg-blue-100 text-blue-700',
    beacon: 'bg-purple-100 text-purple-700',
    cobalt: 'bg-teal-100 text-teal-700',
    merged: 'bg-gray-100 text-gray-700',
}

const columns: ColumnDef<Employee>[] = [
    {
        accessorKey: 'first_name',
        header: 'Name',
        cell: ({ row }) => (
        <div>
            <p className="font-medium text-gray-900">
            {row.original.first_name} {row.original.last_name}
            </p>
            <p className="text-xs text-gray-500">{row.original.email}</p>
        </div>
        ),
    },
    {
        accessorKey: 'department',
        header: 'Department',
    },
    {
        accessorKey: 'job_title',
        header: 'Role',
    },
    {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ getValue }) => {
        const status = getValue<string>()
        return (
            <Badge variant={status as 'active' | 'on_leave' | 'inactive'}>
            {statusLabel[status] ?? status}
            </Badge>
        )
        },
    },
    {
        accessorKey: 'source',
        header: 'Source',
        cell: ({ getValue }) => {
        const source = getValue<string>()
        return (
            <span
            className={cn(
                'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
                sourceColors[source] ?? sourceColors.merged
            )}
            >
            {source}
            </span>
        )
        },
    },
]

interface EmployeeTableProps {
    data: Employee[]
    isLoading?: boolean
}

export function EmployeeTable({ data, isLoading }: EmployeeTableProps) {
    const [sorting, setSorting] = useState<SortingState>([])

    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        getSortedRowModel: getSortedRowModel(),
        onSortingChange: setSorting,
        state: { sorting },
        initialState: { pagination: { pageSize: 20 } },
    })

    if (isLoading) {
        return (
        <div className="flex items-center justify-center h-64 text-gray-400">
            Loading employees...
        </div>
        )
    }

    return (
        <div className="space-y-4">
        <div className="rounded-lg border border-gray-200 overflow-hidden">
            <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
                {table.getHeaderGroups().map(headerGroup => (
                <tr key={headerGroup.id}>
                    {headerGroup.headers.map(header => (
                    <th
                        key={header.id}
                        className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer select-none"
                        onClick={header.column.getToggleSortingHandler()}
                    >
                        <div className="flex items-center gap-1">
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {header.column.getCanSort() && (
                            <span className="text-gray-400">
                            {header.column.getIsSorted() === 'asc' ? (
                                <ChevronUp className="w-3 h-3" />
                            ) : header.column.getIsSorted() === 'desc' ? (
                                <ChevronDown className="w-3 h-3" />
                            ) : (
                                <ChevronsUpDown className="w-3 h-3" />
                            )}
                            </span>
                        )}
                        </div>
                    </th>
                    ))}
                </tr>
                ))}
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white">
                {table.getRowModel().rows.map(row => (
                <tr
                    key={row.id}
                    className="hover:bg-gray-50 transition-colors"
                >
                    {row.getVisibleCells().map(cell => (
                    <td key={cell.id} className="px-4 py-3 text-gray-700">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                    ))}
                </tr>
                ))}
            </tbody>
            </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between text-sm text-gray-500">
            <span>
            Showing {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1}–
            {Math.min(
                (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
                data.length
            )} of {data.length} employees
            </span>
            <div className="flex gap-2">
            <button
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
                className="px-3 py-1 rounded border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition-colors"
            >
                Previous
            </button>
            <button
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
                className="px-3 py-1 rounded border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition-colors"
            >
                Next
            </button>
            </div>
        </div>
        </div>
    )
}