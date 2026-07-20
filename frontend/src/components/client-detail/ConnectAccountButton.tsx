"use client";

import { useState } from "react";
import { useApiClient } from "@/lib/api-client";
import type { ConnectedAccount, Provider } from "@/types/api";

interface ConnectAccountButtonProps {
  provider: Provider;
  clientId: string;
  onConnected: (account: ConnectedAccount) => void;
}

export default function ConnectAccountButton({
  provider,
  clientId,
  onConnected,
}: ConnectAccountButtonProps) {
  const callApi = useApiClient();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const label = provider === "ga4" ? "Connect GA4" : "Connect Google Ads";

  const handleConnect = async () => {
    setLoading(true);
    setError("");
    try {
      const account = await callApi<ConnectedAccount>("/api/v1/connected-accounts", {
        method: "POST",
        body: JSON.stringify({ client_id: clientId, provider }),
      });
      onConnected(account);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Connection failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button
        id={`btn-connect-${provider}`}
        className="btn btn-primary"
        onClick={handleConnect}
        disabled={loading}
      >
        {loading ? <span className="spinner" /> : null}
        {loading ? "Connecting…" : label}
      </button>
      {error && (
        <p style={{ fontSize: "0.8125rem", color: "var(--color-danger)", marginTop: "0.375rem" }}>
          {error}
        </p>
      )}
    </div>
  );
}
