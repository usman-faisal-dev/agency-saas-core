"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { UserButton } from "@clerk/nextjs";
import AgencyProfileModal from "@/components/dashboard/AgencyProfileModal";
import AddClientModal from "@/components/dashboard/AddClientModal";
import ClientList from "@/components/dashboard/ClientList";
import { useApiClient } from "@/lib/api-client";
import type { Client, Organization } from "@/types/api";
import styles from "./page.module.css";

export default function DashboardPage() {
  const { isLoaded } = useAuth();
  const callApi = useApiClient();
  const [org, setOrg] = useState<Organization | null>(null);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showAddClient, setShowAddClient] = useState(false);
  const [clientRefreshKey, setClientRefreshKey] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoaded) return;
    callApi<Organization>("/api/v1/organizations/me")
      .then(setOrg)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [isLoaded, callApi]);

  const handleOrgSaved = (updated: Organization) => {
    setOrg(updated);
    setShowProfileModal(false);
  };

  const handleClientSaved = (_client: Client) => {
    setShowAddClient(false);
    setClientRefreshKey((k) => k + 1);
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
          <button
            id="btn-add-client-header"
            className="btn btn-primary"
            onClick={() => setShowAddClient(true)}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            Add Client
          </button>
        </div>
        <ClientList
          onAddClient={() => setShowAddClient(true)}
          refreshKey={clientRefreshKey}
        />
      </div>

      {/* ── Agency Profile Modal ── */}
      {showProfileModal && (
        <AgencyProfileModal
          org={org}
          onClose={() => setShowProfileModal(false)}
          onSaved={handleOrgSaved}
        />
      )}

      {/* ── Add Client Modal ── */}
      {showAddClient && (
        <AddClientModal
          onClose={() => setShowAddClient(false)}
          onSaved={handleClientSaved}
        />
      )}
    </div>
  );
}
