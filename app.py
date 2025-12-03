from flask import Flask, render_template, request, jsonify
import datetime
import wikipedia
import requests
import os

app = Flask(__name__)


memory = []
ai_mode = "normal"   # normal / funny / formal / motivational


# modes

def apply_personality(text):
    global ai_mode

    if ai_mode == "funny":
        return text + " 😂"

    elif ai_mode == "formal":
        return "Certainly. " + text

    elif ai_mode == "motivational":
        return text + " 💪 Stay positive!"

    return text  # normal mode


def greet_user():
    utc_now = datetime.utcnow()
    ist_now = utc_now + timedelta(hours=5, minutes=30)
    hour = ist_now.hour

    # if 5 <= hour < 12:
    #     return "Good Morning"
    # elif 12 <= hour < 17:
    #     return "Good Afternoon"
    # elif 17 <= hour < 21:
    #     return "Good Evening"
    # else:
    #     return "Good Night"

    # # hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        greeting = "Good morning!"
    elif 12 <= hour < 18:
        greeting = "Good afternoon!"
    else:
        greeting = "Good evening!"
    return {"reply": apply_personality(f"{greeting} I am your AI assistant. How can I help you today?")}



def get_indian_time():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    return now.strftime("%H:%M")

def greet_user():

    hour = datetime.now(ZoneInfo("Asia/Kolkata")).hour
    # hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        greeting = "Good morning!"
    elif 12 <= hour < 18:
        greeting = "Good afternoon!"
    else:
        greeting = "Good evening!"
    return {"reply": apply_personality(f"{greeting} I am your AI assistant. How can I help you today?")}






def tell_joke():
    res = requests.get("https://v2.jokeapi.dev/joke/Any").json()
    if res["type"] == "single":
        return {"reply": apply_personality(res["joke"])}
    return {"reply": apply_personality(f"{res['setup']} ... {res['delivery']}")}


#memory function

def remember(text):
    memory.append(text)
    return {"reply": apply_personality(f"I'll remember that: '{text}'")}


def recall():
    if not memory:
        return {"reply": apply_personality("I don't remember anything yet.")}
    return {"reply": apply_personality("You told me to remember:\n" + "\n".join(memory))}


# weather api

def get_weather(city):
    try:
        api = f"https://wttr.in/{city}?format=%C+%t"
        data = requests.get(api).text
        return {"reply": apply_personality(f"Weather in {city}: {data}")}
    except:
        return {"reply": apply_personality("Unable to fetch weather info.")}




def process_command(command):
    global ai_mode
    original = command
    command = command.lower()

    # Personality mode switching
    if "funny mode" in command:
        ai_mode = "funny"
        return {"reply": "😂 Funny mode activated!"}

    if "formal mode" in command:
        ai_mode = "formal"
        return {"reply": "Formal mode activated."}

    if "motivational mode" in command:
        ai_mode = "motivational"
        return {"reply": "💪 Motivational mode activated!"}

    if "normal mode" in command:
        ai_mode = "normal"
        return {"reply": "Back to normal mode."}

    # Greetings
    if "hello" in command or "hi" in command:
        return greet_user()

    # Math
    calc = original.replace("plus", "+").replace("minus", "-").replace("times", "*").replace("x", "*")
    try:
        if any(ch.isdigit() for ch in calc) and any(op in calc for op in "+-*/"):
            result = eval(calc)
            return {"reply": apply_personality(f"The answer is {result}.")}
    except:
        pass



    # Joke
    if "joke" in command:
        return tell_joke()

    # Music
    if "play" in command:
        song = command.replace("play", "").strip()
        url = f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}"
        return {"reply": apply_personality(f"Playing {song} on YouTube"), "url": url}

    # Memory
    if "remember" in command:
        return remember(command.replace("remember", "").strip())

    if "what did i tell you" in command or "recall" in command:
        return recall()

    # Weather
    if "weather in" in command:
        city = command.replace("weather in", "").strip()
        return get_weather(city)

    # Time
    if "time" in command:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        return {"reply": apply_personality(f"The current time is {now}.")}


    #units
    if "km to miles" in command:
        try:
            km = float(command.replace("km to miles", "").strip())
            miles = round(km * 0.621371, 2)
            return {"reply": f"{km} kilometers is {miles} miles."}
        except:
            return {"reply": "Please specify the distance in kilometers."}

    if "miles to km" in command:
        try:
            miles = float(command.replace("miles to km", "").strip())
            km = round(miles / 0.621371, 2)
            return {"reply": f"{miles} miles is {km} kilometers."}
        except:
            return {"reply": "Please specify the distance in miles."}
        
    # Open sites
    if "open youtube" in command:
        return {"reply": "Opening YouTube.", "url": "https://www.youtube.com"}
    if "open google" in command:
        return {"reply": "Opening Google.", "url": "https://www.google.com"}

    # Search
    if "search" in command:
        query = command.replace("search", "").strip()
        return {"reply": f"Searching for {query}", "url": f"https://www.google.com/search?q={query}"}

    # Time
    if "time" in command:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        return {"reply": f"The current time is {now}."}



    # Wikipedia
    if "wikipedia" in command:
        topic = command.replace("wikipedia", "").strip()
        try:
            summary = wikipedia.summary(topic, sentences=2)
            return {"reply": apply_personality(summary)}
        except:
            return {"reply": apply_personality("Couldn't find that on Wikipedia.")}

    return {"reply": apply_personality("Sorry, I didn’t understand that.")}


# ---------------- ROUTES ----------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")
    response = process_command(user_input)
    return jsonify(response)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
