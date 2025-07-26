import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# load .env file OPENAI_API_KEY=
load_dotenv()

# key input will be the keywords given from history and initializtion
# probably more like 'topic'
key_input = "SQL"

# Hump type is the size of obstacle: big - med - small
hump_type = "big"

if hump_type == "big":
    hump_inst = "The question should be hard difficult and take some thought to solve. Give some context for the question."
elif hump_type == "med":
    hump_inst = "The question should be medium difficulty."
elif hump_type == "small":
    hump_inst = "The question should be simple."

# 🔐 Load API key (or set it directly here)
client = OpenAI()

# 🧠 System prompt
system_prompt = f"""
You are a kind and curious tutor that helps the user learn {key_input}.
You never give the full answer immediately. Make a 4 question 
multiple choice quiz. {hump_inst}. Return as a JSON file with the headers question,
choice1, choice2, choice3, choice4, and correct. The question should contain the quiz question.
choice1, choice2, choice3, choice4 should be the TEXT of the answer, not including the letter of the question.
correct should be the letter of the correct answer (A,B,C,D).
"""

# 💬 User question
user_input = "I'm trying to learn {key_input}. Give me a quiz question related to this."

# 🧠 Call the LLM using the modern API
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ],
    temperature=0.7
)

quiz_json = response.choices[0].message.content.strip()

# with open("response/tutor_response_text.json", "w") as f:
#     json.dump({"reply": quiz_json}, f, indent=2)

# 🖨️ Show output
print("=== 👩‍🏫 Tutor's Response ===")
print(quiz_json)

user_quiz_resp = input()

# 🧠 Follow up system prompt
system_prompt_fb = f"""
You are a kind and curious tutor that helps the user learn {key_input}.
You never give the full answer immediately. You asked this quiz question: {quiz_json}.
The user answered {user_quiz_resp}. Respond so they learn from their mistakes.
"""

user_fb_resp = f"""I think the answer for 
{quiz_json} is {user_quiz_resp}.
Explain to me if I got it wrong or give me congrats for getting it right!"""

# 🧠 Call the LLM using the modern API
feedback = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": system_prompt_fb},
        {"role": "user", "content": user_fb_resp}
    ],
    temperature=0.7
)

# 🖨️ Show output
print("=== 👩‍🏫 Tutor's Response ===")
print(feedback.choices[0].message.content.strip())