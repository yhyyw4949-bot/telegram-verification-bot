import httpx
import logging
from config import API_BASE_URL, API_SECRET

logger = logging.getLogger(__name__)

HEADERS = {"X-Bot-Secret": API_SECRET, "Content-Type": "application/json"}
TIMEOUT = 15.0


class APIClient:
    """HTTP client connecting bot to FastAPI backend"""

    def __init__(self):
        self.base = f"{API_BASE_URL}/api/v1/bot"

    def _get(self, path: str, **kwargs) -> dict:
        try:
            with httpx.Client(timeout=TIMEOUT) as c:
                r = c.get(f"{self.base}{path}", headers=HEADERS, **kwargs)
                r.raise_for_status()
                return r.json()
        except Exception as e:
            logger.error(f"GET {path} error: {e}")
            return {}

    def _post(self, path: str, data: dict) -> dict:
        try:
            with httpx.Client(timeout=TIMEOUT) as c:
                r = c.post(f"{self.base}{path}", json=data, headers=HEADERS)
                r.raise_for_status()
                return r.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"POST {path} HTTP {e.response.status_code}: {e.response.text}")
            return {"error": e.response.json().get("detail", "API error")}
        except Exception as e:
            logger.error(f"POST {path} error: {e}")
            return {"error": str(e)}

    def sync_user(self, telegram_id: int, telegram_username: str, first_name: str,
                  last_name: str = None, referral_code: str = None) -> dict:
        return self._post("/sync-user", {
            "telegram_id": telegram_id,
            "telegram_username": telegram_username,
            "first_name": first_name,
            "last_name": last_name,
            "referral_code": referral_code,
        })

    def get_user(self, telegram_id: int) -> dict:
        return self._get(f"/user/{telegram_id}")

    def get_payment_methods(self) -> list:
        data = self._get("/payment-methods")
        return data if isinstance(data, list) else []

    def get_settings(self) -> dict:
        return self._get("/settings")

    def create_order(self, telegram_id: int, platform: str, verification_type: str,
                     account_data: str = None, verification_link: str = None) -> dict:
        return self._post("/orders", {
            "telegram_id": telegram_id,
            "platform": platform,
            "verification_type": verification_type,
            "account_data": account_data,
            "verification_link": verification_link,
        })

    def get_orders(self, telegram_id: int) -> list:
        data = self._get(f"/orders/{telegram_id}")
        return data if isinstance(data, list) else []

    def create_deposit(self, telegram_id: int, amount: float, payment_method_name: str) -> dict:
        return self._post("/deposits", {
            "telegram_id": telegram_id,
            "amount": amount,
            "payment_method_name": payment_method_name,
        })

    def create_withdrawal(self, telegram_id: int, amount: float, method: str,
                          wallet_address: str) -> dict:
        return self._post("/withdrawals", {
            "telegram_id": telegram_id,
            "amount": amount,
            "method": method,
            "wallet_address": wallet_address,
        })


api = APIClient()
