let messageHistory = [];
let recognition;

function sendMessage() {
  var input = document.getElementById("inputMessage");
  var message = input.value.trim();
  if (message === "") return;
  displayMessage(message, "user");
  input.value = "";
  messageHistory.push({ sender: "user", message: message });
  displayLoading(true);
  fetch("http://lokapi-backend.eastus.azurecontainer.io:8000/generate-text", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      history: messageHistory,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      displayLoading(false);
      if (data.error) {
        displayMessage(data.error, "error");
        messageHistory.push({ sender: "error", message: data.error });
      } else {
        displayMessage(data.response, "system");
        messageHistory.push({ sender: "system", message: data.response });
      }
    })
    .catch((error) => {
      displayLoading(false);
      displayMessage("Failed to communicate with the API.", "error");
      messageHistory.push({
        sender: "error",
        message: "Failed to communicate with the API.",
      });
    });
}

function displayMessage(text, sender) {
  var div = document.createElement("div");
  div.classList.add("message", sender);
  div.textContent = text;
  document.querySelector(".messages").appendChild(div);
  div.scrollIntoView({ behavior: "smooth" });
}

function displayLoading(show) {
  var messagesDiv = document.querySelector(".messages");
  var loading = messagesDiv.querySelector(".loading-dots");
  if (show) {
    if (!loading) {
      loading = document.createElement("div");
      loading.classList.add("loading-dots");
      loading.innerHTML = '<div class="dot"></div><div class="dot"></div>';
      messagesDiv.appendChild(loading);
    }
    loading.style.display = "flex";
  } else if (loading) {
    loading.style.display = "none";
  }
}

document
  .getElementById("inputMessage")
  .addEventListener("keyup", function (event) {
    if (event.key === "Enter") {
      sendMessage();
    }
  });

function startListening() {
  if (!("webkitSpeechRecognition" in window)) {
    displayMessage("Speech recognition not available.", "error");
  } else {
    recognition = new webkitSpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onresult = function (event) {
      const speechResult = event.results[0][0].transcript;
      document.getElementById("inputMessage").value = speechResult;
      sendMessage();
    };
    recognition.onerror = function (event) {
      displayMessage("Speech recognition error: " + event.error, "error");
    };
    recognition.start();
  }
}
