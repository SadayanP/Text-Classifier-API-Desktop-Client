# Text Classifier API + Desktop Client

A full-stack machine learning project that serves a sentiment classification model through a FastAPI backend and a modern PyQt desktop client.

The system supports user authentication, prediction logging, and human feedback on model outputs.

---

## Features

- Model serving with Hugging Face Transformers (`distilbert-base-uncased-finetuned-sst-2-english`)
- REST API built with FastAPI
- JWT authentication (register + login)
- SQLite storage for users and predictions
- Feedback endpoint for marking predictions as correct or incorrect
- Modern PyQt5 desktop client
- Optional Windows executable (`.exe`)
- Basic automated tests with pytest

---

## Tech Stack

- **Backend:** FastAPI, Uvicorn, Pydantic
- **ML Model:** Hugging Face Transformers + PyTorch
- **Auth:** JWT (`python-jose`) + bcrypt (`passlib`)
- **Database:** SQLite
- **Desktop UI:** PyQt5
- **Packaging:** PyInstaller
- **Testing:** pytest

---

## Project Structure

```text
text-classifier/
├── backend/
│   ├── main.py
│   ├── database.py
│   └── schemas.py
├── client/
│   └── main.py
├── tests/
│   └── test_api.py
├── .env.example
├── requirements.txt
├── pytest.ini
└── README.md

Getting Started
1. Clone the repository
Bashgit clone <your-repo-url>
cd text-classifier
2. Create and activate a virtual environment
Bashpython -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
3. Install dependencies
Bashpip install -r requirements.txt
4. Configure environment variables
Create a .env file in the project root:
envSECRET_KEY=your-secret-key-here
For a real deployment, generate a strong random secret.
5. Start the backend
Bashuvicorn backend.main:app --reload
The API will be available at:

http://127.0.0.1:8000
Interactive docs:

http://127.0.0.1:8000/docs
6. Run the desktop client
Bashpython client/main.py
Or run the packaged executable (Windows):
textdist/TextClassifier/TextClassifier.exe
The backend must be running for the client to work.

API Overview

GET /health — Health check (no auth)
POST /register — Create a new user (no auth)
POST /login — Get JWT access token (no auth)
POST /classify — Classify text sentiment (auth required)
POST /feedback — Submit feedback on a prediction (auth required)

Example: Classify
Bashcurl -X POST http://127.0.0.1:8000/classify \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"I really love this product\"}"
Example response:
JSON{
  "prediction_id": 1,
  "text": "I really love this product",
  "label": "POSITIVE",
  "confidence": 0.9998
}

Model Notes
This project uses:
textdistilbert-base-uncased-finetuned-sst-2-english
It is a binary sentiment classifier (POSITIVE / NEGATIVE).
Strengths

Fast inference
Strong performance on clear, short sentences

Limitations

Can struggle with mixed sentiment, negation, or longer nuanced text
Always returns one of two labels even when the input is ambiguous

The feedback feature exists partly to acknowledge that model predictions are not perfect and to capture human judgment.

Running Tests
Bashpytest -v
The tests cover:

Health check
Full flow: register → login → classify → feedback
Authentication protection on /classify


Design Decisions

SQLite was chosen for simplicity and zero setup cost
JWT with a 60-minute expiry keeps authentication straightforward for a local demo
The desktop client stores the token in memory only (no disk persistence)
Scope was deliberately kept tight so the project could be finished cleanly and explained well


Future Improvements

Move from SQLite to PostgreSQL
Add refresh tokens
Support multi-class or more advanced models
Deploy the API
Add more comprehensive test coverage
Improve model confidence handling / abstention for low-confidence predictions


License
MIT
textAfter pasting, check the GitHub preview (or any markdown preview). The code blocks and headings should now display correctly.
