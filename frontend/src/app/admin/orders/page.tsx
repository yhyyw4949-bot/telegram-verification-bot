'use client'
import { useEffect, useState } from 'react'
import api from '@/lib/api'
import toast from 'react-hot-toast'
import { ShoppingBag } from 'lucide-react'

const STATUSES = ['pending','paid','in_progress','completed','rejected','disputed']
const STATUS_LABELS: Record<string, string> = {
  pending:'قيد الانتظار', paid:'مدفوع', in_progress:'جاري التنفيذ',
  completed:'مكتمل', rejected:'مرفوض', disputed:'نزاع'
}
const STATUS_CLS: Record<string, string> = {
  pending:'badge-pending', completed:'badge-completed', rejected:'badge-rejected',
  disputed:'badge-disputed', paid:'badge-approved', in_progress:'badge-pending'
}

export default function AdminOrdersPage() {
  const [orders, setOrders] = useState<any[]>([])
  const [filter, setFilter] = useState('pending')
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    api.get('/admin/orders', { params: { status: filter } })
      .then(r => setOrders(r.data)).finally(() => setLoading(false))
  }
  useEffect(() => { load() }, [filter])

  const updateStatus = async (id: number, status: string) => {
    const notes = status === 'rejected' ? (prompt('سبب الرفض:') || '') : ''
    try {
      await api.put(`/admin/orders/${id}/status`, { status, notes })
      toast.success('تم تحديث الحالة!')
      load()
    } catch { toast.error('حدث خطأ') }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold flex items-center gap-2"><ShoppingBag className="text-purple-400" /> إدارة الطلبات</h1>

      {/* Filter */}
      <div className="flex gap-2 flex-wrap">
        {STATUSES.map(s => (
          <button key={s} onClick={() => setFilter(s)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${filter === s ? 'bg-primary-600 text-white' : 'bg-dark-800 text-gray-400 hover:bg-dark-700'}`}>
            {STATUS_LABELS[s]}
          </button>
        ))}
      </div>

      {loading ? <div className="flex justify-center py-20"><div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>
      : orders.length === 0 ? <div className="card text-center py-16 text-gray-400">لا توجد طلبات</div>
      : (
        <div className="space-y-4">
          {orders.map((o: any) => (
            <div key={o.id} className="card">
              <div className="flex flex-wrap items-start gap-4">
                <div className="flex-1 space-y-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-bold">طلب #{o.id}</span>
                    <span className={STATUS_CLS[o.status] || 'badge-pending'}>{STATUS_LABELS[o.status] || o.status}</span>
                  </div>
                  <p className="text-sm">المشتري: ID {o.buyer_id}</p>
                  <p className="text-sm">المنصة: <span className="text-white font-medium">{o.platform}</span></p>
                  <p className="text-sm">النوع: {o.verification_type}</p>
                  {o.price > 0 && <p className="text-sm">السعر: <span className="text-green-400">{o.price} USDT</span></p>}
                  <p className="text-xs text-gray-400">{new Date(o.created_at).toLocaleString('ar')}</p>
                </div>
                <div className="flex gap-2 flex-wrap">
                  {['in_progress','completed','rejected'].map(s => s !== o.status && (
                    <button key={s} onClick={() => updateStatus(o.id, s)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors
                        ${s === 'completed' ? 'bg-green-700 hover:bg-green-600' :
                          s === 'rejected' ? 'bg-red-800 hover:bg-red-700' : 'bg-blue-800 hover:bg-blue-700'}`}>
                      {STATUS_LABELS[s]}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
