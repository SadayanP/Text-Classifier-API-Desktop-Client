# Text Classifier API + Desktop Client

A full-stack machine learning project that serves a sentiment classification model through a FastAPI backend and a modern PyQt desktop client.

The system supports user authentication, prediction logging, and human feedback on model outputs.

---

## Features

- **Model serving** with Hugging Face Transformers (`distilbert-base-uncased-finetuned-sst-2-english`)
- **REST API** built with FastAPI
- **JWT authentication** (register + login)
- **SQLite** storage for users and predictions
- **Feedback endpoint** so users can mark predictions as correct or incorrect
- **Modern PyQt5 desktop client**
- **Executable client** (`.exe`) for easy demonstration
- Basic automated tests with pytest

---

## Tech Stack

| Layer        | Technology                                      |
|--------------|--------------------------------------------------|
| Backend      | FastAPI, Uvicorn, Pydantic                       |
| ML Model     | Hugging Face Transformers + PyTorch              |
| Auth         | JWT (`python-jose`) + bcrypt (`passlib`)         |
| Database     | SQLite                                           |
| Desktop UI   | PyQt5                                            |
| Packaging    | PyInstaller                                      |
| Testing      | pytest                                           |

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
├── .env
├── requirements.txt
├── pytest.ini
└── README.md
