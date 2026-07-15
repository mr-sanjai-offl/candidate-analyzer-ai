'use client'

import * as React from 'react'
import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  ArrowUpDown,
  Search,
} from 'lucide-react'
import { Button } from './button'
import { Input } from './input'
import { Checkbox } from './checkbox'

export interface ColumnDef<T> {
  id: string
  header: string | ((props: { column: ColumnDef<T> }) => React.ReactNode)
  accessorKey?: keyof T | string
  cell?: (props: { row: T; value: unknown }) => React.ReactNode
  sortable?: boolean
}

interface DataTableProps<T> {
  columns: ColumnDef<T>[]
  data: T[]
  loading?: boolean
  emptyMessage?: string
  bulkActions?: (selectedRows: T[]) => React.ReactNode
  searchPlaceholder?: string
}

export function DataTable<T extends { id: string | number }>({
  columns,
  data,
  loading = false,
  emptyMessage = 'No results found.',
  bulkActions,
  searchPlaceholder = 'Filter rows...',
}: DataTableProps<T>) {
  const [searchTerm, setSearchTerm] = React.useState('')
  const [sortKey, setSortKey] = React.useState<string | null>(null)
  const [sortOrder, setSortOrder] = React.useState<'asc' | 'desc'>('asc')
  const [selectedIds, setSelectedIds] = React.useState<Set<string | number>>(new Set())
  const [currentPage, setCurrentPage] = React.useState(1)
  const pageSize = 10
  const [visibleColumns, setVisibleColumns] = React.useState<Set<string>>(
    new Set(columns.map((c) => c.id))
  )

  // 1. Search Filter
  const filteredData = React.useMemo(() => {
    if (!searchTerm) return data
    const query = searchTerm.toLowerCase()
    return data.filter((row) => {
      const record = row as unknown as Record<string, unknown>
      return Object.keys(record).some((key) => {
        const val = record[key]
        return val && String(val).toLowerCase().includes(query)
      })
    })
  }, [data, searchTerm])

  // 2. Sorting
  const sortedData = React.useMemo(() => {
    if (!sortKey) return filteredData
    return [...filteredData].sort((a, b) => {
      const aRecord = a as unknown as Record<string, unknown>
      const bRecord = b as unknown as Record<string, unknown>
      const aVal = aRecord[sortKey]
      const bVal = bRecord[sortKey]
      if (aVal === bVal) return 0
      const comparison = (aVal ?? '') > (bVal ?? '') ? 1 : -1
      return sortOrder === 'asc' ? comparison : -comparison
    })
  }, [filteredData, sortKey, sortOrder])

  // 3. Pagination
  const totalPages = Math.ceil(sortedData.length / pageSize)
  const paginatedData = React.useMemo(() => {
    const start = (currentPage - 1) * pageSize
    return sortedData.slice(start, start + pageSize)
  }, [sortedData, currentPage, pageSize])

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value)
    setCurrentPage(1)
  }

  // 4. Selection helpers
  const selectedRows = React.useMemo(() => {
    return data.filter((row) => selectedIds.has(row.id))
  }, [data, selectedIds])

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      const allIds = paginatedData.map((row) => row.id)
      setSelectedIds(new Set(allIds))
    } else {
      setSelectedIds(new Set())
    }
  }

  const handleSelectRow = (id: string | number, checked: boolean) => {
    const newSelected = new Set(selectedIds)
    if (checked) {
      newSelected.add(id)
    } else {
      newSelected.delete(id)
    }
    setSelectedIds(newSelected)
  }

  const toggleSort = (id: string) => {
    if (sortKey === id) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(id)
      setSortOrder('asc')
    }
  }

  return (
    <div className="space-y-4">
      {/* Filters and visibility controls */}
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div className="w-full sm:max-w-xs">
          <Input
            placeholder={searchPlaceholder}
            value={searchTerm}
            onChange={handleSearchChange}
            prefix={<Search className="h-4 w-4" />}
          />
        </div>

        <div className="flex items-center gap-2">
          {bulkActions && selectedRows.length > 0 && (
            <div className="flex items-center gap-2 bg-muted px-3 py-1 rounded-md border text-sm">
              <span className="font-medium">{selectedRows.length} selected</span>
              {bulkActions(selectedRows)}
            </div>
          )}

          {/* Simple visibility toggle menu */}
          <div className="relative group">
            <Button variant="outline" size="sm">
              Columns
            </Button>
            <div className="absolute right-0 top-10 z-10 w-48 bg-popover text-popover-foreground border rounded-md shadow-md p-2 hidden group-hover:block hover:block">
              <p className="text-xs font-semibold text-muted-foreground px-2 py-1">Toggle Columns</p>
              <div className="space-y-1 mt-1">
                {columns.map((col) => (
                  <label key={col.id} className="flex items-center gap-2 px-2 py-1 rounded hover:bg-muted text-sm cursor-pointer">
                    <input
                      type="checkbox"
                      checked={visibleColumns.has(col.id)}
                      onChange={(e) => {
                        const newVisible = new Set(visibleColumns)
                        if (e.target.checked) {
                          newVisible.add(col.id)
                        } else if (newVisible.size > 1) {
                          newVisible.delete(col.id)
                        }
                        setVisibleColumns(newVisible)
                      }}
                      className="rounded border-input text-primary focus:ring-primary h-3.5 w-3.5"
                    />
                    <span>{typeof col.header === 'string' ? col.header : col.id}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Table Container */}
      <div className="rounded-md border bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left border-collapse">
            <thead className="bg-muted/50 text-muted-foreground font-medium border-b sticky top-0">
              <tr>
                <th className="p-4 w-[40px]">
                  <Checkbox
                    checked={paginatedData.length > 0 && paginatedData.every((row) => selectedIds.has(row.id))}
                    onCheckedChange={(checked) => handleSelectAll(!!checked)}
                    aria-label="Select all rows"
                  />
                </th>
                {columns
                  .filter((col) => visibleColumns.has(col.id))
                  .map((col) => (
                    <th key={col.id} className="p-4 font-semibold text-muted-foreground">
                      {col.sortable ? (
                        <button
                          onClick={() => toggleSort(col.id)}
                          className="flex items-center gap-1 hover:text-foreground transition-colors"
                        >
                          {typeof col.header === 'string' ? col.header : col.header({ column: col })}
                          <ArrowUpDown className="h-3.5 w-3.5" />
                        </button>
                      ) : typeof col.header === 'string' ? (
                        col.header
                      ) : (
                        col.header({ column: col })
                      )}
                    </th>
                  ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                Array.from({ length: pageSize }).map((_, rIdx) => (
                  <tr key={rIdx} className="border-b animate-pulse">
                    <td className="p-4">
                      <div className="h-4 w-4 bg-muted rounded" />
                    </td>
                    {columns
                      .filter((col) => visibleColumns.has(col.id))
                      .map((col) => (
                        <td key={col.id} className="p-4">
                          <div className="h-4 bg-muted rounded w-2/3" />
                        </td>
                      ))}
                  </tr>
                ))
              ) : paginatedData.length === 0 ? (
                <tr>
                  <td colSpan={columns.length + 1} className="p-8 text-center text-muted-foreground">
                    {emptyMessage}
                  </td>
                </tr>
              ) : (
                paginatedData.map((row) => (
                  <tr key={row.id} className="border-b hover:bg-muted/30 transition-colors">
                    <td className="p-4">
                      <Checkbox
                        checked={selectedIds.has(row.id)}
                        onCheckedChange={(checked) => handleSelectRow(row.id, !!checked)}
                        aria-label={`Select row ${row.id}`}
                      />
                    </td>
                    {columns
                      .filter((col) => visibleColumns.has(col.id))
                      .map((col) => {
                        const val = col.accessorKey ? (row as unknown as Record<string, unknown>)[col.accessorKey as string] : undefined
                        return (
                          <td key={col.id} className="p-4">
                            {col.cell ? col.cell({ row, value: val }) : String(val ?? '')}
                          </td>
                        )
                      })}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-2">
          <p className="text-xs text-muted-foreground">
            Page {currentPage} of {totalPages} ({filteredData.length} total rows)
          </p>
          <div className="flex items-center gap-1">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(1)}
              disabled={currentPage === 1}
            >
              <ChevronsLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(totalPages)}
              disabled={currentPage === totalPages}
            >
              <ChevronsRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
