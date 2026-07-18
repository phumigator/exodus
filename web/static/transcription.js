const form = document.getElementById("upload-form");
const transcribeBtn = document.getElementById("transcribe-btn");
const summarizeBtn = document.getElementById("summarize-btn");
const statusEl = document.getElementById("status");
const transcriptSection = document.getElementById("transcript-section");
const transcriptEl = document.getElementById("transcript");
const summarySection = document.getElementById("summary-section");
const summaryEl = document.getElementById("summary");
const modelSelect = document.getElementById("model-select");

function showStatus(message, isError = false) {
    statusEl.textContent = message;
    statusEl.hidden = !message;
    statusEl.classList.toggle("status-error", isError);
}

async function parseError(response) {
    try {
        const data = await response.json();
        return data.detail || response.statusText;
    } catch {
        return response.statusText;
    }
}

function downloadText(filename, text) {
    const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const fileInput = document.getElementById("file-input");
    const file = fileInput.files[0];
    if (!file) return;

    transcribeBtn.disabled = true;
    summarySection.hidden = true;
    transcriptSection.hidden = true;
    showStatus(I18N.js_status_recognizing);

    const correctionPrompt = document.getElementById("correction-prompt-input").value.trim();
    const model = modelSelect.value.trim();

    const formData = new FormData();
    formData.append("file", file);
    if (correctionPrompt) {
        formData.append("correction_prompt", correctionPrompt);
    }
    if (model) {
        formData.append("correction_model", model);
    }

    try {
        const response = await fetch(`${API_BASE_URL}/transcription/transcribe`, {
            method: "POST",
            body: formData,
        });
        if (!response.ok) {
            throw new Error(await parseError(response));
        }
        const data = await response.json();
        transcriptEl.value = data.text || JSON.stringify(data);
        transcriptSection.hidden = false;
        showStatus(I18N.js_status_done);
    } catch (err) {
        showStatus(`${I18N.js_error_recognition_prefix}${err.message}`, true);
    } finally {
        transcribeBtn.disabled = false;
    }
});

const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatHistoryEl = document.getElementById("chat-history");
const chatSendBtn = document.getElementById("chat-send-btn");
const chatClearBtn = document.getElementById("chat-clear-btn");
const chatStatusEl = document.getElementById("chat-status");

let chatHistory = [];

function showChatStatus(message, isError = false) {
    chatStatusEl.textContent = message;
    chatStatusEl.hidden = !message;
    chatStatusEl.classList.toggle("status-error", isError);
}

function renderChatHistory() {
    chatHistoryEl.innerHTML = "";
    for (const message of chatHistory) {
        const bubble = document.createElement("div");
        bubble.className = `chat-message chat-message-${message.role}`;
        bubble.textContent = message.content;
        chatHistoryEl.appendChild(bubble);
    }
    chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;
}

chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const text = chatInput.value.trim();
    if (!text) return;

    chatHistory.push({ role: "user", content: text });
    renderChatHistory();
    chatInput.value = "";

    chatSendBtn.disabled = true;
    showChatStatus(I18N.js_chat_thinking);

    try {
        const response = await fetch(`${API_BASE_URL}/transcription/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                messages: chatHistory,
                model: modelSelect.value.trim() || null,
            }),
        });
        if (!response.ok) {
            throw new Error(await parseError(response));
        }
        const data = await response.json();
        chatHistory.push({ role: "assistant", content: data.content });
        renderChatHistory();
        showChatStatus("");
    } catch (err) {
        showChatStatus(`${I18N.js_error_chat_prefix}${err.message}`, true);
    } finally {
        chatSendBtn.disabled = false;
    }
});

chatClearBtn.addEventListener("click", () => {
    chatHistory = [];
    renderChatHistory();
    showChatStatus("");
});

summarizeBtn.addEventListener("click", async () => {
    const text = transcriptEl.value.trim();
    if (!text) return;

    summarizeBtn.disabled = true;
    showStatus(I18N.js_status_summarizing);

    const summaryPrompt = document.getElementById("summary-prompt-input").value.trim();

    try {
        const response = await fetch(`${API_BASE_URL}/transcription/summarize`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                text,
                prompt: summaryPrompt || null,
                model: modelSelect.value.trim() || null,
            }),
        });
        if (!response.ok) {
            throw new Error(await parseError(response));
        }
        const data = await response.json();
        summaryEl.textContent = data.summary;
        summarySection.hidden = false;
        showStatus(I18N.js_status_done);
    } catch (err) {
        showStatus(`${I18N.js_error_summarization_prefix}${err.message}`, true);
    } finally {
        summarizeBtn.disabled = false;
    }
});

document.getElementById("download-transcript-btn").addEventListener("click", () => {
    downloadText("transcript.txt", transcriptEl.value);
});

document.getElementById("download-summary-btn").addEventListener("click", () => {
    downloadText("summary.txt", summaryEl.textContent);
});
