# Mapping Service

**Mapping Service** — это мини‑ETL‑платформа, которая принимает произвольные файлы (CSV/XLSX/JSON), нормализует их по настроенному маппингу, проверяет качество данных и отправляет результат во внешний REST API.

<div align="center">
<b>RAW file ➜ Parser ➜ Mapping ➜ Quality ➜ Sender ➜ External API</b>
</div>

---

## ✨ Ключевые возможности

| Шаг            | Модуль    | Что делает                                                                                                 |
| -------------- | --------- | ---------------------------------------------------------------------------------------------------------- |
| **Загрузка**   | `upload`  | Принимает файл (формой или из S3), сохраняет в `uploads/<project_id>/`, публикует событие `file_received`. |
| **Парсинг**    | `parser`  | Определяет формат, читает в `pandas.DataFrame`.                                                            |
| **Маппинг**    | `mapping` | Применяет JSON‑конфиг: переименование, типизация, трансформации строк.                                     |
| **Качество**   | `quality` | Проверки (пропуски, типы, диапазоны). Формирует `reports/<project_id>/quality_report.csv`.                 |
| **Отправка**   | `sender`  | Конвертирует DataFrame в JSON, шлёт во внешний API с ретраями и backoff’ом.                                |
| **Управление** | `project` | CRUD проектов, выдача API‑ключей, авторизация на всех защищённых эндпойнтах.                               |

---

## 🗂️ Структура репозитория

```
Mapping_Service/
├── app/
│   ├── core/           # глобальные настройки (pydantic‑BaseSettings)
│   ├── project/        # управление проектами (CRUD, auth)
│   ├── upload/         # загрузка файлов + фоновые задачи
│   ├── parser/         # чтение файлов в DataFrame
│   ├── mapping/        # применение конфигураций маппинга
│   ├── quality/        # проверки качества и отчёты
│   ├── sender/         # отправка данных наружу
│   └── auth/           # зависимость get_current_project
├── templates/          # минимальный UI (HTMX + Pico.css)
├── uploads/            # сохраняемые файлы (git‑ignored)
├── reports/            # quality‑отчёты (git‑ignored)
├── requirements.txt
└── README.md           # этот файл
```

---

## 🚀 Быстрый старт

```bash
# 1. Клонируем и создаём venv
python -m venv .venv && source .venv/bin/activate

# 2. Ставим зависимости
pip install -r requirements.txt

# 3. Экспортируем переменные окружения (минимум)
export SENDER_ENDPOINT=https://example.com/api/v1/upload

# 4. Запускаем
uvicorn app.main:app --reload
```

Откройте [http://127.0.0.1:8000/upload](http://127.0.0.1:8000/upload) — UI для загрузки.
Swagger доступен на `/docs`.

### Переменные окружения

| Var                                  | По умолчанию       | Описание                     |
| ------------------------------------ | ------------------ | ---------------------------- |
| `UPLOAD_DIR`                         | `./uploads`        | Каталог для RAW‑файлов       |
| `CONFIG_DIR`                         | `./config`         | JSON‑конфиги маппинга        |
| `SENDER_ENDPOINT`                    |  —                 | URL внешнего API             |
| `ALLOWED_EXT`                        | `.csv,.xlsx,.json` | Список расширений            |
| `DB_PATH`                            | `mapping.db`       | SQLite‑файл проектов         |
| S3 vars (`S3_ENDPOINT`, `S3_KEY`, …) |  —                 | Для `upload.store_s3_object` |

---

## 📑 Основные API‑эндпойнты

| Метод                       | URL                                   | Описание |
| --------------------------- | ------------------------------------- | -------- |
| `POST /projects/`           | Создать проект, вернуть `api_key`     |          |
| `GET  /upload`              | Простая страница загрузки (HTMX form) |          |
| `POST /upload/local`        | Загрузить файл (multipart)            |          |
| `GET  /mapping?project_id=` | Получить JSON‑конфиг маппинга         |          |
| `POST /mapping`             | Сохранить/обновить конфиг             |          |
| `POST /send/manual`         | Переотправить последний файл проекта  |          |

> Все защищённые маршруты требуют заголовков `X-PROJECT-ID` и `X-API-KEY`.

---

## 🧪 Тестирование

```bash
pytest -q
```

*Модули используют `respx` для моков HTTP и `pytest-asyncio` для async‑тестов.*

---

## 🛠️ Технологии

* **FastAPI** (+ Uvicorn) — REST & UI
* **pandas** — работа с табличными данными
* **SQLAlchemy 2.x (async)** — хранение проектов (SQLite)
* **httpx + backoff** — надёжные HTTP‑запросы
* **structlog** — структурированное логирование
* **HTMX + Pico.css** — минимальный фронт без сборщика

---

## © 2025 — Mapping Service
