/**
 * Shared TypeScript types that mirror backend Pydantic schemas.
 *
 * Keep in sync with backend/app/schemas/*.py.
 * Only add types here as the corresponding backend schemas are implemented.
 *
 * Convention:
 *   - Read types (returned by GET endpoints) match the backend Read schema exactly.
 *   - Create/Update types (sent to POST/PATCH) match the backend Create/Update schema.
 */

// ----------------------------------------------------------------
// Organization (Phase 0)
// ----------------------------------------------------------------

export interface Organization {
  id: string;
  name: string;
  logo_url: string | null;
  created_at: string; // ISO 8601
}

export interface OrganizationUpdate {
  name?: string;
  logo_url?: string | null;
}

// ----------------------------------------------------------------
// User (Phase 0 — returned from auth dependency, not a direct API endpoint)
// ----------------------------------------------------------------

export interface User {
  id: string;
  clerk_user_id: string;
  org_id: string;
  email: string;
  role: string;
  created_at: string;
}

// ----------------------------------------------------------------
// Client (Phase 1)
// ----------------------------------------------------------------

export interface Client {
  id: string;
  org_id: string;
  name: string;
  logo_url: string | null;
  created_at: string;
}

export interface ClientCreate {
  name: string;
  logo_url?: string | null;
}

export interface ClientUpdate {
  name?: string;
  logo_url?: string | null;
}

// ----------------------------------------------------------------
// Connected Account (Phase 1)
// ----------------------------------------------------------------

export type Provider = "ga4" | "google_ads";
export type ConnectionStatus = "connected" | "disconnected" | "error";

export interface ConnectedAccount {
  id: string;
  client_id: string;
  provider: Provider;
  status: ConnectionStatus;
  token_expiry: string | null;
  created_at: string;
  // Note: encrypted token fields are NEVER returned by the API
}

// ----------------------------------------------------------------
// Report (Phase 3)
// ----------------------------------------------------------------

export type ReportStatus = "draft" | "approved" | "sent";

export interface Report {
  id: string;
  client_id: string;
  start_date: string;  // YYYY-MM-DD
  end_date: string;    // YYYY-MM-DD
  narrative_json: ReportNarrative | null;
  pdf_url: string | null;
  status: ReportStatus;
  created_at: string;
  sent_at: string | null;
}

export interface ReportNarrative {
  executive_summary: string;
  traffic_and_acquisition: string;
  ad_performance: string;
  notable_changes: string;
  recommendations: string;
}

// ----------------------------------------------------------------
// Chat (Phase 5)
// ----------------------------------------------------------------

export type ChatRole = "user" | "assistant";

export interface ChatSession {
  id: string;
  client_id: string;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  chat_session_id: string;
  role: ChatRole;
  content: string;
  created_at: string;
}

// ----------------------------------------------------------------
// Common
// ----------------------------------------------------------------

export interface ApiError {
  detail: string;
}
