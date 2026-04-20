import React, { useEffect, useRef } from "react";
import Message from "./Message";
import InputBar from "./InputBar";
import { useChat } from "../hooks/useChat";

export default function ChatWindow() {
  const { messages, loading, error, send, reset } = useChat();
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        maxWidth: "800px",
        margin: "0 auto",
        background: "#fff",
        boxShadow: "0 0 30px rgba(0,0,0,0.08)",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "16px 20px",
          borderBottom: "1px solid #e5e7eb",
          background: "#fff",
        }}
      >
        <div>
          <h1 style={{ margin: 0, fontSize: "1.2rem", fontWeight: 700, color: "#111827" }}>
            🍽 L'atelier — Culinary AI
          </h1>
          <p style={{ margin: 0, fontSize: "0.8rem", color: "#6b7280" }}>
            Molecular food pairing assistant
          </p>
        </div>
        <button
          onClick={reset}
          style={{
            padding: "6px 14px",
            borderRadius: "8px",
            border: "1px solid #d1d5db",
            background: "#fff",
            cursor: "pointer",
            fontSize: "0.85rem",
            color: "#374151",
          }}
        >
          New Chat
        </button>
      </div>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "20px 16px",
          background: "#f9fafb",
        }}
      >
        {messages.length === 0 && (
          <div
            style={{
              textAlign: "center",
              color: "#9ca3af",
              marginTop: "60px",
              fontSize: "0.95rem",
            }}
          >
            <p>Ask me about food pairings, molecular flavour profiles,</p>
            <p>or OR6A2 genetic sensitivities.</p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <Message key={idx} role={msg.role} content={msg.content} />
        ))}
        {loading && (
          <div style={{ textAlign: "center", color: "#9ca3af", fontSize: "0.85rem" }}>
            Thinking…
          </div>
        )}
        {error && (
          <div style={{ textAlign: "center", color: "#ef4444", fontSize: "0.85rem" }}>
            {error}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <InputBar onSend={send} disabled={loading} />
    </div>
  );
}
