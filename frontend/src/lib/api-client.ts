/**
 * Typed fetch wrapper for the FastAPI backend.
 *
 * - Automatically attaches the Clerk JWT Bearer token from the active session.
 * - Throws a descriptive Error for non-2xx responses.
 * - All API calls in the app go through this — never fetch() directly.
 *
 * Usage:
 *   const org = await apiClient<Organization>("/api/v1/organizations/me");
 *   const updated = await apiClient<Organization>("/api/v1/organizations/me", {
 *     method: "PATCH",
 *     body: JSON.stringify({ name: "New Name" }),
 *   });
 */

import { useAuth } from "@clerk/nextjs";
import { useCallback } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * Fetch a Clerk token from the active session.
 * This helper is used in client components — it calls Clerk's getToken() directly.
 */
async function getClerkToken(): Promise<string | null> {
  // Dynamically import to avoid SSR issues
  const { default: Clerk } = await import("@clerk/clerk-js");
  // We reach into the window.__clerk_frontend_api that Clerk injects
  if (typeof window !== "undefined" && (window as any).__clerk) {
    return (window as any).__clerk.session?.getToken() ?? null;
  }
  return null;
}

/**
 * apiClient<T>(path, init?)
 *
 * Makes an authenticated request to the backend and returns typed JSON.
 * Intended to be called from client components (hooks or event handlers).
 *
 * For use inside React components where useAuth() is available,
 * prefer the useApiClient() hook below instead.
 */
export async function apiClient<T = unknown>(
  path: string,
  init: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string> | undefined),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  });

  if (!res.ok) {
    let detail = `API error ${res.status}`;
    try {
      const body = await res.json();
      if (Array.isArray(body?.detail)) {
        // FastAPI validation errors (422) return an array of error objects
        detail = body.detail.map((e: any) => e.msg || JSON.stringify(e)).join(", ");
      } else {
        detail = body?.detail ?? detail;
      }
    } catch {
      // Non-JSON error body — keep the default message
    }
    throw new Error(detail);
  }

  // 204 No Content
  if (res.status === 204) return undefined as T;

  return res.json() as Promise<T>;
}

/**
 * useApiClient()
 *
 * React hook that returns a pre-authenticated apiClient bound to the
 * current Clerk session token. Use this inside client components.
 *
 * Example:
 *   const call = useApiClient();
 *   const org = await call<Organization>("/api/v1/organizations/me");
 */
export function useApiClient() {
  const { getToken } = useAuth();

  return useCallback(async function call<T = unknown>(
    path: string,
    init: RequestInit = {},
  ): Promise<T> {
    const token = await getToken();
    return apiClient<T>(path, init, token);
  }, [getToken]);
}

/**
 * uploadFile<T>(path, formData, token?)
 *
 * Multipart file upload helper. Does NOT set Content-Type (the browser sets it
 * with the correct multipart/form-data boundary). Use this for file upload
 * endpoints like POST /api/v1/upload/logo.
 */
export async function uploadFile<T = unknown>(
  path: string,
  formData: FormData,
  token?: string | null,
): Promise<T> {
  const headers: Record<string, string> = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!res.ok) {
    let detail = `Upload error ${res.status}`;
    try {
      const body = await res.json();
      detail = body?.detail ?? detail;
    } catch {
      // Non-JSON error body
    }
    throw new Error(detail);
  }

  return res.json() as Promise<T>;
}

/**
 * useUploadFile()
 *
 * React hook that returns a pre-authenticated uploadFile bound to the
 * current Clerk session token.
 */
export function useUploadFile() {
  const { getToken } = useAuth();

  return useCallback(async function upload<T = unknown>(
    path: string,
    formData: FormData,
  ): Promise<T> {
    const token = await getToken();
    return uploadFile<T>(path, formData, token);
  }, [getToken]);
}
