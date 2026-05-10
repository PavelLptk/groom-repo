# GroomCare — монорепозиторий

Структура: **`backend/`** — API (FastAPI), **`frontend/`** — интерфейс (Vite + React).

## Быстрый старт (одна команда для dev)

Первый раз после клонирования:

1. Скопировать `backend/.env.example` в `backend/.env` (и при необходимости поправить `CORS_ORIGINS` — по умолчанию подходит Vite: `http://localhost:5173`).
2. В **корне репозитория**:

   ```bash
   npm run setup
   ```

   Создаётся `backend/.venv`, ставятся Python-зависимости и `npm`-пакеты фронта, в корне — `concurrently` и `run-script-os` для скриптов.

3. Запуск API и Vite **одновременно**:

   ```bash
   npm run dev
   ```

   Откройте фронт по адресу из вывода Vite (обычно `http://localhost:5173`). Запросы к `/api` проксируются на **GroomCare API** на `http://127.0.0.1:8010` (см. `frontend/vite.config.js`). Порт **8010** выбран, чтобы не пересекаться с другими сервисами на `8000`.

**Требования:** Node.js с `npm`, Python 3 с командой `python` (Windows) или `python3` (macOS/Linux).

---

## Запуск вручную (без корневого npm)

### Бэкенд

1. Каталог `backend/`.
2. `python -m venv .venv`, активировать venv, `pip install -r requirements.txt`.
3. Файл `.env` рядом с `backend/.env.example`.
4. `uvicorn app.main:app --reload --host 0.0.0.0 --port 8010`

Файл `.env` ищется **в каталоге `backend/`** независимо от рабочей директории процесса.

### Фронтенд

1. Каталог `frontend/`: `npm install`, затем `npm run dev`.

Когда подключите реальный API из кода, используйте пути вида `/api/v1/...`.

## .gitignore

Игнорируются корневой и `frontend/` `node_modules`, сборка фронта, `backend/.venv`, локальные `.env`, кэш Python (`__pycache__`, `.pyc`).
