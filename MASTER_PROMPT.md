# MASTER PROMPT — Masar Study Landing Page MVP

You are a senior product designer, conversion-focused copywriter, and full-stack engineer. Build a complete, polished, production-preparable **Arabic RTL university-admissions landing page** for an independent consultancy serving Egyptian students. The brand name **"مسار | MASAR STUDY"** is a provisional placeholder and may be renamed later. Do not imply the company is legally registered or formally partnered with universities.

## Target market
- Egyptian students in Egypt seeking **Bachelor's** and **Master's** degrees in **Germany** or **Austria**.
- Programmes taught in **German**, **English**, or both.
- Focus on clarity, trust, and useful planning—not false promises or aggressive sales.

## Visual direction
- Corporate design (style A): navy `#102b44`, muted teal `#0f8779`, clean whites, tasteful pale blue-grey surfaces.
- Professional Arabic typography, spacious composition, responsive and mobile-first UX.
- A large tasteful photographic-style image of a European university campus and authentic-feeling study destinations. Do not label a generated building as a real university.
- Elegant RTL navigation, responsive hamburger, rounded cards, accessible forms, subtle animations.

## Content and sections
1. Hero with the headline "الدراسة في أوروبا، بخطة أوضح. ومستقبل أوسع." and CTA "ابدأ تقييم ملفك مجانًا".
2. Germany and Austria cards with official-source links and clear Bachelor/Master context.
3. Services: assess academic eligibility, shortlist programmes, organise and review documents (CV/motivation letter/transcripts), assist with application portals, general administrative orientation for transition to Europe.
4. Four-step explanation of the process.
5. Student assessment form and optional consultation request.
6. Honest FAQs about who makes admissions decisions, whether students can self-apply, possible third-party fees, programme language and booking confirmations.
7. WhatsApp CTA, legal links, no fabricated testimonials/statistics/partners.

## Assessment form (4 steps)
1. Name, WhatsApp, email, Egyptian nationality default, city.
2. Destination (DE/AT/both), Bachelor/Master, major, language (EN/DE/both), target term, first-year budget.
3. Previous degree, grade/GPA, field, graduation year, English/German levels, optional upload of up to 3 PDF/JPG/PNG documents (5MB per file/10MB total).
4. Summary, optional preferred consultation date and time-of-day, notes, privacy consent.

## Behaviour
- The student sees a clearly-labelled free initial assessment, not an automated admissions decision.
- The operator **manually** reviews requests.
- When enabled and configured, submission emails the details and uploaded documents to a **business mailbox**. Do not use insecure public cloud file uploads or expose SMTP credentials in frontend code. No permanent user account and no database in MVP.
- If the backend or privacy configuration is not ready, the demo UI must **honestly state that nothing was sent**.
- Appointment selection is a **request for an available time**, subject to confirmation; do not claim live availability.
- WhatsApp Business uses a **configurable** number, which is not published until supplied and confirmed.
- No prices are displayed: quote comes after reviewing the student's requirements.
- No customer dashboard, payments, AI admission scoring, CRM, university affiliate claims, or testimonials in V1.

## Privacy, compliance and accuracy
- Use no false guarantees of university admission or visa issuance.
- Provide draft privacy and legal disclosure routes, clearly marked as needing completion and legal review before public launch.
- Avoid collecting sensitive passport/identity information at the initial stage; encourage redaction.
- Apply upload limits, file signature validation, basic spam protection and HTTPS for deployment.
- Ensure GDPR processing and retention, lawful contact details, operator's residence/work authorization, and legal disclosure are verified before launch.
- Link official resources: DAAD degree programmes and admission guidance and OeAD Study in Austria admissions.

## Deliverables
- Fully responsive runnable landing page, frontend and API submission route, .env.example, README, and test coverage.
- Offline preview mode and clear instructions for activating the submission workflow.
- Do not hallucinate business addresses, phone numbers, email addresses, university partnerships, prices or reviews.
