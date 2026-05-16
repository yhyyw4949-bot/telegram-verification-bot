'use client'
import Link from 'next/link'
import { Shield, Zap, Globe, Star, ArrowLeft, CheckCircle } from 'lucide-react'

const platforms = ['Binance', 'Bybit', 'KuCoin', 'Bitget', 'Gate.io']
const features = [
  { icon: Shield, title: 'آمن 100%', desc: 'جميع المعاملات مشفرة ومحمية بأعلى معايير الأمان' },
  { icon: Zap, title: 'سريع وفعّال', desc: 'معالجة فورية للطلبات مع إشعارات لحظية' },
  { icon: Globe, title: 'منصات متعددة', desc: 'ندعم أكبر منصات تداول العملات الرقمية' },
  { icon: Star, title: 'موثوق به', desc: 'آلاف العملاء الراضين ونظام تقييم شفاف' },
]

export default function HomePage() {
  return (
    <div className="min-h-screen bg-dark-950 text-white">
      {/* Navbar */}
      <nav className="border-b border-dark-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <Shield size={18} />
          </div>
          <span className="font-bold text-lg">VerifPlatform</span>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/login" className="text-gray-400 hover:text-white transition-colors px-4 py-2">تسجيل الدخول</Link>
          <Link href="/register" className="btn-primary text-sm">إنشاء حساب</Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="text-center py-24 px-6">
        <div className="inline-flex items-center gap-2 bg-primary-600/20 text-primary-400 px-4 py-1.5 rounded-full text-sm mb-6">
          <CheckCircle size={14} /> منصة التوثيق الأولى في المنطقة
        </div>
        <h1 className="text-5xl md:text-6xl font-extrabold mb-6 leading-tight">
          احصل على توثيق <br />
          <span className="text-primary-500">منصات التداول</span> بسهولة
        </h1>
        <p className="text-gray-400 text-xl max-w-2xl mx-auto mb-10">
          خدمات توثيق احترافية وسريعة لمنصات Binance و Bybit و KuCoin وغيرها. نظام آمن وموثوق مع دعم على مدار الساعة.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/register" className="btn-primary flex items-center justify-center gap-2 text-base px-8 py-3">
            ابدأ الآن مجاناً <ArrowLeft size={18} />
          </Link>
          <Link href="/marketplace" className="btn-secondary flex items-center justify-center gap-2 text-base px-8 py-3">
            تصفح الخدمات
          </Link>
        </div>
      </section>

      {/* Platforms */}
      <section className="py-12 border-y border-dark-800">
        <p className="text-center text-gray-500 mb-8 text-sm uppercase tracking-widest">المنصات المدعومة</p>
        <div className="flex flex-wrap justify-center gap-6 px-6">
          {platforms.map(p => (
            <div key={p} className="bg-dark-900 border border-dark-800 rounded-xl px-8 py-4 text-lg font-bold text-white">
              {p}
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-6 max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">لماذا VerifPlatform؟</h2>
        <div className="grid md:grid-cols-2 gap-6">
          {features.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="card flex items-start gap-4 hover:border-primary-800 transition-colors">
              <div className="w-12 h-12 bg-primary-600/20 rounded-xl flex items-center justify-center flex-shrink-0">
                <Icon size={22} className="text-primary-400" />
              </div>
              <div>
                <h3 className="font-bold text-lg mb-1">{title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 text-center">
        <div className="bg-gradient-to-r from-primary-900/40 to-primary-800/20 border border-primary-800/30 rounded-3xl p-12 max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold mb-4">جاهز للبدء؟</h2>
          <p className="text-gray-400 mb-8">انضم إلى آلاف المستخدمين الراضين اليوم</p>
          <Link href="/register" className="btn-primary text-lg px-10 py-3.5 inline-flex items-center gap-2">
            إنشاء حساب مجاني <ArrowLeft size={20} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-dark-800 py-8 text-center text-gray-500 text-sm">
        <p>© 2025 VerifPlatform. جميع الحقوق محفوظة.</p>
      </footer>
    </div>
  )
}
