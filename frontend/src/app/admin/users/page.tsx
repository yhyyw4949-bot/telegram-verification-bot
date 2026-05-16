'use client'
import { useEffect, useState } from 'react'
import api from '@/lib/api'
import toast from 'react-hot-toast'
import { Users, Ban, CheckCircle, DollarSign } from 'lucide-react'

export default function AdminUsersPage() {
  const [users, setUsers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  const load = () => api.get('/users', { params: { limit: 100 } }).then(r => setUsers(r.data)).finally(() => setLoading(false))
  useEffect(() => { load() }, [])

  const ban = async (id: number) => {
    const reason = prompt('سبب الحظر:'); if (!reason) return
    try { await api.post(`/users/${id}/ban`, null, { params: { reason } }); toast.success('تم حظر المستخدم'); load() }
    catch { toast.error('حدث خطأ') }
  }
  const unban = async (id: number) => {
    try { await api.post(`/users/${id}/unban`); toast.success('تم فك الحظر'); load() }
    catch { toast.error('حدث خطأ') }
  }
  const editBalance = async (id: number) => {
    const amt = prompt('المبلغ (يمكن أن يكون سالباً للخصم):'); if (!amt) return
    const amount = parseFloat(amt)
    const op = amount >= 0 ? 'add' : 'subtract'
    try {
      await api.post('/admin/balance/edit', { user_id: id, amount: Math.abs(amount), operation: op, reason: 'تعديل يدوي من الأدمن' })
      toast.success('تم تعديل الرصيد!'); load()
    } catch { toast.error('حدث خطأ') }
  }

  const filtered = users.filter(u =>
    !search || u.username?.includes(search) || u.first_name?.includes(search) || String(u.id).includes(search)
  )

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold flex items-center gap-2"><Users className="text-blue-400" /> إدارة المستخدمين</h1>

      <input className="input max-w-sm" placeholder="بحث بالاسم أو ID..."
        value={search} onChange={e => setSearch(e.target.value)} />

      {loading ? <div className="flex justify-center py-20"><div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>
      : (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-dark-800 text-gray-400 text-right">
              <th className="pb-3">#</th><th className="pb-3">المستخدم</th>
              <th className="pb-3">Telegram</th><th className="pb-3">الحالة</th>
              <th className="pb-3">التاريخ</th><th className="pb-3">إجراءات</th>
            </tr></thead>
            <tbody>
              {filtered.map((u: any) => (
                <tr key={u.id} className="border-b border-dark-800/50 hover:bg-dark-800/30">
                  <td className="py-3 text-gray-400">{u.id}</td>
                  <td className="py-3">
                    <div>
                      <p className="font-medium">{u.first_name} {u.last_name || ''}</p>
                      <p className="text-xs text-gray-400">@{u.username}</p>
                      {u.email && <p className="text-xs text-gray-500">{u.email}</p>}
                    </div>
                  </td>
                  <td className="py-3 text-gray-400">{u.telegram_username ? `@${u.telegram_username}` : '-'}</td>
                  <td className="py-3">
                    {u.is_banned ? <span className="badge-rejected">محظور</span>
                     : u.is_admin ? <span className="badge-completed">أدمن</span>
                     : <span className="badge-approved">نشط</span>}
                  </td>
                  <td className="py-3 text-gray-400">{new Date(u.created_at).toLocaleDateString('ar')}</td>
                  <td className="py-3">
                    <div className="flex gap-2">
                      <button onClick={() => editBalance(u.id)} title="تعديل الرصيد"
                        className="p-1.5 bg-primary-900/40 text-primary-400 rounded-lg hover:bg-primary-800/40">
                        <DollarSign size={14} />
                      </button>
                      {u.is_banned ? (
                        <button onClick={() => unban(u.id)} title="فك الحظر"
                          className="p-1.5 bg-green-900/40 text-green-400 rounded-lg hover:bg-green-800/40">
                          <CheckCircle size={14} />
                        </button>
                      ) : (
                        <button onClick={() => ban(u.id)} title="حظر"
                          className="p-1.5 bg-red-900/40 text-red-400 rounded-lg hover:bg-red-800/40">
                          <Ban size={14} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
