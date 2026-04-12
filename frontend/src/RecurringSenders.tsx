import { useState } from 'react';
import { Trash2 } from 'lucide-react'
import type { RecurringSender } from './App'

type Props = {
  senders: RecurringSender[]
  isLoading: boolean
  onFetch: (amount: number) => void
  onDelete: (id: string) => void
}

function RecurringSenders({ senders, isLoading, onFetch, onDelete }: Props) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set())
  const [maxResults, setMaxResults] = useState("")

  function toggleExpand(sender: string) {
    setExpanded(prev => {
      const next = new Set(prev)
      if (next.has(sender)) {
        next.delete(sender)
      } else {
        next.add(sender)
      }
      return next
    })
  }

  function deleteAll(ids: string[]) {
    ids.forEach(id => onDelete(id))
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={() => onFetch(maxResults === "" ? 100 : Number(maxResults))}
          className="h-10 px-4 bg-blue-600 text-white rounded font-medium hover:bg-blue-700"
        >
          {isLoading ? "Loading..." : "Scan"}
        </button>
        {!isLoading && <input
          type="number"
          value={maxResults}
          onChange={e => {
            const val = e.target.value
            if (val === "" || Number(val) > 0) setMaxResults(val)
          }}
          className="h-10 w-28 px-4 border rounded font-medium text-gray-700"
          placeholder="Amount"
        />}
      </div>
      {senders.map(sender => (
        <div key={sender.sender} className="bg-white rounded-lg shadow p-5 mb-4">
          <div className="flex justify-between items-center">
            <p className="text-gray-800 font-medium">{sender.sender}</p>
            <div className="flex items-center gap-3">
              <p className="text-gray-500 text-sm">{sender.count} Emails</p>
              <button
                onClick={() => toggleExpand(sender.sender)}
                className="text-blue-600 text-sm hover:underline"
              >
                {expanded.has(sender.sender) ? "Collapse" : "Expand"}
              </button>
              <button
                onClick={() => deleteAll(sender.emails.map(e => e.id))}
                className="text-red-400 hover:text-red-600 cursor-pointer"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
          {expanded.has(sender.sender) && (
            <div className="mt-3 pt-3">
              {sender.emails.map(email => (
                <div key={email.id} className="flex justify-between items-center py-1">
                  <p className="text-gray-600 text-sm">{email.subject}</p>
                  <button
                    onClick={() => onDelete(email.id)}
                    className="text-red-400 hover:text-red-600 cursor-pointer"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

export default RecurringSenders
