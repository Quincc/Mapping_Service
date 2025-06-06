"""
Константы/настройки, используемые модулем sender.
Благодаря отдельному файлу не нужно импортировать `core.settings`
в каждом месте — настройки централизованы.
"""
from core.settings import settings

# URL конечной точки, куда шлём датафрейм.
DEFAULT_ENDPOINT: str = settings.SENDER_ENDPOINT  # https://api.partner.com/v1/upload

# Заголовки авторизации и маршрутизации
HDR_PROJECT: str = "X-PROJECT-ID"
HDR_APIKEY: str  = "X-API-KEY"

# Сколько раз client.py сделает retry, если получит network‑ошибку
DEFAULT_RETRIES: int = 3