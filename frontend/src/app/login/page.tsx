'use client'
import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { Shield, Eye, EyeOff } from 'lucide-react'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)
  const { login } = useAuthStore()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(username, password)
      toast.success('مرحباً بك!')
      router.push('/dashboard')
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'بيانات خاطئة')
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
          <h1 className="text-2xl font-bold">تسجيل الدخول</h1>
          <p className="text-gray-400 mt-1">أهلاً بك في VerifPlatform</p>
        </div>

        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">اسم المستخدم</label>
              <input
                className="input"
                placeholder="username"
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">كلمة المرور</label>
              <div className="relative">
                <input
                  className="input pl-12"
                  type={showPass ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                />
                <button type="button" onClick={() => setShowPass(!showPass)}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white">
                  {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>
            <button type="submit" disabled={loading}
              className="btn-primary w-full py-3 disabled:opacity-60 disabled:cursor-not-allowed">
              {loading ? 'جاري الدخول...' : 'تسجيل الدخول'}
            </button>
          </form>
        </div>

        <p className="text-center text-gray-400 mt-6 text-sm">
          ليس لديك حساب؟{' '}
          <Link href="/register" className="text-primary-400 hover:text-primary-300">إنشاء حساب</Link>
        </p>
      </div>
    </div>
  )
}
