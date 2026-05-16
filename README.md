# 🛡️ VerifPlatform — منصة التوثيق الاحترافية

منصة متكاملة لشراء وبيع خدمات التوثيق لمنصات العملات الرقمية (Binance, Bybit, KuCoin, Bitget, Gate.io).

---

## 📁 هيكل المشروع

```
verif_platform/
├── backend/          # FastAPI (Python) — REST API
├── bot/              # Telegram Bot (pyTelegramBotAPI)
├── frontend/         # Next.js 14 (React/TypeScript) — الموقع
├── docker-compose.yml
└── .env.example
```

---

## ⚡ طريقة التشغيل السريعة (Docker)

### المتطلبات
- Docker Desktop (أو Docker + Docker Compose)
- بوت تيليغرام مُنشأ من @BotFather

### الخطوات

```bash
# 1. انسخ ملف البيئة
cp .env.example .env

# 2. عدّل .env وأضف بيانات البوت
nano .env
# أضف: BOT_TOKEN=توكن_البوت_هنا
# أضف: ADMIN_IDS=رقم_تيليغرام_الخاص_بك

# 3. شغّل المنصة كاملة
docker compose up --build -d

# 4. افتح المتصفح
# الموقع:       http://localhost:3000
# API Docs:     http://localhost:8000/api/docs
# Admin Panel:  http://localhost:3000/admin  (بعد تعيين is_admin=true)
```

---

## 🖥️ تشغيل يدوي (بدون Docker)

### 1. قاعدة البيانات والكاش

تحتاج PostgreSQL و Redis يعملان محلياً، أو استخدم:
```bash
docker compose up postgres redis -d
```

### 2. Backend (FastAPI)

```bash
cd backend

# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate      # Linux/Mac
# أو: venv\Scripts\activate   # Windows

# تثبيت المكتبات
pip install -r requirements.txt

# نسخ وتعديل الإعدادات
cp ../.env.example .env
# عدّل DATABASE_URL و REDIS_URL و BOT_TOKEN و ADMIN_IDS

# تشغيل السيرفر
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

الـ API يعمل على: **http://localhost:8000**
توثيق الـ API: **http://localhost:8000/api/docs**

### 3. Bot (Telegram)

```bash
cd bot

# تثبيت المكتبات
pip install -r requirements.txt

# نسخ الإعدادات
cp ../.env.example .env
# تأكد من: BOT_TOKEN, ADMIN_IDS, API_BASE_URL=http://localhost:8000, API_SECRET

# تشغيل البوت
python main.py
```

### 4. Frontend (Next.js)

```bash
cd frontend

# تثبيت المكتبات
npm install

# إنشاء ملف بيئة
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_WS_URL=ws://localhost:8000" >> .env.local

# وضع التطوير
npm run dev
# أو للإنتاج:
npm run build && npm start
```

الموقع يعمل على: **http://localhost:3000**

---

## 🔑 إعداد حساب الأدمن

بعد تشغيل المنصة:

1. سجّل حساباً عادياً على الموقع أو عبر البوت
2. شغّل الأمر التالي في PostgreSQL لترقيته لأدمن:

```sql
-- اتصل بقاعدة البيانات
docker exec -it verif_postgres psql -U verifuser -d verifdb

-- ارقّ المستخدم (غيّر 1 لرقم ID الخاص بك)
UPDATE users SET is_admin = true WHERE id = 1;

-- أو عبر اسم المستخدم
UPDATE users SET is_admin = true WHERE username = 'your_username';
\q
```

3. سجّل خروجاً ودخولاً، ستظهر لوحة الأدمن في القائمة الجانبية.

---

## ⚙️ إعداد الأدمن الأولي

بعد تسجيل الدخول كأدمن:

### 1. إضافة طرق الدفع
- اذهب إلى `/admin/settings`
- أضف طريقة دفع (مثل USDT TRC20) مع عنوان المحفظة

### 2. ضبط الإعدادات
- حدد الحد الأدنى للإيداع والسحب
- حدد مكافأة الإحالة
- أضف اسم مستخدم الدعم الفني

### 3. مراجعة الطلبات
- الإيداعات المعلقة: `/admin/deposits`
- السحوبات المعلقة: `/admin/withdrawals`
- الطلبات: `/admin/orders`

---

## 🤖 وظائف البوت

```
/start          — تسجيل وبدء الاستخدام
🛒 شراء توثيق  — شراء خدمة توثيق
💰 رصيدي       — عرض الرصيد الحالي
💳 إيداع        — إيداع رصيد
💸 سحب          — سحب رصيد
📋 طلباتي       — عرض آخر الطلبات
🔗 الإحالات     — رابط الإحالة الخاص بك
📞 الدعم الفني  — التواصل مع الدعم
/admin          — لوحة الأدمن (للمشرفين فقط)
```

### إحالة عبر البوت
أرسل `/start REF_CODE` أو شارك رابط `https://t.me/YOUR_BOT?start=REF_CODE`

---

## 🌐 صفحات الموقع

| الصفحة | الرابط |
|--------|--------|
| الرئيسية | `/` |
| تسجيل الدخول | `/login` |
| إنشاء حساب | `/register` |
| السوق | `/marketplace` |
| لوحة التحكم | `/dashboard` |
| إيداع | `/dashboard/deposit` |
| سحب | `/dashboard/withdraw` |
| طلباتي | `/dashboard/orders` |
| الإحالات | `/dashboard/referral` |
| الدعم الفني | `/dashboard/support` |
| أدمن — الرئيسية | `/admin` |
| أدمن — المستخدمون | `/admin/users` |
| أدمن — الإيداعات | `/admin/deposits` |
| أدمن — السحوبات | `/admin/withdrawals` |
| أدمن — الطلبات | `/admin/orders` |
| أدمن — الإعدادات | `/admin/settings` |

---

## 🔌 API Endpoints الرئيسية

```
POST  /api/v1/auth/register        — تسجيل
POST  /api/v1/auth/login           — دخول
GET   /api/v1/users/me             — بيانات المستخدم الحالي
GET   /api/v1/users/me/balance     — الرصيد
GET   /api/v1/marketplace/listings — قائمة الخدمات
POST  /api/v1/marketplace/orders   — إنشاء طلب
GET   /api/v1/transactions/payment-methods — طرق الدفع
POST  /api/v1/transactions/deposits        — طلب إيداع
POST  /api/v1/transactions/withdrawals     — طلب سحب
GET   /api/v1/admin/stats          — إحصائيات (أدمن)
GET   /api/v1/admin/deposits/pending — إيداعات معلقة
```

التوثيق الكامل: **http://localhost:8000/api/docs**

---

## 🔒 ملاحظات أمان

- غيّر `SECRET_KEY` في `.env` لقيمة عشوائية قوية في الإنتاج
- غيّر `API_SECRET` (المفتاح المشترك بين البوت والباكند)
- استخدم HTTPS في الإنتاج
- لا تنشر `.env` أبداً في Git (مُضاف لـ .gitignore)

---

## 📞 تقنيات المستخدمة

| المكوّن | التقنية |
|---------|---------|
| Backend API | FastAPI + SQLAlchemy + PostgreSQL |
| Cache | Redis |
| Bot | pyTelegramBotAPI |
| Frontend | Next.js 14 + TypeScript + Tailwind CSS |
| State | Zustand |
| Charts | Recharts |
| Deploy | Docker Compose |
