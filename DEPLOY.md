# Деплой: фронтенд и бэкенд (пошагово)

Фронтенд и бэкенд деплоятся **отдельно**:

| Что | Где обычно деплоят | Почему |
|-----|-------------------|--------|
| **Фронтенд** (Vite + React) | **Vercel** | Статическая сборка, удобный деплой из GitHub |
| **Бэкенд** (FastAPI + планировщик) | **Railway**, Render, Fly и т.п. | Нужен **постоянно работающий** процесс (не «serverless» как у Vercel для Python) |

Ниже — один понятный сценарий: **Neon** (база) → **Railway** (API) → **Vercel** (сайт). Можно заменить Neon на Supabase/Railway Postgres, логика та же.

---

## Что подготовить заранее

1. Код проекта лежит в **репозитории на GitHub** (Vercel и Railway подключаются к нему).
2. Аккаунты (можно один и тот же GitHub): **GitHub**, **Neon** (или другой Postgres), **Railway**, **Vercel**.

---

## Шаг 1. База данных PostgreSQL (Neon)

1. Откройте [https://console.neon.tech](https://console.neon.tech) и войдите (через GitHub удобно).
2. **Create project** / «Создать проект», выберите регион (ближе к вам), имя любое → создайте.
3. На экране проекта найдите **Connection string** (строка подключения). Формат похож на:
   `postgresql://USER:PASSWORD@HOST/neondb?sslmode=require`
4. **Скопируйте** эту строку целиком — это значение переменной **`DATABASE_URL`** для бэкенда. Никуда в чаты не публикуйте (там пароль).

---

## Шаг 2. Деплой бэкенда (Railway + Docker)

1. Откройте [https://railway.app](https://railway.app) → **Login** → войдите через **GitHub**.
2. **New project** → **Deploy from GitHub repo** (если спросит — **Authorize Railway** и выдайте доступ к нужному репозиторию `telemetry-platform`).
3. Выберите репозиторий → Railway создаст сервис. Дождитесь первого билда или сразу настройте сервис.
4. Откройте **созданный сервис** (клик по нему в проекте).
5. Вкладка **Settings** (настройки сервиса):
   - Найдите **Root Directory** / «Корень репозитория» и укажите: **`backend`**  
     (чтобы Railway собирал образ из папки `backend`, где лежит `Dockerfile`).
   - Сохраните, если есть кнопка **Save**.
6. Вкладка **Variables** (переменные окружения) — **Add** / «Добавить» и задайте:

   | Имя переменной | Значение |
   |----------------|----------|
   | `DATABASE_URL` | Вставьте **полную** строку из Neon (шаг 1). |
   | `OWEN_DEVICE_ID` | ID устройства Owen Cloud (например `628583`), как локально. |
   | `OWEN_POLL_INTERVAL_SECONDS` | Интервал опроса API в секундах (по умолчанию `60`). |
   | `CORS_ORIGINS` | Пока можно указать **`http://localhost:5173`** — чтобы локальный фронт ходил к API. После деплоя фронта на Vercel вы **добавите** сюда URL вида `https://ваш-проект.vercel.app` (см. шаг 4). Несколько адресов — **через запятую без пробелов**: `http://localhost:5173,https://xxx.vercel.app` |

   **`PORT`** вручную обычно **не задают** — Railway подставит сам.

7. Убедитесь, что билд использует **Dockerfile** из `backend` (после установки Root Directory Railway пересоберёт образ). Во вкладке **Deployments** дождитесь успешного деплоя (зелёный статус).
8. Чтобы получить **публичный URL API**:
   - В сервисе откройте **Settings** → раздел **Networking** / «Домен» → **Generate domain** (или аналог: публичный URL).
   - Скопируйте адрес вида `https://something.up.railway.app` — это **базовый URL бэкенда** (без `/login` в конце).

9. Проверка в браузере: откройте `https://ваш-url/` — должно вернуться что-то вроде `{"status":"ok"}`.

Если билд падает — в **Deployments** откройте последний деплой и читайте лог; чаще всего ошибка в переменных или в Root Directory не `backend`.

---

## Шаг 3. Деплой фронтенда (Vercel)

1. Откройте [https://vercel.com](https://vercel.com) → **Sign up** / войдите через **GitHub**.
2. **Add New…** → **Project** / «Добавить проект».
3. **Import** ваш репозиторий `telemetry-platform` (при необходимости **Adjust GitHub App Permissions** и дайте доступ к репо).
4. Перед деплоем настройте проект:
   - **Framework Preset**: **Vite** (часто определяется сам).
   - **Root Directory** → **Edit** → укажите **`frontend`** → **Continue**.
   - Команда сборки и папка вывода обычно: **Build Command** `npm run build`, **Output Directory** `dist` (как в Vite по умолчанию).
5. Раскройте **Environment Variables**:
   - **Name**: `VITE_API_URL`
   - **Value**: **только origin** вашего бэкенда из шага 2, например `https://something.up.railway.app`  
     **Без** слэша в конце, **без** `/login`.
   - Окружение: отметьте **Production** (и при желании Preview для превью-деплоев).
6. Нажмите **Deploy** и дождитесь окончания.
7. На экране успеха нажмите **Visit** / откройте выданный домен вида `https://telemetry-platform-xxx.vercel.app` — это URL **фронта**.

---

## Шаг 4. Связать фронт и бэкенд (CORS)

Браузер разрешит запросы с Vercel только если URL фронта указан в **`CORS_ORIGINS`** на бэкенде.

1. Скопируйте **точный** URL продакшн-фронта из Vercel (с `https://`, без пути, например `https://telemetry-platform-xxx.vercel.app`).
2. Зайдите в **Railway** → ваш сервис → **Variables**.
3. Отредактируйте **`CORS_ORIGINS`**: добавьте URL Vercel **через запятую** к уже существующим, например:  
   `http://localhost:5173,https://telemetry-platform-xxx.vercel.app`
4. Сохраните — Railway обычно **перезапускает** деплой автоматически. Дождитесь зелёного статуса.

После этого на продакшн-сайте форма логина должна успешно вызывать `POST /login` на Railway.

---

## Шаг 5. Проверка «всё работает»

1. Откройте сайт на **Vercel**, введите логин/пароль Owen Cloud → должен быть переход на `/home`.
2. При ошибке входа — сообщение Ant Design; если «Network Error» / CORS — перепроверьте **`CORS_ORIGINS`** и **`VITE_API_URL`** (без опечаток, без лишнего `/`).
3. Поллер на сервере начинает ходить в Owen **после первого успешного логина** (токен сохраняется в памяти процесса). После рестарта контейнера на Railway нужен **повторный вход** в приложение.

---

## Краткая шпаргалка по переменным

| Где | Переменная | Значение |
|-----|------------|----------|
| **Railway** | `DATABASE_URL` | Строка Neon |
| **Railway** | `OWEN_DEVICE_ID` | ID устройства Owen Cloud |
| **Railway** | `OWEN_POLL_INTERVAL_SECONDS` | Интервал опроса (сек), опционально |
| **Railway** | `CORS_ORIGINS` | `http://localhost:5173` + запятая + URL Vercel |
| **Vercel** | `VITE_API_URL` | Публичный URL Railway API (без `/`) |

---

## Если что-то пошло не так

- **Фронт собирается, но логин не работает с продакшна** — чаще всего неверный **`VITE_API_URL`** или **`CORS_ORIGINS`**. Пересоберите фронт на Vercel после смены env (**Redeploy** в Vercel при необходимости).
- **Бэкенд не стартует** — логи **Deployments** в Railway; проверьте `DATABASE_URL` и что Root Directory = **`backend`**.
- **`ProgrammingError: column "box_id" of relation "metrics" does not exist`** — в базе осталась **старая** таблица `metrics` (другие колонки). SQLAlchemy `create_all()` **не** меняет уже существующие таблицы. Нужно **один раз** пересоздать таблицу по актуальной схеме: в репозитории есть [`backend/migrations/recreate_metrics.sql`](backend/migrations/recreate_metrics.sql) (скрипт **удаляет все строки** в `metrics`). Выполните его от имени той же БД, что в `DATABASE_URL`, например локально: `psql "$DATABASE_URL" -f backend/migrations/recreate_metrics.sql`, либо вставьте SQL в SQL Editor у Neon. После этого перезапуск бэкенда подхватит пустую таблицу; данные начнут снова накапливаться с поллера после входа в приложение.

---

*English summary: deploy Postgres (e.g. Neon), deploy `backend/` with Docker on Railway using `DATABASE_URL`, `OWEN_DEVICE_ID`, optional `OWEN_POLL_INTERVAL_SECONDS`, `CORS_ORIGINS`; deploy `frontend/` on Vercel with `VITE_API_URL` pointing at the API; then add the Vercel URL to `CORS_ORIGINS`.*
