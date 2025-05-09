from fastapi import Body
from pydantic import BaseModel, Field
from config.database import Base
from sqlalchemy import Column, String

class InterviewProperties(BaseModel):
    candidate_name: str = Field(..., min_length=1)
    job_title: str = Field(..., min_length=1)
    interview_type: str = Field(..., pattern="^(technical|behavioral)$")
    number_of_questions: int = Field(..., gt=2, le=15)
    skills: list[str] = []

class InterviewRequest(BaseModel):
    interview_id: int   

class InterviewResponse(BaseModel):
    response: str

class Instructions(Base):
    __tablename__ = "instructions"

    interview_type = Column(String, primary_key=True, nullable=False)
    job_title = Column(String, primary_key=True, nullable=False)
    content = Column(String, nullable=False)

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    message: str = Field(..., min_length=1)

class ChatRequest(InterviewRequest, BaseModel):
    prompt: str = Field(..., min_length=1)

class ChatResponse(BaseModel):
    response: str
    ended: bool