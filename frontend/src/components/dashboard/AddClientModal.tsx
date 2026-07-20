"use client";

import { useState, useRef, useEffect } from "react";
import { useApiClient, useUploadFile } from "@/lib/api-client";
import type { Client, UploadResponse } from "@/types/api";
import styles from "./AddClientModal.module.css";

interface Props {
  onClose: () => void;
  onSaved: (client: Client) => void;
}

export default function AddClientModal({ onClose, onSaved }: Props) {
  const callApi = useApiClient();
  const upload = useUploadFile();
  const [name, setName] = useState("");
  const [logoPreview, setLogoPreview] = useState("");
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [warning, setWarning] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  // Revoke object URLs to avoid memory leaks
  useEffect(() => {
    return () => {
      if (logoPreview.startsWith("blob:")) {
        URL.revokeObjectURL(logoPreview);
      }
    };
  }, [logoPreview]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) {
      setError("Logo must be under 2 MB");
      return;
    }
    setError("");
    setLogoFile(file);
    setLogoPreview(URL.createObjectURL(file));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) { setError("Client name is required"); return; }
    setSaving(true);
    setError("");
    setWarning("");

    try {
      // Step 1: Create the client (name only)
      const created = await callApi<Client>("/api/v1/clients", {
        method: "POST",
        body: JSON.stringify({ name: name.trim() }),
      });

      // Step 2: If a logo file was selected, upload it and patch the client
      if (logoFile) {
        try {
          const formData = new FormData();
          formData.append("logo", logoFile);
          formData.append("client_id", created.id);
          const result = await upload<UploadResponse>("/api/v1/upload/logo", formData);

          const updated = await callApi<Client>(`/api/v1/clients/${created.id}`, {
            method: "PATCH",
            body: JSON.stringify({ logo_url: result.url }),
          });
          onSaved(updated);
          return;
        } catch {
          // Client was created but logo upload/patch failed — keep the client
          setWarning(
            "Client created, but the logo couldn't be uploaded. You can update it later from the client page."
          );
          onSaved(created);
          return;
        }
      }

      onSaved(created);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create client — please try again");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className={styles.overlay} onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className={styles.modal} role="dialog" aria-modal="true" aria-labelledby="add-client-title">
        {/* Header */}
        <div className={styles.header}>
          <h2 className={styles.title} id="add-client-title">Add Client</h2>
          <button
            id="btn-close-add-client"
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
              id="btn-upload-client-logo"
              className={styles.logoTarget}
              onClick={() => fileRef.current?.click()}
              title="Click to upload logo"
            >
              {logoPreview ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={logoPreview} alt="Client logo preview" className={styles.logoImg} />
              ) : (
                <span className={styles.logoPlaceholder}>
                  {name?.[0]?.toUpperCase() ?? "C"}
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
              accept="image/png,image/jpeg,image/webp"
              style={{ display: "none" }}
              onChange={handleFileChange}
              id="input-client-logo-file"
            />
            <p className={styles.logoHint}>PNG, JPG or WebP · max 2 MB</p>
          </div>

          {/* Client name */}
          <div className={styles.field}>
            <label htmlFor="input-client-name">Client Name</label>
            <input
              id="input-client-name"
              className="input"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Acme Corp"
              maxLength={255}
              required
            />
          </div>

          {/* Error / Warning */}
          {error && <p className={styles.error}>{error}</p>}
          {warning && <p className={styles.warning}>{warning}</p>}

          {/* Actions */}
          <div className={styles.actions}>
            <button
              type="button"
              id="btn-cancel-add-client"
              className="btn btn-ghost"
              onClick={onClose}
              disabled={saving}
            >
              Cancel
            </button>
            <button
              type="submit"
              id="btn-save-add-client"
              className="btn btn-primary"
              disabled={saving || !name.trim()}
            >
              {saving ? <span className="spinner" /> : null}
              {saving ? "Creating…" : "Add Client"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
