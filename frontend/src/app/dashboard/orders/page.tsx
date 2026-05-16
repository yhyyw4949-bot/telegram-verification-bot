'use client'
import { useEffect, useState } from 'react'
import api from '@/lib/api'
import { FileText, Clock } from 'lucide-react'
import { format } from 'date-fns'

const statusMap: Record<string, { label: string; cls: string }> = {
  pending:     { label: 'قيد الانتظار', cls: 'badge-pending' },
  paid:        { label: 'مدفوع', cls: 'badge-approved' },
  in_progress: { label: 'جاري التنفيذ', cls: 'badge-pending' },
  completed:   { label: 'مكتمل', cls: 'badge-completed' },
  rejected:    { label: 'مرفوض', cls: 'badge-rejected' },
  disputed:    { label: 'نزاع', cls: 'badge-disputed' },
}

export default function OrdersPage() {
  const [orders, setOrders] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/marketplace/orders').then(r => setOrders(r.data)).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex items-center justify-center py-20"><div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2"><FileText className="text-primary-400" /> طلباتي</h1>
        <p className="text-gray-400 mt-1">جميع طلبات التوثيق الخاصة بك</p>
      </div>

      {orders.length === 0 ? (
        <div className="card text-center py-16">
          <FileText size={48} className="text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">لا توجد طلبات بعد</p>
          <a href="/marketplace" className="btn-primary inline-block mt-4">تصفح السوق</a>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((o: any) => (
            <div key={o.id} className="card hover:border-primary-800/50 transition-colors">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-bold">طلب #{o.id}</span>
                    <span className={(statusMap[o.status]?.cls) || 'badge-pending'}>
                      {statusMap[o.status]?.label || o.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400">المنصة: <span className="text-white font-medium">{o.platform}</span></p>
                  <p className="text-sm text-gray-400">نوع التوثيق: <span className="text-white font-medium">{o.verification_type}</span></p>
                  {o.price > 0 && <p className="text-sm text-gray-400">السعر: <span className="text-green-400 font-semibold">{o.price} USDT</span></p>}
                  {o.admin_notes && (
                    <p className="text-sm text-yellow-400 mt-2 bg-yellow-900/20 rounded-lg px-3 py-2">
                      ملاحظة: {o.admin_notes}
                    </p>
                  )}
                </div>
                <div className="text-left text-sm text-gray-500 flex items-center gap-1">
                  <Clock size={12} />
                  {format(new Date(o.created_at), 'dd/MM/yyyy HH:mm')}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
