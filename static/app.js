document.addEventListener("DOMContentLoaded", function () {
  var chatContainer = document.getElementById("chatContainer");
  var messageInput = document.getElementById("messageInput");
  var sendBtn = document.getElementById("sendBtn");
  var clearBtn = document.getElementById("clearBtn");
  var welcome = document.getElementById("welcome");

  var isLoading = false;

  // Auto-resize textarea
  messageInput.addEventListener("input", function () {
    messageInput.style.height = "auto";
    messageInput.style.height = Math.min(messageInput.scrollHeight, 150) + "px";
  });

  // Enter to send, Shift+Enter for newline
  messageInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  sendBtn.addEventListener("click", sendMessage);

  clearBtn.addEventListener("click", function () {
    chatContainer.innerHTML = "";
    chatContainer.appendChild(welcome);
    welcome.style.display = "block";
  });

  // Expose globally for inline onclick on suggestion buttons
  window.useSuggestion = function (btn) {
    messageInput.value = btn.textContent;
    sendMessage();
  };

  function sendMessage() {
    var text = messageInput.value.trim();
    if (!text || isLoading) return;

    // Hide welcome
    welcome.style.display = "none";

    // Add user message
    appendMessage("user", text);
    messageInput.value = "";
    messageInput.style.height = "auto";

    // Show typing indicator
    var typingEl = showTyping();
    isLoading = true;
    sendBtn.disabled = true;

    fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    })
      .then(function (res) {
        if (!res.ok) throw new Error("Server responded with " + res.status + ": " + res.statusText);
        return res.json();
      })
      .then(function (data) {
        removeTyping(typingEl);
        var formatted = formatResponse(data.response);
        appendBotMessage(formatted);
      })
      .catch(function (err) {
        removeTyping(typingEl);
        appendError(err.message);
      })
      .finally(function () {
        isLoading = false;
        sendBtn.disabled = false;
        messageInput.focus();
      });
  }

  function appendMessage(role, text) {
    var msg = document.createElement("div");
    msg.className = "message " + role;

    var avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = role === "user" ? "You" : "AI";

    var content = document.createElement("div");
    content.className = "message-content";

    var bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.textContent = text;

    content.appendChild(bubble);
    msg.appendChild(avatar);
    msg.appendChild(content);
    chatContainer.appendChild(msg);
    scrollToBottom();
  }

  function appendBotMessage(formatted) {
    var msg = document.createElement("div");
    msg.className = "message bot";

    var avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = "AI";

    var content = document.createElement("div");
    content.className = "message-content";

    var bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.innerHTML = formatted.answer;

    content.appendChild(bubble);

    if (formatted.sources.length > 0) {
      var sourcesDiv = document.createElement("div");
      sourcesDiv.className = "sources-block";
      sourcesDiv.innerHTML =
        '<div class="sources-block-title">Sources</div>' +
        formatted.sources
          .map(function (s) {
            return '<div class="source-item">' + escapeHtml(s) + "</div>";
          })
          .join("");
      content.appendChild(sourcesDiv);
    }

    msg.appendChild(avatar);
    msg.appendChild(content);
    chatContainer.appendChild(msg);
    scrollToBottom();
  }

  function appendError(errMsg) {
    var msg = document.createElement("div");
    msg.className = "message bot";

    var avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = "AI";

    var content = document.createElement("div");
    content.className = "message-content";

    var bubble = document.createElement("div");
    bubble.className = "error-bubble";
    bubble.innerHTML =
      "<strong>Error:</strong> " +
      escapeHtml(errMsg) +
      '<br><span style="font-size:12px;color:#6b7280;margin-top:4px;display:inline-block;">Make sure the backend server is running.</span>';

    content.appendChild(bubble);
    msg.appendChild(avatar);
    msg.appendChild(content);
    chatContainer.appendChild(msg);
    scrollToBottom();
  }

  function showTyping() {
    var msg = document.createElement("div");
    msg.className = "message bot";
    msg.id = "typing";

    var avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = "AI";

    var content = document.createElement("div");
    content.className = "message-content";

    var bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.innerHTML =
      '<div class="typing-indicator">' +
      '<div class="typing-dot"></div>' +
      '<div class="typing-dot"></div>' +
      '<div class="typing-dot"></div>' +
      "</div>";

    content.appendChild(bubble);
    msg.appendChild(avatar);
    msg.appendChild(content);
    chatContainer.appendChild(msg);
    scrollToBottom();
    return msg;
  }

  function removeTyping(el) {
    if (el && el.parentNode) el.parentNode.removeChild(el);
  }

  /**
   * Parse the response string into answer HTML + sources array.
   * The backend returns text like:
   *   "Answer text [1] more text [2]...\n\nSources:\n[1] file.pdf\n[2] other.txt"
   */
  function formatResponse(raw) {
    var answer = raw;
    var sources = [];

    // Split on "Sources:" section
    var sourceSplit = raw.split(/\n\s*Sources?:\s*\n/i);
    if (sourceSplit.length > 1) {
      answer = sourceSplit[0].trim();
      var sourceLines = sourceSplit[1].trim().split("\n");
      for (var i = 0; i < sourceLines.length; i++) {
        var cleaned = sourceLines[i].replace(/^\[\d+\]\s*/, "").trim();
        if (cleaned) sources.push(cleaned);
      }
    } else {
      // Handle "Sources:" at end without trailing newline
      var altSplit = raw.split(/\n\s*Sources?:\s*$/im);
      if (altSplit.length > 1) {
        answer = altSplit[0].trim();
      }
    }

    // Escape HTML first, then style citation markers
    answer = escapeHtml(answer);
    answer = answer.replace(
      /\[(\d+)\]/g,
      '<span class="citation-marker">$1</span>'
    );

    // Convert newlines to <br>
    answer = answer.replace(/\n/g, "<br>");

    return { answer: answer, sources: sources };
  }

  function escapeHtml(str) {
    var div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  function scrollToBottom() {
    requestAnimationFrame(function () {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    });
  }
});
