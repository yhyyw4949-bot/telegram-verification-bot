'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import Sidebar from '@/components/layout/Sidebar'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, fetchMe } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) { router.push('/login'); return }
    if (!user) fetchMe()
  }, [])

  useEffect(() => {
    if (!loading && user === null && !localStorage.getItem('access_token')) {
      router.push('/login')
    }
  }, [user, loading])

  if (loading || !user) {
    return (
      <div className="min-h-screen bg-dark-950 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="flex min-h-screen bg-dark-950">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <div className="max-w-6xl mx-auto p-6">{children}</div>
      </main>
    </div>
  )
}
