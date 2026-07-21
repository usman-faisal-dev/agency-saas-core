agency-saas-core/
│
├── frontend/                          # Next.js app — deployed to Vercel
│   ├── src/
│   │   ├── app/                       # Next.js App Router
│   │   │   ├── (auth)/                # Clerk sign-in/sign-up routes
│   │   │   ├── dashboard/
│   │   │   │   ├── page.tsx           # Client list + Agency Profile modal trigger
│   │   │   │   ├── page.module.css
│   │   │   │   ├── layout.tsx
│   │   │   │   └── layout.module.css
│   │   │   ├── clients/
│   │   │   │   └── [clientId]/
│   │   │   │       ├── page.tsx       # Client Detail: charts, connect buttons, chat panel entry
│   │   │   │       └── reports/
│   │   │   │           └── [reportId]/page.tsx   # Report Review screen
│   │   │   └── layout.tsx             # Root layout, Clerk provider
│   │   │
│   │   ├── components/
│   │   │   ├── dashboard/
│   │   │   │   ├── AgencyProfileModal.tsx
│   │   │   │   ├── AgencyProfileModal.module.css
│   │   │   │   ├── AddClientModal.tsx
│   │   │   │   ├── AddClientModal.module.css
│   │   │   │   ├── ClientList.tsx
│   │   │   │   └── ClientList.module.css
│   │   │   ├── client-detail/
│   │   │   │   ├── ConnectAccountButton.tsx
│   │   │   │   ├── MetricsChart.tsx
│   │   │   │   ├── StatCard.tsx
│   │   │   │   └── ReportHistoryList.tsx
│   │   │   ├── chat/
│   │   │   │   ├── ChatPanel.tsx      # Slide-out panel
│   │   │   │   ├── ChatMessage.tsx
│   │   │   │   └── ChatInput.tsx
│   │   │   ├── reports/
│   │   │   │   ├── ReportNarrative.tsx
│   │   │   │   ├── PdfPreview.tsx
│   │   │   │   └── ApproveSendButton.tsx
│   │   │   └── ui/                    # Shared primitives (buttons, modals, inputs)
│   │   │
│   │   ├── lib/
│   │   │   ├── api-client.ts          # Typed fetch wrapper for FastAPI backend
│   │   │   ├── clerk.ts
│   │   │   └── utils.ts
│   │   │
│   │   ├── types/
│   │   │   └── api.ts                 # Shared TS types mirroring backend Pydantic schemas
│   │   │
│   │   ├── styles/
│   │   │   └── globals.css             # Global styles, CSS custom properties
│   │   │
│   │   └── middleware.ts               # Next.js middleware (Clerk auth guard)
│   │
│   ├── public/
│   ├── .env.local.example
│   ├── next.config.js
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                            # FastAPI app — deployed to Render
│   ├── .venv/                          # Virtual environment (use `uv venv`)
│   ├── app/
│   │   ├── main.py                     # FastAPI app instance, router registration
│   │   ├── config.py                   # Settings via pydantic-settings, env-driven
│   │   ├── dependencies.py             # Shared deps: current_org, current_user, db session
│   │   │
│   │   ├── core/                       # Cross-cutting, pillar-agnostic infrastructure
│   │   │   ├── database.py             # SQLAlchemy engine/session, Neon connection
│   │   │   ├── security.py             # Token encryption (Fernet), Clerk JWT verification
│   │   │   ├── celery_app.py           # Celery instance + Redis broker config
│   │   │   └── exceptions.py           # Shared exception types + handlers
│   │   │
│   │   ├── models/                     # SQLAlchemy models — one file per table
│   │   │   ├── __init__.py             # Barrel export for all models
│   │   │   ├── organization.py
│   │   │   ├── user.py
│   │   │   ├── client.py
│   │   │   ├── connected_account.py
│   │   │   ├── metrics_daily.py
│   │   │   ├── report.py
│   │   │   ├── job_run.py
│   │   │   ├── chat_session.py
│   │   │   └── chat_message.py
│   │   │
│   │   ├── schemas/                    # Pydantic request/response models
│   │   │   ├── organization.py
│   │   │   ├── client.py
│   │   │   ├── connected_account.py
│   │   │   ├── report.py
│   │   │   └── chat.py
│   │   │
│   │   ├── api/                        # Route handlers, grouped by resource
│   │   │   ├── v1/
│   │   │   │   ├── clients.py
│   │   │   │   ├── connected_accounts.py
│   │   │   │   ├── metrics.py
│   │   │   │   ├── reports.py
│   │   │   │   ├── chat.py
│   │   │   │   ├── organizations.py    # Agency profile endpoint
│   │   │   │   └── upload.py           # File upload (logo → R2)
│   │   │   └── router.py               # Aggregates all v1 routers
│   │   │
│   │   ├── integrations/               # Provider-abstracted data pull layer
│   │   │   ├── base.py                 # Abstract interface: fetch_daily_metrics(...)
│   │   │   ├── ga4/
│   │   │   │   ├── client.py           # GA4-specific API calls (demo property)
│   │   │   │   └── mapper.py           # Maps GA4 response → metrics_daily schema
│   │   │   └── google_ads/
│   │   │       ├── client.py           # Google Ads-specific API calls (sandbox)
│   │   │       └── mapper.py
│   │   │
│   │   ├── pillars/                    # Self-registering, non-importing-each-other pillars
│   │   │   └── reporting/              # v1 — the only pillar shipping in MVP
│   │   │       ├── aggregation.py      # Sum raw metrics, compute ratios fresh (never stored)
│   │   │       ├── narrative.py        # Builds structured prompt input, calls LLM layer
│   │   │       ├── pdf_renderer.py     # HTML → PDF (WeasyPrint/Playwright)
│   │   │       ├── templates/
│   │   │       │   └── report.html     # Jinja2 template: branded, text/table only
│   │   │       └── service.py          # generate_report(client_id, start_date, end_date)
│   │   │       # future pillars (agents/, content_ops/, internal_ops/) slot in here
│   │   │       # as siblings, same shape, without touching core/ or reporting/
│   │   │
│   │   ├── ai/                         # Vendor-agnostic LLM abstraction
│   │   │   ├── provider_interface.py   # Abstract LLMProvider base class
│   │   │   ├── providers/
│   │   │   │   ├── groq_provider.py    # Active implementation (free tier)
│   │   │   │   ├── openai_provider.py  # Present, inactive — toggled via env var
│   │   │   │   └── anthropic_provider.py  # Present, inactive — toggled via env var
│   │   │   ├── factory.py              # Selects provider based on LLM_PROVIDER env var
│   │   │   └── chat_context_builder.py # Builds pre-aggregated snapshot for chat injection
│   │   │
│   │   ├── storage/                     # File storage abstraction (logos, future assets)
│   │   │   ├── __init__.py             # upload_logo() / delete_logo() / extract_logo_key() helpers
│   │   │   ├── interface.py             # Abstract StorageProvider base class
│   │   │   ├── r2_provider.py           # Cloudflare R2 via boto3 (S3-compatible API)
│   │   │   └── factory.py              # get_storage() — cached singleton, swap backend here
│   │   │
│   │   ├── email/
│   │   │   └── resend_client.py         # Resend integration, "Approve & Send" logic
│   │   │
│   │   ├── tasks/                       # Celery task definitions
│   │   │   ├── backfill.py              # 60-day historical backfill job
│   │   │   └── report_generation.py     # Async wrapper around reporting/service.py
│   │   │
│   │   └── db/
│   │       └── alembic/                 # Migrations
│   │           ├── versions/
│   │           └── env.py
│   │
│   ├── tests/                           # pytest — targeted, per SPEC.md §7 discipline
│   │   ├── conftest.py                  # Fixtures: test DB, fixture clients/orgs
│   │   ├── test_tenant_isolation.py     # Cross-client data leak checks
│   │   ├── test_clients_isolation.py    # Isolation tests for clients/accounts endpoints
│   │   ├── test_token_encryption.py     # Encrypt/decrypt round-trip
│   │   ├── test_report_pipeline.py      # Aggregation correctness + full pipeline
│   │   ├── test_upload_isolation.py     # Upload endpoint tenant-isolation (org_id from session only)
│   │   └── test_logo_cleanup.py         # R2 orphaned file cleanup tests
│   │
│   ├── .env.example
│   ├── alembic.ini
│   ├── requirements.txt
│   └── pyproject.toml
│
├── docs/
│   ├── SPEC.md
│   ├── PLAN.md
│   ├── STRUCTURE.md
│   ├── agency_saas_PRD.pdf
│   └── architecture-decisions.md        # Optional: lightweight ADR log as you build
│
├── .github/
│   └── workflows/
│       ├── backend-ci.yml               # pytest on PR
│       └── frontend-ci.yml              # lint/typecheck on PR
│
├── .gitignore
└── README.md