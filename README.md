# مسار Study — University Admissions Landing Page (MVP)

Arabic RTL corporate landing page for Egyptian students considering bachelor's or master's programmes in Germany and Austria (German/English).

**Status:** Working design and interactive intake prototype. Sending applications is **OFF** by default, so uploads and personal data cannot silently go to an unconfigured recipient. The visible word “مسار Study” is a **provisional brand name**, not a checked or registered trade name.

## Included

- Responsive one-page design with a custom-generated European-style campus illustration/photo composite (no implied affiliation with a real university).
- Country cards for Germany/Austria linking to official DAAD / Study in Austria sources.
- Service sections, honest FAQ, no fabricated testimonials or universities, no admission/visa guarantee.
- **Four-stage assessment form:** contact, degree/country/major/language/budget, qualification and supporting documents, optional consultation time request and consent.
- Up to **3 PDF/JPG/PNG attachments**, max 5 MB per file and 10 MB total.
- FastAPI backend which emails application data and attachments to a **business mailbox** using SMTP SSL/STARTTLS, after legal readiness is confirmed; no database and no files stored on disk.
- Optional WhatsApp Business link (not enabled until number is configured).
- Separate draft Privacy/Impressum pages, intentionally labelled incomplete.

### What “booking” means in V1

A student can request a **preferred consultation day and time period**. This is **not a confirmed booking**; you must confirm manually. To offer guaranteed available slots in V2, connect Cal.com, Calendly, or a real calendar integration.

## Quick start

```bash
cd masar-study-mvp
python -m venv .venv
source .venv/bin/activate             # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

Open http://localhost:8000. Without SMTP configuration, the form works as an interactive preview, but the final send button explicitly states that **nothing was submitted**.

## Deploying a safe public preview

A `render.yaml` Blueprint and a `/health` endpoint are included. See [DEPLOYMENT.md](DEPLOYMENT.md) for exact steps and safety requirements. The preview has no enabled intake, sets a `noindex, nofollow` response header, and uses draft legal pages that **must be completed before business launch**. The hosting account must be connected by the site owner; a local ZIP file is not itself a live public site.

## Enabling email submission

1. Copy `.env.example` to `.env` and enter actual credentials for a **business email/SMTP provider**. Do not put credentials in `site/` or browser JavaScript.
2. Enter `INBOX_EMAIL` (recipient) and `WHATSAPP_BUSINESS_NUMBER` (business number, digits only); don't use personal contact information by accident.
3. Enter `PUBLIC_SITE_URL`, e.g. `https://example.com`.
4. Complete and legally review `/privacy.html` and `/impressum.html`, plus the business registration/residence requirements. Confirm the mailbox provider's GDPR arrangements, retention policy, and contractual processor obligations. **Only then** set `PRIVACY_POLICY_APPROVED=true` in `.env`.
5. Restart the server and test with synthetic/non-sensitive data and a small test PDF. Verify arrival of documents in your inbox and that you can respond to the student.
6. Deploy on a hosting service that supports Python ASGI (e.g. Render or Railway), enforce HTTPS, configure environment variables on the hosting dashboard, and provide a custom domain when available. Do not deploy `.env` or server logs containing PII.

Start command: `uvicorn server:app --host 0.0.0.0 --port $PORT` (some hosts supply `PORT`).

## Security notes / limits

- This is an MVP, not a security audit: for production, arrange a legal GDPR/Impressum review, adequate anti-abuse protection, antivirus/document scanning if needed, secure mailbox permissions and deletion workflow.
- Files are read in memory (not written to a file directory) and attached to email; storing them in an email provider is still personal-data processing.
- Do **not** request identity numbers, full passports, bank statements, or sensitive documents for an initial assessment. Advise students to redact them.
- There is no marketing tracking, CRM, user account, automated eligibility scoring, or payment workflow.
- The current site fetches Cairo-friendly font files from Google Fonts; self-host fonts or revise disclosure as needed before publication.
- Rates, eligibility, visa and university deadlines vary; verify with official institutions for each student.

## Relevant official public sources

- [DAAD Degree Programmes](https://www.daad.de/en/studying-in-germany/universities/all-degree-programmes/)
- [DAAD Admissions Database](https://www.daad.de/en/studying-in-germany/requirements/admission-database/)
- [OeAD Study in Austria: Application & Admission](https://studyinaustria.at/en/plan-your-studies/application-and-admission)
- [§5 DDG Impressum](https://www.gesetze-im-internet.de/ddg/__5.html)

## Next practical decisions

- Final registered company name / brand and verified domain/trademark availability.
- Work email address and business WhatsApp number **with your permission to display them**.
- Exact legal operator identity and final privacy/Impressum text.
- Pricing after validating customer demand; intentionally not displayed in V1.
- Whether to add a confirmed scheduling integration and a proper CRM later.

## Standalone offline preview

Open `preview.html` in a browser to inspect the site without running Python. CSS/JS and the campus picture are embedded. The form runs in **demo mode** and cannot transmit personal data; the separate legal documents remain inside `site/`.
