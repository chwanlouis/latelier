import axios from "axios";
import { v4 as uuidv4 } from "uuid";

const BASE_URL = import.meta.env.VITE_CHATBOT_URL || "/api/v1";

let sessionId = null;

export function getSessionId() {
  if (!sessionId) {
    sessionId = uuidv4();
  }
  return sessionId;
}

export function resetSession() {
  sessionId = null;
}

export async function sendMessage(message) {
  const sid = getSessionId();
  const response = await axios.post(`${BASE_URL}/chat/`, {
    session_id: sid,
    message,
  });
  return response.data;
}

export async function clearSession() {
  const sid = getSessionId();
  await axios.delete(`${BASE_URL}/chat/${sid}`);
  resetSession();
}
