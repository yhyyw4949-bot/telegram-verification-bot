'use client'
import { useEffect, useState } from 'react'
import api from '@/lib/api'
import toast from 'react-hot-toast'
import { ShoppingBag, Search, Filter, Star } from 'lucide-react'
import Link from 'next/link'

const PLATFORMS = ['الكل', 'Binance', 'Bybit', 'KuCoin', 'Bitget', 'Gate.io']
const VTYPES = ['الكل', 'account', 'link', 'manual']
const VTYPE_LABELS: Record<string, string> = { account: 'عبر الحساب', link: 'عبر الرابط', manual: 'يدوي' }

export default function MarketplacePage() {
  const [listings, setListings] = useState<any[]>([])
  const [platform, setPlatform] = useState('الكل')
  const [vtype, setVtype] = useState('الكل')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [ordering, setOrdering] = useState<number | null>(null)

  const load = () => {
    setLoading(true)
    const params: any = {}
    if (platform !== 'الكل') params.platform = platform
    if (vtype !== 'الكل') params.vtype = vtype
    api.get('/marketplace/listings', { params }).then(r => setListings(r.data)).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [platform, vtype])

  const buyNow = async (listing: any) => {
    const token = typeof window !== 'undefined' && localStorage.getItem('access_token')
    if (!token) { window.location.href = '/login'; return }
    setOrdering(listing.id)
    try {
      await api.post('/marketplace/orders', {
        listing_id: listing.id,
        platform: listing.platform,
        verification_type: listing.verification_type,
      })
      toast.success('تم إرسال الطلب!')
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'حدث خطأ')
    } finally { setOrdering(null) }
  }

  const filtered = listings.filter(l =>
    !search || l.title.includes(search) || l.platform.includes(search)
  )

  return (
    <div className="min-h-screen bg-dark-950 text-white">
      {/* Header */}
      <div className="border-b border-dark-800 bg-dark-900 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/" className="text-gray-400 hover:text-white text-sm">الرئيسية</Link>
          <span className="text-gray-600">/</span>
          <span className="font-semibold">السوق</span>
        </div>
        <Link href="/login" className="btn-primary text-sm">لوحة التحكم</Link>
      </div>

      <div className="max-w-6xl mx-auto p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2"><ShoppingBag className="text-primary-400" /> سوق التوثيق</h1>
          <p className="text-gray-400 mt-1">تصفح خدمات التوثيق المتاحة</p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-3">
          <div className="relative flex-1 min-w-48">
            <Search size={16} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input className="input pr-9" placeholder="بحث..." value={search} onChange={e => setSearch(e.target.value)} />
          </div>
          <div className="flex gap-2 flex-wrap">
            {PLATFORMS.map(p => (
              <button key={p} onClick={() => setPlatform(p)}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${platform === p ? 'bg-primary-600 text-white' : 'bg-dark-800 text-gray-400 hover:bg-dark-700'}`}>
                {p}
              </button>
            ))}
          </div>
        </div>

        {/* Listings */}
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="card text-center py-16">
            <ShoppingBag size={48} className="text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">لا توجد خدمات متاحة</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map((l: any) => (
              <div key={l.id} className="card hover:border-primary-800/50 transition-all group">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <span className="bg-primary-600/20 text-primary-400 text-xs px-2 py-1 rounded-full">{l.platform}</span>
                    <span className="bg-dark-700 text-gray-400 text-xs px-2 py-1 rounded-full mr-2">{VTYPE_LABELS[l.verification_type] || l.verification_type}</span>
                  </div>
                  <div className="flex items-center gap-1 text-yellow-400 text-sm">
                    <Star size={12} fill="currentColor" />
                    <span>4.8</span>
                  </div>
                </div>
                <h3 className="font-bold mb-2">{l.title}</h3>
                {l.description && <p className="text-gray-400 text-sm mb-3 line-clamp-2">{l.description}</p>}
                <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
                  <span>⏱ {l.delivery_days} {l.delivery_days === 1 ? 'يوم' : 'أيام'}</span>
                  <span>•</span>
                  <span>{l.total_orders} طلب</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-primary-400">{l.price} <span className="text-sm">USDT</span></span>
                  <button onClick={() => buyNow(l)} disabled={ordering === l.id}
                    className="btn-primary text-sm px-5 py-2 disabled:opacity-60">
                    {ordering === l.id ? '...' : 'اشترِ الآن'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
