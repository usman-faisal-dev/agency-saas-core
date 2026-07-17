# PLAN.md — 30-Day Implementation Roadmap

**Companion to:** SPEC.md
**Structure:** Six phases, each independently executable and independently demoable. Do not start a phase until the previous phase's demo checkpoint passes — this is what keeps a 30-day solo build from unraveling.

---

## Phase 0 — Foundation (Days 1–4)

**Goal:** Empty but real skeleton — auth works, database exists, deployment pipeline works, nothing depends on guesswork later.

**Tasks:**
- Initialize Next.js app, deploy to Vercel (even as a blank page) — prove the deploy pipeline first.
- Initialize FastAPI app, deploy to Render as a web service — prove it responds.
- Provision Neon Postgres; connect FastAPI via SQLAlchemy/Alembic (or your ORM of choice).
- Provision Redis on Render; stand up a Celery worker as a co-located background process alongside Uvicorn inside the same free Render Web Service container (using `wait -n` orchestration); run a trivial test task end-to-end.
- Integrate Clerk on the Next.js frontend; wire a single-role session through to FastAPI (JWT verification middleware).
- Create core tables per SPEC.md §5.1: `organizations`, `users`, `clients` (migration only — other tables come in later phases as needed).
- Implement the `org_id` scoping pattern as a reusable query helper/dependency in FastAPI (not enforced yet everywhere, but the pattern exists and is used from the first query onward).
- Build the Agency Profile modal (name + logo upload) on the Dashboard header shell integrated directly with Cloudflare R2 object storage via an abstract `StorageProvider` interface

**Demo checkpoint:** A user can sign up via Clerk, land on an (empty) Dashboard, set their agency name/logo, and the whole stack (Vercel ↔ Render ↔ Neon ↔ Redis/Celery ↔ Cloudflare R2) is proven live, not just local.

**Deliverable artifacts:** Alembic migration files, Clerk integration, Cloudflare R2 integration + tenant-isolation tests, deployed URLs for both services.

---

## Phase 1 — Clients, Simulated Connections & Encrypted Token Schema (Days 5–9)

**Goal:** Add/view clients; simulate the connect flow with a production-shaped, encrypted `connected_accounts` table.

**Tasks:**
- `clients` CRUD: add client (name, logo), list clients on Dashboard.
  - **Logo upload reuses the Phase 0 storage module** (`upload_logo()` / the existing `/api/v1/upload/logo` endpoint) — do not reimplement upload logic or introduce a second storage path for clients.
  - Extend the R2 key convention to be client-scoped: `logos/{org_id}/clients/{client_id}/{uuid}.{ext}`, keeping the same org-prefix isolation guarantee established in Phase 0.
- Migration: `connected_accounts` table per SPEC.md §5.1.
- Build the field-level encryption utility for `access_token_encrypted` / `refresh_token_encrypted` (e.g. Fernet/cryptography lib with a key from env/secrets manager) — this is a standalone, testable module.
- Build the "Connect GA4" / "Connect Google Ads" buttons on the Client Detail page: on click, simulate success, write encrypted sandbox-derived credentials (from hardcoded env vars) into `connected_accounts`, set `status = connected`.
- **pytest deliverable:** encryption/decryption round-trip test — write a token, read it back, assert it matches, assert the raw DB value is not plaintext.

**Demo checkpoint:** Add a client, click both "Connect" buttons, see status flip to connected, confirm in the DB that tokens are encrypted at rest. Encryption test passes.

---

## Phase 2 — Data Pull & 60-Day Backfill (Days 10–14)

**Goal:** Real metrics flowing from GA4 demo property + Google Ads test manager account into `metrics_daily`.

**Tasks:**
- Migration: `metrics_daily` (typed columns + JSONB `properties`), `job_runs`.
- Build GA4 pull function against the public demo property (sessions, conversions, top traffic sources/mediums into `properties`).
- Build Google Ads pull function against the sandbox/test manager account (impressions, clicks, spend, conversions, campaign-level splits into `properties`).
- Wrap both behind a common internal interface (e.g. `fetch_daily_metrics(client_id, provider, date_range)`) so provider-specific logic never leaks into calling code — mirrors the LLM vendor-agnostic pattern for consistency.
- Celery task: on "Connect" success (from Phase 1), enqueue a 60-day backfill job per provider; log start/success/failure to `job_runs`.
- Client Detail page: render 1–2 Recharts time-series charts (sessions, spend) and basic stat cards from real backfilled data.

**Demo checkpoint:** Connecting a client actually results in 60 days of real, correctly-typed metrics rows in Postgres, visible as charts/numbers on the Client Detail page, with a `job_runs` row proving it happened.

---

## Phase 3 — Report Generation Pipeline: The Core Differentiator (Days 15–21)

**Goal:** The single most important phase. Aggregation → LLM narrative → branded PDF, fully deterministic on the numbers side.

**Tasks:**
- Build the aggregation function: given `client_id`, `start_date`, `end_date` — sum raw typed metrics across the period, compute CTR/CPC/conversion rate fresh from those sums (never from stored ratios), extract top campaigns/sources from `properties` JSONB.
- Build the vendor-agnostic `LLMProvider` interface (`generate_narrative(structured_input) -> structured_output`) with a Groq implementation live and Anthropic/OpenAI implementations stubbed behind the same interface, selected via env var.
- Design the prompt contract: input is the pre-computed structured metrics (never raw rows); output must be structured JSON matching the five fixed sections (Executive Summary, Traffic & Acquisition, Ad Performance, Notable Changes/Anomalies, Recommendations), with every claim citing an exact backend-computed value — the LLM narrates, never calculates.
- Build the `generate_report(client_id, start_date, end_date)` core function — cadence-agnostic by construction, callable on-demand now, wrappable by Celery Beat later without modification.
- Build the HTML template (agency logo/name, structured sections, tables) and HTML→PDF rendering step (WeasyPrint/Playwright).
- Migration: `reports` table. Store `narrative_json` + rendered `pdf_url` + `status`.
- Log every generation attempt to `job_runs`.
- **pytest deliverable:** given a fixed, known set of `metrics_daily` fixture rows, assert the aggregation produces mathematically correct sums/ratios, and assert the pipeline produces a valid `reports` row with all five sections populated and a non-empty PDF.

**Demo checkpoint:** Click "Generate Report" on a real client's data, get back a structured narrative citing exact real numbers, rendered as a clean PDF. Pipeline test suite passes.

---

## Phase 4 — Review, Approve & Send (Days 22–24)

**Goal:** Close the loop with a human-in-the-middle send step.

**Tasks:**
- Build the Report Review screen: render narrative sections + embedded PDF preview, show `status`.
- Add "Approve & Send" action: integrate Resend, send the PDF to a client contact email, set `status = sent`, `sent_at`.
- Add "Regenerate" action: re-runs Phase 3's `generate_report` for the same range, replaces the draft.
- Add report history list on Client Detail page (past reports, statuses, view links).

**Demo checkpoint:** Full loop works end-to-end live: connect → backfill → generate → review → approve → real email lands in an inbox with the PDF attached.

---

## Phase 5 — Ask-Your-Data Chat (Days 25–28)

**Goal:** Free-form chat, context-injection architecture, fully persisted.

**Tasks:**
- Migration: `chat_sessions`, `chat_messages`.
- Build the snapshot function: pre-aggregated summary stats (totals, weekly rollups, % changes, top campaigns/sources) for a client — reuses Phase 3's aggregation logic, not a separate implementation.
- Build the chat endpoint: on session start, generate the snapshot once, inject as system/context content; each user message + snapshot context goes to the `LLMProvider` interface; persist both user and assistant messages to `chat_messages`.
- Build the slide-out chat panel UI on the Client Detail page (free-form text input, message history, loading state).
- Sanity-check Groq context window against real snapshot size; trim/summarize further if needed (should already be safe given pre-aggregation, but verify empirically with real data volumes).

**Demo checkpoint:** Open chat on a real client, ask an arbitrary question ("what drove the spend increase this month?"), get an accurate answer grounded in real numbers, refresh the page, confirm history persisted.

---

## Phase 6 — Isolation Hardening, Testing Pass & Demo Polish (Days 29–30)

**Goal:** Prove the zero-data-leak requirement holds, tie off loose ends, prepare the demo.

**Tasks:**
- **pytest deliverable:** tenant isolation test suite — create two clients under different simulated scenarios, assert every data-fetching function/endpoint scoped to client A never returns client B's rows (metrics, reports, chat messages).
  - **Extends** `tests/test_upload_isolation.py` (from Phase 0) with metrics/reports/chat coverage — does not duplicate the upload-path isolation tests already passing.
- Manual pass: click through every screen as a second client to visually confirm no cross-client leakage in the UI.
- Fix any rough edges surfaced by the above.
- Final polish: loading states, error states (failed backfill, failed generation), empty states (no clients yet, no reports yet).
- Rehearse the full demo script: sign up → agency profile → add client → connect → backfill → view dashboard → generate report → review → approve & send → chat.

**Demo checkpoint:** All three pytest suites pass (encryption, pipeline, isolation). Full demo script runs clean, live, start to finish.

---

## Cross-Cutting Notes (apply throughout, not phase-specific)

- **LLM provider swap:** at no point should any phase's code call Groq/OpenAI/Anthropic SDKs directly outside the `LLMProvider` interface module. Violating this in a "just this once" moment is the most likely silent scope-creep risk in the whole plan.
- **Storage provider boundary:** at no point should any phase's code call `boto3`/R2 directly outside the `storage/` module (`StorageProvider` interface, `upload_logo()`/`delete_logo()`). Any future file type (report assets, client-uploaded documents) goes through the same interface — this is the same discipline as the LLM rule, for the same reason.
- **Cadence-agnostic reports:** the `generate_report(client_id, start_date, end_date)` function must never be modified to assume "on-demand" — it should look identical whether called from a button click or a future Celery Beat schedule.
- **Ratios:** never introduce a stored ratio column anywhere, ever, even as a "just for caching" shortcut — this was explicitly identified as a correctness risk.
- **Every new tenant-scoped table** must include `org_id` or a traceable path to it (via `client_id`) from the moment it's created — retrofitting this later is expensive; adding it now is free.

---

## What Happens After Day 30 (explicitly not part of this plan, for context only)

Real OAuth + Google/Meta app review, Postgres RLS enforcement, multi-org support, role-based permissions, Stripe billing, automated report scheduling via Celery Beat (wrapping the existing `generate_report` function), per-client branding, RAG-based historical chat via pgvector, HubSpot/Meta Ads integrations, and broader test coverage. None of these require rearchitecting what's built in this plan — that was the point of every "production-ready schema, simplified flow" decision made during discovery.
