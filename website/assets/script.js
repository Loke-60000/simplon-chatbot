document.getElementById("openChat").onclick = function () {
  document.getElementById("chatModal").style.display = "flex";
};

document.getElementById("closeChat").onclick = function () {
  document.getElementById("chatModal").style.display = "none";
};

document
  .getElementById("chatInput")
  .addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
      event.preventDefault();
      sendMessage();
    }
  });

function sendMessage() {
  var message = document.getElementById("chatInput").value;
  if (message.trim() === "") return;

  appendMessage(message, "user-message");

  document.getElementById("chatInput").value = "";

  fetch("http://127.0.0.1:8000/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message: message }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(
          "Network response was not ok. Status: " + response.status
        );
      }
      return response.json();
    })
    .then((data) => {
      appendMessage(data.response, "ai-message");
    })
    .catch((error) => {
      console.error("Error:", error);
      appendMessage(
        "Sorry, there was an error processing your message.",
        "ai-message"
      );
    });
}

function appendMessage(message, messageType) {
  var chatContent = document.getElementById("chatContent");
  var messageDiv = document.createElement("div");
  messageDiv.textContent =
    messageType === "user-message" ? "You: " + message : "LokB0t: " + message;
  messageDiv.classList.add("message", messageType);
  chatContent.appendChild(messageDiv);
  chatContent.scrollTop = chatContent.scrollHeight;
}
