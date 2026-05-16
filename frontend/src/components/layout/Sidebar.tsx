'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import {
  LayoutDashboard, ShoppingBag, Wallet, ArrowDownCircle, ArrowUpCircle,
  Users, FileText, MessageSquare, Settings, LogOut, Shield, Bell, Gift
} from 'lucide-react'
import clsx from 'clsx'

const userLinks = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'لوحة التحكم' },
  { href: '/marketplace', icon: ShoppingBag, label: 'السوق' },
  { href: '/dashboard/deposit', icon: ArrowDownCircle, label: 'إيداع' },
  { href: '/dashboard/withdraw', icon: ArrowUpCircle, label: 'سحب' },
  { href: '/dashboard/orders', icon: FileText, label: 'طلباتي' },
  { href: '/dashboard/referral', icon: Gift, label: 'الإحالات' },
  { href: '/dashboard/support', icon: MessageSquare, label: 'الدعم الفني' },
]
const adminLinks = [
  { href: '/admin', icon: Shield, label: 'لوحة الأدمن' },
  { href: '/admin/users', icon: Users, label: 'المستخدمون' },
  { href: '/admin/orders', icon: FileText, label: 'الطلبات' },
  { href: '/admin/deposits', icon: ArrowDownCircle, label: 'الإيداعات' },
  { href: '/admin/withdrawals', icon: ArrowUpCircle, label: 'السحوبات' },
  { href: '/admin/settings', icon: Settings, label: 'الإعدادات' },
]

export default function Sidebar() {
  const pathname = usePathname()
  const { user, logout } = useAuthStore()

  return (
    <aside className="w-64 bg-dark-900 border-l border-dark-800 flex flex-col h-screen sticky top-0">
      {/* Logo */}
      <div className="p-6 border-b border-dark-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-primary-600 rounded-xl flex items-center justify-center">
            <Shield size={18} />
          </div>
          <span className="font-bold text-lg">VerifPlatform</span>
        </div>
      </div>

      {/* User info */}
      <div className="p-4 border-b border-dark-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-600/30 rounded-full flex items-center justify-center text-primary-400 font-bold">
            {user?.first_name?.[0] || 'U'}
          </div>
          <div className="min-w-0">
            <p className="font-semibold text-sm truncate">{user?.first_name}</p>
            <p className="text-xs text-gray-400 truncate">@{user?.username}</p>
          </div>
        </div>
        <div className="mt-3 bg-dark-800 rounded-xl px-3 py-2 flex items-center gap-2">
          <Wallet size={14} className="text-primary-400" />
          <span className="text-sm font-semibold text-primary-400">
            {typeof user?.balance === 'number' ? user.balance.toFixed(2) : '0.00'} USDT
          </span>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto p-3 space-y-1">
        {userLinks.map(({ href, icon: Icon, label }) => (
          <Link key={href} href={href}
            className={clsx('sidebar-link', pathname === href && 'active')}>
            <Icon size={18} />
            <span className="text-sm">{label}</span>
          </Link>
        ))}
        {user?.is_admin && (
          <>
            <div className="pt-4 pb-1 px-4">
              <span className="text-xs text-gray-600 uppercase tracking-widest">الإدارة</span>
            </div>
            {adminLinks.map(({ href, icon: Icon, label }) => (
              <Link key={href} href={href}
                className={clsx('sidebar-link', pathname.startsWith(href) && 'active')}>
                <Icon size={18} />
                <span className="text-sm">{label}</span>
              </Link>
            ))}
          </>
        )}
      </nav>

      {/* Logout */}
      <div className="p-3 border-t border-dark-800">
        <button onClick={logout}
          className="sidebar-link w-full text-red-400 hover:bg-red-900/20 hover:text-red-300">
          <LogOut size={18} />
          <span className="text-sm">تسجيل الخروج</span>
        </button>
      </div>
    </aside>
  )
}
