# Voice Summary API

تبدیل پیام‌های صوتی به متن و خلاصه با استفاده از مدل‌های Whisper و GPT شرکت OpenAI، همراه با پشتیبانی چندکاربره و پرامپت‌های قابل شخصی‌سازی.

---

title: Voice Summary API
description: API بک‌اند برای پردازش فایل‌های صوتی با قابلیت تبدیل گفتار به متن و خلاصه‌سازی خودکار، همراه با احراز هویت چندکاربره و مدیریت قالب‌های پرامپت توسط ادمین.
status: در حال توسعه فعال
category: بک‌اند / پردازش صوت
stack: FastAPI, SQLAlchemy, PostgreSQL, OpenAI API, Alembic
featured: false
github: [https://github.com/imanlangaran/SpeachToSummaryText_backend](https://github.com/imanlangaran/SpeachToSummaryText_backend)
demo: ندارد

---

## معرفی

Voice Summary API یک سرویس بک‌اند است که به کاربران اجازه می‌دهد فایل‌های صوتی را آپلود کرده و نسخه متنی و خلاصه‌ی خودکار آن‌ها را به زبان فارسی دریافت کنند. این سیستم از Whisper شرکت OpenAI برای تبدیل دقیق گفتار به متن و از مدل‌های GPT (از طریق OpenAI Assistants) برای خلاصه‌سازی هوشمند متن استفاده می‌کند.

**چه مشکلی را حل می‌کند:**

* تبدیل پیام‌های صوتی به متن نوشتاری
* تولید خلاصه‌های مفهومی از محتوای تبدیل‌شده
* مدیریت چندین کاربر با جداسازی داده‌ها
* امکان ساخت و مدیریت پرامپت‌های سفارشی خلاصه‌سازی توسط ادمین

**مناسب چه کسانی است:**

* سازمان‌هایی که با ارتباطات صوتی فارسی‌زبان سروکار دارند
* اپلیکیشن‌هایی که به قابلیت پردازش صوت نیاز دارند
* تیم‌هایی که به منطق خلاصه‌سازی انعطاف‌پذیر و قابل شخصی‌سازی نیاز دارند

**چرا اهمیت دارد:**
این پروژه چندین سرویس هوش مصنوعی را در قالب یک جریان کاری یکپارچه ترکیب می‌کند؛ همراه با مدیریت وضعیت، جداسازی کاربران و رفتار قابل تنظیم. معماری پروژه مسئولیت‌ها را بین تبدیل گفتار به متن، خلاصه‌سازی و مدیریت پرامپت تفکیک می‌کند — به این صورت می‌توان از یک متن واحد، با استفاده از پرامپت‌های مختلف، خلاصه‌های متفاوتی تولید کرد.

## قابلیت‌ها

* **آپلود و تبدیل صوت به متن** – آپلود فایل MP3/صوتی و تبدیل خودکار گفتار به متن با استفاده از Whisper و پشتیبانی از زبان فارسی
* **پرامپت‌های سفارشی خلاصه‌سازی** – ادمین‌ها می‌توانند پرامپت تعریف و مدیریت کنند؛ کاربران نیز می‌توانند از یک متن، با پرامپت‌های مختلف، چند خلاصه تولید کنند
* **معماری چندکاربره** – دسترسی مبتنی بر نقش (کاربر/ادمین) همراه با جداسازی داده‌ها
* **احراز هویت JWT** – احراز هویت مبتنی بر توکن با انقضای ۳۰ دقیقه‌ای
* **یکپارچه‌سازی با OpenAI Assistants** – استفاده از Assistant API برای جریان‌های کاری پیشرفته خلاصه‌سازی
* **بررسی سلامت سرویس** – مانیتورینگ داخلی سلامت API همراه با بررسی اختیاری اتصال دیتابیس
* **مدیریت فایل‌های صوتی** – دریافت تاریخچه تبدیل‌های صوتی و خلاصه‌های مرتبط
* **مهاجرت دیتابیس** – نسخه‌بندی ساختار دیتابیس با Alembic

## تکنولوژی‌ها

**بک‌اند**

* FastAPI 0.116.1 – فریمورک مدرن و async پایتون
* SQLAlchemy 2.0.41 – ORM برای ارتباط با دیتابیس
* Uvicorn 0.35.0 – سرور ASGI

**دیتابیس**

* PostgreSQL (از طریق SQLAlchemy) یا MySQL با پشتیبانی PyMySQL 1.1.1
* Alembic 1.16.4 – مدیریت migrationهای دیتابیس

**هوش مصنوعی / سرویس‌ها**

* OpenAI SDK 1.97.1 – برای تبدیل صوت و خلاصه‌سازی
* Pydub 0.25.1 – پردازش و chunk کردن فایل‌های صوتی

**احراز هویت و امنیت**

* Python-Jose 3.5.0 – مدیریت توکن‌های JWT
* Passlib 1.7.4 – هش کردن رمز عبور با bcrypt
* PyASN1 0.6.1 – پشتیبانی ASN.1

**ابزارها**

* Pydantic 2.11.7 – اعتبارسنجی و serialization داده‌ها
* Python-dotenv 1.1.1 – مدیریت متغیرهای محیطی
* CORS middleware – مدیریت درخواست‌های cross-origin

## معماری

### جریان درخواست

```text
درخواست کلاینت
    ↓
CORS Middleware
    ↓
Router (Admin/User)
    ↓
Authentication (JWT → get_current_user)
    ↓
Service Layer (audio.py, prompt.py, transcription_service.py, summarise_service.py)
    ↓
Database Layer (SQLAlchemy models → PostgreSQL/MySQL)
    ↓
External APIs (OpenAI Whisper, OpenAI Assistants)
    ↓
پاسخ به کلاینت
```

### مرزبندی سرویس‌ها

**سرویس احراز هویت**

* ثبت‌نام و ورود کاربران
* تولید و اعتبارسنجی JWT
* مجوزدهی مبتنی بر نقش (ادمین یا کاربر عادی)

**سرویس صوت** (`app/services/audio.py`)

* اعتبارسنجی آپلود فایل
* هماهنگی فرآیند تبدیل متن و خلاصه‌سازی
* پاک‌سازی فایل‌های موقت
* پشتیبانی از chunk کردن فایل‌های طولانی‌تر از ۲ دقیقه

**سرویس تبدیل متن** (`app/services/transcription_service.py`)

* فراخوانی Whisper API
* تقسیم فایل‌های بزرگ (>۲ دقیقه یا >۲۵ مگابایت) به بخش‌های کوچک‌تر
* استانداردسازی صوت به 16kHz mono برای سازگاری بیشتر
* ترکیب خروجی chunkها

**سرویس خلاصه‌سازی** (`app/services/summarise_service.py`)

* دو مسیر: خلاصه‌سازی مستقیم با GPT یا استفاده از OpenAI Assistants
* استفاده از Assistant API برای خلاصه‌سازی‌های پیشرفته مبتنی بر قالب
* مدیریت threadها و polling برای دریافت نتیجه

**سرویس پرامپت** (`app/services/prompt.py`)

* عملیات کامل CRUD برای پرامپت‌های ادمین
* استفاده از الگوی soft-delete برای حفظ داده‌ها
* نگهداری شناسه Assistant مربوط به هر پرامپت

### مدل داده

**Users** – ایمیل، رمز عبور هش‌شده، شناسه تلگرام (اختیاری)، وضعیت ادمین، زمان ساخت

**Transcriptions** – متادیتای فایل صوتی، کاربر مرتبط، نتیجه تبدیل متن، وضعیت پردازش، پرامپت‌های کمکی

**Prompts** – قالب‌های خلاصه‌سازی، شناسه OpenAI Assistant، پشتیبانی soft-delete، تاریخچه تغییرات

**Summaries** – نتایج خلاصه‌سازی، متصل به transcription + prompt + user، همراه با وضعیت پردازش

**روابط:**

* Users → چندین Transcription
* Users → چندین Summary
* Prompts → چندین Summary
* Transcriptions → چندین Summary
* محدودیت یکتا: `(user_id, transcription_id, prompt_id)` برای جلوگیری از خلاصه‌های تکراری

## ساختار پروژه

```text
app/
├── main.py                 # راه‌اندازی FastAPI، health check، ثبت routeها
├── auth/
│   ├── auth_router.py      # endpointهای ثبت‌نام و ورود
│   ├── auth_utils.py       # هش رمز عبور و جستجوی کاربر
│   ├── jwt_handler.py      # ساخت و decode کردن JWT
│   └── dependencies.py     # OAuth2 scheme، get_current_user، admin_required
├── api/
│   ├── upload.py           # آپلود قدیمی فایل صوتی (در حال حاضر استفاده نمی‌شود)
│   ├── admin/
│   │   ├── routes.py       # تجمیع routeهای ادمین
│   │   └── prompt.py       # endpointهای CRUD پرامپت
│   └── client/
│       ├── routes.py       # تجمیع routeهای کاربر
│       ├── audio.py        # endpointهای صوت کاربر
│       └── prompt.py       # لیست پرامپت‌ها
├── services/
│   ├── openai_client.py    # مقداردهی Singleton کلاینت OpenAI
│   ├── audio.py            # منطق اصلی پردازش صوت
│   ├── transcription_service.py  # اتصال Whisper همراه با chunking
│   ├── summarise_service.py      # خلاصه‌سازی با GPT و Assistant
│   └── prompt.py           # منطق تجاری CRUD پرامپت
├── models/
│   ├── __init__.py         # تشخیص خودکار Alembic
│   ├── user.py
│   ├── transcription.py
│   ├── prompt.py
│   └── summary.py
├── db/
│   ├── database.py         # SQLAlchemy engine، session، health check
│   └── schemas.py          # مدل‌های Pydantic

alembic/
├── env.py                  # تنظیمات محیط migration
├── script.py.mako          # قالب migration
└── versions/               # اسکریپت‌های versioned migration

requirements.txt            # وابستگی‌های پایتون
alembic.ini                 # تنظیمات Alembic
.env.example                # قالب متغیرهای محیطی
```

## مستندات API

### احراز هویت

**POST /auth/register**

```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

خروجی: آبجکت کاربر شامل شناسه، ایمیل و وضعیت ادمین

**POST /auth/login**

```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

خروجی:

```json
{"access_token": "...", "token_type": "bearer"}
```

**POST /auth/loginSwagger**

* مخصوص Swagger UI
* پارامترها: `username` (ایمیل)، `password`

**GET /auth/me**

* نیازمند Bearer Token
* خروجی: ایمیل کاربر فعلی و وضعیت ادمین

### بررسی سلامت سرویس

**GET /health?include_db=true**

* `include_db`: مقدار بولی اختیاری
* خروجی:

```json
{"api": "✅ Service is operational", "database": "...", "timestamp": "..."}
```

### endpointهای صوت کاربر

تمام endpointها نیازمند JWT معتبر در هدر `Authorization: Bearer <token>` هستند.

**POST /user/audio/upload**

* فرم multipart:

  * `file`: فایل صوتی
  * `prompt` (اختیاری): متن راهنما برای Whisper
* خروجی:

```json
{"filename": "...", "transcript": "...", "id": <transcription_id>}
```

**POST /user/audio/upload_summarize**

* فرم multipart:

  * `file`
  * `transcribePrompt`
  * `summaryPromptId`
* خروجی:

```json
{"success": "true", "data": {"summarise_text": "...", "audioId": <id>}}
```

**GET /user/audio/**

* دریافت تمام transcriptionهای کاربر

**GET /user/audio/{audio_id}**

* دریافت تمام خلاصه‌های مربوط به یک transcription

**POST /user/audio/summarize**

* پارامترها:

  * `audioId`
  * `summaryPromptId`
* تولید خلاصه جدید از متن موجود

**GET /user/prompt/**

* دریافت پرامپت‌های فعال

### endpointهای ادمین

تمام endpointها نیازمند JWT معتبر با `is_admin=true` هستند.

**POST /admin/prompt/**

* ساخت پرامپت جدید

**GET /admin/prompt/**

* دریافت لیست پرامپت‌ها

**PUT /admin/prompt/{prompt_id}**

* بروزرسانی اطلاعات پرامپت

**PATCH /admin/prompt/{prompt_id}/delete**

* soft-delete کردن پرامپت

**PATCH /admin/prompt/{prompt_id}/restore**

* بازگردانی پرامپت حذف‌شده

## طراحی دیتابیس

### جدول Users

```sql
CREATE TABLE users (
  id INT PRIMARY KEY,
  email VARCHAR(254) UNIQUE NOT NULL,
  hashed_password VARCHAR(60) NOT NULL,
  telegram_id VARCHAR(128),
  is_admin BOOLEAN DEFAULT FALSE,
  created_at DATETIME DEFAULT UTC_NOW
);
```

### جدول Transcriptions

```sql
CREATE TABLE transcriptions (
  id INT PRIMARY KEY,
  user_id INT FOREIGN KEY,
  file_path VARCHAR(512),
  prompt TEXT,
  status VARCHAR(20) DEFAULT 'pending',
  result TEXT,
  error_message TEXT,
  created_at DATETIME,
  updated_at DATETIME
);
```

### جدول Prompts

```sql
CREATE TABLE prompts (
  id INT PRIMARY KEY,
  title VARCHAR(100) NOT NULL,
  content TEXT,
  assistant_id TEXT NOT NULL,
  is_deleted BOOLEAN DEFAULT FALSE,
  created_at DATETIME,
  updated_at DATETIME
);
```

### جدول Summaries

```sql
CREATE TABLE summaries (
  id INT PRIMARY KEY,
  user_id INT FOREIGN KEY,
  transcription_id INT FOREIGN KEY,
  prompt_id INT FOREIGN KEY,
  summary TEXT,
  result TEXT,
  status VARCHAR(20) DEFAULT 'pending',
  created_at DATETIME,
  UNIQUE(user_id, transcription_id, prompt_id)
);
```

**تصمیم کلیدی طراحی:**
محدودیت یکتا روی `(user_id, transcription_id, prompt_id)` از تولید خلاصه‌های تکراری جلوگیری می‌کند. یک متن می‌تواند چند بار با پرامپت‌های مختلف خلاصه شود، اما هر کاربر فقط یک خلاصه برای هر جفت `(transcript, prompt)` خواهد داشت.

## احراز هویت و مجوزدهی

**احراز هویت مبتنی بر JWT**

* ساخت توکن:

```python
create_access_token(data={"sub": user_email})
```

با انقضای ۳۰ دقیقه‌ای

* الگوریتم: HS256

**مجوزدهی**

* `get_current_user`: اعتبارسنجی توکن و دریافت کاربر
* `admin_required`: بررسی دسترسی ادمین
* تمام routeهای محافظت‌شده از `Depends()` استفاده می‌کنند

**امنیت رمز عبور**

* هش‌کردن با bcrypt و Passlib
* رمزها هرگز به صورت plaintext ذخیره نمی‌شوند

## عملکرد و مقیاس‌پذیری

### پردازش صوت

* فایل‌های بزرگ به chunkهای ۲ دقیقه‌ای تقسیم می‌شوند
* هر chunk جداگانه پردازش شده و نتایج ترکیب می‌شوند
* فایل‌های موقت بلافاصله حذف می‌شوند

### دیتابیس

* SQLAlchemy ORM همراه با connection pooling
* ایندکس روی `user_id`، `email` و `prompt.is_deleted`

### ملاحظات OpenAI API

* محدودیت ۲۵ مگابایتی Whisper با chunking مدیریت می‌شود
* Assistant API مبتنی بر polling است
* retry یا backoff پیاده‌سازی نشده است

### Async I/O

* endpointهای صوتی async هستند
* از runtime غیرهمزمان Uvicorn استفاده می‌شود

## تصمیمات مهندسی

### چرا FastAPI؟

* پشتیبانی native از async/await
* اعتبارسنجی داخلی با Pydantic
* مستندات خودکار Swagger/OpenAPI
* سیستم Dependency Injection ساده و تمیز

### چرا SQLAlchemy 2.0؟

* API مدرن و type-safe
* یکپارچگی با Alembic
* مدیریت خودکار relationها

### چرا OpenAI Assistants؟

* پشتیبانی از چندین خلاصه برای یک متن با پرامپت‌های متفاوت
* امکان تعریف workflowهای stateful و template-based

### چرا Soft Delete؟

* حفظ integrity داده‌ها
* امکان بازیابی داده‌های حذف‌شده

### چرا Chunk کردن صوت؟

* محدودیت Whisper روی حجم فایل
* امکان پردازش فایل‌های طولانی بدون قطع شدن

## چالش‌ها و راهکارها

### محدودیت نرخ OpenAI API

* مشکل: درخواست‌های همزمان زیاد
* وضعیت فعلی: retry/backoff وجود ندارد
* راهکار آینده: exponential backoff

### فایل‌های صوتی بزرگ

* مشکل: محدودیت Whisper
* راهکار: تقسیم خودکار فایل

### ذخیره‌سازی فایل‌های صوتی

* مشکل: فایل‌های موقت
* راهکار: پاک‌سازی در `finally`

### جلوگیری از خلاصه‌های تکراری

* راهکار: unique constraint در دیتابیس

### خلاصه‌سازی async

* وضعیت فعلی: synchronous
* امکان توسعه: افزودن Celery یا task queue

## نصب

### پیش‌نیازها

* Python 3.9+
* FFmpeg
* PostgreSQL یا MySQL
* کلید API شرکت OpenAI

### وابستگی‌های سیستمی

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg -y

# Windows
choco install ffmpeg
```

### راه‌اندازی پایتون

```bash
python -m venv venv

source venv/bin/activate
# یا
venv\Scripts\activate

pip install -r requirements.txt
```

### راه‌اندازی دیتابیس

```bash
alembic upgrade head
```

### متغیرهای محیطی

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/voice_summary

OPENAI_API_KEY=sk-...

SECRET_KEY=your-secret-key-here-min-32-chars
```

## اجرای محلی

### اجرای سرور توسعه

```bash
uvicorn app.main:app --reload
```

* آدرس API:
  `http://localhost:8000`

* Swagger:
  `http://localhost:8000/docs`

* ReDoc:
  `http://localhost:8000/redoc`

### Migrationهای دیتابیس

```bash
alembic revision --autogenerate -m "Add new table"

alembic upgrade head

alembic downgrade -1

alembic history
```

### تست احراز هویت

در Swagger:

1. روی "Authorize" کلیک کنید
2. از `/auth/loginSwagger` توکن بگیرید
3. توکن را وارد کنید
4. درخواست‌های احراز هویت‌شده ارسال کنید

## استقرار (Deployment)

این API قابلیت containerize شدن دارد و برای استقرار ابری مناسب است.

### پشتیبانی Docker

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### تنظیمات محیط

* تمام secretها از طریق environment variable
* محدود کردن CORS به دامنه فرانت‌اند

### استراتژی Migration

```bash
alembic upgrade head
```

### Reverse Proxy

* استفاده از Nginx یا Caddy توصیه می‌شود
* مدیریت HTTPS، compression و rate limiting

### مانیتورینگ

* endpoint سلامت:

```http
GET /health?include_db=true
```

## بهبودهای آینده

### عملکرد

* استفاده کامل از async mode در SQLAlchemy
* افزودن Redis cache
* پیاده‌سازی Celery برای jobهای طولانی

### پردازش صوت

* chunking همراه با overlap
* پشتیبانی از فرمت‌های بیشتر
* حذف نویز و normalization

### خلاصه‌سازی

* داشبورد ادمین برای تحلیل کیفیت خلاصه‌ها
* تست A/B برای پرامپت‌ها
* fallback در صورت شکست خلاصه‌سازی

### API

* آپلود گروهی فایل‌ها
* Webhook برای اعلان تکمیل پردازش
* خروجی PDF یا متن فرمت‌شده
* rate limiting برای کاربران

### دیتابیس

* soft delete برای transcription و summary
* آرشیو داده‌های قدیمی
* full-text search

### زیرساخت

* Distributed tracing
* Structured logging
* جمع‌آوری metricها
* هشدار برای نرخ بالای خطاهای API

<!-- 
## License

هیچ لایسنسی مشخص نشده است. لطفاً یک فایل `LICENSE` به مخزن اضافه کنید (مانند MIT، Apache 2.0 یا proprietary).
-->
