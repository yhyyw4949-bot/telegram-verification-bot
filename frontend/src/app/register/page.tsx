'use client'
import { useState } from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { Shield } from 'lucide-react'
import toast from 'react-hot-toast'

export default function RegisterPage() {
  const params = useSearchParams()
  const [form, setForm] = useState({
    username: '', first_name: '', email: '', password: '',
    referral_code: params.get('ref') || '', language: 'ar'
  })
  const [loading, setLoading] = useState(false)
  const { register } = useAuthStore()
  const router = useRouter()

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await register(form)
      toast.success('تم إنشاء حسابك بنجاح!')
      router.push('/dashboard')
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'حدث خطأ')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-dark-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Shield size={28} />
          </div>
          <h1 className="text-2xl font-bold">إنشاء حساب جديد</h1>
          <p className="text-gray-400 mt-1">انضم إلى VerifPlatform اليوم</p>
        </div>

        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm text-gray-400 mb-1.5">الاسم الأول *</label>
                <input className="input" placeholder="محمد" value={form.first_name}
                  onChange={e => set('first_name', e.target.value)} required />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1.5">اسم المستخدم *</label>
                <input className="input" placeholder="username" value={form.username}
                  onChange={e => set('username', e.target.value)} required />
              </div>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">البريد الإلكتروني</label>
              <input className="input" type="email" placeholder="email@example.com"
                value={form.email} onChange={e => set('email', e.target.value)} />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">كلمة المرور *</label>
              <input className="input" type="password" placeholder="••••••••"
                value={form.password} onChange={e => set('password', e.target.value)} required />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">كود الإحالة (اختياري)</label>
              <input className="input" placeholder="XXXXXXXX"
                value={form.referral_code} onChange={e => set('referral_code', e.target.value)} />
            </div>
            <button type="submit" disabled={loading}
              className="btn-primary w-full py-3 disabled:opacity-60">
              {loading ? 'جاري الإنشاء...' : 'إنشاء الحساب'}
            </button>
          </form>
        </div>

        <p className="text-center text-gray-400 mt-6 text-sm">
          لديك حساب؟{' '}
          <Link href="/login" className="text-primary-400 hover:text-primary-300">تسجيل الدخول</Link>
        </p>
      </div>
    </div>
  )
}
