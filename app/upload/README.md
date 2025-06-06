# Upload module (app/upload)

## 📌 Purpose

Handles **ingress of raw data files** into the mapping-service:

* Accepts multi‑part uploads from the browser / cURL
* Can pull a file from an S3‑compatible bucket
* Saves the payload into `<UPLOAD_DIR>/<project_id>/` under a collision‑free UUID filename
* Emits structured events (`file_received`, `file_processed`, …)
* Launches the full ETL pipeline in a FastAPI background‑task

---

## 🌐 Public API

| Method | Route           | Body / Params                | Auth                        | Description                                             |
| ------ | --------------- | ---------------------------- | --------------------------- | ------------------------------------------------------- |
| `POST` | `/upload/local` | `multipart/form‑data` `file` | `X-PROJECT-ID`, `X-API-KEY` | Saves an uploaded file, returns `201` + path, fires ETL |

> **Auth** comes from the common dependency `get_current_project`.

Response example

```jsonc
{
  "detail": "file_saved",
  "path": "/abs/path/to/uploads/<project_id>/<uuid>.csv"
}
```

---

## 📂 Directory layout

```
app/upload/
├── router.py     # FastAPI endpoints
├── service.py    # I/O: local FS + S3
├── tasks.py      # background wrapper around run_full_pipeline()
├── utils.py      # publish_event()
└── schemas.py    # Pydantic DTOs
```

---

## 🛠 Key components

### service.py

* **store\_local\_file** – streams the `UploadFile` to disk in 1 MiB chunks; validates extension (see `ALLOWED_EXT`).
* **store\_s3\_object** – downloads an object via `boto3` and stores it in the same project directory.
* Both functions publish `file_received` immediately after the file hits the disk.

### tasks.py

```text
launch_pipeline → run_full_pipeline → publish file_processed/file_failed
```

Keeps HTTP handler lean; ideal place for timers, Prometheus metrics or retry‑logic if needed later.

### utils.py

Thin wrapper around `structlog` so that changing the transport (Kafka, NATS, …) won’t touch business code.

---

## ⚙️ Configuration

| Variable               | Purpose                                                        | Example                              | Default            |
| ---------------------- | -------------------------------------------------------------- | ------------------------------------ | ------------------ |
| `UPLOAD_DIR`           | Root directory for stored files                                | `./uploads`                          | `./uploads`        |
| `ALLOWED_EXT`          | Comma‑separated whitelist of extensions (lower‑case, with dot) | `.csv,.xlsx,.json`                   | `.csv,.xlsx,.json` |
| `S3_ENDPOINT`          | URL of the S3‑compatible service                               | `https://s3.us‑east‑1.amazonaws.com` | —                  |
| `S3_REGION`            | Region string                                                  | `us‑east‑1`                          | —                  |
| `S3_KEY` / `S3_SECRET` | Access credentials                                             | —                                    | —                  |

All variables are read via **core/settings.py** (Pydantic settings).

---

## 🚦 Event flow

```mermaid
sequenceDiagram
    Browser →> API: POST /upload/local (file)
    API →> service.store_local_file: stream file
    service -->> utils.publish_event: file_received
    API -->> Browser: 201 Created
    API ➤➤ bg task: launch_pipeline()
    launch_pipeline →> ETL: run_full_pipeline
    run_full_pipeline -->> publish_event: file_processed / file_failed
```

Events are logged as structured JSON; can be piped to Loki/OpenSearch or any log shipper.

---

## 🧩 Extending

* **Chunked uploads** – add a new route `/upload/multipart/init|part|complete` and store parts to temp dir.
* **Virus scan** – call a ClamAV micro‑service right after `store_local_file`.
* **Cloud storage only** – swap out `store_local_file` for an S3 `put_object` and store just the URI.

---

## 🧪 Testing hints

* Use **pytest + respx** to stub S3.
* For filesystem tests rely on `tmp_path` fixture: pass it via `monkeypatch.setattr(settings, "UPLOAD_DIR", tmp_path)`.
* Assert that `publish_event` is called (patch with `unittest.mock.AsyncMock`).

---

© Mapping‑Service team, 2025
