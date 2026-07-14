# Internship Task 1 — Multi-Turn Groq CLI Chat

Консольний чат на базі Groq, який підтримує багатокроковий діалог,
real-time streaming, підрахунок токенів, власний system prompt і постійне
збереження розмов у Markdown.

## Що було зроблено

- застосунок повністю переведено з OpenAI Python SDK на офіційний Groq Python
  SDK;
- стандартною production-моделлю встановлено `llama-3.3-70b-versatile`;
- `ChatSession` зберігає повну історію ролей `system`, `user` та `assistant` у
  межах поточного запуску;
- додано стандартний prompt викладача та можливість замінити його через CLI;
- API-ключ завантажується з `.env` через `GROQ_API_KEY`;
- реалізовано streaming через Groq Chat Completions із `stream=True`;
- chunks одразу друкуються в CLI, але одночасно накопичуються в повну відповідь;
- token usage читається з фінальної Groq streaming metadata;
- рахуються input, output і total tokens останнього запиту та всієї сесії;
- кожна сесія зберігається в окремому Markdown-журналі з timestamps;
- перервана відповідь позначається як `incomplete` і не додається до наступного
  модельного контексту;
- обробляються authentication errors, HTTP 429, timeout, connection errors,
  інші Groq API errors, `Ctrl+C`, EOF і помилки запису журналу;
- реалізовано bonus-аргументи `-prompt` / `--prompt` і `--model`;
- додано sample log, `.env.example` та список залежностей.

## Структура проєкту

```text
task1/
├── app.py                       # CLI, друк chunks і обробка команд
├── chat_session.py              # Groq API, історія, токени та журнали
├── README.md                    # документація проєкту
├── requirements.txt             # Python-залежності
├── .env.example                 # шаблон змінної GROQ_API_KEY
└── logs/
    └── example_conversation.md  # приклад Groq-журналу
```

Автоматично створені `conversation_*.md` ігноруються Git, щоб особисті діалоги
не потрапляли в репозиторій. Демонстраційний `example_conversation.md`
залишається частиною deliverables.

## Архітектура

```text
Користувач
    ↓
app.py — читає input і друкує chunks
    ↓
ChatSession — додає історію, викликає Groq, рахує tokens
    ↓
Groq Chat Completions API
    ↓
streaming chunks → app.py → консоль
    ↓
готова відповідь → history + Markdown log
```

### За що відповідає `chat_session.py`

- завантаження `.env`;
- перевірка API-ключа;
- створення `Groq` client;
- system prompt і message history;
- Groq Chat Completions request;
- накопичення streaming chunks;
- token usage;
- timestamps;
- створення Markdown-журналу;
- підсумкова статистика.

### За що відповідає `app.py`

- CLI-аргументи;
- введення користувача;
- `[Assistant is typing...]`;
- друк chunks із `flush=True`;
- команди `q`, `quit`, `exit`;
- зрозумілі повідомлення про помилки;
- фінальний session summary.

Таке розділення дозволяє пізніше використати `ChatSession` у вебінтерфейсі,
не переписуючи Groq-логіку.

## Що таке Groq у цьому проєкті

GroqCloud надає API для швидкого inference різних мовних моделей. Проєкт
використовує нативний Python-пакет `groq` і Chat Completions API. Groq API має
OpenAI-сумісну структуру `messages`, але застосунок не залежить від пакета
`openai`.

Цей chatbot не використовує Groq Compound, web search, tools або зовнішню
пам'ять. Моделі надсилається тільки system prompt і поточна історія діалогу.

## Створення Groq API-ключа

1. Відкрий [Groq Console](https://console.groq.com/).
2. Увійди або створи обліковий запис.
3. Вибери або створи Groq project.
4. Перейди на сторінку [API Keys](https://console.groq.com/keys).
5. Створи новий ключ і одразу збережи його у `.env`.

API-ключ є секретом. Не вставляй його у Python-файли, README, screenshots або
Git commits.

## Встановлення

Потрібен Python 3.10 або новіший.

Із кореня репозиторію встанови залежності у вибране virtual environment:

```text
python -m pip install -r task1/requirements.txt
```

Встановлюються:

- `groq` — офіційний Groq Python SDK;
- `python-dotenv` — завантаження `.env`.

## Налаштування `.env`

Скопіюй `task1/.env.example` у `.env` у корені репозиторію або в `task1` і
встав Groq API-ключ:

```text
GROQ_API_KEY=your_real_groq_api_key
```

Для сумісності з початковою версією цього проєкту код також розпізнає
`API_KEY`, але рекомендована офіційна назва — `GROQ_API_KEY`. Змінна
`API_SECRET` не потрібна Groq SDK і не використовується.

Файл `.env` уже додано до `.gitignore`.

## Запуск

Із кореня репозиторію:

```text
python task1/app.py
```

У Windows із наявним `.venv`:

```text
.venv\Scripts\python.exe task1\app.py
```

Очікуваний початок роботи:

```text
System Prompt: Ти — уважний викладач...
Model: llama-3.3-70b-versatile
Type 'quit', 'exit', or 'q' to finish.

You:
```

## CLI-аргументи

### Власний system prompt

```text
python task1/app.py -prompt "You are a patient math tutor."
```

Також підтримується:

```text
python task1/app.py --prompt "You are a Python tutor."
```

### Вибір моделі

```text
python task1/app.py --model llama-3.1-8b-instant
```

### Довідка CLI

```text
python task1/app.py --help
```

## Вибір Groq-моделі

Модель за замовчуванням:

```text
llama-3.3-70b-versatile
```

Вона обрана як production-модель із кращою якістю для пояснень та
багатокрокового tutor-діалогу.

Інші актуальні production-варіанти:

| Model ID | Коли використовувати |
|---|---|
| `llama-3.1-8b-instant` | коли пріоритетом є швидкість і менша вартість |
| `llama-3.3-70b-versatile` | універсальний tutor/chat, модель за замовчуванням |
| `openai/gpt-oss-20b` | швидкі загальні та reasoning-задачі |
| `openai/gpt-oss-120b` | складніші задачі, де важливіша якість |

Назва `openai/` у model ID GPT-OSS позначає родину моделі, а не використання
OpenAI SDK: inference усе одно виконує Groq.

Список моделей і статус preview/production може змінюватися. Перед зміною
default model перевіряй [Supported Models](https://console.groq.com/docs/models)
і [Model Deprecations](https://console.groq.com/docs/deprecations).

## Multi-turn history

На початку `ChatSession.messages` містить system prompt:

```text
system: Ти — уважний викладач...
```

Після першого ходу:

```text
system: ...
user: Explain overfitting.
assistant: Overfitting is...
```

Після другого повідомлення Groq отримує всю історію:

```text
system: ...
user: Explain overfitting.
assistant: Overfitting is...
user: Give me another example.
```

Тому модель розуміє контекст. Історія існує тільки в поточному Python-процесі.
Markdown logs не завантажуються як пам'ять під час наступного запуску.

## Як працює streaming

`ChatSession.get_response()` викликає Groq Chat Completions із `stream=True`.
Groq повертає iterator із partial message deltas. Кожен непорожній
`chunk.choices[0].delta.content`:

1. додається до списку частин відповіді;
2. одразу повертається в `app.py`;
3. друкується без нового рядка з `flush=True`.

Після завершення chunks об'єднуються в один рядок. Тільки повна успішна
відповідь додається до контексту наступного запиту.

Якщо stream обірветься, частковий текст зберігається зі статусом `incomplete`,
але не додається до `messages`.

## Підрахунок токенів

Groq повертає usage metadata у фінальній частині stream. Поточний код підтримує
обидва представлення SDK:

- `chunk.x_groq.usage` — Groq-specific streaming metadata;
- `chunk.usage` — top-level usage, якщо воно присутнє у відповіді SDK.

Використовуються поля:

- `prompt_tokens` → input tokens;
- `completion_tokens` → output tokens;
- `total_tokens` → загальні токени запиту.

Програма показує:

```text
[Tokens — input: 120 | output: 56 | request: 176 | session: 325]
```

`request` — останній завершений Groq request, а `session` — сума всіх успішних
запитів поточного запуску. Якщо stream обірвався до фінальної metadata, його
usage не додається до session totals.

`tiktoken` не використовується, оскільки provider metadata краще відображає
фактичний запит до конкретної Groq-моделі.

## Markdown-журнали

Файли створюються за шаблоном:

```text
task1/logs/conversation_YYYY-MM-DD_HH-MM-SS-microseconds.md
```

Журнал містить:

- час початку з локальним часовим поясом;
- Groq model ID;
- system prompt;
- user та assistant messages;
- timestamp кожного запису;
- статус `complete`, `failed` або `incomplete`;
- token usage завершених відповідей;
- session totals.

Журнал перезаписується актуальним станом після кожної завершеної відповіді та
під час нормального виходу.

## Обробка помилок Groq

Застосунок використовує конкретні exception types з Groq Python SDK:

- `AuthenticationError` — неправильний або неактивний ключ;
- `RateLimitError` — HTTP 429;
- `APITimeoutError` — перевищено timeout;
- `APIConnectionError` — немає з'єднання з Groq;
- `APIStatusError` — інший HTTP status;
- `APIError` — інша помилка Groq SDK.

Groq SDK автоматично повторює частину тимчасових помилок, зокрема connection
errors, HTTP 408, 409, 429 та server errors. У клієнті явно налаштовано
`max_retries=2` і `timeout=30.0` секунд.

## Rate limits

Groq може обмежувати:

- RPM — requests per minute;
- RPD — requests per day;
- TPM — tokens per minute;
- TPD — tokens per day;
- окремі input/output token limits для деяких організацій.

Ліміти залежать від project, plan і моделі. Актуальні значення потрібно
дивитися у Groq Console. При перевищенні повертається HTTP 429, який застосунок
обробляє як `RateLimitError`.

Докладніше: [Groq Rate Limits](https://console.groq.com/docs/rate-limits).

## Приклади prompt-ів

- Explain: `Explain overfitting in simple terms.`
- Quiz: `Ask me three questions to test my Python knowledge.`
- Compare: `Compare supervised and unsupervised learning.`
- Summarize: `Summarize this paragraph: ...`
- Follow-up: `Can you give me another example?`

## Troubleshooting

### `GROQ_API_KEY is missing`

Перевір, що файл називається саме `.env`, змінна має назву `GROQ_API_KEY`, а
запуск відбувається з кореня репозиторію або папки `task1`.

### `Authentication failed`

Створи новий ключ у Groq Console, встав його без зайвих лапок і перезапусти
Python-процес.

### HTTP 403

Модель може бути заборонена у project або organization settings. Перевір
[Model Permissions](https://console.groq.com/docs/model-permissions).

### HTTP 404 або повідомлення про decommissioned model

Перевір актуальний model ID у [Supported Models](https://console.groq.com/docs/models)
і заміни `--model` або default model.

### HTTP 429

Зачекай до reset rate limit, зменш частоту запитів або перевір limits у Groq
Console.

### Після встановлення `groq` import не працює

Переконайся, що `pip` та `python` належать одному virtual environment:

```text
python -m pip show groq
python task1/app.py
```

## Перевірка реалізації

Під час розробки перевіряються:

- Python syntax;
- CLI `--help`;
- створення Groq client;
- streaming iterator;
- multi-turn message history;
- top-level і `x_groq` token usage;
- Markdown logging;
- interrupted stream rollback;
- graceful CLI shutdown.

Локальні automated checks використовують fake stream і не витрачають Groq
API-кредити. Для остаточної end-to-end перевірки потрібен справжній
`GROQ_API_KEY` і один тестовий запит.

## Офіційна документація Groq

- [Groq Quickstart](https://console.groq.com/docs/quickstart) — ключ, SDK і
  перший request;
- [Text Generation and Streaming](https://console.groq.com/docs/text-chat) —
  messages і `stream=True`;
- [Groq API Reference](https://console.groq.com/docs/api-reference) — повний
  Chat Completions request/response schema;
- [Official Groq Python SDK](https://github.com/groq/groq-python) — Python
  client, exception types, retries та timeout;
- [Supported Models](https://console.groq.com/docs/models) — актуальні model
  IDs і production/preview status;
- [Model Deprecations](https://console.groq.com/docs/deprecations) — моделі,
  які вимикаються, та рекомендовані replacements;
- [API Error Codes](https://console.groq.com/docs/errors) — HTTP statuses і
  Groq error objects;
- [Rate Limits](https://console.groq.com/docs/rate-limits) — RPM, RPD, TPM та
  headers;
- [Projects](https://console.groq.com/docs/projects) — Groq projects, keys і
  usage tracking;
- [Model Permissions](https://console.groq.com/docs/model-permissions) —
  organization/project model access;
- [Prompting Guide](https://console.groq.com/docs/prompting) — system prompts
  та generation parameters;
- [Production Checklist](https://console.groq.com/docs/production-readiness/production-ready-checklist)
  — рекомендації для production;
- [Optimizing Latency](https://console.groq.com/docs/production-readiness/optimizing-latency)
  — streaming і latency practices;
- [Spend Limits](https://console.groq.com/docs/spend-limits) — budget limits та
  alerts;
- [Billing FAQ](https://console.groq.com/docs/billing-faqs) — usage і billing;
- [python-dotenv](https://pypi.org/project/python-dotenv/) — завантаження
  `.env`;
- [Python argparse](https://docs.python.org/3/library/argparse.html) —
  CLI-аргументи;
- [Python pathlib](https://docs.python.org/3/library/pathlib.html) — робота з
  файлами журналів;
- [Python datetime](https://docs.python.org/3/library/datetime.html) —
  timestamps. 