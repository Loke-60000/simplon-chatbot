document.getElementById("openChat").onclick = function () {
  document.getElementById("chatModal").style.display = "flex";
};

document.getElementById("closeChat").onclick = function () {
  document.getElementById("chatModal").style.display = "none";
};

// Listen for enter key in chat input
document
  .getElementById("chatInput")
  .addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
      event.preventDefault(); // Prevent the form from submitting
      sendMessage();
    }
  });

function sendMessage() {
  var message = document.getElementById("chatInput").value;
  if (message.trim() === "") return; // Don't send empty messages

  // Add the user's message to the chat content
  appendMessage(message, "user-message");

  // Clear the input field
  document.getElementById("chatInput").value = "";

  // AJAX request to Flask API
  fetch("http://127.0.0.1:5000/chat", {
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
  messageDiv.classList.add("message", messageType); // Add classes for styling
  chatContent.appendChild(messageDiv);
  // Scroll to the latest message
  chatContent.scrollTop = chatContent.scrollHeight;
}
