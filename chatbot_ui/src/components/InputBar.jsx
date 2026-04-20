import React, { useState } from "react";

export default function InputBar({ onSend, disabled }) {
  const [value, setValue] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (!value.trim() || disabled) return;
    onSend(value.trim());
    setValue("");
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      handleSubmit(e);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        display: "flex",
        gap: "8px",
        padding: "12px 16px",
        borderTop: "1px solid #e5e7eb",
        background: "#fff",
      }}
    >
      <textarea
        rows={1}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask about ingredients, pairings, or food science…"
        disabled={disabled}
        style={{
          flex: 1,
          resize: "none",
          padding: "10px 14px",
          borderRadius: "12px",
          border: "1px solid #d1d5db",
          fontSize: "0.95rem",
          outline: "none",
          fontFamily: "inherit",
        }}
      />
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        style={{
          padding: "10px 20px",
          borderRadius: "12px",
          border: "none",
          background: "#2563eb",
          color: "#fff",
          fontWeight: 600,
          cursor: disabled ? "not-allowed" : "pointer",
          opacity: disabled ? 0.6 : 1,
          fontSize: "0.95rem",
        }}
      >
        Send
      </button>
    </form>
  );
}
