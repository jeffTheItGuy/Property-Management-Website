import { useState } from 'react'

export default function DataTable({ columns, rows, actions, searchKey }) {
  const [filter, setFilter] = useState('')

  const filtered = rows.filter((r) =>
    String(r[searchKey] || '').toLowerCase().includes(filter.toLowerCase())
  )

  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        <input
          type="text"
          placeholder="Search..."
          className="input max-w-xs"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />
        {actions}
      </div>
      <div className="overflow-x-auto border rounded-lg">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-100 text-left">
            <tr>
              {columns.map((c) => (
                <th key={c.key} className="px-4 py-2 font-semibold text-gray-700">{c.label}</th>
              ))}
              <th className="px-4 py-2"></th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {filtered.map((row, i) => (
              <tr key={row.id || i} className="hover:bg-gray-50">
                {columns.map((c) => (
                  <td key={c.key} className="px-4 py-2">{c.format ? c.format(row[c.key], row) : row[c.key]}</td>
                ))}
                <td className="px-4 py-2 text-right">{row._actions}</td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan={columns.length + 1} className="px-4 py-6 text-center text-gray-500">No records found.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}