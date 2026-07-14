"use client";

interface ChatPanelProps {
  clientId: string;
}

export default function ChatPanel({ clientId }: ChatPanelProps) {
  return (
    <div className="flex flex-col h-full border rounded-lg p-4">
      <p className="text-sm text-gray-500">Chat panel for client {clientId}</p>
    </div>
  );
}
