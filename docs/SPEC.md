# SPEC.md — Agency Reporting SaaS: 30-Day MVP

**Status:** Locked v1 (MVP scope)
**Parent document:** Agency Automation SaaS PRD (Draft v1) — this spec carves out the buildable 30-day slice of that PRD's Phase 0–3 vision.
**Core principle:** Ship the full narrative loop — *connect → pull data → AI narrative → human-reviewed PDF → email* — for one agency, two integrations, end to end. Everything else is deferred by explicit, documented decision, not by accident.

---

## 1. Product Summary

A single-agency (multi-client) SaaS where an account manager connects a client's GA4 and Google Ads accounts, the system backfills 60 days of history, and on demand generates an AI-written, structured, numbers-grounded performance report as a branded PDF — reviewed and manually sent to the client via email. A persistent, free-form chat lets the account manager ask natural-language questions about a client's data, answered by an LLM grounded in pre-aggregated real metrics (no hallucinated numbers, no tool-calling brittleness).

The differentiator being proven in this MVP is **not** connector breadth — it's **narrative quality**: an AI analyst that explains what changed and why, citing exact computed metrics, indistinguishable in rigor from a human-written report.

---

## 2. Explicit MVP Scope Decisions

These are the load-bearing decisions from discovery. Each one deliberately narrows the parent PRD for a 30-day build — documented here so nothing is "quietly" descoped.

| Area | MVP Decision | Deferred to Post-MVP |
|---|---|---|
| Integrations | GA4 + Google Ads only | HubSpot, Meta Ads |
| Tenancy | Single org (one agency), multiple clients; app-layer `org_id` scoping | Full Postgres RLS; multi-org isolation |
| Auth roles | Single role — everyone is admin | Owner vs. Account Manager permission gating |
| Billing | None — no Stripe integration | Plans, usage limits, upgrade prompts, Stripe checkout/webhooks |
| LLM provider | Groq (free tier) via vendor-agnostic service layer | Instant swap to Anthropic/OpenAI via env var |
| Ask-your-data | Free-form NL chat, context-injection (pre-aggregated snapshot), **not** tool-calling/text-to-SQL | Dynamic tool-calling, RAG over historical narratives (pgvector) |
| pgvector | Not used in MVP | RAG-based historical narrative retrieval |
| Report cadence | On-demand only; generation function is `start_date`/`end_date` parameterized | Celery Beat monthly/weekly automated scheduling (wraps existing function, no rewrite) |
| OAuth | Simulated UI flow; backend schema is production-ready (encrypted token columns) but populated from hardcoded sandbox env vars | Real per-client OAuth consent flow; Google/Meta app review |
| Email delivery | Manual "Approve & Send" — human-in-the-loop always | Automatic send-on-generation (explicitly rejected as a permanent design choice, not just MVP) |
| Report branding | Agency-level only (logo + name), not per-client | Per-client white-label branding |
| PDF content | Text + tables only, no charts | Chart/image embedding in PDF |
| In-app charts | Minimal time-series charts (Recharts), 1–2 per Client Detail page | Full BI/dashboarding suite (explicit PRD non-goal, still holds) |
| Testing | Targeted pytest coverage: tenant isolation, token encryption round-trip, report generation pipeline | Full endpoint auth test coverage, chat logic tests, job failure-mode tests |
| Backfill | Fixed 60-day window on connect | Configurable backfill window |

---

## 3. Target Users (MVP)

- **Agency user** (single role, no permission tiers) — signs up, connects clients, generates/reviews/sends reports, uses chat. One person or a small team, all with identical permissions in-app.
- **End client** — receives the emailed PDF only. No login, no in-app presence. (Unchanged from PRD.)

---

## 4. Tech Stack (Locked)

| Layer | Choice | Notes |
|---|---|---|
| Frontend | Next.js | Deployed on Vercel |
| Backend API | FastAPI | Deployed on Render (web service) |
| Background jobs | Celery + Redis | Both on Render (worker + Redis instance) |
| Database | Postgres (Neon) | Branching used for safe schema iteration; pgvector available but unused in MVP |
| Auth | Clerk | Single role, single org |
| Billing | None | Explicitly out of scope |
| LLM | Groq (free tier) behind a vendor-agnostic `LLMProvider` interface | Anthropic/OpenAI clients present but toggled off via env var |
| Email | Resend | Manual send trigger only |
| File storage | Cloudflare R2 behind a vendor-agnostic `StorageProvider` interface | `boto3`-based, S3-compatible; org/client-scoped key prefixes for isolation |
| PDF rendering | HTML → PDF (WeasyPrint or Playwright) | Text/table templates only, no chart images |
| Testing | pytest | Targeted, not exhaustive |

**Vendor-agnostic LLM contract:** all narrative/chat calls go through a single internal interface (e.g. `generate_narrative(prompt, context) -> text`), with Groq/OpenAI/Anthropic as interchangeable backends selected by a single environment variable. No calling code should ever reference a provider SDK directly.

**Vendor-agnostic storage contract:** all file uploads (agency logos, client logos, and any future asset type) go through a single internal interface (`StorageProvider.upload()` / `.delete()`), with R2 as the only implementation for MVP but S3/other backends swappable via the same interface. No calling code should ever reference `boto3` or an R2 endpoint directly outside the `storage/` module.

---

## 5. Data Model

### 5.1 Core Tables

**`organizations`**
- `id`, `name`, `logo_url`, `created_at`
- Single row for MVP; `org_id` foreign key exists on all tenant tables to make future multi-org support a config change, not a migration.
- `logo_url` is a reference to a file stored in Cloudflare R2 (via the `StorageProvider` interface, §4) — never a base64/data URI. Uploaded through `POST /api/v1/upload/logo`, key convention `logos/{org_id}/{uuid}.{ext}`.

**`users`**
- `id`, `clerk_user_id`, `org_id`, `email`, `created_at`
- No `role` column enforcement in MVP logic (single role), but field may exist for forward compatibility.

**`clients`**
- `id`, `org_id`, `name`, `logo_url`, `created_at`
- `logo_url` follows the same storage convention as `organizations.logo_url` — same upload endpoint and `StorageProvider`, client-scoped key: `logos/{org_id}/clients/{client_id}/{uuid}.{ext}`.

**`connected_accounts`**
- `id`, `client_id`, `provider` (`ga4` | `google_ads`), `status`, `access_token_encrypted`, `refresh_token_encrypted`, `token_expiry`, `created_at`
- Production-shaped schema populated via simulated flow + hardcoded sandbox credentials in MVP.

**`metrics_daily`**
- `id`, `client_id`, `provider`, `date`
- Typed columns: `sessions`, `conversions`, `impressions`, `clicks`, `spend`
- `properties` (JSONB) — daily snapshot array of contextual metadata:
  - GA4: top traffic sources/mediums for that day
  - Google Ads: campaign-level performance splits for that day
- **No stored ratios.** CTR, CPC, and conversion rate are always computed at query/report time from summed raw values over the requested period — never stored or averaged daily, to avoid mathematically invalid aggregation.

**`reports`**
- `id`, `client_id`, `start_date`, `end_date`, `narrative_json` (structured sections), `pdf_url`, `status` (`draft` | `approved` | `sent`), `created_at`, `sent_at`

**`job_runs`**
- `id`, `job_type` (`backfill` | `report_generation`), `client_id`, `status`, `error_message`, `started_at`, `completed_at`
- Satisfies PRD's "every job audited via JobRun" NFR.

**`chat_sessions`**
- `id`, `client_id`, `created_at`

**`chat_messages`**
- `id`, `chat_session_id`, `role` (`user` | `assistant`), `content`, `created_at`
- Fully persisted from day one.

### 5.2 Tenant Isolation (MVP approach)
- Every tenant-relevant table carries `org_id` (directly or via `client_id → clients.org_id`).
- Enforcement is **app-layer** (every query explicitly scoped), **not** Postgres RLS, for MVP.
- Schema is RLS-ready: adding `ENABLE ROW LEVEL SECURITY` + policies post-MVP requires no column changes.
- Isolation extends to file storage, not just DB rows: R2 object keys are always org-prefixed (and client-prefixed where applicable), and `org_id` used in key generation is always resolved server-side from the authenticated session — never from client-supplied input. Covered by `tests/test_upload_isolation.py`.

---

## 6. Functional Requirements (MVP User Stories)

1. As an agency user, I can sign up and log in via Clerk (single org, single role).
2. As an agency user, I can set my agency name and upload a logo via a global "Agency Profile" modal on the Dashboard header.
3. As an agency user, I can add a new client (name, logo).
4. As an agency user, I can trigger a simulated "Connect GA4" and "Connect Google Ads" flow for a client, which populates `connected_accounts` with sandbox-derived, encrypted token records and triggers a 60-day historical backfill job.
5. As the system, I backfill 60 days of daily metrics (typed core fields + JSONB contextual properties) per connected provider, logging the attempt in `job_runs`.
6. As an agency user, I can view a Client Detail page showing current metric snapshots and 1–2 time-series charts (sessions, spend).
7. As an agency user, I can trigger report generation for a client over an arbitrary `start_date`/`end_date` range (UI defaults to a sensible period, e.g. last 30 days).
8. As the system, I aggregate raw metrics over the requested period, compute all ratios fresh (CTR, CPC, conversion rate) from summed values, generate a structured AI narrative (Executive Summary → Traffic & Acquisition → Ad Performance → Notable Changes → Recommendations) with exact metric values injected inline, and render it as a branded (agency logo/name) text-and-table PDF.
9. As an agency user, I review the generated report (narrative + PDF preview) and either **Approve & Send** (emails the client via Resend, sets `status = sent`) or **Regenerate**.
10. As an agency user, I can open a slide-out chat panel on the Client Detail page, ask free-form natural-language questions about that client's data, and receive answers grounded in a pre-aggregated summary-stats snapshot (never raw daily dumps) injected into the LLM context.
11. As the system, I persist all chat messages per client for later review.

---

## 7. Non-Functional Requirements (MVP-adjusted)

| Area | MVP Requirement |
|---|---|
| Tenancy | App-layer `org_id`/`client_id` scoping on every tenant query; schema RLS-ready |
| Security | Token columns encrypted at rest (even though populated from sandbox env vars); tokens never logged or returned in API responses. File uploads validated by content (not client-supplied MIME/extension) via Pillow; SVG rejected outright (XSS vector) |
| Reliability | `job_runs` audit log on every backfill and report generation attempt; basic retry on external API calls |
| Performance | Report generation (on-demand) completes and is reviewable within minutes of trigger |
| LLM cost | $0 — Groq free tier for all dev/demo narrative and chat generation |
| Data integrity | Ratios never stored pre-computed at daily granularity; always derived fresh from summed raw metrics at the requested aggregation level |
| Human oversight | No report is ever emailed without an explicit human "Approve & Send" action |

---

## 8. Explicitly Out of Scope (MVP)

- HubSpot, Meta Ads integrations
- Real OAuth consent flows (Google app review, per-client authorization)
- Multi-org / cross-agency tenancy and RLS enforcement
- Role-based permissions (owner vs. account manager)
- Billing, plans, usage limits, Stripe
- Automated report scheduling (monthly/weekly)
- Automatic (non-approved) email sending
- Per-client branding/white-labeling
- Charts inside PDF reports
- RAG/pgvector-based chat (historical narrative retrieval)
- Dynamic LLM tool-calling / text-to-SQL
- Comprehensive test coverage (only targeted high-risk areas covered)

---

## 9. Success Criteria (MVP demo)

- A user can sign up, connect a client (simulated), and see a fully backfilled 60-day dataset without manual data entry.
- A generated report's narrative cites specific, correct, computed metrics matching the underlying `metrics_daily` data for the selected period.
- Ratios in the narrative are always correct for the aggregation period (no averaging artifacts).
- A report can be approved and actually arrives in an inbox via Resend.
- The chat panel answers arbitrary natural-language questions about a client's data accurately, using only pre-aggregated context, with no fabricated numbers.
- No client's data is ever visible when viewing another client's pages (isolation holds under manual + targeted automated testing).