"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useApiClient } from "@/lib/api-client";
import ConnectAccountButton from "@/components/client-detail/ConnectAccountButton";
import type { Client, ConnectedAccount, Provider } from "@/types/api";
import styles from "./page.module.css";

const ALL_PROVIDERS: { key: Provider; label: string }[] = [
  { key: "ga4", label: "Google Analytics 4" },
  { key: "google_ads", label: "Google Ads" },
];

export default function ClientDetailPage() {
  const params = useParams();
  const clientId = params.clientId as string;
  const callApi = useApiClient();

  const [client, setClient] = useState<Client | null>(null);
  const [accounts, setAccounts] = useState<ConnectedAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchData = useCallback(async () => {
    try {
      const [clientData, accountsData] = await Promise.all([
        callApi<Client>(`/api/v1/clients/${clientId}`),
        callApi<ConnectedAccount[]>(`/api/v1/connected-accounts?client_id=${clientId}`),
      ]);
      setClient(clientData);
      setAccounts(accountsData);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load client");
    } finally {
      setLoading(false);
    }
  }, [callApi, clientId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleConnected = (account: ConnectedAccount) => {
    setAccounts((prev) => {
      const idx = prev.findIndex((a) => a.id === account.id);
      if (idx >= 0) {
        const next = [...prev];
        next[idx] = account;
        return next;
      }
      return [...prev, account];
    });
  };

  const getAccountForProvider = (provider: Provider) =>
    accounts.find((a) => a.provider === provider);

  if (loading) {
    return (
      <div className={styles.page}>
        <div className={styles.skeletonHeader} />
        <div className={styles.skeletonSection} />
      </div>
    );
  }

  if (error || !client) {
    return (
      <div className={styles.page}>
        <div className={styles.errorState}>
          <h2>Unable to load client</h2>
          <p>{error || "Client not found"}</p>
          <Link href="/dashboard" className="btn btn-ghost">
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      {/* ── Header ── */}
      <header className={styles.header}>
        <Link href="/dashboard" className={styles.backLink}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="15 18 9 12 15 6" />
          </svg>
          Back
        </Link>
        <div className={styles.clientInfo}>
          {client.logo_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={client.logo_url} alt={`${client.name} logo`} className={styles.clientLogo} />
          ) : (
            <span className={styles.clientLogoPlaceholder}>
              {client.name[0]?.toUpperCase() ?? "C"}
            </span>
          )}
          <h1 className={styles.clientName}>{client.name}</h1>
        </div>
      </header>

      {/* ── Connected Accounts ── */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Connected Accounts</h2>
        <div className={styles.accountsGrid}>
          {ALL_PROVIDERS.map(({ key, label }) => {
            const account = getAccountForProvider(key);
            const isConnected = account?.status === "connected";
            return (
              <div key={key} className={styles.accountCard}>
                <div className={styles.accountInfo}>
                  <h3 className={styles.accountLabel}>{label}</h3>
                  {account ? (
                    <span
                      className={`${styles.badge} ${
                        isConnected ? styles.badgeConnected : styles.badgeDisconnected
                      }`}
                    >
                      {account.status}
                    </span>
                  ) : (
                    <span className={styles.badge}>not connected</span>
                  )}
                </div>
                {!isConnected && (
                  <ConnectAccountButton
                    provider={key}
                    clientId={clientId}
                    onConnected={handleConnected}
                  />
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* ── Metrics placeholder (Phase 2) ── */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Metrics</h2>
        <div className={styles.placeholder}>
          <p>Metrics and charts will appear here in Phase 2.</p>
        </div>
      </section>
    </div>
  );
}
