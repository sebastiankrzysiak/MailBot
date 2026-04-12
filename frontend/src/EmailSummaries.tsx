import type { EmailSummary } from './App'
import { Trash2, ExternalLink } from 'lucide-react'
import { useState } from 'react'

type Props = {
  emails: EmailSummary[]
  isLoading: boolean
  onFetch: (amount: number) => void
  onDelete: (id: string) => void
}

function EmailSummaries({ emails, isLoading, onFetch, onDelete }: Props) {
  const [maxResults, setMaxResults] = useState("")

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
      {emails.map(email => (
        <div key={email.id} className="bg-white rounded-lg shadow p-5 mb-4">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-gray-500 mb-1">{email.sender}</p>
              <p className="text-xs text-gray-400 mb-1">{email.date}</p>
              <h2 className="text-lg font-semibold text-gray-800 mb-2">{email.subject}</h2>
            </div>
            <div className="flex items-center gap-2">
              <a
                href={`https://mail.google.com/mail/u/0/#inbox/${email.id}`}
                target="_blank"
                rel="noreferrer"
                className="text-gray-400 hover:text-blue-600"
              >
                <ExternalLink size={16} />
              </a>
              <button
                onClick={() => onDelete(email.id)}
                className="text-red-400 hover:text-red-600 cursor-pointer"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
          <p className="text-gray-600 text-sm">{email.summary}</p>
        </div>
      ))}
    </div>
  )
}

export default EmailSummaries
