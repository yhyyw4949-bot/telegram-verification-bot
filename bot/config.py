import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_SECRET = os.getenv("API_SECRET", "bot_secret_key")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")

PLATFORMS = ["Binance", "Bybit", "KuCoin", "Bitget", "Gate.io"]
VERIFICATION_TYPES = {
    "account": "توثيق عبر الحساب",
    "link": "توثيق عبر الرابط (Bybit فقط)",
    "manual": "توثيق يدوي",
}
