"use client";

import styles from "./ClientList.module.css";

/**
 * Phase 0: empty state only.
 * Phase 1 will replace this with a real list from GET /api/v1/clients.
 */
export default function ClientList() {
  return (
    <div className={styles.emptyState}>
      <div className={styles.emptyIcon}>
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round" strokeLinejoin="round">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
          <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
      </div>
      <h3 className={styles.emptyTitle}>No clients yet</h3>
      <p className={styles.emptyDescription}>
        Add your first client to start connecting their ad accounts and generating reports.
      </p>
      {/* "Add Client" button wired up in Phase 1 */}
      <button id="btn-add-client-placeholder" className="btn btn-primary" disabled>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
          <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        Add Client
      </button>
    </div>
  );
}
