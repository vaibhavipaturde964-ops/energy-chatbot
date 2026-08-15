/**
 * EcoBot — Frontend chat logic
 *
 * The backend URL is read from window.BACKEND_URL (injected by Vercel
 * environment at build time via a _redirects/config approach) or falls
 * back to localhost for local development.
 *
 * The GROQ_API_KEY is NEVER present in this file or any frontend file.
 * All RAG processing happens server-side on Render.
 */

// ---------------------------------------------------------------------------
// Configuration
// Backend URL: set BACKEND_URL as a Vercel environment variable.
// For local dev, the proxy in the fetch call falls back to localhost.
// ---------------------------------------------------------------------------
const BACKEND_URL = (window.__ENV && window.__ENV.BACKEND_URL)
  ? window.__ENV.BACKEND_URL
  : "http://localhost:8000";

// ---------------------------------------------------------------------------
// DOM references
// ---------------------------------------------------------------------------
const chatWindow = document.getElementById("chatWindow");
const userInput  = document.getElementById("userInput");
const sendBtn    = document.getElementById("sendBtn");
const clearBtn   = document.getElementById("clearBtn");
const errorBanner = document.getElementById("errorBanner");

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
let isLoading = false;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function showError(msg) {
  errorBanner.textContent = "⚠️ " + msg;
  errorBanner.style.display = "block";
}

function hideError() {
  errorBanner.style.display = "none";
}

function scrollToBottom() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function removeWelcome() {
  const welcome = chatWindow.querySelector(".welcome-msg");
  if (welcome) welcome.remove();
}

/**
 * Append a message bubble to the chat window.
 * @param {"user"|"bot"} role
 * @param {string} text
 * @param {string[]} sources
 * @returns {HTMLElement} the bubble element (used for typing placeholder)
 */
function appendMessage(role, text, sources = []) {
  removeWelcome();

  const row = document.createElement("div");
  row.className = `msg-row ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "👤" : "🌱";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  // Add sources if present
  if (sources.length > 0) {
    const srcDiv = document.createElement("div");
    srcDiv.className = "sources";
    srcDiv.innerHTML = "📄 Sources: " + sources.map(s => `<span>${s}</span>`).join("");
    bubble.appendChild(srcDiv);
  }

  row.appendChild(avatar);
  row.appendChild(bubble);
  chatWindow.appendChild(row);
  scrollToBottom();
  return bubble;
}

/**
 * Show an animated typing indicator while waiting for the API.
 * Returns a function that removes it.
 */
function showTyping() {
  removeWelcome();
  const row = document.createElement("div");
  row.className = "msg-row bot typing";
  row.id = "typingIndicator";

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = "🌱";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = "🤖 EcoBot is thinking… 🌱⚡✨";

  row.appendChild(avatar);
  row.appendChild(bubble);
  chatWindow.appendChild(row);
  scrollToBottom();

  return () => {
    const el = document.getElementById("typingIndicator");
    if (el) el.remove();
  };
}

// ---------------------------------------------------------------------------
// Core: send question to backend
// ---------------------------------------------------------------------------
async function sendMessage() {
  const question = userInput.value.trim();
  if (!question || isLoading) return;

  hideError();
  isLoading = true;
  sendBtn.disabled = true;
  userInput.value = "";

  // Show user message
  appendMessage("user", question);

  // Show typing indicator
  const removeTyping = showTyping();

  try {
    const response = await fetch(`${BACKEND_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    removeTyping();

    if (!response.ok) {
      let detail = `Server error ${response.status}`;
      try {
        const err = await response.json();
        detail = err.detail || detail;
      } catch (_) {}
      throw new Error(detail);
    }

    const data = await response.json();
    appendMessage("bot", data.answer, data.sources || []);

  } catch (err) {
    removeTyping();
    const msg = err.message.includes("Failed to fetch")
      ? "Cannot reach the backend. Check that the server is running and BACKEND_URL is correct."
      : err.message;
    showError(msg);
    appendMessage("bot", "Sorry, something went wrong. Please try again.");
  } finally {
    isLoading = false;
    sendBtn.disabled = false;
    userInput.focus();
  }
}

// ---------------------------------------------------------------------------
// Event listeners
// ---------------------------------------------------------------------------
sendBtn.addEventListener("click", sendMessage);

userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

clearBtn.addEventListener("click", () => {
  chatWindow.innerHTML = "";
  const welcome = document.createElement("div");
  welcome.className = "welcome-msg";
  welcome.innerHTML = "<p>👋 Ask me anything about energy efficiency, smart grids, renewables, or the UK energy dataset.</p>";
  chatWindow.appendChild(welcome);
  hideError();
  userInput.focus();
});
