'use client'
import { useEffect, useState } from 'react'
import api from '@/lib/api'
import toast from 'react-hot-toast'
import { MessageSquare, Send, Plus } from 'lucide-react'

export default function SupportPage() {
  const [tickets, setTickets] = useState<any[]>([])
  const [active, setActive] = useState<any>(null)
  const [reply, setReply] = useState('')
  const [newTicket, setNewTicket] = useState({ subject: '', message: '' })
  const [creating, setCreating] = useState(false)
  const [sending, setSending] = useState(false)

  const load = () => api.get('/support/tickets').then(r => setTickets(r.data)).catch(() => {})
  useEffect(() => { load() }, [])

  const create = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreating(true)
    try {
      await api.post('/support/tickets', newTicket)
      toast.success('تم فتح تذكرة دعم!')
      setNewTicket({ subject: '', message: '' }); load()
    } catch { toast.error('حدث خطأ') } finally { setCreating(false) }
  }

  const sendReply = async () => {
    if (!active || !reply.trim()) return
    setSending(true)
    try {
      await api.post(`/support/tickets/${active.id}/messages`, { content: reply })
      setReply('')
      const updated = await api.get('/support/tickets')
      const t = updated.data.find((t: any) => t.id === active.id)
      setActive(t); setTickets(updated.data)
    } catch { toast.error('حدث خطأ') } finally { setSending(false) }
  }

  const statusCls: Record<string, string> = { open: 'badge-pending', in_progress: 'badge-approved', closed: 'badge-rejected' }
  const statusLbl: Record<string, string> = { open: 'مفتوح', in_progress: 'قيد المعالجة', closed: 'مغلق' }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold flex items-center gap-2"><MessageSquare className="text-purple-400" /> الدعم الفني</h1>

      <div className="grid md:grid-cols-2 gap-6">
        {/* New ticket */}
        <div className="card">
          <h2 className="font-bold mb-4 flex items-center gap-2"><Plus size={18} /> فتح تذكرة جديدة</h2>
          <form onSubmit={create} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">الموضوع</label>
              <input className="input" placeholder="مشكلة في الإيداع..." value={newTicket.subject}
                onChange={e => setNewTicket(n => ({ ...n, subject: e.target.value }))} required />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">الرسالة</label>
              <textarea className="input resize-none" rows={4} placeholder="اشرح مشكلتك بالتفصيل..."
                value={newTicket.message} onChange={e => setNewTicket(n => ({ ...n, message: e.target.value }))} required />
            </div>
            <button type="submit" disabled={creating} className="btn-primary w-full">
              {creating ? 'جاري الإرسال...' : 'فتح التذكرة'}
            </button>
          </form>
        </div>

        {/* Ticket list */}
        <div className="card">
          <h2 className="font-bold mb-4">تذاكرك</h2>
          {tickets.length === 0 ? (
            <p className="text-gray-500 text-center py-8">لا توجد تذاكر</p>
          ) : (
            <div className="space-y-3">
              {tickets.map((t: any) => (
                <button key={t.id} onClick={() => setActive(t)}
                  className={`w-full text-right p-3 rounded-xl border transition-all ${active?.id === t.id ? 'border-primary-500 bg-primary-900/20' : 'border-dark-700 bg-dark-800 hover:border-dark-600'}`}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-sm">#{t.id} {t.subject}</span>
                    <span className={statusCls[t.status]}>{statusLbl[t.status]}</span>
                  </div>
                  <p className="text-xs text-gray-400">{new Date(t.created_at).toLocaleDateString('ar')}</p>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Chat */}
      {active && (
        <div className="card">
          <h2 className="font-bold mb-4">#{active.id} — {active.subject}</h2>
          <div className="space-y-3 max-h-80 overflow-y-auto mb-4 p-2">
            {(active.messages || []).map((m: any) => (
              <div key={m.id} className={`flex ${m.is_admin ? 'justify-start' : 'justify-end'}`}>
                <div className={`max-w-xs rounded-2xl px-4 py-2 text-sm ${m.is_admin ? 'bg-dark-700 text-white' : 'bg-primary-600 text-white'}`}>
                  {m.is_admin && <p className="text-xs text-primary-300 mb-1 font-semibold">الدعم الفني</p>}
                  {m.content}
                </div>
              </div>
            ))}
          </div>
          {active.status !== 'closed' && (
            <div className="flex gap-3">
              <input className="input flex-1" placeholder="اكتب ردك..." value={reply}
                onChange={e => setReply(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendReply()} />
              <button onClick={sendReply} disabled={sending || !reply.trim()} className="btn-primary px-4">
                <Send size={18} />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
