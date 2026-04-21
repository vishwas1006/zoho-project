// frontend/pages/chat.tsx

import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Hello! I can help you manage your Zoho projects. What would you like to do?" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [confirmationId, setConfirmationId] = useState<string | null>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auth check on page load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch("http://localhost:8000/auth/check", {
          credentials: "include",
        });
        if (res.status === 401) {
          window.location.href = "/";
          return;
        }
        setAuthChecked(true);
      } catch (err) {
        window.location.href = "/";
      }
    };
    checkAuth();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading || confirmationId) return;

    const userMessage = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ message: userMessage }),
      });

      if (res.status === 401) {
        window.location.href = "/";
        return;
      }

      const data = await res.json();
      setMessages(prev => [...prev, { role: "assistant", content: data.message }]);

      if (data.requires_confirmation && data.confirmation_id) {
        setConfirmationId(data.confirmation_id);
      }

    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", content: "Something went wrong. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (confirmed: boolean) => {
    if (!confirmationId) return;
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat/confirm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ confirmation_id: confirmationId, confirmed }),
      });

      const data = await res.json();
      setMessages(prev => [...prev, { role: "assistant", content: data.message }]);

    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", content: "Something went wrong. Please try again." }]);
    } finally {
      setConfirmationId(null);
      setLoading(false);
    }
  };

  // Show nothing while checking auth
  if (!authChecked) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <p className="text-gray-400 text-sm">Loading...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col">

      {/* Header */}
      <div className="bg-gray-800 px-6 py-4 flex items-center justify-between border-b border-gray-700">
        <div>
          <h1 className="text-white font-bold text-lg">Zoho Project Assistant</h1>
          <p className="text-gray-400 text-xs">Powered by AI</p>
        </div>
        <button
          onClick={() => window.location.href = "/"}
          className="text-gray-400 hover:text-white text-sm transition"
        >
          Logout
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-2xl px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap leading-relaxed ${
              msg.role === "user"
                ? "bg-blue-600 text-white rounded-br-none"
                : "bg-gray-700 text-gray-100 rounded-bl-none"
            }`}>
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-700 text-gray-400 px-4 py-3 rounded-2xl rounded-bl-none text-sm">
              Thinking...
            </div>
          </div>
        )}

        {/* HIL Confirmation Buttons */}
        {confirmationId && !loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 border border-gray-600 text-gray-100 px-5 py-4 rounded-2xl text-sm max-w-md">
              <p className="mb-1 font-semibold text-white">Please confirm this action</p>
              <p className="text-gray-400 text-xs mb-4">This will make changes to your Zoho Projects account.</p>
              <div className="flex gap-3">
                <button
                  onClick={() => handleConfirm(true)}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg font-medium transition text-sm"
                >
                  Confirm
                </button>
                <button
                  onClick={() => handleConfirm(false)}
                  className="bg-gray-600 hover:bg-gray-500 text-white px-5 py-2 rounded-lg font-medium transition text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="bg-gray-800 border-t border-gray-700 px-4 py-4">
        <div className="flex gap-3 max-w-4xl mx-auto">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && sendMessage()}
            placeholder="Type your message..."
            disabled={loading || !!confirmationId}
            className="flex-1 bg-gray-700 text-white placeholder-gray-400 px-4 py-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 text-sm"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !!confirmationId}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-6 py-3 rounded-xl font-semibold transition text-sm"
          >
            Send
          </button>
        </div>
      </div>

    </div>
  );
}