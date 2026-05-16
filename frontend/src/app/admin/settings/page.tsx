'use client'
import { useEffect, useState } from 'react'
import api from '@/lib/api'
import toast from 'react-hot-toast'
import { Settings, Plus, Trash2 } from 'lucide-react'

const SETTING_LABELS: Record<string, string> = {
  min_deposit: 'الحد الأدنى للإيداع (USDT)',
  min_withdrawal: 'الحد الأدنى للسحب (USDT)',
  referral_reward: 'مكافأة الإحالة (USDT)',
  support_username: 'اسم مستخدم الدعم',
  platform_name: 'اسم المنصة',
  maintenance_mode: 'وضع الصيانة (true/false)',
}

export default function AdminSettingsPage() {
  const [settings, setSettings] = useState<Record<string, string>>({})
  const [methods, setMethods] = useState<any[]>([])
  const [newMethod, setNewMethod] = useState({ name: '', wallet_address: '', description: '', instructions: '' })
  const [loading, setLoading] = useState(true)

  const load = () => {
    Promise.all([
      api.get('/admin/settings'),
      api.get('/admin/payment-methods'),
    ]).then(([s, m]) => { setSettings(s.data); setMethods(m.data) }).finally(() => setLoading(false))
  }
  useEffect(() => { load() }, [])

  const saveSetting = async (key: string, value: string) => {
    try { await api.put('/admin/settings', { key, value }); toast.success('تم الحفظ!') }
    catch { toast.error('حدث خطأ') }
  }

  const addMethod = async (e: React.FormEvent) => {
    e.preventDefault()
    try { await api.post('/admin/payment-methods', newMethod); toast.success('تم إضافة طريقة الدفع!'); setNewMethod({ name: '', wallet_address: '', description: '', instructions: '' }); load() }
    catch { toast.error('حدث خطأ') }
  }

  const deleteMethod = async (id: number) => {
    if (!confirm('هل أنت متأكد؟')) return
    try { await api.delete(`/admin/payment-methods/${id}`); toast.success('تم الحذف!'); load() }
    catch { toast.error('حدث خطأ') }
  }

  if (loading) return <div className="flex justify-center py-20"><div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold flex items-center gap-2"><Settings className="text-gray-400" /> الإعدادات</h1>

      {/* Platform settings */}
      <div className="card">
        <h2 className="font-bold mb-6">إعدادات المنصة</h2>
        <div className="grid md:grid-cols-2 gap-4">
          {Object.entries(settings).map(([key, value]) => (
            <div key={key}>
              <label className="block text-sm text-gray-400 mb-1.5">{SETTING_LABELS[key] || key}</label>
              <div className="flex gap-2">
                <input className="input flex-1" defaultValue={value}
                  onBlur={e => { if (e.target.value !== value) saveSetting(key, e.target.value) }}
                  onKeyDown={e => e.key === 'Enter' && saveSetting(key, (e.target as HTMLInputElement).value)} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Payment methods */}
      <div className="card">
        <h2 className="font-bold mb-6">طرق الدفع</h2>
        <div className="space-y-3 mb-6">
          {methods.map((m: any) => (
            <div key={m.id} className={`flex items-center justify-between p-4 rounded-xl border ${m.is_active ? 'border-dark-700 bg-dark-800' : 'border-red-900/30 bg-red-900/10 opacity-60'}`}>
              <div>
                <p className="font-medium">{m.name}</p>
                <p className="text-xs text-gray-400 font-mono break-all">{m.wallet_address}</p>
                {!m.is_active && <span className="text-xs text-red-400">معطل</span>}
              </div>
              {m.is_active && (
                <button onClick={() => deleteMethod(m.id)} className="text-red-400 hover:text-red-300 p-1.5 hover:bg-red-900/20 rounded-lg">
                  <Trash2 size={16} />
                </button>
              )}
            </div>
          ))}
        </div>

        <h3 className="font-semibold mb-4 flex items-center gap-2"><Plus size={18} /> إضافة طريقة دفع</h3>
        <form onSubmit={addMethod} className="grid md:grid-cols-2 gap-4">
          {[
            { key: 'name', label: 'اسم الطريقة', placeholder: 'USDT TRC20' },
            { key: 'wallet_address', label: 'عنوان المحفظة', placeholder: 'T...' },
            { key: 'description', label: 'الوصف (اختياري)', placeholder: 'تحويل عبر شبكة TRC20' },
            { key: 'instructions', label: 'التعليمات (اختياري)', placeholder: 'أرسل فقط USDT على شبكة TRC20' },
          ].map(({ key, label, placeholder }) => (
            <div key={key}>
              <label className="block text-sm text-gray-400 mb-1.5">{label}</label>
              <input className="input" placeholder={placeholder} value={(newMethod as any)[key]}
                onChange={e => setNewMethod(n => ({ ...n, [key]: e.target.value }))}
                required={key === 'name' || key === 'wallet_address'} />
            </div>
          ))}
          <div className="md:col-span-2">
            <button type="submit" className="btn-primary">إضافة طريقة الدفع</button>
          </div>
        </form>
      </div>
    </div>
  )
}
