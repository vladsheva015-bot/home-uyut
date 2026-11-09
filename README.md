# Дом и Уют — сервис приоритизации заявок

FastAPI-сервис принимает заявки из сайта, Avito и Telegram, рассчитывает их приоритет и сохраняет в PostgreSQL.

## Возможности

- приём заявки через `POST /leads`;
- автоматический расчёт приоритета `high`, `medium` или `low`;
- сохранение заявок в PostgreSQL;
- получение одной заявки и списка заявок с фильтром по приоритету;
- запуск API и PostgreSQL одной командой Docker Compose;
- 17 Pytest-тестов, включая граничные случаи.

## Структура проекта

```text
.
├── app/                 # FastAPI-приложение
├── data/leads.csv       # 30 вымышленных заявок
├── tests/               # Pytest-тесты
├── compose.yaml         # API и PostgreSQL
├── Dockerfile
└── requirements.txt
```

## Правила приоритета

Правила применяются сверху вниз: используется первое совпавшее правило.

- **high** — сумма от `100000` рублей; либо текст содержит отдельное слово
  «срочно», «сегодня», `asap` или «горит» без учёта регистра; либо заявка из
  Telegram поступила по московскому времени с `09:00` включительно до `18:00`
  не включительно.
- **medium** — если `high` не сработал: сумма от `30000` до `99999` рублей;
  либо заявка пришла с сайта и сумма составляет не менее 10 000 рублей.
- **low** — все остальные заявки.

## Запуск через Docker Compose

Требования: установленный и запущенный Docker Desktop.

Из корня проекта выполните:

```powershell
docker compose up --build
```

После запуска сервис доступен по адресу <http://localhost:8000>.

Интерактивная документация API доступна по адресу <http://localhost:8000/docs>.

Чтобы остановить контейнеры, нажмите `Ctrl+C` в окне запуска или выполните:

```powershell
docker compose down
```

## Пример создания заявки

### PowerShell

```powershell
$body = @{
  source = "avito"
  text = "Need a sofa ASAP"
  amount = 1000
  created_at = "2026-11-09T19:00:00+03:00"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/leads `
  -ContentType "application/json; charset=utf-8" `
  -Body $body
```

Ожидаемый результат: заявка со статусом `201` и полем `priority: "high"`, так
как текст содержит `ASAP`.

### curl

```bash
curl -X POST http://localhost:8000/leads \
  -H "Content-Type: application/json" \
  -d '{"source":"site","text":"Нужен кухонный гарнитур","amount":150000,"created_at":"2026-11-09T10:15:00+03:00"}'
```

## Получение заявок

Получить список всех заявок:

```text
GET http://localhost:8000/leads
```

Получить только срочные заявки:

```text
GET http://localhost:8000/leads?priority=high
```

Получить одну заявку:

```text
GET http://localhost:8000/leads/{id}
```

Список заявок отсортирован по приоритету `high → medium → low`, а внутри одного
приоритета — от новых заявок к старым.

## Запуск тестов без Docker

Создайте и активируйте виртуальное окружение, затем установите зависимости:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
```

Тесты используют временную SQLite-базу, поэтому для их запуска PostgreSQL и Docker не требуются.

Проверенный результат:

```text
17 passed
```
