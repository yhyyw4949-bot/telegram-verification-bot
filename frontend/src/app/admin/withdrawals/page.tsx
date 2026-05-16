'use client'
import { useEffect, useState } from 'react'
import api from '@/lib/api'
import toast from 'react-hot-toast'
import { ArrowUpCircle, CheckCircle, XCircle } from 'lucide-react'

export default function AdminWithdrawalsPage() {
  const [wds, setWds] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const load = () => api.get('/admin/withdrawals/pending').then(r => setWds(r.data)).finally(() => setLoading(false))
  useEffect(() => { load() }, [])

  const approve = async (id: number) => {
    try { await api.post(`/admin/withdrawals/${id}/approve`); toast.success('تم قبول السحب!'); load() }
    catch { toast.error('حدث خطأ') }
  }
  const reject = async (id: number) => {
    const reason = prompt('سبب الرفض:'); if (!reason) return
    try { await api.post(`/admin/withdrawals/${id}/reject`, null, { params: { reason } }); toast.success('تم رفض السحب وإعادة الرصيد'); load() }
    catch { toast.error('حدث خطأ') }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold flex items-center gap-2"><ArrowUpCircle className="text-orange-400" /> السحوبات المعلقة</h1>

      {loading ? <div className="flex justify-center py-20"><div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>
      : wds.length === 0 ? <div className="card text-center py-16 text-gray-400">✅ لا توجد سحوبات معلقة</div>
      : (
        <div className="space-y-4">
          {wds.map((w: any) => (
            <div key={w.id} className="card">
              <div className="flex flex-wrap items-start gap-4">
                <div className="flex-1 space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-lg">#{w.id}</span>
                    <span className="badge-pending">قيد المراجعة</span>
                  </div>
                  <p className="text-sm">المستخدم: <span className="text-white font-medium">ID: {w.user_id}</span></p>
                  <p className="text-sm">المبلغ: <span className="text-orange-400 font-bold text-lg">{w.amount} USDT</span></p>
                  <p className="text-sm">الطريقة: <span className="text-white">{w.method}</span></p>
                  <p className="text-sm">العنوان: <code className="text-primary-300 text-xs break-all">{w.wallet_address}</code></p>
                  <p className="text-sm text-gray-400">{new Date(w.created_at).toLocaleString('ar')}</p>
                </div>
                <div className="flex gap-3">
                  <button onClick={() => approve(w.id)}
                    className="flex items-center gap-2 bg-green-700 hover:bg-green-600 px-4 py-2 rounded-xl text-sm font-semibold transition-colors">
                    <CheckCircle size={16} /> قبول وإرسال
                  </button>
                  <button onClick={() => reject(w.id)}
                    className="flex items-center gap-2 bg-red-800 hover:bg-red-700 px-4 py-2 rounded-xl text-sm font-semibold transition-colors">
                    <XCircle size={16} /> رفض وإرجاع
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
