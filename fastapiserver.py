from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import uuid

load_dotenv()

app = FastAPI(title="Learning Extension API", version="1.0.0")

# Add CORS middleware to allow requests from Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your extension's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
# Make sure to set your OPENAI_API_KEY environment variable
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create data directory for storing quiz data
DATA_DIR = "quiz_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

QUIZ_HISTORY_FILE = os.path.join(DATA_DIR, "quiz_history.json")

# Pydantic models for request/response validation
class LearningTopicsRequest(BaseModel):
    topics: List[str]  # List of topics the user wants to learn

class KeywordsByTopicResponse(BaseModel):
    keywords_by_topic: Dict[str, List[str]]

class QuizRequest(BaseModel):
    topic: str  # The topic to generate quiz for
    keywords: List[str]  # Keywords for that topic
    difficulty: str = "medium"  # Can be "small" (easy), "medium", or "big" (hard)

class Question(BaseModel):
    question: str
    choice1: str
    choice2: str
    choice3: str
    choice4: str
    correct: str  # Will be "A", "B", "C", or "D"
    keyword: str
    difficulty: str = "medium"

class QuizResponse(BaseModel):
    topic: str
    questions: List[Question]
    generated_at: str
    quiz_id: str  # Add unique ID for each quiz

class UserAnswer(BaseModel):
    question_index: int
    selected_answer: str  # "A", "B", "C", or "D"
    is_correct: bool

class QuizSubmission(BaseModel):
    quiz_id: str
    topic: str
    keyword: str  # The keyword that triggered the quiz
    user_answers: List[UserAnswer]
    completed_at: str

class SavedQuiz(BaseModel):
    quiz_id: str
    topic: str
    keyword: str
    questions: List[Question]
    user_answers: List[UserAnswer]
    generated_at: str
    completed_at: Optional[str] = None
    score: Optional[int] = None
    total_questions: int

class QuizHistoryResponse(BaseModel):
    quizzes: List[SavedQuiz]
    total_count: int

def load_quiz_history() -> List[Dict]:
    """Load quiz history from JSON file"""
    try:
        if os.path.exists(QUIZ_HISTORY_FILE):
            with open(QUIZ_HISTORY_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading quiz history: {str(e)}")
        return []

def save_quiz_history(quizzes: List[Dict]):
    """Save quiz history to JSON file"""
    try:
        with open(QUIZ_HISTORY_FILE, 'w') as f:
            json.dump(quizzes, f, indent=2)
    except Exception as e:
        print(f"Error saving quiz history: {str(e)}")

def save_quiz_to_history(quiz_data: Dict):
    """Add a new quiz to the history"""
    history = load_quiz_history()
    history.append(quiz_data)
    save_quiz_history(history)

def update_quiz_submission(quiz_id: str, submission: QuizSubmission):
    """Update quiz with user answers and completion data"""
    history = load_quiz_history()
    
    for quiz in history:
        if quiz.get('quiz_id') == quiz_id:
            quiz['user_answers'] = [answer.dict() for answer in submission.user_answers]
            quiz['completed_at'] = submission.completed_at
            quiz['score'] = sum(1 for answer in submission.user_answers if answer.is_correct)
            break
    
    save_quiz_history(history)

async def generate_keywords_with_openai(topic: str) -> List[str]:
    """
    Generate relevant keywords for a given topic using OpenAI API.
    """
    try:
        prompt = f"""Generate a list of 10-15 important keywords or key terms that someone learning about "{topic}" should encounter and understand. 

These keywords should be:
- Core concepts, terms, or technologies related to {topic}
- Things that would commonly appear in articles, tutorials, or discussions about {topic}
- Fundamental building blocks of knowledge in this area

Return only the keywords as a simple comma-separated list, no explanations or numbering.

Example format: keyword1, keyword2, keyword3, etc."""

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert educator who creates comprehensive learning keyword lists."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        keywords_text = response.choices[0].message.content.strip()
        
        # Parse the comma-separated keywords
        keywords = [keyword.strip() for keyword in keywords_text.split(',')]
        keywords = [k for k in keywords if k]  # Remove empty strings
        
        return keywords[:15]  # Limit to 15 keywords max
        
    except Exception as e:
        print(f"Error generating keywords for {topic}: {str(e)}")
        # Fallback to basic keywords if OpenAI fails
        return [f"{topic}_concept", f"{topic}_basics", f"{topic}_fundamentals"]

async def generate_quiz_with_openai(topic: str, keywords: List[str], difficulty: str = "medium") -> List[Question]:
    """
    Generate multiple choice quiz questions based on topic and keywords using OpenAI API.
    """
    try:
        keywords_str = ", ".join(keywords)
        
        # Set difficulty instruction based on input
        if difficulty == "big":
            difficulty_instruction = "The question should be hard/difficult and take some thought to solve. Give some context for the question."
        elif difficulty == "small":
            difficulty_instruction = "The question should be simple and easy to answer."
        else:  # medium
            difficulty_instruction = "The question should be medium difficulty."
        
        prompt = f"""You are a kind and curious tutor that helps the user learn {topic}.
You never give the full answer immediately. Create multiple choice quiz questions about "{topic}" focusing on these keywords: {keywords_str}

{difficulty_instruction}

Generate 3-5 multiple choice questions. Each question should have 4 answer choices.

Format your response as a JSON array like this:
[
  {{
    "question": "The quiz question text here?",
    "choice1": "First answer option text",
    "choice2": "Second answer option text", 
    "choice3": "Third answer option text",
    "choice4": "Fourth answer option text",
    "correct": "A",
    "keyword": "relevant_keyword",
    "difficulty": "{difficulty}"
  }},
  ...
]

Important:
- The question should test understanding of the keyword in context
- choice1 through choice4 should contain ONLY the answer text (no A, B, C, D labels)
- correct should be the letter (A, B, C, or D) of the correct answer
- choice1 corresponds to A, choice2 to B, choice3 to C, choice4 to D
- Make the incorrect options plausible but clearly wrong
- Questions should be educational and test real understanding"""

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert educator who creates comprehensive multiple choice quizzes. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        questions_json = response.choices[0].message.content.strip()
        
        # Parse the JSON response
        questions_data = json.loads(questions_json)
        
        questions = []
        for q_data in questions_data:
            # Ensure the keyword exists in our keyword list
            keyword = q_data.get("keyword", keywords[0] if keywords else "general")
            if keyword not in keywords:
                keyword = keywords[0] if keywords else "general"
                
            questions.append(Question(
                question=q_data["question"],
                choice1=q_data["choice1"],
                choice2=q_data["choice2"],
                choice3=q_data["choice3"],
                choice4=q_data["choice4"],
                correct=q_data["correct"],
                keyword=keyword,
                difficulty=q_data.get("difficulty", difficulty)
            ))
        
        return questions
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from OpenAI response: {str(e)}")
        # Fallback question
        return [Question(
            question=f"What is the most important concept to understand about {topic}?",
            choice1=f"Understanding {keywords[0] if keywords else topic}",
            choice2="Memorizing syntax without understanding",
            choice3="Copying code from tutorials",
            choice4="Avoiding documentation",
            correct="A",
            keyword=keywords[0] if keywords else "general",
            difficulty="medium"
        )]
    except Exception as e:
        print(f"Error generating quiz for {topic}: {str(e)}")
        # Fallback question
        return [Question(
            question=f"Which of these is most relevant to {topic}?",
            choice1=f"{keywords[0] if keywords else topic} concepts",
            choice2="Unrelated programming concepts",
            choice3="Hardware specifications",
            choice4="None of the above",
            correct="A",
            keyword=keywords[0] if keywords else "general",
            difficulty="medium"
        )]

@app.get("/")
async def root():
    return {"message": "Learning Extension API is running with OpenAI integration!"}

@app.post("/generate-keywords", response_model=KeywordsByTopicResponse)
async def generate_keywords(request: LearningTopicsRequest):
    """
    Generate keywords for each topic using OpenAI API.
    Returns a dictionary with topics as keys and keyword lists as values.
    """
    try:
        if not openai_client.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        if not request.topics:
            raise HTTPException(status_code=400, detail="No topics provided")
        
        keywords_by_topic = {}
        
        for topic in request.topics:
            if not topic.strip():
                continue
                
            keywords = await generate_keywords_with_openai(topic.strip())
            keywords_by_topic[topic.strip()] = keywords
        
        if not keywords_by_topic:
            raise HTTPException(status_code=400, detail="No valid topics provided")
        
        return KeywordsByTopicResponse(keywords_by_topic=keywords_by_topic)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating keywords: {str(e)}")

@app.post("/generate-quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    """
    Generate quiz questions for a specific topic and its keywords using OpenAI API.
    Each quiz is automatically saved to the history file.
    """
    try:
        if not openai_client.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        if not request.topic.strip():
            raise HTTPException(status_code=400, detail="No topic provided")
        
        if not request.keywords:
            raise HTTPException(status_code=400, detail="No keywords provided")
        
        # Generate unique quiz ID
        quiz_id = str(uuid.uuid4())
        
        # Generate questions using OpenAI
        questions = await generate_quiz_with_openai(request.topic, request.keywords, request.difficulty)
        
        if not questions:
            raise HTTPException(status_code=400, detail="No questions could be generated")
        
        # Create quiz data for saving
        generated_at = datetime.now().isoformat()
        quiz_data = {
            "quiz_id": quiz_id,
            "topic": request.topic,
            "keyword": request.keywords[0] if request.keywords else "general",  # Use first keyword as trigger
            "questions": [question.dict() for question in questions],
            "user_answers": [],  # Will be filled when user submits answers
            "generated_at": generated_at,
            "completed_at": None,
            "score": None,
            "total_questions": len(questions)
        }
        
        # Save quiz to history
        save_quiz_to_history(quiz_data)
        
        return QuizResponse(
            topic=request.topic,
            questions=questions,
            generated_at=generated_at,
            quiz_id=quiz_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")

@app.post("/submit-quiz")
async def submit_quiz(submission: QuizSubmission):
    """
    Submit user answers for a quiz and update the saved quiz data.
    """
    try:
        # Update the quiz with user answers
        update_quiz_submission(submission.quiz_id, submission)
        
        return {
            "message": "Quiz submission saved successfully",
            "quiz_id": submission.quiz_id,
            "score": submission.user_answers and sum(1 for answer in submission.user_answers if answer.is_correct),
            "total": len(submission.user_answers) if submission.user_answers else 0
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting quiz: {str(e)}")

@app.get("/quiz-history", response_model=QuizHistoryResponse)
async def get_quiz_history():
    """
    Get all saved quiz history for the Flutter frontend.
    Returns all quizzes with their questions and user responses.
    """
    try:
        history_data = load_quiz_history()
        
        saved_quizzes = []
        for quiz_data in history_data:
            # Convert dict back to SavedQuiz model
            saved_quiz = SavedQuiz(
                quiz_id=quiz_data.get("quiz_id", ""),
                topic=quiz_data.get("topic", ""),
                keyword=quiz_data.get("keyword", ""),
                questions=[Question(**q) for q in quiz_data.get("questions", [])],
                user_answers=[UserAnswer(**a) for a in quiz_data.get("user_answers", [])],
                generated_at=quiz_data.get("generated_at", ""),
                completed_at=quiz_data.get("completed_at"),
                score=quiz_data.get("score"),
                total_questions=quiz_data.get("total_questions", 0)
            )
            saved_quizzes.append(saved_quiz)
        
        return QuizHistoryResponse(
            quizzes=saved_quizzes,
            total_count=len(saved_quizzes)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving quiz history: {str(e)}")

@app.get("/quiz-history/{quiz_id}")
async def get_quiz_by_id(quiz_id: str):
    """
    Get a specific quiz by its ID.
    """
    try:
        history_data = load_quiz_history()
        
        for quiz_data in history_data:
            if quiz_data.get("quiz_id") == quiz_id:
                return SavedQuiz(
                    quiz_id=quiz_data.get("quiz_id", ""),
                    topic=quiz_data.get("topic", ""),
                    keyword=quiz_data.get("keyword", ""),
                    questions=[Question(**q) for q in quiz_data.get("questions", [])],
                    user_answers=[UserAnswer(**a) for a in quiz_data.get("user_answers", [])],
                    generated_at=quiz_data.get("generated_at", ""),
                    completed_at=quiz_data.get("completed_at"),
                    score=quiz_data.get("score"),
                    total_questions=quiz_data.get("total_questions", 0)
                )
        
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving quiz: {str(e)}")

@app.delete("/quiz-history/{quiz_id}")
async def delete_quiz(quiz_id: str):
    """
    Delete a specific quiz from history.
    """
    try:
        history_data = load_quiz_history()
        original_length = len(history_data)
        
        # Filter out the quiz with the specified ID
        history_data = [quiz for quiz in history_data if quiz.get("quiz_id") != quiz_id]
        
        if len(history_data) == original_length:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        save_quiz_history(history_data)
        
        return {"message": "Quiz deleted successfully", "quiz_id": quiz_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting quiz: {str(e)}")

@app.get("/quiz-stats")
async def get_quiz_stats():
    """
    Get quiz statistics for analytics.
    """
    try:
        history_data = load_quiz_history()
        
        total_quizzes = len(history_data)
        completed_quizzes = len([q for q in history_data if q.get("completed_at")])
        
        # Calculate average score for completed quizzes
        completed_with_scores = [q for q in history_data if q.get("score") is not None and q.get("total_questions", 0) > 0]
        avg_score_percentage = 0
        if completed_with_scores:
            total_percentage = sum((q["score"] / q["total_questions"]) * 100 for q in completed_with_scores)
            avg_score_percentage = total_percentage / len(completed_with_scores)
        
        # Topic breakdown
        topic_counts = {}
        for quiz in history_data:
            topic = quiz.get("topic", "Unknown")
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        return {
            "total_quizzes": total_quizzes,
            "completed_quizzes": completed_quizzes,
            "pending_quizzes": total_quizzes - completed_quizzes,
            "average_score_percentage": round(avg_score_percentage, 2),
            "topics": topic_counts
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving quiz stats: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    api_key_status = "configured" if openai_client.api_key else "missing"
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "openai_api_key": api_key_status
    }

@app.get("/test-openai")
async def test_openai():
    """Test OpenAI API connection"""
    try:
        if not openai_client.api_key:
            return {"status": "error", "message": "OpenAI API key not configured"}
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        
        return {"status": "success", "message": "OpenAI API is working"}
    except Exception as e:
        return {"status": "error", "message": f"OpenAI API error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)