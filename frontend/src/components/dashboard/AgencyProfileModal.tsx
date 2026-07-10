"use client";

import { useState, useRef } from "react";
import { apiClient } from "@/lib/api-client";
import type { Organization } from "@/types/api";
import styles from "./AgencyProfileModal.module.css";

interface Props {
  org: Organization | null;
  onClose: () => void;
  onSaved: (org: Organization) => void;
}

export default function AgencyProfileModal({ org, onClose, onSaved }: Props) {
  const [name, setName] = useState(org?.name ?? "");
  const [logoUrl, setLogoUrl] = useState(org?.logo_url ?? "");
  const [logoPreview, setLogoPreview] = useState(org?.logo_url ?? "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  /** Convert uploaded file → base64 data URI stored as logo_url (MVP approach) */
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) {
      setError("Logo must be under 2 MB");
      return;
    }
    const reader = new FileReader();
    reader.onload = (ev) => {
      const dataUrl = ev.target?.result as string;
      setLogoUrl(dataUrl);
      setLogoPreview(dataUrl);
    };
    reader.readAsDataURL(file);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) { setError("Agency name is required"); return; }
    setSaving(true);
    setError("");
    try {
      const updated = await apiClient<Organization>("/api/v1/organizations/me", {
        method: "PATCH",
        body: JSON.stringify({
          name: name.trim(),
          logo_url: logoUrl || null,
        }),
      });
      onSaved(updated);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to save — please try again");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className={styles.overlay} onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className={styles.modal} role="dialog" aria-modal="true" aria-labelledby="modal-title">
        {/* Header */}
        <div className={styles.header}>
          <h2 className={styles.title} id="modal-title">Agency Profile</h2>
          <button
            id="btn-close-profile-modal"
            className={styles.closeBtn}
            onClick={onClose}
            aria-label="Close modal"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          {/* Logo upload */}
          <div className={styles.logoSection}>
            <button
              type="button"
              id="btn-upload-logo"
              className={styles.logoTarget}
              onClick={() => fileRef.current?.click()}
              title="Click to upload logo"
            >
              {logoPreview ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={logoPreview} alt="Agency logo preview" className={styles.logoImg} />
              ) : (
                <span className={styles.logoPlaceholder}>
                  {name?.[0]?.toUpperCase() ?? "A"}
                </span>
              )}
              <span className={styles.logoOverlay}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" />
                </svg>
              </span>
            </button>
            <input
              ref={fileRef}
              type="file"
              accept="image/png,image/jpeg,image/webp,image/svg+xml"
              style={{ display: "none" }}
              onChange={handleFileChange}
              id="input-logo-file"
            />
            <p className={styles.logoHint}>PNG, JPG, WebP or SVG · max 2 MB</p>
          </div>

          {/* Agency name */}
          <div className={styles.field}>
            <label htmlFor="input-agency-name">Agency Name</label>
            <input
              id="input-agency-name"
              className="input"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Meridian Digital"
              maxLength={255}
              required
            />
          </div>

          {/* Error */}
          {error && <p className={styles.error}>{error}</p>}

          {/* Actions */}
          <div className={styles.actions}>
            <button
              type="button"
              id="btn-cancel-profile"
              className="btn btn-ghost"
              onClick={onClose}
              disabled={saving}
            >
              Cancel
            </button>
            <button
              type="submit"
              id="btn-save-profile"
              className="btn btn-primary"
              disabled={saving || !name.trim()}
            >
              {saving ? <span className="spinner" /> : null}
              {saving ? "Saving…" : "Save Changes"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
