'use client'
import { useEffect, useState, useRef } from 'react'
import api from '@/lib/api'
import toast from 'react-hot-toast'
import { ArrowDownCircle, Copy, CheckCircle, Upload } from 'lucide-react'

export default function DepositPage() {
  const [methods, setMethods] = useState<any[]>([])
  const [selected, setSelected] = useState<any>(null)
  const [amount, setAmount] = useState('')
  const [proof, setProof] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [deposits, setDeposits] = useState<any[]>([])
  const [copied, setCopied] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    api.get('/transactions/payment-methods').then(r => setMethods(r.data)).catch(() => {})
    api.get('/transactions/deposits').then(r => setDeposits(r.data)).catch(() => {})
  }, [])

  const copy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
    toast.success('تم النسخ!')
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selected) { toast.error('اختر طريقة الدفع'); return }
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('amount', amount)
      fd.append('payment_method_id', selected.id)
      if (proof) fd.append('proof', proof)
      await api.post('/transactions/deposits', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      toast.success('تم إرسال طلب الإيداع! سيتم مراجعته خلال 30 دقيقة.')
      setAmount(''); setProof(null); setSelected(null)
      api.get('/transactions/deposits').then(r => setDeposits(r.data))
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'حدث خطأ')
    } finally {
      setLoading(false)
    }
  }

  const statusMap: Record<string, string> = { pending: 'badge-pending', approved: 'badge-approved', rejected: 'badge-rejected' }
  const statusLabel: Record<string, string> = { pending: 'قيد المراجعة', approved: 'مقبول', rejected: 'مرفوض' }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2"><ArrowDownCircle className="text-green-400" /> إيداع رصيد</h1>
        <p className="text-gray-400 mt-1">أرسل المبلغ إلى محفظة الأدمن وأرفق إثبات الدفع</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Step 1: Choose method */}
        <div className="card">
          <h2 className="font-bold mb-4">① اختر طريقة الدفع</h2>
          <div className="space-y-3">
            {methods.map(m => (
              <button key={m.id} onClick={() => setSelected(m)}
                className={`w-full text-right p-4 rounded-xl border transition-all ${selected?.id === m.id ? 'border-primary-500 bg-primary-900/20' : 'border-dark-700 bg-dark-800 hover:border-dark-600'}`}>
                <p className="font-semibold">{m.name}</p>
                {m.description && <p className="text-sm text-gray-400 mt-0.5">{m.description}</p>}
              </button>
            ))}
          </div>
        </div>

        {/* Step 2: Send & confirm */}
        <div className="card">
          <h2 className="font-bold mb-4">② أرسل وأكد الدفع</h2>
          {selected ? (
            <div className="space-y-4">
              <div className="bg-dark-800 rounded-xl p-4">
                <p className="text-sm text-gray-400 mb-1">عنوان المحفظة ({selected.name})</p>
                <div className="flex items-center gap-2">
                  <code className="text-sm text-green-400 flex-1 break-all">{selected.wallet_address}</code>
                  <button onClick={() => copy(selected.wallet_address)}
                    className="text-gray-400 hover:text-white flex-shrink-0">
                    {copied ? <CheckCircle size={18} className="text-green-400" /> : <Copy size={18} />}
                  </button>
                </div>
              </div>
              {selected.instructions && (
                <div className="bg-yellow-900/20 border border-yellow-800/30 rounded-xl p-4 text-sm text-yellow-300">
                  📌 {selected.instructions}
                </div>
              )}
              <form onSubmit={submit} className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1.5">المبلغ (USDT)</label>
                  <input className="input" type="number" min="1" step="0.01" placeholder="50"
                    value={amount} onChange={e => setAmount(e.target.value)} required />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1.5">إثبات الدفع (صورة)</label>
                  <div onClick={() => fileRef.current?.click()}
                    className="border-2 border-dashed border-dark-700 rounded-xl p-6 text-center cursor-pointer hover:border-primary-600 transition-colors">
                    {proof ? (
                      <p className="text-green-400 text-sm">✅ {proof.name}</p>
                    ) : (
                      <div className="flex flex-col items-center gap-2 text-gray-400">
                        <Upload size={24} />
                        <span className="text-sm">انقر لرفع صورة الإثبات</span>
                      </div>
                    )}
                  </div>
                  <input ref={fileRef} type="file" accept="image/*" className="hidden"
                    onChange={e => setProof(e.target.files?.[0] || null)} />
                </div>
                <button type="submit" disabled={loading} className="btn-primary w-full py-3">
                  {loading ? 'جاري الإرسال...' : 'إرسال طلب الإيداع'}
                </button>
              </form>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-12">اختر طريقة دفع من اليمين</p>
          )}
        </div>
      </div>

      {/* History */}
      <div className="card">
        <h2 className="font-bold mb-4">سجل الإيداعات</h2>
        {deposits.length === 0 ? (
          <p className="text-gray-500 text-center py-8">لا توجد إيداعات بعد</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-dark-800 text-gray-400">
                <th className="pb-3 text-right">#</th>
                <th className="pb-3 text-right">المبلغ</th>
                <th className="pb-3 text-right">الطريقة</th>
                <th className="pb-3 text-right">الحالة</th>
                <th className="pb-3 text-right">التاريخ</th>
              </tr></thead>
              <tbody>
                {deposits.map((d: any) => (
                  <tr key={d.id} className="border-b border-dark-800/50">
                    <td className="py-3 text-gray-400">{d.id}</td>
                    <td className="py-3 font-semibold text-green-400">{d.amount} USDT</td>
                    <td className="py-3">{d.payment_method_name}</td>
                    <td className="py-3"><span className={statusMap[d.status] || 'badge-pending'}>{statusLabel[d.status] || d.status}</span></td>
                    <td className="py-3 text-gray-400">{new Date(d.created_at).toLocaleDateString('ar')}</td>
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
