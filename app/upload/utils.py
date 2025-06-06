"""
Утилиты уровня «upload».

Сейчас здесь одна функция `publish_event`, которая проксирует
структурированный лог в шину событий. Если позже решите подключать
Rabbit/Kafka — меняйте реализацию здесь, а вызовы по коду останутся теми
же.
"""
import structlog, asyncio
log = structlog.get_logger()

async def publish_event(event: str, payload: dict):
    """
        Лёгкая обёртка для логирования события.

        • `evt`     – строковый код события (file_received / file_processed …)
        • `payload` – произвольный JSON-совместимый словарь
        """
    # NB: ключ 'evt', а не 'event', чтобы не конфликтовать с позиционным
    log.info("event.emitted", evt=event, payload=payload)
    await asyncio.sleep(0)
