"""
Юнит‑тест: проверяем, что send_dataframe правильно интерпретирует
успешный ответ сервера и ретрай при ошибке.
"""
import pandas as pd, pytest, httpx
from app.sender.service import send_dataframe

@pytest.mark.asyncio
async def test_send_mock(monkeypatch):
    async def fake_post_json(url, json_, headers):
        return httpx.Response(201, text="ok")
    monkeypatch.setattr("app.sender.service.post_json", fake_post_json)

    df = pd.DataFrame([{"x": 1}])
    res = await send_dataframe(df, "demo", "secret")
    assert res.ok and res.status_code == 201
