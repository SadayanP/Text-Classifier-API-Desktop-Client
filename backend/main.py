import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set in the environment")


from datetime import datetime, timedelta, timezone

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from transformers import pipeline


from backend.database import create_tables, get_db
from backend.schemas import (
    ClassifyRequest,
    ClassifyResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    FeedbackRequest,
    FeedbackResponse,
)


app = FastAPI()

MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
classifier = pipeline("sentiment-analysis", model=MODEL_NAME)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set in the environment")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


@app.on_event("startup")
async def startup_event():
    create_tables()



def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        subject = payload.get("sub")

        if subject is None:
            raise credentials_exception

        user_id = int(subject)

    except (JWTError, ValueError):
        raise credentials_exception

    with get_db() as conn:
        user = conn.execute(
            "SELECT id FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

    if user is None:
        raise credentials_exception

    return user_id


@app.get("/health")
def read_health():
    return {"status": "ok"}


@app.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest):
    password_hash = pwd_context.hash(request.password)

    try:
        with get_db() as conn:
            cursor = conn.execute(
                """
                INSERT INTO users (username, password_hash)
                VALUES (?, ?)
                """,
                (request.username, password_hash),
            )
            conn.commit()

            user_id = cursor.lastrowid

    except Exception as exc:
        if "UNIQUE constraint failed: users.username" in str(exc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create user",
        )

    return RegisterResponse(
        id=user_id,
        username=request.username,
    )


@app.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    with get_db() as conn:
        user = conn.execute(
            """
            SELECT id, username, password_hash
            FROM users
            WHERE username = ?
            """,
            (request.username,),
        ).fetchone()

    if user is None or not pwd_context.verify(
        request.password,
        user[2],
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user[0])

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
    )


@app.post("/classify", response_model=ClassifyResponse)
def classify(
    request: ClassifyRequest,
    user_id: int = Depends(get_current_user_id),
):
    result = classifier(request.text)[0]

    label = result["label"].upper()
    confidence = float(result["score"])

    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO predictions (
                user_id,
                text,
                label,
                confidence
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                request.text,
                label,
                confidence,
            ),
        )

        conn.commit()
        prediction_id = cursor.lastrowid

    return ClassifyResponse(
        prediction_id=prediction_id,
        text=request.text,
        label=label,
        confidence=confidence,
    )
    
@app.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(
    request: FeedbackRequest,
    user_id: int = Depends(get_current_user_id),
):
    feedback_value = 1 if request.is_correct else 0

    with get_db() as conn:
        cursor = conn.execute(
            """
            UPDATE predictions
            SET feedback = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                feedback_value,
                request.prediction_id,
                user_id,
            ),
        )

        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prediction not found",
            )

    return FeedbackResponse(
        prediction_id=request.prediction_id,
        feedback=request.is_correct,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)