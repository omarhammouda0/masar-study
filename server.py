"""Masar Study MVP — static landing page and email-only lead intake.

No database, no on-disk file storage. Uploaded documents are validated in memory
and attached to an email only after SMTP and legal readiness are configured.
"""
from __future__ import annotations

import asyncio
import os
import re
import smtplib
import time
from collections import defaultdict
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
load_dotenv(ROOT / ".env")

app = FastAPI(title="Masar Study", docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/assets", StaticFiles(directory=SITE / "assets"), name="assets")

MAX_FILE = 5 * 1024 * 1024
MAX_TOTAL = 10 * 1024 * 1024
MAX_REQUEST = 11 * 1024 * 1024
ALLOWED_SUFFIXES = {".pdf": "application/pdf", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}
RATE: dict[str,list[float]] = defaultdict(list)


def enabled() -> bool:
    keys = ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM", "INBOX_EMAIL")
    return all(os.getenv(k, "").strip() for k in keys) and os.getenv("PRIVACY_POLICY_APPROVED", "").lower() == "true"


@app.middleware("http")
async def security_headers(request: Request, call_next):
    # Edge proxy / hosting service must enforce HTTPS for production.
    if request.url.path == "/api/assessment":
        try:
            declared_size = int(request.headers.get("content-length", "0"))
        except ValueError:
            declared_size = 0
        if declared_size > MAX_REQUEST:
            return JSONResponse({"detail":"حجم الطلب كبير جدًا (أقصى حجم 11 MB)."},status_code=413)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/api/") else "public, max-age=3600"
    if not enabled():
        # Preview is not ready for commercial launch or search indexing.
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
    return response


@app.get("/")
async def homepage():
    return FileResponse(SITE / "index.html", media_type="text/html")


@app.get("/privacy.html")
async def privacy_page():
    return FileResponse(SITE / "privacy.html", media_type="text/html")


@app.get("/impressum.html")
async def impressum_page():
    return FileResponse(SITE / "impressum.html", media_type="text/html")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/config")
async def config():
    number = re.sub(r"\D", "", os.getenv("WHATSAPP_BUSINESS_NUMBER", ""))
    return {"form_enabled": enabled(), "whatsapp_number":number}


def value_clean(value: str, max_len: int = 250) -> str:
    return re.sub(r"[\x00-\x1f\x7f]", " ", (value or "").strip())[:max_len]


def verify_file(data: bytes, suffix: str) -> bool:
    if suffix == ".pdf": return data.startswith(b"%PDF-")
    if suffix == ".png": return data.startswith(b"\x89PNG\r\n\x1a\n")
    if suffix in (".jpg", ".jpeg"): return data.startswith(b"\xff\xd8\xff")
    return False


def deliver_email(message: EmailMessage) -> None:
    host = os.environ["SMTP_HOST"]
    port = int(os.environ["SMTP_PORT"])
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]
    timeout = 20
    if port == 465:
        with smtplib.SMTP_SSL(host,port,timeout=timeout) as connection:
            connection.login(user,password)
            connection.send_message(message)
    elif port == 587:
        with smtplib.SMTP(host,port,timeout=timeout) as connection:
            connection.ehlo()
            connection.starttls()
            connection.ehlo()
            connection.login(user,password)
            connection.send_message(message)
    else:
        raise RuntimeError("SMTP_PORT must be 465 (SSL) or 587 (STARTTLS)")


@app.post("/api/assessment")
async def assessment(
    request: Request,
    full_name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    residence_city: str = Form(""),
    nationality: str = Form("Egyptian"),
    destination: str = Form(...),
    degree: str = Form(...),
    target_major: str = Form(...),
    study_language: str = Form(...),
    intake: str = Form("Not sure"),
    first_year_budget: str = Form("Not sure"),
    current_qualification: str = Form(...),
    grade: str = Form(""),
    current_major: str = Form(""),
    graduation_year: str = Form(""),
    english_level: str = Form("Not sure"),
    german_level: str = Form("Not sure"),
    wants_consultation: str = Form(""),
    preferred_date: str = Form(""),
    preferred_slot: str = Form(""),
    notes: str = Form(""),
    privacy_consent: str = Form(""),
    documents: list[UploadFile] | None = File(default=None),
):
    if not enabled():
        raise HTTPException(503, "الاستقبال غير مفعل حاليًا. البيانات لم تُرسل.")
    origin = request.headers.get("origin", "")
    allowed_hosts = {request.headers.get("host", "")}
    public_url = os.getenv("PUBLIC_SITE_URL", "")
    if public_url: allowed_hosts.add(urlsplit(public_url).netloc)
    if origin and urlsplit(origin).netloc not in allowed_hosts:
        raise HTTPException(403, "طلب غير مسموح من مصدر خارجي.")
    client_key = (request.client.host if request.client else "unknown")
    now = time.monotonic()
    RATE[client_key] = [t for t in RATE[client_key] if now-t < 3600]
    if len(RATE[client_key]) >= 4:
        raise HTTPException(429, "تم تجاوز عدد الطلبات المسموح بها. حاول لاحقًا.")
    RATE[client_key].append(now)

    if not full_name.strip() or len(full_name.strip()) > 120:
        raise HTTPException(400, "من فضلك ادخل اسمك الصحيح.")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email.strip()) or len(email.strip()) > 180:
        raise HTTPException(400, "البريد الإلكتروني غير صحيح.")
    if len(re.sub(r"\D", "", phone)) < 9 or len(phone) > 30:
        raise HTTPException(400, "رقم واتساب غير صحيح.")
    if destination not in ("Germany","Austria","Both") or degree not in ("Bachelor","Master") or study_language not in ("English","German","Both"):
        raise HTTPException(400, "اختيارات الدراسة غير صحيحة.")
    if current_qualification not in ("High School","Bachelor","Other"):
        raise HTTPException(400, "المؤهل الدراسي غير صحيح.")
    if not target_major.strip() or len(target_major) > 120:
        raise HTTPException(400, "التخصص المطلوب غير صحيح.")
    if privacy_consent != "on":
        raise HTTPException(400, "موافقة الخصوصية مطلوبة.")
    if wants_consultation == "on":
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", preferred_date) or preferred_slot not in ("Morning","Afternoon","Evening"):
            raise HTTPException(400,"لازم تحدد اليوم والفترة المفضلة للاستشارة.")
    else:
        preferred_date = preferred_slot = ""
    if len(notes) > 2000:
        raise HTTPException(400, "الملاحظات طويلة جدًا.")

    checked_docs: list[tuple[str,bytes,str]] = []
    total = 0
    all_docs = documents or []
    if len(all_docs) > 3:
        raise HTTPException(400,"أقصى عدد للمستندات 3 ملفات.")
    for document in all_docs:
        original = (document.filename or "").replace("\\", "/")
        name = value_clean(Path(original).name, 120)
        suffix = Path(name).suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            raise HTTPException(400,"أنواع الملفات المسموحة: PDF أو JPG أو PNG.")
        data = await document.read(MAX_FILE+1)
        if len(data) > MAX_FILE:
            raise HTTPException(413,"الملف الواحد لا يمكن أن يتجاوز 5 MB.")
        total += len(data)
        if total > MAX_TOTAL:
            raise HTTPException(413,"إجمالي المستندات لا يمكن أن يتجاوز 10 MB.")
        if not verify_file(data, suffix):
            raise HTTPException(400,"صيغة ملف غير متطابقة مع نوعه. تحقق من المستندات.")
        checked_docs.append((name,data,ALLOWED_SUFFIXES[suffix]))
        await document.close()

    values = {
        "الاسم":full_name,"البريد":email,"واتساب":phone,"المدينة":residence_city,"الجنسية":nationality,
        "الوجهة":destination,"المرحلة":degree,"التخصص المطلوب":target_major,"لغة الدراسة":study_language,
        "الفصل المستهدف":intake,"ميزانية السنة الأولى":first_year_budget,"المؤهل الحالي":current_qualification,
        "الدرجة / المعدل":grade,"التخصص السابق":current_major,"سنة التخرج":graduation_year,
        "الإنجليزية":english_level,"الألمانية":german_level,
        "يريد استشارة": "نعم، طلب موعد غير مؤكد" if wants_consultation == "on" else "لا",
        "التاريخ المفضل":preferred_date,"الفترة المفضلة (بتوقيت مصر)":preferred_slot,
        "ملاحظات":notes,
    }
    body = "طلب تقييم طالب جديد (راجع المستندات المرفقة بحذر)\n\n" + "\n".join(f"{k}: {value_clean(v, 2000)}" for k,v in values.items())
    mail = EmailMessage()
    mail["Subject"] = "[MASAR] New student assessment — " + value_clean(full_name,80)
    mail["From"] = os.environ["SMTP_FROM"]
    mail["To"] = os.environ["INBOX_EMAIL"]
    mail["Reply-To"] = email.strip()
    mail.set_content(body)
    for name,data,mime in checked_docs:
        major,minor = mime.split("/",1)
        mail.add_attachment(data,maintype=major,subtype=minor,filename=name)

    try:
        await asyncio.to_thread(deliver_email, mail)
    except Exception:
        # Do not log PII or attachment contents.
        raise HTTPException(502,"تعذر تسليم الرسالة حاليًا. لم نؤكد الاستلام؛ حاول لاحقًا.")
    return {"ok":True,"message":"تم إرسال الطلب بنجاح"}
