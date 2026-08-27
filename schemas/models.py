from pydantic import BaseModel
from typing import Any, Optional



class StandardResponse(BaseModel):
    message: str
    saved_file: Optional[str] = None  
    result: Optional[Any] = None  




class ChapterSummaryModel(BaseModel):
    chapter_number: int
    summary: str

class LLMSummaryOutput(BaseModel):
    chapters: list[ChapterSummaryModel]




class QuestionModel(BaseModel):
    difficulty: str
    question: str
    ideal_answer: str


class ChapterQuizModel(BaseModel):
    chapter_number: int
    questions: list[QuestionModel]


class LLMQuizOutput(BaseModel):
    quiz: list[ChapterQuizModel]    