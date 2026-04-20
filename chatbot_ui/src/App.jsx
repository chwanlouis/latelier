import React from "react";
import ChatWindow from "./components/ChatWindow";

export default function App() {
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #f0f4ff 0%, #fafafa 100%)",
        fontFamily: "'Inter', 'Segoe UI', sans-serif",
      }}
    >
      <ChatWindow />
    </div>
  );
}
