# README: app/auth

Модуль `auth` отвечает за аутентификацию и авторизацию проектов на основе API-ключей, передаваемых в заголовках запроса. Основная цель модуля — получение текущего проекта по заголовкам и проверка его валидности.

---

## Структура модуля

### `project.py`

Функции:

* `get_current_project`: получает `project_id` и `api_key` из заголовков.

  * Проверяет, существует ли проект в базе и совпадает ли ключ.
  * При ошибках генерирует HTTP 401/404.
* `get_project_api_key`: для бекенда, чтобы вытящить ключ проекта по ID.

---

### `dependencies.py`

Функция:

* `verify_token`: (пока пустой шаблон) может быть расширен для OAuth/JWT авторизации.

---

## Пример использования

```python
@router.post("/upload")
async def upload_file(
    project = Depends(get_current_project)
):
    # project.id и project.api_key доступны
    ...
```

---

## Заметки

* Заголовки, ожидаемые от клиента:

  * `X-API-KEY`
  * `X-PROJECT-ID`
* Оборужение неверных ключей или несуществующих проектов ведёт к HTTP 401/сообщению об ошибке.

---

## Возможные улучшения

* Добавить OAuth/аутентификацию с ролями.
* Логгирование успехов/ошибок авторизации.

---
