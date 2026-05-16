'use client'
import { useEffect, useState } from 'react'
import api from '@/lib/api'
import toast from 'react-hot-toast'
import { ArrowUpCircle } from 'lucide-react'

const METHODS = ['TON', 'USDT (TRC20)', 'USDT (ERC20)', 'Binance Pay']

export default function WithdrawPage() {
  const [balance, setBalance] = useState(0)
  const [form, setForm] = useState({ amount: '', method: '', wallet_address: '' })
  const [loading, setLoading] = useState(false)
  const [withdrawals, setWithdrawals] = useState<any[]>([])

  useEffect(() => {
    api.get('/users/me/balance').then(r => setBalance(r.data.amount)).catch(() => {})
    api.get('/transactions/withdrawals').then(r => setWithdrawals(r.data)).catch(() => {})
  }, [])

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }))

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await api.post('/transactions/withdrawals', { ...form, amount: parseFloat(form.amount) })
      toast.success('تم إرسال طلب السحب!')
      setForm({ amount: '', method: '', wallet_address: '' })
      api.get('/users/me/balance').then(r => setBalance(r.data.amount))
      api.get('/transactions/withdrawals').then(r => setWithdrawals(r.data))
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'رصيد غير كافٍ أو مبلغ أقل من الحد الأدنى')
    } finally {
      setLoading(false)
    }
  }

  const statusCls: Record<string, string> = { pending: 'badge-pending', approved: 'badge-approved', rejected: 'badge-rejected' }
  const statusLbl: Record<string, string> = { pending: 'قيد المراجعة', approved: 'مقبول', rejected: 'مرفوض' }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2"><ArrowUpCircle className="text-orange-400" /> سحب رصيد</h1>
        <p className="text-gray-400 mt-1">اسحب رصيدك إلى محفظتك الخاصة</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="card">
          <div className="bg-dark-800 rounded-xl p-4 mb-6 text-center">
            <p className="text-gray-400 text-sm mb-1">الرصيد المتاح</p>
            <p className="text-3xl font-bold text-orange-400">{balance.toFixed(2)} <span className="text-lg">USDT</span></p>
          </div>
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">طريقة السحب</label>
              <select className="input" value={form.method} onChange={e => set('method', e.target.value)} required>
                <option value="">اختر طريقة...</option>
                {METHODS.map(m => <option key={m} value={m}>{m}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">عنوان المحفظة / معرّف الحساب</label>
              <input className="input" placeholder="أدخل عنوان المحفظة" value={form.wallet_address}
                onChange={e => set('wallet_address', e.target.value)} required />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">المبلغ (USDT)</label>
              <input className="input" type="number" min="5" step="0.01" placeholder="50"
                value={form.amount} onChange={e => set('amount', e.target.value)} required />
              <p className="text-xs text-gray-500 mt-1">الحد الأدنى: 5 USDT</p>
            </div>
            <button type="submit" disabled={loading || balance === 0} className="btn-primary w-full py-3 disabled:opacity-60">
              {loading ? 'جاري الإرسال...' : 'إرسال طلب السحب'}
            </button>
          </form>
        </div>

        <div className="card">
          <h2 className="font-bold mb-4">تعليمات مهمة</h2>
          <div className="space-y-3 text-sm text-gray-400">
            {['يتم خصم المبلغ من رصيدك فور إرسال الطلب', 'مدة المعالجة: 1-24 ساعة عمل', 'تأكد من صحة عنوان المحفظة قبل الإرسال', 'في حال الرفض سيُعاد الرصيد تلقائياً', 'التواصل مع الدعم لأي استفسار'].map(t => (
              <div key={t} className="flex items-start gap-2">
                <span className="text-primary-400 mt-0.5 flex-shrink-0">•</span>
                <span>{t}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="font-bold mb-4">سجل السحوبات</h2>
        {withdrawals.length === 0 ? (
          <p className="text-gray-500 text-center py-8">لا توجد سحوبات بعد</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-dark-800 text-gray-400">
                <th className="pb-3 text-right">#</th><th className="pb-3 text-right">المبلغ</th>
                <th className="pb-3 text-right">الطريقة</th><th className="pb-3 text-right">الحالة</th>
                <th className="pb-3 text-right">التاريخ</th>
              </tr></thead>
              <tbody>
                {withdrawals.map((w: any) => (
                  <tr key={w.id} className="border-b border-dark-800/50">
                    <td className="py-3 text-gray-400">{w.id}</td>
                    <td className="py-3 font-semibold text-orange-400">{w.amount} USDT</td>
                    <td className="py-3">{w.method}</td>
                    <td className="py-3"><span className={statusCls[w.status] || 'badge-pending'}>{statusLbl[w.status] || w.status}</span></td>
                    <td className="py-3 text-gray-400">{new Date(w.created_at).toLocaleDateString('ar')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
