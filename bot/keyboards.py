from telebot import types
from config import PLATFORMS, VERIFICATION_TYPES


def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        types.KeyboardButton("🛒 شراء توثيق"),
        types.KeyboardButton("💰 رصيدي"),
        types.KeyboardButton("💳 إيداع"),
        types.KeyboardButton("💸 سحب"),
        types.KeyboardButton("📋 طلباتي"),
        types.KeyboardButton("🔗 الإحالات"),
        types.KeyboardButton("📞 الدعم الفني"),
        types.KeyboardButton("ℹ️ معلومات الخدمة"),
    )
    return kb


def admin_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        types.KeyboardButton("📦 الطلبات المعلقة"),
        types.KeyboardButton("💳 الإيداعات المعلقة"),
        types.KeyboardButton("💸 السحوبات المعلقة"),
        types.KeyboardButton("📊 الإحصائيات"),
        types.KeyboardButton("❌ حظر مستخدم"),
        types.KeyboardButton("🔓 فك حظر مستخدم"),
        types.KeyboardButton("📢 رسالة جماعية"),
        types.KeyboardButton("⚙️ الإعدادات"),
        types.KeyboardButton("🔙 القائمة الرئيسية"),
    )
    return kb


def platforms_keyboard():
    kb = types.InlineKeyboardMarkup()
    for p in PLATFORMS:
        kb.add(types.InlineKeyboardButton(p, callback_data=f"platform_{p}"))
    kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    return kb


def verification_types_keyboard(platform: str):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("💼 توثيق عبر الحساب", callback_data=f"vtype_account_{platform}"))
    if platform == "Bybit":
        kb.add(types.InlineKeyboardButton("🔗 توثيق عبر الرابط", callback_data=f"vtype_link_{platform}"))
    kb.add(types.InlineKeyboardButton("🛠️ توثيق يدوي", callback_data=f"vtype_manual_{platform}"))
    kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="buy_verification"))
    return kb


def payment_methods_keyboard(methods: list):
    kb = types.InlineKeyboardMarkup()
    for m in methods:
        kb.add(types.InlineKeyboardButton(m["name"], callback_data=f"pay_method_{m['name']}"))
    kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    return kb


def withdrawal_methods_keyboard():
    kb = types.InlineKeyboardMarkup()
    for method in ["TON", "USDT (TRC20)", "USDT (ERC20)", "Binance Pay"]:
        kb.add(types.InlineKeyboardButton(method, callback_data=f"wd_method_{method}"))
    kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    return kb


def confirm_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ تأكيد", callback_data="confirm"),
        types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel"),
    )
    return kb
