'use client'
import { useEffect, useState } from 'react'
import { useAuthStore } from '@/store/authStore'
import api from '@/lib/api'
import { Wallet, ShoppingBag, ArrowDownCircle, ArrowUpCircle, Bell, Clock } from 'lucide-react'
import Link from 'next/link'
import { format } from 'date-fns'

const statusMap: Record<string, { label: string; cls: string }> = {
  pending:     { label: 'قيد الانتظار', cls: 'badge-pending' },
  paid:        { label: 'مدفوع', cls: 'badge-approved' },
  in_progress: { label: 'جاري التنفيذ', cls: 'badge-pending' },
  completed:   { label: 'مكتمل', cls: 'badge-completed' },
  rejected:    { label: 'مرفوض', cls: 'badge-rejected' },
  disputed:    { label: 'نزاع', cls: 'badge-disputed' },
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const [balance, setBalance] = useState<any>(null)
  const [orders, setOrders] = useState<any[]>([])
  const [notifications, setNotifications] = useState<any[]>([])

  useEffect(() => {
    api.get('/users/me/balance').then(r => setBalance(r.data)).catch(() => {})
    api.get('/marketplace/orders').then(r => setOrders(r.data.slice(0, 5))).catch(() => {})
    api.get('/users/me/notifications').then(r => setNotifications(r.data.slice(0, 5))).catch(() => {})
  }, [])

  const stats = [
    { icon: Wallet, label: 'رصيدك', value: `${balance?.amount?.toFixed(2) || '0.00'} USDT`, color: 'text-primary-400', bg: 'bg-primary-600/20' },
    { icon: ArrowDownCircle, label: 'إجمالي الإيداعات', value: `${balance?.total_deposited?.toFixed(2) || '0.00'} USDT`, color: 'text-green-400', bg: 'bg-green-600/20' },
    { icon: ArrowUpCircle, label: 'إجمالي السحوبات', value: `${balance?.total_withdrawn?.toFixed(2) || '0.00'} USDT`, color: 'text-orange-400', bg: 'bg-orange-600/20' },
    { icon: ShoppingBag, label: 'عدد الطلبات', value: orders.length, color: 'text-purple-400', bg: 'bg-purple-600/20' },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">مرحباً، {user?.first_name} 👋</h1>
        <p className="text-gray-400 mt-1">هذه نظرة عامة على حسابك</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map(({ icon: Icon, label, value, color, bg }) => (
          <div key={label} className="card">
            <div className={`w-10 h-10 ${bg} rounded-xl flex items-center justify-center mb-3`}>
              <Icon size={20} className={color} />
            </div>
            <p className="text-gray-400 text-sm">{label}</p>
            <p className={`text-xl font-bold mt-1 ${color}`}>{value}</p>
          </div>
        ))}
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { href: '/marketplace', label: 'شراء توثيق', icon: ShoppingBag, color: 'bg-primary-600' },
          { href: '/dashboard/deposit', label: 'إيداع', icon: ArrowDownCircle, color: 'bg-green-700' },
          { href: '/dashboard/withdraw', label: 'سحب', icon: ArrowUpCircle, color: 'bg-orange-700' },
          { href: '/dashboard/support', label: 'الدعم الفني', icon: Bell, color: 'bg-purple-700' },
        ].map(({ href, label, icon: Icon, color }) => (
          <Link key={href} href={href}
            className={`${color} rounded-2xl p-4 flex flex-col items-center gap-2 hover:opacity-90 transition-opacity`}>
            <Icon size={24} />
            <span className="font-semibold text-sm">{label}</span>
          </Link>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Recent orders */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold flex items-center gap-2"><ShoppingBag size={18} /> آخر الطلبات</h2>
            <Link href="/dashboard/orders" className="text-primary-400 text-sm hover:text-primary-300">عرض الكل</Link>
          </div>
          {orders.length === 0 ? (
            <p className="text-gray-500 text-sm text-center py-6">لا توجد طلبات بعد</p>
          ) : (
            <div className="space-y-3">
              {orders.map((o: any) => (
                <div key={o.id} className="flex items-center justify-between bg-dark-800 rounded-xl p-3">
                  <div>
                    <p className="font-medium text-sm">#{o.id} — {o.platform}</p>
                    <p className="text-xs text-gray-400 flex items-center gap-1 mt-0.5">
                      <Clock size={10} /> {format(new Date(o.created_at), 'dd/MM/yyyy')}
                    </p>
                  </div>
                  <span className={statusMap[o.status]?.cls || 'badge-pending'}>
                    {statusMap[o.status]?.label || o.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Notifications */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold flex items-center gap-2"><Bell size={18} /> الإشعارات</h2>
          </div>
          {notifications.length === 0 ? (
            <p className="text-gray-500 text-sm text-center py-6">لا توجد إشعارات</p>
          ) : (
            <div className="space-y-3">
              {notifications.map((n: any) => (
                <div key={n.id} className={`flex gap-3 p-3 rounded-xl ${n.is_read ? 'bg-dark-800/50' : 'bg-primary-900/20 border border-primary-800/30'}`}>
                  <div className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0" />
                  <div>
                    <p className="font-medium text-sm">{n.title}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{n.body}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
