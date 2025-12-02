let selectedVoice = null;
let speechRate = 1;
let recognition = null;

// Load voices into dropdown
function loadVoices() {
    const synth = window.speechSynthesis;//buitl-in text-speech
    const voices = synth.getVoices(); // Get list of available voices
    const voiceSelect = document.getElementById("voiceSelect");

    voiceSelect.innerHTML = "";
    voices.forEach(voice => {
        let option = document.createElement("option");
        option.value = voice.name;
        option.textContent = voice.name;
        voiceSelect.appendChild(option);// Add each voice as an option
    });

    selectedVoice = voiceSelect.value;

    voiceSelect.onchange = () => {
        selectedVoice = voiceSelect.value;//update the voice
    };
}

window.speechSynthesis.onvoiceschanged = loadVoices;

// Update speech rate from slider
document.getElementById("speedRange").addEventListener("input", e => {
    speechRate = parseFloat(e.target.value);//slider for speech rate
    document.getElementById("speedValue").textContent = speechRate.toFixed(1);// Update display next to slider
});
// });


// SPEAK FUNCTION

function speak(text) {
    const synth = window.speechSynthesis;
    synth.cancel();//stop existing one speech

    const utterance = new SpeechSynthesisUtterance(text);//speech object

    const voices = synth.getVoices();
    const voice = voices.find(v => v.name === selectedVoice);

    if (voice) utterance.voice = voice;//set voice

    utterance.rate = speechRate;//set rate
    synth.speak(utterance);
}

// LISTEN FUNCTION

function startListening() {
    if (!('SpeechRecognition' in window) && !('webkitSpeechRecognition' in window)) {
        alert("Sorry, your browser doesn't support Speech Recognition.");
        return;
    }

    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = "en-IN";
    recognition.continuous = false;

    // Add mic button animation class
    const micBtn = document.getElementById("mic-btn");
    micBtn.classList.add("listening");

    recognition.start();

    recognition.onresult = event => {
        const userSpeech = event.results[0][0].transcript;//GET TEXT
        displayMessage(userSpeech, "user");//display in window              
        sendToBackend(userSpeech);
    };

    recognition.onerror = event => {
        console.error("Speech recognition error", event.error);
        micBtn.classList.remove("listening");//rwmove animation
    };

    recognition.onend = () => {
        micBtn.classList.remove("listening");
    };
}

// SEND TEXT

function sendText() {
    const input = document.getElementById("text-input");
    const userText = input.value.trim();
    if (userText === "") return;

    displayMessage(userText, "user");//add to chat window
    sendToBackend(userText);//send backend
    input.value = "";//reset
}

document.getElementById("text-input")
    .addEventListener("keypress", e => {
        if (e.key === "Enter") sendText();
    });

// BACKEND COMMUNICATION

function sendToBackend(message) {
    showTypingIndicator(true);
    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    })
    .then(res => res.json())
    .then(data => {
        showTypingIndicator(false);
        displayMessage(data.reply, "ai");
        speak(data.reply);

        if (data.url) window.open(data.url, "_blank");//open url automatically
    })
    .catch(err => {
        showTypingIndicator(false);
        console.error(err);
    });
}

//DISPLAY MESSAGE

function displayMessage(message, sender) {
    const chatWindow = document.getElementById("chat-window");
    const msgDiv = document.createElement("div");

    msgDiv.classList.add("message", sender);

    // Add timestamp
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute:'2-digit' });
    msgDiv.textContent = message + " ";
    const timeSpan = document.createElement("span");//to show timw
    timeSpan.style.fontSize = "10px";
    timeSpan.style.color = sender === "user" ? "#bbb" : "#555";
    timeSpan.textContent = timestamp;

    msgDiv.appendChild(timeSpan);
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

//TYPING INDICATOR

function showTypingIndicator(show) {
    const indicator = document.getElementById("typing-indicator");
    indicator.style.display = show ? "block" : "none";
}

//DOWNLOAD CHAT

function downloadChat() {
    const chatWindow = document.getElementById("chat-window");
    const messages = chatWindow.querySelectorAll(".message");
    let chatContent = "";
    messages.forEach(msg => {
        chatContent += msg.textContent + "\n";
    });

    const blob = new Blob([chatContent], { type: "text/plain" });
    const link = document.createElement("a");

    link.href = URL.createObjectURL(blob);
    link.download = "VoiceMate_Chat.txt";
    link.click();
}

//CLEAR CHAT

function clearChat() {
    if (confirm("Are you sure you want to clear the chat?")) {
        const chatWindow = document.getElementById("chat-window");
        chatWindow.innerHTML = "";
    }
}
