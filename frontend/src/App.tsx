import { useState, useEffect } from 'react';
import EmailSummaries from './EmailSummaries'
import RecurringSenders from './RecurringSenders'

export type EmailSummary = {
  id: string
  subject: string
  sender: string
  summary: string
  date: string
}

export type Email = {
  id: string
  subject: string
}

export type RecurringSender = {
  sender: string
  count: number
  emails: Email[]
}

function App() {
  const [active, setActive] = useState("summaries")
  const [emails, setEmails] = useState<EmailSummary[]>([])
  const [senders, setSenders] = useState<RecurringSender[]>([])
  const [jobsEmails, setJobsEmails] = useState<EmailSummary[]>([])
  const [schoolEmails, setSchoolEmails] = useState<EmailSummary[]>([])

  const [emailsLoading, setEmailsLoading] = useState(false)
  const [sendersLoading, setSendersLoading] = useState(false)
  const [jobsLoading, setJobsLoading] = useState(false)
  const [schoolLoading, setSchoolLoading] = useState(false)

  async function fetchEmails(amount: number) {
    setEmailsLoading(true)
    const res = await fetch(`http://localhost:8000/summarize?max_results=${amount}`)
    const data = await res.json()
    setEmails(data)
    setEmailsLoading(false)
  }

  async function fetchRecurringSenders(amount: number) {
    setSendersLoading(true)
    const res = await fetch(`http://localhost:8000/recurring?max_results=${amount}`)
    const data = await res.json()
    setSenders(data)
    setSendersLoading(false)
  }

  async function fetchJobs(amount: number) {
    setJobsLoading(true)
    const res = await fetch(`http://localhost:8000/jobs?max_results=${amount}`)
    const data = await res.json()
    setJobsEmails(data)
    setJobsLoading(false)
  }

  async function fetchSchool(amount: number) {
    setSchoolLoading(true)
    const res = await fetch(`http://localhost:8000/school?max_results=${amount}`)
    const data = await res.json()
    setSchoolEmails(data)
    setSchoolLoading(false)
  }

  function renderTab() {
    if (active === "summaries") return <EmailSummaries emails={emails} isLoading={emailsLoading} onFetch={fetchEmails} onDelete={deleteEmail} />
    if (active === "jobs") return <EmailSummaries emails={jobsEmails} isLoading={jobsLoading} onFetch={fetchJobs} onDelete={deleteEmail} />
    if (active === "school") return <EmailSummaries emails={schoolEmails} isLoading={schoolLoading} onFetch={fetchSchool} onDelete={deleteEmail} />
    return <RecurringSenders senders={senders} isLoading={sendersLoading} onFetch={fetchRecurringSenders} onDelete={deleteEmail} />
  }

  async function deleteEmail(id: string) {
    await fetch(`http://localhost:8000/emails/${id}`, { method: "DELETE" })
    setSenders(prev => prev
      .map(s => ({
        ...s,
        emails: s.emails.filter(e => e.id !== id),
        count: s.emails.filter(e => e.id !== id).length
      }))
      .filter(s => s.count > 0)
    )
    setEmails(prev => prev.filter(e => e.id !== id))
    setJobsEmails(prev => prev.filter(e => e.id !== id))
    setSchoolEmails(prev => prev.filter(e => e.id !== id))
  }

  useEffect(() => {
    if (active === "summaries" && emails.length === 0) fetchEmails(100)
    if (active === "jobs" && jobsEmails.length === 0) fetchJobs(100)
    if (active === "school" && schoolEmails.length === 0) fetchSchool(100)
    if (active === "recurring" && senders.length === 0) fetchRecurringSenders(100)
  }, [active])

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto pt-10 px-4">
        <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">MailBot</h1>
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActive("summaries")}
            className={`flex-1 py-1 rounded font-medium flex flex-col items-center ${active === "summaries" ? "bg-blue-600 text-white" : "bg-white text-gray-600 shadow"}`}
          >
            <span>Inbox</span>
            <span className="text-xs opacity-75">{emails.length}</span>
          </button>
          <button
            onClick={() => setActive("jobs")}
            className={`flex-1 py-1 rounded font-medium flex flex-col items-center ${active === "jobs" ? "bg-blue-600 text-white" : "bg-white text-gray-600 shadow"}`}
          >
            <span>Jobs</span>
            <span className="text-xs opacity-75">{jobsEmails.length}</span>
          </button>
          <button
            onClick={() => setActive("school")}
            className={`flex-1 py-1 rounded font-medium flex flex-col items-center ${active === "school" ? "bg-blue-600 text-white" : "bg-white text-gray-600 shadow"}`}
          >
            <span>School</span>
            <span className="text-xs opacity-75">{schoolEmails.length}</span>
          </button>
          <button
            onClick={() => setActive("recurring")}
            className={`flex-1 py-1 rounded font-medium flex flex-col items-center ${active === "recurring" ? "bg-blue-600 text-white" : "bg-white text-gray-600 shadow"}`}
          >
            <span>Top Senders</span>
            <span className="text-xs opacity-75">{senders.length}</span>
          </button>
        </div>
        {renderTab()}
      </div>
    </div>
  )
}

export default App