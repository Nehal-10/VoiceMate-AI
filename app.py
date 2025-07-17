from flask import Flask, render_template, request, jsonify
import datetime
import wikipedia

app = Flask(__name__)

# Function to process user commands
def process_command(command):
    command = command.lower()

    # Replace math words with symbols
    command = command.replace("plus", "+").replace("minus", "-")
    command = command.replace("times", "*").replace("multiplied by", "*")
    command = command.replace("divided by", "/").replace("over", "/")

    # ✅ Math calculation
    try:
        if any(char.isdigit() for char in command) and any(op in command for op in "+-*/"):
            result = eval(command)
            return {"reply": f"The answer is {result}"}
    except:
        return {"reply": "Sorry, I couldn't calculate that."}

    # ✅ Unit conversion (simple example)
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

    # ✅ Open websites
    if "open youtube" in command:
        return {"reply": "Opening YouTube.", "url": "https://www.youtube.com"}

    if "open google" in command:
        return {"reply": "Opening Google.", "url": "https://www.google.com"}

    # ✅ Google search
    if "search" in command:
        search_query = command.replace("search", "").strip()
        search_url = f"https://www.google.com/search?q={search_query}"
        return {"reply": f"Searching for {search_query}", "url": search_url}

    # ✅ Tell time
    if "what is the time" in command:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        return {"reply": f"The time is {now}"}

    # ✅ Wikipedia summary
    if "wikipedia" in command:
        topic = command.replace("wikipedia", "").strip()
        try:
            summary = wikipedia.summary(topic, sentences=2)
            return {"reply": summary}
        except:
            return {"reply": "Sorry, I couldn't find anything on Wikipedia."}

    return {"reply": "Sorry, I didn't understand that."}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message")
    response = process_command(user_input)
    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
