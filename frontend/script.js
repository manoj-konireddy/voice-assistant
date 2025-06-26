async function startRecording() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mediaRecorder = new MediaRecorder(stream);
  const audioChunks = [];

  mediaRecorder.ondataavailable = event => {
    audioChunks.push(event.data);
  };

  mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    const formData = new FormData();
    formData.append('file', audioBlob, 'voice.webm');

    try {
      const res = await fetch('http://127.0.0.1:8000/voice-to-text/', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      const userMessage = data.transcription || data.error;
      document.getElementById('result').textContent = userMessage;
      appendMessage(userMessage, 'user');

      if (data.transcription) {
        appendMessage("⏳ Thinking...", 'assistant');

        const chatForm = new FormData();
        chatForm.append('user_input', data.transcription);

        const chatRes = await fetch('http://127.0.0.1:8000/chat-response/', {
          method: 'POST',
          body: chatForm
        });

        const chatData = await chatRes.json();
        const responseText = chatData.response || chatData.error || "No response";

        removeLastAssistantMessage();
        appendMessage(responseText, 'assistant');
      }

    } catch (error) {
      console.error("❌ Voice error:", error);
      appendMessage("⚠️ Failed to process voice input.", 'assistant');
    } finally {
      stream.getTracks().forEach(track => track.stop());
    }
  };

  mediaRecorder.start();
  setTimeout(() => mediaRecorder.stop(), 5000);
}

async function handleTextSubmit() {
  const inputEl = document.getElementById('textInput');
  const userInput = inputEl.value.trim();
  if (!userInput) return;

  appendMessage(userInput, 'user');
  inputEl.value = "";
  appendMessage("⏳ Thinking...", 'assistant');

  const formData = new FormData();
  formData.append('user_input', userInput);

  try {
    const res = await fetch('http://127.0.0.1:8000/chat-response/', {
      method: 'POST',
      body: formData
    });

    const data = await res.json();
    const response = data.response || data.error || "No response";

    removeLastAssistantMessage();
    appendMessage(response, 'assistant');
  } catch (error) {
    console.error("❌ Text error:", error);
    removeLastAssistantMessage();
    appendMessage("⚠️ Failed to fetch response.", 'assistant');
  }
}

function appendMessage(text, role) {
  const chatContainer = document.getElementById('chatHistory');
  const messageWrapper = document.createElement('div');
  messageWrapper.className = `message ${role}`;

  const formatted = formatResponse(text);
  messageWrapper.innerHTML = `<div class="bubble">${formatted}</div>`;
  chatContainer.appendChild(messageWrapper);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeLastAssistantMessage() {
  const chatContainer = document.getElementById('chatHistory');
  const messages = chatContainer.querySelectorAll('.message.assistant');
  if (messages.length > 0) {
    messages[messages.length - 1].remove();
  }
}

function formatResponse(text) {
  const escapedText = text
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  if (escapedText.includes("```")) {
    const parts = escapedText.split(/```/);
    return parts.map((part, i) =>
      i % 2 === 1 ? `<pre><code>${part.trim()}</code></pre>` : wrapTextLines(part)
    ).join('');
  }

  return wrapTextLines(escapedText);
}

function wrapTextLines(text) {
  return text.split('\n').map(line => {
    const trimmed = line.trim();
    if (/^\d+\./.test(trimmed)) return `<ol><li>${trimmed.slice(2)}</li></ol>`;
    if (/^[-*] /.test(trimmed)) return `<ul><li>${trimmed.slice(2)}</li></ul>`;
    if (trimmed) return `<p>${trimmed}</p>`;
    return '';
  }).join('');
}

document.getElementById('textForm').addEventListener('submit', e => {
  e.preventDefault();
  handleTextSubmit();
});

// -------- Theme Handling --------
function applySavedOrSystemTheme() {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    document.body.classList.toggle('dark', savedTheme === 'dark');
  } else {
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.body.classList.toggle('dark', systemPrefersDark);
  }
}

// Apply on load
applySavedOrSystemTheme();

// Watch system preference change if user hasn’t overridden manually
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
  if (!localStorage.getItem('theme')) {
    document.body.classList.toggle('dark', e.matches);
  }
});

// Toggle manually and store preference
document.getElementById('darkToggle').addEventListener('click', () => {
  const isDark = document.body.classList.toggle('dark');
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
});

// -------- Share --------
function toggleSharePopup() {
  const popup = document.getElementById("sharePopup");
  popup.classList.toggle("show");
}

function copyLink() {
  navigator.clipboard.writeText("https://127.0.0.1:5500");
  alert("✅ Link copied to clipboard!");
}

document.addEventListener("click", (e) => {
  const btn = document.querySelector(".share-toggle");
  const popup = document.getElementById("sharePopup");
  if (!btn.contains(e.target) && !popup.contains(e.target)) {
    popup.classList.remove("show");
  }
});
