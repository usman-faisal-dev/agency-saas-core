"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useApiClient } from "@/lib/api-client";
import type { Client } from "@/types/api";
import styles from "./ClientList.module.css";

interface Props {
  onAddClient: () => void;
  refreshKey: number;
}

export default function ClientList({ onAddClient, refreshKey }: Props) {
  const callApi = useApiClient();
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    callApi<Client[]>("/api/v1/clients")
      .then(setClients)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [callApi, refreshKey]);

  if (loading) {
    return (
      <div className={styles.grid}>
        {[1, 2, 3].map((i) => (
          <div key={i} className={styles.skeleton} />
        ))}
      </div>
    );
  }

  if (clients.length === 0) {
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
        <button id="btn-add-client" className="btn btn-primary" onClick={onAddClient}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
            <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Add Client
        </button>
      </div>
    );
  }

  return (
    <div className={styles.grid}>
      {clients.map((client) => (
        <Link
          key={client.id}
          href={`/clients/${client.id}`}
          className={styles.card}
          id={`client-card-${client.id}`}
        >
          <div className={styles.cardLogo}>
            {client.logo_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={client.logo_url} alt={`${client.name} logo`} className={styles.cardLogoImg} />
            ) : (
              <span className={styles.cardLogoPlaceholder}>
                {client.name[0]?.toUpperCase() ?? "C"}
              </span>
            )}
          </div>
          <div className={styles.cardBody}>
            <h3 className={styles.cardName}>{client.name}</h3>
            <p className={styles.cardDate}>
              Added {new Date(client.created_at).toLocaleDateString()}
            </p>
          </div>
        </Link>
      ))}
    </div>
  );
}
