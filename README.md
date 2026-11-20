# Nova AI — AI Chatbot Web Application

A responsive AI chatbot built with **Python, Flask, SQLite/ PostgreSQL, HTML, CSS and JavaScript**, powered by the OpenAI API. The project includes a modern chat interface, conversation history, typing animation, responsive layout and dark mode.

## Important: how the AI works

The application uses an AI model through the OpenAI API. It can answer a broad range of questions, explain concepts, help with coding, writing, learning and problem-solving. No application can truthfully guarantee that it knows literally everything or is always correct. Live/current facts may require external browsing, which is not included in this starter version.

**An OpenAI API key is required for real AI responses.** The key is private and must only be stored in environment variables, never in frontend JavaScript or committed to GitHub. API usage may incur charges depending on your account and model.

## Features

- Modern landing/welcome screen and chat interface
- AI-generated replies through the OpenAI Responses API
- Conversation history saved in a database
- Multiple conversations and delete-chat controls
- Typing/loading animation
- Responsive mobile layout
- Dark mode toggle
- Basic input validation and friendly API error messages
- SQLite for local development; PostgreSQL supported for hosting
- Health endpoint at `/health`

## Folder structure

```text
ai_chatbot_web_app/
├── app.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   └── js/app.js
└── screenshots/
```

## Run locally (Fedora / Linux)

1. Extract the ZIP and open the project folder in VS Code.
2. Open a terminal in the project folder.
3. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Create your environment file:

   ```bash
   cp .env.example .env
   ```

6. Open `.env` and replace `your_openai_api_key_here` with your API key. Keep the key private. You can create/manage API keys in the OpenAI developer platform.
7. Start the application:

   ```bash
   python app.py
   ```

8. Visit **http://127.0.0.1:5000** in your browser.

## Configuration

| Variable | Purpose | Default |
|---|---|---|
| `OPENAI_API_KEY` | Secret key for AI requests | Required |
| `OPENAI_MODEL` | Model used for responses | `gpt-4.1-mini` |
| `SECRET_KEY` | Flask session signing secret | Development placeholder |
| `DATABASE_URL` | Database connection | `sqlite:///chatbot.db` |
| `PORT` | Server port | `5000` |

For production, set a strong random `SECRET_KEY`, use PostgreSQL, and configure all secrets in your host's environment-variable dashboard. Never upload `.env`.

## Deploying

This Flask application can be deployed to a Python-capable host such as Render.

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Add environment variables: `OPENAI_API_KEY`, `OPENAI_MODEL`, `SECRET_KEY`, and `DATABASE_URL`.
- Use a managed PostgreSQL database for persistent hosted chat history. A host's temporary filesystem may not preserve SQLite data across deployments/restarts.

After deployment, open `/health`; it should return `{"status":"ok"}`.

## Testing checklist

- [ ] Homepage loads without errors.
- [ ] Send a message and receive an AI response.
- [ ] Loading dots appear while waiting.
- [ ] Refresh and verify conversation history is available in the same browser session.
- [ ] Create a second conversation.
- [ ] Delete a conversation.
- [ ] Test the layout on a phone-sized screen.
- [ ] Toggle dark mode.
- [ ] Confirm `.env` is not tracked by Git.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Main web application |
| `GET` | `/health` | Health check |
| `GET` | `/api/chats` | List current session conversations |
| `POST` | `/api/chats` | Create a conversation |
| `GET` | `/api/chats/<id>/messages` | Load messages |
| `DELETE` | `/api/chats/<id>` | Delete a conversation |
| `POST` | `/api/chat` | Send a message and receive an AI reply |

## Project description for submission

**Nova AI** is a responsive AI Chatbot Web Application developed using Python Flask, HTML, CSS and JavaScript. It integrates an AI language model through the OpenAI API to provide conversational responses across a wide range of topics. The application features a modern chat interface, message loading animation, conversation history, multiple chats, dark mode and mobile-responsive design. SQLite is used for local data storage, with PostgreSQL support for production deployment.

## Notes for students

This is a working project foundation, not a claim that the AI is infallible or has unrestricted knowledge. Review the code, understand each route, customize the UI, test it, and take your own screenshots before submitting. Add your own name, internship details and repository/live links to your final submission.
