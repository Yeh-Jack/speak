# Exam System Skill

## Description
Spaced repetition learning with SM-2 algorithm, adaptive testing, and multiple question types.

## When to Use
Use this skill when implementing the exam system, SM-2 algorithm, question generation, or spaced repetition review.

## Language Rule

**MANDATORY: ALL Chinese text must be Traditional Chinese (繁體中文). No Simplified Chinese allowed.**

Every LLM prompt that may generate Chinese content MUST include this instruction:
```
IMPORTANT: When generating any Chinese text (explanations, feedback, question content),
you MUST use Traditional Chinese (繁體中文). Do NOT use Simplified Chinese.
```

## Guidelines

### SM-2 Algorithm

The SM-2 algorithm tracks review intervals based on performance:

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

@dataclass
class SM2Card:
    """Represents a learning item (vocabulary word, grammar rule, etc.)."""
    id: str
    ease_factor: float = 2.5  # EF
    interval: int = 0         # I in days
    repetition: int = 0       # Number of successful reviews
    next_review: Optional[datetime] = None
    last_review: Optional[datetime] = None
    
def calculate_sm2(
    card: SM2Card,
    quality: int  # 0-5 rating
) -> SM2Card:
    """
    Apply SM-2 algorithm.
    
    Quality levels:
    0 - Complete blackout
    1 - Incorrect but familiar
    2 - Incorrect but easy to recall
    3 - Correct with difficulty
    4 - Correct after hesitation
    5 - Perfect response
    """
    if quality < 3:
        # Failed - reset repetition count but keep ease factor
        card.repetition = 0
        card.interval = 1  # Review tomorrow
    else:
        # Successful review
        card.repetition += 1
        
        if card.repetition == 1:
            card.interval = 1  # 1 day
        elif card.repetition == 2:
            card.interval = 6  # 6 days
        else:
            card.interval = int(card.interval * card.ease_factor)
    
    # Update ease factor: EF' = EF + (0.1 - (5-q)(0.08 + (5-q)*0.02))
    card.ease_factor = max(
        1.3,  # Minimum EF
        card.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    )
    
    card.last_review = datetime.utcnow()
    card.next_review = card.last_review + timedelta(days=card.interval)
    
    return card
```

### SM-2 Implementation with Database

```python
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from uuid import UUID, uuid4

class VocabularyCard(Base):
    """Vocabulary item with SM-2 tracking."""
    __tablename__ = "vocabularies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    word = Column(String(200), nullable=False)
    definition = Column(Text)
    context = Column(Text)  # Example sentence from video
    cefr_level = Column(String(10))  # A1, A2, B1, B2, C1, C2
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"))
    
    # SM-2 fields
    ease_factor = Column(Float, default=2.5)
    interval = Column(Integer, default=0)  # days
    repetition = Column(Integer, default=0)
    next_review = Column(DateTime)
    last_review = Column(DateTime)
    
    # Stats
    total_reviews = Column(Integer, default=0)
    correct_reviews = Column(Integer, default=0)
    streak = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="vocabularies")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'word', name='unique_user_word'),
    )

class SM2Service:
    """Service for SM-2 spaced repetition calculations."""
    
    MIN_EASE_FACTOR = 1.3
    
    @staticmethod
    def calculate_next_review(
        card: VocabularyCard,
        quality: int
    ) -> VocabularyCard:
        """
        Calculate next review date using SM-2 algorithm.
        
        Args:
            card: The vocabulary card
            quality: Quality of recall (0-5)
        
        Returns:
            Updated card with new interval and next review date
        """
        if not 0 <= quality <= 5:
            raise ValueError("Quality must be between 0 and 5")
        
        card.total_reviews += 1
        card.last_review = datetime.utcnow()
        
        if quality < 3:
            # Failed response
            card.repetition = 0
            card.streak = 0
            card.interval = 1
        else:
            # Successful response
            card.correct_reviews += 1
            card.streak += 1
            card.repetition += 1
            
            if card.repetition == 1:
                card.interval = 1
            elif card.repetition == 2:
                card.interval = 6
            else:
                card.interval = round(card.interval * card.ease_factor)
        
        # Update ease factor
        new_ef = card.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        card.ease_factor = max(SM2Service.MIN_EASE_FACTOR, new_ef)
        
        # Calculate next review
        card.next_review = card.last_review + timedelta(days=card.interval)
        
        return card
    
    @staticmethod
    def get_due_cards(
        session: AsyncSession,
        user_id: UUID,
        limit: int = 20
    ) -> List[VocabularyCard]:
        """Get cards due for review."""
        now = datetime.utcnow()
        
        result = await session.execute(
            select(VocabularyCard)
            .where(
                and_(
                    VocabularyCard.user_id == user_id,
                    or_(
                        VocabularyCard.next_review <= now,
                        VocabularyCard.next_review == None
                    )
                )
            )
            .order_by(VocabularyCard.next_review.nulls_first())
            .limit(limit)
        )
        
        return result.scalars().all()
    
    @staticmethod
    def get_stats(session: AsyncSession, user_id: UUID) -> dict:
        """Get spaced repetition statistics."""
        total = await session.scalar(
            select(func.count(VocabularyCard.id))
            .where(VocabularyCard.user_id == user_id)
        )
        
        due = await session.scalar(
            select(func.count(VocabularyCard.id))
            .where(
                and_(
                    VocabularyCard.user_id == user_id,
                    VocabularyCard.next_review <= datetime.utcnow()
                )
            )
        )
        
        new_cards = await session.scalar(
            select(func.count(VocabularyCard.id))
            .where(
                and_(
                    VocabularyCard.user_id == user_id,
                    VocabularyCard.repetition == 0
                )
            )
        )
        
        return {
            "total_cards": total,
            "due_for_review": due,
            "new_cards": new_cards
        }
```

### Question Types

```python
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_BLANK = "fill_blank"
    DICTATION = "dictation"
    SPEAKING = "speaking"
    TRANSLATION = "translation"

class Question(BaseModel):
    id: str
    type: QuestionType
    question: str
    options: Optional[List[str]] = None  # For multiple choice
    correct_answer: str
    explanation: str
    difficulty: str  # A1, A2, B1, B2, C1, C2
    video_timestamp: Optional[float] = None
    chunk_index: Optional[int] = None

class Exam(BaseModel):
    id: str
    video_id: str
    user_id: str
    questions: List[Question]
    total_questions: int
    time_limit: Optional[int] = None  # seconds

# Example questions by type

MULTIPLE_CHOICE_EXAMPLE = {
    "id": "1",
    "type": "multiple_choice",
    "question": "What does 'innovation' mean?",
    "options": [
        "A new idea or method",
        "A type of music",
        "A historical event",
        "A mathematical formula"
    ],
    "correct_answer": "A new idea or method",
    "explanation": "Innovation means the introduction of something new, especially a new idea or method.",
    "difficulty": "B2"
}

FILL_BLANK_EXAMPLE = {
    "id": "2",
    "type": "fill_blank",
    "question": "The company is known for its ______ in the tech industry.",
    "correct_answer": "innovation",
    "explanation": "The context shows the company is introducing new ideas in tech.",
    "difficulty": "B2"
}

DICTATION_EXAMPLE = {
    "id": "3",
    "type": "dictation",
    "question": "Type what you hear",
    "correct_answer": "Innovation drives progress in every industry.",
    "explanation": "Practice listening and spelling key vocabulary.",
    "difficulty": "B1",
    "audio_url": "/api/audio/sample.mp3"
}

SPEAKING_EXAMPLE = {
    "id": "4",
    "type": "speaking",
    "question": "Say the sentence: 'Innovation drives progress.'",
    "correct_answer": "Innovation drives progress.",
    "explanation": "Practice pronunciation of the word 'innovation'.",
    "difficulty": "B1"
}

TRANSLATION_EXAMPLE = {
    "id": "5",
    "type": "translation",
    "question": "Translate to your native language: 'The innovation transformed the industry.'",
    "correct_answer": "[User native language translation]",
    "explanation": "Translate the sentence to reinforce understanding.",
    "difficulty": "B2"
}
```

### Exam Generation with LLM

```python
class ExamGenerationService:
    """Generate exam questions using LLM."""
    
    SYSTEM_PROMPT = """You are an expert English teacher creating adaptive tests.
Generate exam questions based on the provided vocabulary and transcript.

IMPORTANT: All Chinese text MUST be Traditional Chinese (繁體中文). No Simplified Chinese.
When providing explanations, feedback, or any Chinese content, use Traditional Chinese only.
Examples: 是、開發、學習、詞彙、語法

Create questions covering:
- Vocabulary meaning and usage
- Grammar concepts from the context
- Listening comprehension
- Translation skills

Respond ONLY with valid JSON array of questions in this format:
[
    {
        "type": "multiple_choice|fill_blank|dictation|speaking|translation",
        "question": "string (English)",
        "question_zh": "string (Traditional Chinese)",
        "options": ["A", "B", "C", "D"],  // For multiple_choice only
        "correct_answer": "string",
        "explanation": "string (English)",
        "explanation_zh": "string (Traditional Chinese)",
        "difficulty": "A1|A2|B1|B2|C1|C2",
        "video_timestamp": 45.5  // Optional - timestamp in seconds
    }
]

Generate at least 10 questions total with varied difficulty levels."""
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
    
    async def generate_exam(
        self,
        video_id: str,
        vocabulary: List[dict],
        transcript: List[dict],
        chunk_index: int
    ) -> List[Question]:
        """Generate exam questions for a video chunk."""
        
        # Build context
        vocab_text = "\n".join([
            f"- {v['word']} ({v['cefr']}): {v['definition']}"
            for v in vocabulary[:20]
        ])
        
        transcript_sample = "\n".join([
            f"[{t['start']}] {t['text']}"
            for t in transcript[:30]
        ])
        
        user_prompt = f"""Video Chunk: {chunk_index + 1}

Vocabulary to test:
{vocab_text}

Transcript Sample:
{transcript_sample}

Generate exam questions as JSON array."""
        
        response = await self.llm.generate(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=user_prompt,
            max_tokens=4096
        )
        
        import json
        import re
        
        try:
            questions_data = json.loads(response)
        except json.JSONDecodeError:
            # Extract JSON from markdown
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group(1))
            else:
                raise ValueError("Failed to parse exam questions")
        
        questions = []
        for q_data in questions_data:
            questions.append(Question(
                id=str(uuid4()),
                type=QuestionType(q_data["type"]),
                question=q_data["question"],
                options=q_data.get("options"),
                correct_answer=q_data["correct_answer"],
                explanation=q_data["explanation"],
                difficulty=q_data["difficulty"],
                video_timestamp=q_data.get("video_timestamp"),
                chunk_index=chunk_index
            ))
        
        return questions
```

### Exam Submission and Scoring

```python
from pydantic import BaseModel
from typing import List

class AnswerSubmission(BaseModel):
    question_id: str
    answer: str
    time_spent: int  # seconds

class ExamSubmission(BaseModel):
    exam_id: str
    answers: List[AnswerSubmission]
    total_time: int  # seconds

class ExamResult(BaseModel):
    exam_id: str
    total_questions: int
    correct_answers: int
    score: float  # percentage
    time_taken: int
    question_results: List[dict]
    recommendations: List[str]  # Vocabulary to review

class ExamService:
    """Exam submission and scoring service."""
    
    def __init__(self, sm2_service: SM2Service):
        self.sm2 = sm2_service
    
    async def submit_exam(
        self,
        submission: ExamSubmission,
        user_id: UUID
    ) -> ExamResult:
        """Process exam submission and return results."""
        
        # Get exam from database
        exam = await self.get_exam(submission.exam_id)
        
        question_results = []
        correct_count = 0
        
        for answer_sub in submission.answers:
            question = next(
                (q for q in exam.questions if q.id == answer_sub.question_id),
                None
            )
            
            if not question:
                continue
            
            is_correct = self._check_answer(
                question,
                answer_sub.answer
            )
            
            if is_correct:
                correct_count += 1
            
            question_results.append({
                "question_id": question.id,
                "type": question.type,
                "is_correct": is_correct,
                "correct_answer": question.correct_answer,
                "user_answer": answer_sub.answer,
                "explanation": question.explanation
            })
            
            # Update SM-2 for vocabulary items
            if question.type in [QuestionType.MULTIPLE_CHOICE, QuestionType.FILL_BLANK]:
                await self._update_vocabulary_review(
                    user_id,
                    question.question,
                    is_correct
                )
        
        score = (correct_count / len(exam.questions)) * 100
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(
            user_id,
            question_results
        )
        
        return ExamResult(
            exam_id=submission.exam_id,
            total_questions=len(exam.questions),
            correct_answers=correct_count,
            score=score,
            time_taken=submission.total_time,
            question_results=question_results,
            recommendations=recommendations
        )
    
    def _check_answer(self, question: Question, user_answer: str) -> bool:
        """Check if answer is correct (case-insensitive)."""
        return user_answer.strip().lower() == question.correct_answer.strip().lower()
    
    async def _update_vocabulary_review(
        self,
        user_id: UUID,
        question_text: str,
        is_correct: bool
    ):
        """Update SM-2 status for vocabulary words tested."""
        # Extract vocabulary word from question
        # Update card with quality based on correctness
        quality = 4 if is_correct else 2  # 4=correct, 2=incorrect
        # ... update in database
    
    async def _generate_recommendations(
        self,
        user_id: UUID,
        results: List[dict]
    ) -> List[str]:
        """Generate study recommendations based on weak areas."""
        weak_topics = [
            r["question_id"]
            for r in results
            if not r["is_correct"]
        ]
        
        # Query vocabulary for these questions
        # Return list of words to review
        return []
```

### API Endpoints

```python
from fastapi import APIRouter, Depends
from typing import List

router = APIRouter(prefix="/api/exams")

@router.post("/{video_id}/generate")
async def generate_exam(
    video_id: str,
    current_user: User = Depends(get_current_user)
) -> dict:
    """Generate exam questions for video."""
    # Queue Celery task
    task = generate_exam_questions_task.delay(video_id)
    return {"task_id": task.id, "status": "pending"}

@router.get("/history")
async def get_exam_history(
    current_user: User = Depends(get_current_user)
) -> List[dict]:
    """Get user's exam history."""
    # Query database for past exams
    pass

@router.post("/{exam_id}/submit")
async def submit_exam(
    exam_id: str,
    submission: ExamSubmission,
    current_user: User = Depends(get_current_user)
) -> ExamResult:
    """Submit exam answers."""
    service = ExamService(sm2_service)
    return await service.submit_exam(submission, current_user.id)

@router.get("/vocabulary/review")
async def get_due_vocabulary(
    limit: int = 20,
    current_user: User = Depends(get_current_user)
) -> List[dict]:
    """Get vocabulary cards due for review."""
    cards = await SM2Service.get_due_cards(session, current_user.id, limit)
    return cards

@router.post("/vocabulary/{word_id}/review")
async def submit_review(
    word_id: str,
    quality: int,  # 0-5
    current_user: User = Depends(get_current_user)
) -> dict:
    """Submit review result and update SM-2 schedule."""
    card = await get_vocabulary_card(word_id)
    updated = SM2Service.calculate_next_review(card, quality)
    await save_vocabulary_card(updated)
    return {"next_review": updated.next_review, "interval": updated.interval}
```

## Question Distribution

| Type | Percentage | Count per Exam |
|------|------------|----------------|
| Multiple Choice | 40% | 4 |
| Fill-in-the-Blank | 20% | 2 |
| Dictation | 20% | 2 |
| Speaking | 10% | 1 |
| Translation | 10% | 1 |
| **Total** | 100% | **10** |

## Dependencies

```
# Database
sqlalchemy>=2.0.0
asyncpg>=0.28.0

# Date/time
python-dateutil>=2.8.0
```

## Environment Variables

```bash
# Exam configuration
MIN_QUESTIONS_PER_EXAM=10
MAX_QUESTIONS_PER_EXAM=20
EXAM_TIME_LIMIT_MINUTES=30

# SM-2 defaults
DEFAULT_EASE_FACTOR=2.5
MIN_EASE_FACTOR=1.3
```

## Notes

- Minimum 10 questions per exam
- Immediate feedback with explanations
- SM-2 algorithm adjusts review intervals automatically
- Support multiple question types with different UI requirements
- Track weak areas for targeted practice
- Integration with vocabulary system for seamless review
