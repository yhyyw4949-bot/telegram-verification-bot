'use client'
import { useEffect, useState } from 'react'
import api from '@/lib/api'
import toast from 'react-hot-toast'
import { ArrowDownCircle, CheckCircle, XCircle, ExternalLink } from 'lucide-react'

export default function AdminDepositsPage() {
  const [deposits, setDeposits] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const load = () => api.get('/admin/deposits/pending').then(r => setDeposits(r.data)).finally(() => setLoading(false))
  useEffect(() => { load() }, [])

  const approve = async (id: number) => {
    try { await api.post(`/admin/deposits/${id}/approve`); toast.success('تم قبول الإيداع!'); load() }
    catch { toast.error('حدث خطأ') }
  }
  const reject = async (id: number) => {
    const reason = prompt('سبب الرفض:'); if (!reason) return
    try { await api.post(`/admin/deposits/${id}/reject`, null, { params: { reason } }); toast.success('تم رفض الإيداع'); load() }
    catch { toast.error('حدث خطأ') }
  }

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold flex items-center gap-2"><ArrowDownCircle className="text-green-400" /> الإيداعات المعلقة</h1>

      {loading ? <div className="flex justify-center py-20"><div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>
      : deposits.length === 0 ? <div className="card text-center py-16 text-gray-400">✅ لا توجد إيداعات معلقة</div>
      : (
        <div className="space-y-4">
          {deposits.map((d: any) => (
            <div key={d.id} className="card">
              <div className="flex flex-wrap items-start gap-4">
                <div className="flex-1 space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-lg">#{d.id}</span>
                    <span className="badge-pending">قيد المراجعة</span>
                  </div>
                  <p className="text-sm">المستخدم: <span className="text-white font-medium">ID: {d.user_id}</span></p>
                  <p className="text-sm">المبلغ: <span className="text-green-400 font-bold text-lg">{d.amount} USDT</span></p>
                  <p className="text-sm">الطريقة: <span className="text-white">{d.payment_method_name}</span></p>
                  <p className="text-sm text-gray-400">{new Date(d.created_at).toLocaleString('ar')}</p>
                </div>
                {d.proof_image && (
                  <a href={`${API_URL}${d.proof_image}`} target="_blank" rel="noopener noreferrer"
                    className="flex items-center gap-2 text-primary-400 hover:text-primary-300 text-sm bg-primary-900/20 px-3 py-2 rounded-xl">
                    <ExternalLink size={14} /> عرض الإثبات
                  </a>
                )}
                <div className="flex gap-3">
                  <button onClick={() => approve(d.id)}
                    className="flex items-center gap-2 bg-green-700 hover:bg-green-600 px-4 py-2 rounded-xl text-sm font-semibold transition-colors">
                    <CheckCircle size={16} /> قبول
                  </button>
                  <button onClick={() => reject(d.id)}
                    className="flex items-center gap-2 bg-red-800 hover:bg-red-700 px-4 py-2 rounded-xl text-sm font-semibold transition-colors">
                    <XCircle size={16} /> رفض
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
