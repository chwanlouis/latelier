import { useState, useCallback } from "react";
import { sendMessage, clearSession } from "../services/api";

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const send = useCallback(async (text) => {
    if (!text.trim()) return;

    const userMsg = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    setError(null);

    try {
      const data = await sendMessage(text);
      const assistantMsg = { role: "assistant", content: data.reply };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setError("Failed to get a response. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(async () => {
    await clearSession();
    setMessages([]);
    setError(null);
  }, []);

  return { messages, loading, error, send, reset };
}
