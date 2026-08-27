from typing import Literal

from pydantic import BaseModel, Field


class ClassifyRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class ClassifyResponse(BaseModel):
    prediction_id: int
    text: str
    label: str
    confidence: float


class RegisterRequest(BaseModel):
    username: str
    password: str


class RegisterResponse(BaseModel):
    id: int
    username: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"]
    
class FeedbackRequest(BaseModel):
    prediction_id: int
    is_correct: bool


class FeedbackResponse(BaseModel):
    prediction_id: int
    feedback: bool