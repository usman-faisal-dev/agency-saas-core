"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { UserButton } from "@clerk/nextjs";
import AgencyProfileModal from "@/components/dashboard/AgencyProfileModal";
import ClientList from "@/components/dashboard/ClientList";
import { apiClient } from "@/lib/api-client";
import type { Organization } from "@/types/api";
import styles from "./page.module.css";

export default function DashboardPage() {
  const { isLoaded } = useAuth();
  const [org, setOrg] = useState<Organization | null>(null);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoaded) return;
    apiClient<Organization>("/api/v1/organizations/me")
      .then(setOrg)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [isLoaded]);

  const handleOrgSaved = (updated: Organization) => {
    setOrg(updated);
    setShowProfileModal(false);
  };

  return (
    <div className={styles.page}>
      {/* ── Header ── */}
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          {loading ? (
            <div className={styles.orgSkeleton} />
          ) : (
            <button
              id="btn-agency-profile"
              className={styles.orgButton}
              onClick={() => setShowProfileModal(true)}
              title="Edit Agency Profile"
            >
              {org?.logo_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={org.logo_url}
                  alt="Agency logo"
                  className={styles.orgLogo}
                />
              ) : (
                <span className={styles.orgLogoPlaceholder}>
                  {org?.name?.[0]?.toUpperCase() ?? "A"}
                </span>
              )}
              <span className={styles.orgName}>{org?.name ?? "My Agency"}</span>
              <svg
                width="14" height="14" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" strokeWidth="2"
                strokeLinecap="round" strokeLinejoin="round"
                style={{ opacity: 0.5 }}
              >
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
              </svg>
            </button>
          )}
        </div>
        <div className={styles.headerRight}>
          <UserButton afterSignOutUrl="/sign-in" />
        </div>
      </header>

      {/* ── Page body ── */}
      <div className={styles.body}>
        <div className={styles.titleRow}>
          <h1 className={styles.title}>Clients</h1>
          {/* Add Client button lives here in Phase 1 */}
        </div>
        <ClientList />
      </div>

      {/* ── Agency Profile Modal ── */}
      {showProfileModal && (
        <AgencyProfileModal
          org={org}
          onClose={() => setShowProfileModal(false)}
          onSaved={handleOrgSaved}
        />
      )}
    </div>
  );
}
