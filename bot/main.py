#!/usr/bin/env python3
"""
VerifPlatform Telegram Bot
Fully connected to the FastAPI backend via internal API.
"""
import logging
import telebot
from telebot import types
from config import BOT_TOKEN, ADMIN_IDS, PLATFORMS
from api_client import api
from keyboards import (main_menu, admin_menu, platforms_keyboard,
                        verification_types_keyboard, payment_methods_keyboard,
                        withdrawal_methods_keyboard, confirm_keyboard)
from utils.spam import is_spam

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("VerifBot")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


# ── Helpers ────────────────────────────────────────────────
def is_admin(user_id: int) -> bool:
    if user_id in ADMIN_IDS:
        return True
    u = api.get_user(user_id)
    return u.get("is_admin", False)


def get_user_or_block(message) -> dict | None:
    u = api.get_user(message.from_user.id)
    if u.get("is_banned"):
        bot.send_message(message.from_user.id, "❌ حسابك مُحظور. تواصل مع الدعم الفني.")
        return None
    return u


# ── /start ─────────────────────────────────────────────────
@bot.message_handler(commands=["start"])
def cmd_start(message):
    user_id = message.from_user.id
    ref_code = None
    if message.text and len(message.text.split()) > 1:
        ref_code = message.text.split()[1]

    user = api.sync_user(
        telegram_id=user_id,
        telegram_username=message.from_user.username or "",
        first_name=message.from_user.first_name or "",
        last_name=message.from_user.last_name,
        referral_code=ref_code,
    )

    settings = api.get_settings()
    platform_name = settings.get("platform_name", "VerifPlatform")

    welcome = f"""
👋 <b>أهلاً بك في {platform_name}!</b>

نوفر خدمات توثيق آمنة وسريعة للمنصات التالية:
✅ Binance | ✅ Bybit | ✅ KuCoin | ✅ Bitget | ✅ Gate.io

اختر من القائمة أدناه للبدء 👇
"""
    bot.send_message(user_id, welcome, reply_markup=main_menu())
    logger.info(f"User {user_id} started bot")


# ── /admin ─────────────────────────────────────────────────
@bot.message_handler(commands=["admin"])
def cmd_admin(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(user_id, "❌ غير مصرح.")
        return
    bot.send_message(user_id, "🛡️ <b>لوحة التحكم الإدارية</b>", reply_markup=admin_menu())


# ── شراء توثيق ─────────────────────────────────────────────
@bot.message_handler(func=lambda m: m.text and "شراء توثيق" in m.text)
def buy_verification(message):
    if is_spam(message.from_user.id, "buy"):
        bot.send_message(message.from_user.id, "⏰ يرجى الانتظار قليلاً.")
        return
    if not get_user_or_block(message):
        return
    bot.send_message(message.from_user.id, "🏢 <b>اختر المنصة المطلوبة:</b>",
                     reply_markup=platforms_keyboard())


# ── رصيدي ──────────────────────────────────────────────────
@bot.message_handler(func=lambda m: m.text and "رصيدي" in m.text)
def my_balance(message):
    user = get_user_or_block(message)
    if not user:
        return
    bot.send_message(message.from_user.id,
                     f"💰 <b>رصيدك الحالي:</b> <code>{user.get('balance', 0):.2f} USDT</code>",
                     reply_markup=main_menu())


# ── إيداع ──────────────────────────────────────────────────
@bot.message_handler(func=lambda m: m.text and "إيداع" in m.text)
def deposit(message):
    if not get_user_or_block(message):
        return
    methods = api.get_payment_methods()
    if not methods:
        bot.send_message(message.from_user.id,
                         "❌ لا توجد طرق دفع متاحة حالياً. تواصل مع الدعم.")
        return
    bot.send_message(message.from_user.id, "💳 <b>اختر طريقة الدفع:</b>",
                     reply_markup=payment_methods_keyboard(methods))


# ── سحب ───────────────────────────────────────────────────
@bot.message_handler(func=lambda m: m.text and "سحب" in m.text)
def withdraw(message):
    user = get_user_or_block(message)
    if not user:
        return
    balance = user.get("balance", 0)
    settings = api.get_settings()
    min_wd = float(settings.get("min_withdrawal", 5))
    if balance < min_wd:
        bot.send_message(message.from_user.id,
                         f"❌ رصيدك ({balance:.2f}) أقل من الحد الأدنى للسحب ({min_wd} USDT).")
        return
    bot.send_message(message.from_user.id,
                     f"💸 <b>الرصيد المتاح:</b> <code>{balance:.2f} USDT</code>\n\nاختر طريقة السحب:",
                     reply_markup=withdrawal_methods_keyboard())


# ── طلباتي ─────────────────────────────────────────────────
@bot.message_handler(func=lambda m: m.text and "طلباتي" in m.text)
def my_orders(message):
    user = get_user_or_block(message)
    if not user:
        return
    orders = api.get_orders(message.from_user.id)
    if not orders:
        bot.send_message(message.from_user.id, "📋 لا توجد طلبات لديك.", reply_markup=main_menu())
        return
    status_ar = {
        "pending": "⏳ قيد الانتظار",
        "paid": "💳 مدفوع",
        "in_progress": "🔄 جاري التنفيذ",
        "completed": "✅ مكتمل",
        "rejected": "❌ مرفوض",
        "disputed": "⚠️ نزاع",
    }
    text = "📋 <b>طلباتك الأخيرة:</b>\n\n"
    for o in orders[:5]:
        st = status_ar.get(o.get("status", ""), o.get("status", ""))
        text += f"• طلب #{o['id']} — {o['platform']} — {st}\n"
    bot.send_message(message.from_user.id, text, reply_markup=main_menu())


# ── الإحالات ───────────────────────────────────────────────
@bot.message_handler(func=lambda m: m.text and "الإحالات" in m.text)
def referrals(message):
    user = get_user_or_block(message)
    if not user:
        return
    code = user.get("referral_code", "")
    bot_info = bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={code}"
    settings = api.get_settings()
    reward = settings.get("referral_reward", "2")
    text = f"""
🔗 <b>نظام الإحالات</b>

رابط الإحالة الخاص بك:
<code>{ref_link}</code>

💰 مكافأة كل إحالة: <b>{reward} USDT</b>

شارك الرابط مع أصدقائك واحصل على مكافأة فورية عند تسجيلهم!
"""
    bot.send_message(message.from_user.id, text, reply_markup=main_menu())


# ── الدعم الفني ────────────────────────────────────────────
@bot.message_handler(func=lambda m: m.text and "الدعم الفني" in m.text)
def support(message):
    settings = api.get_settings()
    username = settings.get("support_username", "support_admin")
    bot.send_message(message.from_user.id,
                     f"📞 <b>الدعم الفني</b>\n\n👤 @{username}\n\nتواصل مباشرة مع فريق الدعم.",
                     reply_markup=main_menu())


# ── معلومات الخدمة ─────────────────────────────────────────
@bot.message_handler(func=lambda m: m.text and "معلومات" in m.text)
def service_info(message):
    text = """
ℹ️ <b>معلومات الخدمة</b>

🏢 <b>المنصات المدعومة:</b>
• Binance  • Bybit  • KuCoin  • Bitget  • Gate.io

📝 <b>أنواع التوثيق:</b>
• توثيق عبر الحساب (Email:Password)
• توثيق عبر الرابط (Bybit فقط)
• توثيق يدوي

💳 <b>طرق الدفع:</b>
• TON  • USDT  • Binance Pay

🔒 جميع المعاملات مؤمنة وسرية.
"""
    bot.send_message(message.from_user.id, text, reply_markup=main_menu())


# ══════════════════════════════════════════════════════════
# ADMIN HANDLERS
# ══════════════════════════════════════════════════════════

@bot.message_handler(func=lambda m: m.text and "القائمة الرئيسية" in m.text)
def back_main(message):
    bot.send_message(message.from_user.id, "🏠 القائمة الرئيسية", reply_markup=main_menu())


@bot.message_handler(func=lambda m: m.text and "الإيداعات المعلقة" in m.text)
def admin_pending_deposits(message):
    if not is_admin(message.from_user.id):
        return
    # Would call admin API
    bot.send_message(message.from_user.id,
                     "💳 الإيداعات المعلقة:\n\nللمراجعة الكاملة، استخدم لوحة التحكم الإدارية على الموقع.",
                     reply_markup=admin_menu())


@bot.message_handler(func=lambda m: m.text and "الإحصائيات" in m.text)
def admin_stats(message):
    if not is_admin(message.from_user.id):
        return
    # Could call /api/v1/admin/stats with admin JWT
    bot.send_message(message.from_user.id,
                     "📊 <b>الإحصائيات</b>\n\nللإحصائيات التفصيلية، تفضل بزيارة لوحة التحكم على الموقع.",
                     reply_markup=admin_menu())


# ══════════════════════════════════════════════════════════
# CALLBACK QUERY HANDLERS
# ══════════════════════════════════════════════════════════

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data

    # ── Platform selection ──
    if data.startswith("platform_") or data == "buy_verification":
        if data == "buy_verification":
            bot.edit_message_text("🏢 <b>اختر المنصة المطلوبة:</b>",
                                   user_id, call.message.message_id,
                                   reply_markup=platforms_keyboard(), parse_mode="HTML")
            return
        platform = data.replace("platform_", "")
        bot.edit_message_text(f"🏢 <b>المنصة:</b> {platform}\n\n📝 اختر نوع التوثيق:",
                               user_id, call.message.message_id,
                               reply_markup=verification_types_keyboard(platform), parse_mode="HTML")

    # ── Verification type ──
    elif data.startswith("vtype_"):
        parts = data.split("_", 2)
        vtype = parts[1]
        platform = parts[2]
        prompts = {
            "account": "📝 أرسل بيانات الحساب بالصيغة:\n<code>email@example.com:password</code>",
            "link": "🔗 أرسل رابط التوثيق:",
            "manual": "📝 أرسل تفاصيل طلبك (المنصة والنوع والبيانات المطلوبة):",
        }
        bot.answer_callback_query(call.id)
        msg = bot.send_message(user_id, prompts.get(vtype, "أرسل البيانات:"), parse_mode="HTML")
        bot.register_next_step_handler(msg, process_verification_input, platform, vtype)

    # ── Payment method ──
    elif data.startswith("pay_method_"):
        method_name = data.replace("pay_method_", "")
        methods = api.get_payment_methods()
        method = next((m for m in methods if m["name"] == method_name), None)
        if not method:
            bot.answer_callback_query(call.id, "خطأ: طريقة الدفع غير متاحة")
            return
        settings = api.get_settings()
        min_dep = settings.get("min_deposit", "5")
        text = (f"💳 <b>طريقة الدفع:</b> {method['name']}\n\n"
                f"📍 <b>عنوان المحفظة:</b>\n<code>{method['wallet_address']}</code>\n\n")
        if method.get("instructions"):
            text += f"📌 <b>التعليمات:</b>\n{method['instructions']}\n\n"
        text += f"💡 الحد الأدنى للإيداع: {min_dep} USDT\n\n⬇️ أرسل المبلغ الذي قمت بتحويله:"
        bot.answer_callback_query(call.id)
        msg = bot.send_message(user_id, text, parse_mode="HTML")
        bot.register_next_step_handler(msg, process_deposit_amount, method_name)

    # ── Withdrawal method ──
    elif data.startswith("wd_method_"):
        method = data.replace("wd_method_", "")
        bot.answer_callback_query(call.id)
        msg = bot.send_message(user_id, f"💸 <b>طريقة السحب:</b> {method}\n\nأرسل المبلغ ثم العنوان بالصيغة:\n<code>50 - عنوان_المحفظة</code>", parse_mode="HTML")
        bot.register_next_step_handler(msg, process_withdrawal_input, method)

    # ── Confirm / Cancel ──
    elif data == "confirm":
        bot.answer_callback_query(call.id, "✅ تم التأكيد")
        bot.edit_message_text("✅ تم إرسال طلبك بنجاح!", user_id, call.message.message_id)

    elif data in ("cancel", "back_main"):
        bot.answer_callback_query(call.id)
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(user_id, "🏠 تم الإلغاء", reply_markup=main_menu())


# ── Step handlers ──────────────────────────────────────────
def process_verification_input(message, platform: str, vtype: str):
    user_id = message.from_user.id
    text = message.text or ""
    account_data = text if vtype == "account" else None
    link = text if vtype == "link" else None

    result = api.create_order(user_id, platform, vtype, account_data, link)
    if "error" in result:
        bot.send_message(user_id, f"❌ خطأ: {result['error']}", reply_markup=main_menu())
        return
    bot.send_message(user_id,
                     f"✅ <b>تم إرسال طلبك بنجاح!</b>\n\n"
                     f"📦 رقم الطلب: <code>#{result.get('order_id')}</code>\n"
                     f"🏢 المنصة: {platform}\n"
                     f"📊 الحالة: ⏳ قيد المراجعة\n\n"
                     f"سيتم إشعارك فور معالجة طلبك.",
                     reply_markup=main_menu(), parse_mode="HTML")


def process_deposit_amount(message, method_name: str):
    user_id = message.from_user.id
    try:
        amount = float(message.text.strip().replace(",", "."))
    except ValueError:
        bot.send_message(user_id, "❌ المبلغ غير صالح. أرسل رقماً صحيحاً.", reply_markup=main_menu())
        return

    result = api.create_deposit(user_id, amount, method_name)
    if "error" in result:
        bot.send_message(user_id, f"❌ {result['error']}", reply_markup=main_menu())
        return

    bot.send_message(user_id,
                     f"✅ <b>تم استلام طلب الإيداع!</b>\n\n"
                     f"💰 المبلغ: <code>{amount} USDT</code>\n"
                     f"🔢 رقم الطلب: <code>#{result.get('deposit_id')}</code>\n\n"
                     f"سيتم مراجعة طلبك وتحديث رصيدك خلال 30 دقيقة.",
                     reply_markup=main_menu(), parse_mode="HTML")


def process_withdrawal_input(message, method: str):
    user_id = message.from_user.id
    try:
        parts = message.text.strip().split("-", 1)
        amount = float(parts[0].strip())
        wallet = parts[1].strip() if len(parts) > 1 else ""
    except (ValueError, IndexError):
        bot.send_message(user_id, "❌ صيغة خاطئة. مثال: <code>50 - عنوان_المحفظة</code>",
                         reply_markup=main_menu(), parse_mode="HTML")
        return

    result = api.create_withdrawal(user_id, amount, method, wallet)
    if "error" in result:
        bot.send_message(user_id, f"❌ {result['error']}", reply_markup=main_menu())
        return

    bot.send_message(user_id,
                     f"✅ <b>تم استلام طلب السحب!</b>\n\n"
                     f"💸 المبلغ: <code>{amount} USDT</code>\n"
                     f"📍 العنوان: <code>{wallet}</code>\n"
                     f"🔢 رقم الطلب: <code>#{result.get('withdrawal_id')}</code>\n\n"
                     f"سيتم معالجة طلبك خلال 24 ساعة.",
                     reply_markup=main_menu(), parse_mode="HTML")


# ── Catch-all ──────────────────────────────────────────────
@bot.message_handler(func=lambda m: True)
def handle_unknown(message):
    bot.send_message(message.from_user.id,
                     "❓ لم أفهم رسالتك. استخدم الأزرار أدناه.",
                     reply_markup=main_menu())


# ── Main ───────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("🤖 VerifPlatform Bot starting...")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
    finally:
        logger.info("Bot stopped.")
