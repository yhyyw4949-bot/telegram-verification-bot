'use client'
import { useEffect, useState } from 'react'
import api from '@/lib/api'
import { Users, ShoppingBag, ArrowDownCircle, ArrowUpCircle, DollarSign, TrendingUp } from 'lucide-react'

export default function AdminPage() {
  const [stats, setStats] = useState<any>({})

  useEffect(() => {
    api.get('/admin/stats').then(r => setStats(r.data)).catch(() => {})
  }, [])

  const cards = [
    { icon: Users, label: 'إجمالي المستخدمين', value: stats.total_users || 0, color: 'text-blue-400', bg: 'bg-blue-600/20' },
    { icon: ShoppingBag, label: 'إجمالي الطلبات', value: stats.total_orders || 0, color: 'text-purple-400', bg: 'bg-purple-600/20' },
    { icon: TrendingUp, label: 'طلبات معلقة', value: stats.pending_orders || 0, color: 'text-yellow-400', bg: 'bg-yellow-600/20' },
    { icon: ShoppingBag, label: 'طلبات مكتملة', value: stats.completed_orders || 0, color: 'text-green-400', bg: 'bg-green-600/20' },
    { icon: ArrowDownCircle, label: 'إجمالي الإيداعات', value: `${(stats.total_deposits || 0).toFixed(2)} USDT`, color: 'text-green-400', bg: 'bg-green-600/20' },
    { icon: ArrowUpCircle, label: 'إجمالي السحوبات', value: `${(stats.total_withdrawals || 0).toFixed(2)} USDT`, color: 'text-orange-400', bg: 'bg-orange-600/20' },
  ]

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">🛡️ لوحة تحكم الأدمن</h1>
        <p className="text-gray-400 mt-1">نظرة عامة على المنصة</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {cards.map(({ icon: Icon, label, value, color, bg }) => (
          <div key={label} className="card">
            <div className={`w-10 h-10 ${bg} rounded-xl flex items-center justify-center mb-3`}>
              <Icon size={20} className={color} />
            </div>
            <p className="text-gray-400 text-sm">{label}</p>
            <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        {[
          { href: '/admin/deposits', label: 'مراجعة الإيداعات', desc: 'قبول أو رفض طلبات الإيداع', icon: ArrowDownCircle, color: 'bg-green-700' },
          { href: '/admin/withdrawals', label: 'مراجعة السحوبات', desc: 'قبول أو رفض طلبات السحب', icon: ArrowUpCircle, color: 'bg-orange-700' },
          { href: '/admin/orders', label: 'إدارة الطلبات', desc: 'تحديث حالة طلبات التوثيق', icon: ShoppingBag, color: 'bg-primary-700' },
        ].map(({ href, label, desc, icon: Icon, color }) => (
          <a key={href} href={href} className={`${color} rounded-2xl p-6 block hover:opacity-90 transition-opacity`}>
            <Icon size={28} className="mb-3" />
            <h3 className="font-bold text-lg">{label}</h3>
            <p className="text-white/70 text-sm mt-1">{desc}</p>
          </a>
        ))}
      </div>
    </div>
  )
}
