import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "change-this-secret-before-deployment"
)

database_url = os.getenv("DATABASE_URL", "sqlite:///chatbot.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(80), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False, default="New conversation")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(
        db.Integer, db.ForeignKey("chat.id"), nullable=False, index=True
    )
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    chat = db.relationship(
        "Chat",
        backref=db.backref(
            "messages", lazy=True, cascade="all, delete-orphan"
        ),
    )


with app.app_context():
    db.create_all()


def get_session_id():
    if "chat_session_id" not in session:
        import secrets
        session["chat_session_id"] = secrets.token_urlsafe(24)
    return session["chat_session_id"]


@app.get("/")
def index():
    get_session_id()
    return render_template("index.html")


@app.get("/api/chats")
def list_chats():
    sid = get_session_id()
    chats = Chat.query.filter_by(session_id=sid).order_by(
        Chat.created_at.desc()
    ).all()
    return jsonify([{"id": c.id, "title": c.title} for c in chats])


@app.post("/api/chats")
def new_chat():
    sid = get_session_id()
    chat = Chat(session_id=sid, title="New conversation")
    db.session.add(chat)
    db.session.commit()
    return jsonify({"id": chat.id, "title": chat.title})


@app.get("/api/chats/<int:chat_id>/messages")
def get_messages(chat_id):
    chat = Chat.query.filter_by(
        id=chat_id, session_id=get_session_id()
    ).first_or_404()
    return jsonify([
        {"role": m.role, "content": m.content} for m in chat.messages
    ])


@app.delete("/api/chats/<int:chat_id>")
def delete_chat(chat_id):
    chat = Chat.query.filter_by(
        id=chat_id, session_id=get_session_id()
    ).first_or_404()
    db.session.delete(chat)
    db.session.commit()
    return jsonify({"success": True})


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    chat_id = data.get("chat_id")

    if not message:
        return jsonify({"error": "Please type a message first."}), 400

    if len(message) > 12000:
        return jsonify({
            "error": "Message is too long. Please keep it under 12,000 characters."
        }), 400

    sid = get_session_id()

    if chat_id:
        chat_record = Chat.query.filter_by(
            id=chat_id, session_id=sid
        ).first()

        if not chat_record:
            return jsonify({
                "error": "Conversation not found. Start a new chat."
            }), 404
    else:
        chat_record = Chat(
            session_id=sid,
            title=message[:48] + ("…" if len(message) > 48 else "")
        )
        db.session.add(chat_record)
        db.session.commit()

    previous = Message.query.filter_by(
        chat_id=chat_record.id
    ).order_by(Message.created_at.asc()).all()

    history = [
        {"role": m.role, "content": m.content}
        for m in previous[-20:]
    ]
    history.append({"role": "user", "content": message})

    system_prompt = (
        "You are Nova, a helpful, knowledgeable, friendly AI assistant. "
        "Answer questions across a wide range of subjects. Explain clearly, "
        "adapt to the user's level, and be honest when uncertain. "
        "Do not claim to know literally everything or invent facts. "
        "For current events or information beyond your knowledge, explain "
        "when live browsing or external sources would be needed. "
        "Give practical, safe guidance and use examples when useful."
    )

    ollama_messages = [
        {"role": "system", "content": system_prompt}
    ] + history

    if not GEMINI_API_KEY:
        return jsonify({"error": "Gemini API key is not configured."}), 503

    gemini_contents = [
        {
            "role": "model" if item["role"] == "assistant" else "user",
            "parts": [{"text": item["content"]}]
        }
        for item in history
    ]

    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
            headers={"x-goog-api-key": GEMINI_API_KEY},
            json={
                "systemInstruction": {
                    "parts": [{"text": system_prompt}]
                },
                "contents": gemini_contents,
                "generationConfig": {"temperature": 0.7}
            },
            timeout=120
        )
        response.raise_for_status()

        result = response.json()
        answer = "".join(
            part.get("text", "")
            for part in result.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [])
        ).strip()

        if not answer:
            raise ValueError("Gemini returned an empty response.")

    except requests.exceptions.HTTPError:
        app.logger.exception("Gemini API request failed: %s", response.text[:1000])
        return jsonify({
            "error": "Gemini API rejected the request. Check your API key, model access, and quota."
        }), 502

    except requests.exceptions.RequestException:
        app.logger.exception("Cannot connect to Gemini API")
        return jsonify({
            "error": "Cannot connect to Gemini. Please try again."
        }), 503

    except Exception:
        app.logger.exception("Gemini response processing failed")
        return jsonify({
            "error": "Gemini could not complete the request."
        }), 502

    db.session.add(Message(
        chat_id=chat_record.id,
        role="user",
        content=message
    ))
    db.session.add(Message(
        chat_id=chat_record.id,
        role="assistant",
        content=answer
    ))
    db.session.commit()

    return jsonify({
        "chat_id": chat_record.id,
        "title": chat_record.title,
        "reply": answer
    })


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "ai_provider": "ollama",
        "model": OLLAMA_MODEL
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG") == "1"
    )
