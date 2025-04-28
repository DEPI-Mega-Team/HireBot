from pydantic import BaseModel
from config.database import Base
from sqlalchemy import Column, Integer, String, JSON

class InterviewRequest(BaseModel):
    interview_id: int
    candidate_name: str
    job_title: str
    interview_type: str  # "technical" or "behavioral"
    number_of_questions: int = 5
    skills: list[str] = []

class InterviewResponse(BaseModel):
    interview_id: int
    response: str

class Interview(Base):
    __tablename__ = "interviews"

    interview_id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    interview_type = Column(String, nullable=False)  # "technical" or "behavioral"
    number_of_questions = Column(Integer, default=5)
    skills = Column(JSON, default=[])
    instructions = Column(String, nullable=False)

class ChatMessage(BaseModel):
    role: str     # "user" or "assistant"
    message: str

class ChatRequest(BaseModel):
    interview_id: int
    chat_history: list[ChatMessage]
    prompt: str

class ChatResponse(BaseModel):
    interview_id: int
    response: str
    ended: bool = False