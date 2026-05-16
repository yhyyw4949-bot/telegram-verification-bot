'use client'
import { useEffect, useState } from 'react'
import { useAuthStore } from '@/store/authStore'
import api from '@/lib/api'
import toast from 'react-hot-toast'
import { Gift, Copy, CheckCircle, Users } from 'lucide-react'

export default function ReferralPage() {
  const { user } = useAuthStore()
  const [referrals, setReferrals] = useState<any[]>([])
  const [copied, setCopied] = useState(false)

  const refLink = typeof window !== 'undefined'
    ? `${window.location.origin}/register?ref=${user?.referral_code}`
    : ''

  useEffect(() => {
    api.get('/users/me/referrals').then(r => setReferrals(r.data)).catch(() => {})
  }, [])

  const copy = () => {
    navigator.clipboard.writeText(refLink)
    setCopied(true)
    toast.success('تم نسخ رابط الإحالة!')
    setTimeout(() => setCopied(false), 2000)
  }

  const totalEarned = referrals.reduce((s, r) => s + (r.reward_amount || 0), 0)

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2"><Gift className="text-yellow-400" /> نظام الإحالات</h1>
        <p className="text-gray-400 mt-1">ادعُ أصدقاءك واحصل على مكافآت</p>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="card text-center">
          <Users size={32} className="text-primary-400 mx-auto mb-2" />
          <p className="text-3xl font-bold">{referrals.length}</p>
          <p className="text-gray-400 text-sm">عدد الإحالات</p>
        </div>
        <div className="card text-center">
          <Gift size={32} className="text-green-400 mx-auto mb-2" />
          <p className="text-3xl font-bold text-green-400">{totalEarned.toFixed(2)}</p>
          <p className="text-gray-400 text-sm">إجمالي المكافآت (USDT)</p>
        </div>
        <div className="card text-center">
          <div className="text-3xl mb-2">🏆</div>
          <p className="text-3xl font-bold text-yellow-400">{user?.referral_code}</p>
          <p className="text-gray-400 text-sm">كود الإحالة الخاص بك</p>
        </div>
      </div>

      <div className="card">
        <h2 className="font-bold mb-4">رابط الإحالة</h2>
        <div className="flex items-center gap-3 bg-dark-800 rounded-xl p-4">
          <code className="flex-1 text-sm text-primary-300 break-all">{refLink}</code>
          <button onClick={copy} className="flex-shrink-0 text-gray-400 hover:text-white transition-colors">
            {copied ? <CheckCircle size={20} className="text-green-400" /> : <Copy size={20} />}
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-3">
          عندما يسجل شخص باستخدام رابطك، تحصل تلقائياً على مكافأة في رصيدك.
        </p>
      </div>

      <div className="card">
        <h2 className="font-bold mb-4">سجل الإحالات</h2>
        {referrals.length === 0 ? (
          <p className="text-gray-500 text-center py-8">لا توجد إحالات بعد. شارك رابطك!</p>
        ) : (
          <div className="space-y-3">
            {referrals.map((r: any) => (
              <div key={r.id} className="flex items-center justify-between bg-dark-800 rounded-xl p-3">
                <div>
                  <p className="font-medium text-sm">مستخدم #{r.referred_id}</p>
                  <p className="text-xs text-gray-400">{new Date(r.created_at).toLocaleDateString('ar')}</p>
                </div>
                <span className="text-green-400 font-bold">+{r.reward_amount} USDT</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
