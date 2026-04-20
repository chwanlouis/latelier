import React from "react";

export default function Message({ role, content }) {
  const isUser = role === "user";
  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: "12px",
      }}
    >
      <div
        style={{
          maxWidth: "70%",
          padding: "10px 14px",
          borderRadius: isUser ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
          background: isUser ? "#2563eb" : "#f3f4f6",
          color: isUser ? "#fff" : "#111827",
          fontSize: "0.95rem",
          lineHeight: "1.5",
          whiteSpace: "pre-wrap",
          boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
        }}
      >
        {content}
      </div>
    </div>
  );
}
