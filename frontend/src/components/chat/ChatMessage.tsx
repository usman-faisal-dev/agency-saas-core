interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
}

export default function ChatMessage({ role, content }: ChatMessageProps) {
  return (
    <div className={`flex ${role === "user" ? "justify-end" : "justify-start"} mb-2`}>
      <div className="max-w-[75%] rounded-lg px-3 py-2 text-sm bg-gray-100">
        <p>{content}</p>
      </div>
    </div>
  );
}
