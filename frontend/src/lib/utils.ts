/**
 * Shared utility functions.
 * Keep pure — no React, no API calls.
 */

import { type ClassValue } from "clsx";
import clsx from "clsx";

/**
 * Merge CSS class names (similar to cn() in shadcn/ui).
 * Combines clsx for conditional classes.
 */
export function cn(...inputs: ClassValue[]) {
  return clsx(...inputs);
}

/**
 * Format a Date or ISO string as a human-readable short date.
 * e.g. "Jul 10, 2026"
 */
export function formatDate(date: Date | string): string {
  return new Date(date).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

/**
 * Format a number as a compact currency string.
 * e.g. 12345.6 → "$12,345.60"
 */
export function formatCurrency(value: number, currency = "USD"): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

/**
 * Format a ratio as a percentage string.
 * e.g. 0.0345 → "3.45%"
 */
export function formatPercent(value: number, decimals = 2): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Truncate a string to maxLength characters, appending "…" if needed.
 */
export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength).trimEnd() + "…";
}

/**
 * Return initials from a name string (up to 2 characters).
 * e.g. "Meridian Digital" → "MD", "Acme" → "AC"
 */
export function initials(name: string): string {
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}
