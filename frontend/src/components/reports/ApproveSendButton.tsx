"use client";

interface ApproveSendButtonProps {
  reportId: string;
  status: "draft" | "approved" | "sent";
  onAction?: () => void;
}

export default function ApproveSendButton({ reportId, status, onAction }: ApproveSendButtonProps) {
  const isDraft = status === "draft";
  const label = isDraft ? "Approve & Send" : status === "approved" ? "Sending…" : "Sent";

  return (
    <button
      className={`px-4 py-2 text-sm font-medium rounded-lg transition ${
        status === "sent"
          ? "bg-gray-200 text-gray-500 cursor-not-allowed"
          : "bg-green-600 text-white hover:bg-green-700"
      }`}
      disabled={status === "sent"}
      onClick={() => {
        // TODO: call approve/send endpoint
        console.log(`Approve & send report ${reportId}`);
        onAction?.();
      }}
    >
      {label}
    </button>
  );
}
