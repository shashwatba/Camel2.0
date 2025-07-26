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

class Question(BaseModel):
    question: str
    answer: str
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

async def generate_quiz_with_openai(topic: str, keywords: List[str]) -> List[Question]:
    """
    Generate quiz questions and answers based on topic and keywords using OpenAI API.
    """
    try:
        keywords_str = ", ".join(keywords)
        
        prompt = f"""Create a quiz about "{topic}" focusing on these keywords: {keywords_str}

Generate 5-8 questions that test understanding of these keywords in the context of {topic}. 

For each question, provide:
1. A clear, specific question
2. A comprehensive answer
3. Which keyword it primarily relates to

Format your response as a JSON array like this:
[
  {{
    "question": "What is...",
    "answer": "Detailed answer explaining...",
    "keyword": "relevant_keyword",
    "difficulty": "medium"
  }},
  ...
]

Make sure questions are educational and test real understanding, not just memorization."""

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert educator who creates comprehensive quizzes. Always respond with valid JSON."},
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
                answer=q_data["answer"],
                keyword=keyword,
                difficulty=q_data.get("difficulty", "medium")
            ))
        
        return questions
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from OpenAI response: {str(e)}")
        # Fallback questions
        return [Question(
            question=f"What are the key concepts to understand about {topic}?",
            answer=f"The key concepts include: {', '.join(keywords[:3])} and their practical applications.",
            keyword=keywords[0] if keywords else "general",
            difficulty="medium"
        )]
    except Exception as e:
        print(f"Error generating quiz for {topic}: {str(e)}")
        # Fallback questions
        return [Question(
            question=f"What should someone know about {topic}?",
            answer=f"Understanding {topic} involves learning about {', '.join(keywords[:3])} and their applications.",
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
        questions = await generate_quiz_with_openai(request.topic, request.keywords)
        
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