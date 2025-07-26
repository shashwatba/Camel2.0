from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

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
    """
    try:
        if not openai_client.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        if not request.topic.strip():
            raise HTTPException(status_code=400, detail="No topic provided")
        
        if not request.keywords:
            raise HTTPException(status_code=400, detail="No keywords provided")
        
        # Generate questions using OpenAI
        questions = await generate_quiz_with_openai(request.topic, request.keywords, request.difficulty)
        
        if not questions:
            raise HTTPException(status_code=400, detail="No questions could be generated")
        
        return QuizResponse(
            topic=request.topic,
            questions=questions,
            generated_at=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")

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