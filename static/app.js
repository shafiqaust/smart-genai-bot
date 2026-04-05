document.addEventListener("DOMContentLoaded", function () {
    var chatMessages = document.getElementById("chat-messages");
    var chatForm = document.getElementById("chat-form");
    var messageInput = document.getElementById("message-input");
    var typingIndicator = document.getElementById("typing-indicator");
    var sendButton = document.getElementById("send-button");

    chatForm.addEventListener("submit", function (e) {
        e.preventDefault();
        var text = messageInput.value.trim();
        if (!text) return;

        appendMessage(text, "user");
        messageInput.value = "";
        sendButton.disabled = true;
        typingIndicator.classList.add("visible");
        scrollToBottom();

        fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text }),
        })
            .then(function (res) {
                if (!res.ok) throw new Error("Server error");
                return res.json();
            })
            .then(function (data) {
                appendMessage(data.response, "bot");
            })
            .catch(function () {
                appendMessage("Sorry, something went wrong. Please try again.", "bot");
            })
            .finally(function () {
                typingIndicator.classList.remove("visible");
                sendButton.disabled = false;
                messageInput.focus();
            });
    });

    function appendMessage(text, sender) {
        var messageDiv = document.createElement("div");
        messageDiv.className = "message " + sender;

        var contentDiv = document.createElement("div");
        contentDiv.className = "message-content";

        if (sender === "bot") {
            contentDiv.innerHTML = formatBotResponse(text);
        } else {
            contentDiv.textContent = text;
        }

        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    function formatBotResponse(rawText) {
        var parts = rawText.split(/\n\s*Sources?:\s*\n/i);
        var answerText = parts[0];
        var sourcesText = parts.length > 1 ? parts[1] : null;

        // Also handle "Sources:" at end without trailing newline before it
        if (!sourcesText) {
            var altParts = rawText.split(/\n\s*Sources?:\s*$/im);
            if (altParts.length > 1) {
                answerText = altParts[0];
                sourcesText = altParts[1] || "";
            }
        }

        var answerHtml = escapeHtml(answerText);
        answerHtml = answerHtml.replace(/\[(\d+)\]/g, '<span class="citation">[$1]</span>');
        answerHtml = answerHtml.replace(/\n/g, "<br>");

        var sourcesHtml = "";
        if (sourcesText && sourcesText.trim()) {
            var lines = sourcesText.trim().split("\n").filter(Boolean);
            var items = lines.map(function (line) {
                var escaped = escapeHtml(line.trim());
                return escaped.replace(
                    /^\[(\d+)\]\s*(.+)$/,
                    '<div class="source-item"><span class="citation">[$1]</span> <strong>$2</strong></div>'
                );
            });
            sourcesHtml =
                '<div class="sources-block">' +
                '<div class="sources-header">Sources</div>' +
                items.join("") +
                "</div>";
        }

        return answerHtml + sourcesHtml;
    }

    function escapeHtml(str) {
        var div = document.createElement("div");
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
