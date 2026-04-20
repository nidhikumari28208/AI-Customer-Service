from flask import Flask, render_template, request
from groq import Groq
import json
import os
import re
from difflib import SequenceMatcher
app = Flask(__name__)
client = Groq(api_key="")
MEMORY_FILE = "memory.json"
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"chat_history": []}
    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {"chat_history": []}
            if "chat_history" not in data:
                data["chat_history"] = []
            return data
    except:
        return {"chat_history": []}
def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)
def is_similar(new_msg, chat_history):
    if not chat_history:
        return False
    last_user = None
    for msg in reversed(chat_history):
        if msg["role"] == "user":
            last_user = msg["content"]
            break
    if not last_user:
        return False
    similarity = SequenceMatcher(
        None, last_user.lower(), new_msg.lower()
    ).ratio()
    return similarity > 0.85
@app.route("/")
def landing():
    return render_template("landing5.html")
@app.route("/chatpage")
def home():
    memory = load_memory()
    return render_template("ui7.html", chat_history=memory["chat_history"])
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form.get("message")
    if not user_message:
        return render_template("ui7.html", chat_history=[])
    memory = load_memory()
    chat_history = memory.get("chat_history", [])
    if is_similar(user_message, chat_history):
        reply = "Haan 🙂 mujhe yaad hai tumne ye pehle bhi poocha tha. Main dobara help karta hoon..."
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": reply})
    else:
        chat_history.append({"role": "user", "content": user_message})
        try
            MAX_MESSAGES = 10
            messages = chat_history[-MAX_MESSAGES:]
            response = client.chat.completions.create(
                model="qwen/qwen3-32b",
                messages=messages
            )
            reply = response.choices[0].message.content
            reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL).strip()
        except Exception as e:
            reply = f"Error: {str(e)}"
        chat_history.append({"role": "assistant", "content": reply})
    memory["chat_history"] = chat_history
    save_memory(memory)
    return render_template("ui6.html", chat_history=chat_history)


if __name__ == "__main__":
    app.run(debug=True)
