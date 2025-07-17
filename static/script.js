function startListening() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-IN';
    recognition.start();

    recognition.onresult = function(event) {
        const userSpeech = event.results[0][0].transcript;
        displayMessage(userSpeech, "user");
        sendToBackend(userSpeech);
    };

    recognition.onerror = function(event) {
        console.error("Speech recognition error:", event.error);
    };
}

function sendText() {
    const input = document.getElementById("text-input");
    const userText = input.value.trim();
    if (userText !== "") {
        displayMessage(userText, "user");
        sendToBackend(userText);
        input.value = "";
    }
}

function sendToBackend(message) {
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        displayMessage(data.reply, "ai");
        speak(data.reply);

        if (data.url) {
            window.open(data.url, "_blank");
        }
    });
}

function displayMessage(message, sender) {
    const chatWindow = document.getElementById("chat-window");
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message", sender);
    msgDiv.textContent = message;
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTo({
        top: chatWindow.scrollHeight,
        behavior: 'smooth'
    });
}

function speak(text) {
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1;
    synth.speak(utterance);
}
