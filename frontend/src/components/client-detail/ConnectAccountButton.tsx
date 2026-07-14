"use client";

interface ConnectAccountButtonProps {
  provider: "ga4" | "google_ads";
  clientId: string;
}

export default function ConnectAccountButton({ provider, clientId }: ConnectAccountButtonProps) {
  const label = provider === "ga4" ? "Connect GA4" : "Connect Google Ads";

  return (
    <button
      className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition"
      onClick={() => {
        // TODO: implement OAuth flow
        console.log(`Connect ${provider} for client ${clientId}`);
      }}
    >
      {label}
    </button>
  );
}
