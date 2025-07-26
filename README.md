# 🐫 Camel: Browser Plugin to Learn Instead of Lookup

Camel is a browser extension that intercepts your AI-related queries and turns them into *teachable moments*.

Instead of giving you direct answers from ChatGPT, Bard, or other LLMs, CamelTutor asks questions back, coaches you through the concepts (e.g., SQL, Python, ML), and helps you grow your skills.

---

## ✨ Features

- 🧠 **Intercepts AI usage** and classifies questions
- 🎓 **Context-aware tutoring** using an LLM-powered backend
- ⛔ **Blocks or delays direct answers** to promote thinking
- 📈 **Adaptive difficulty** ("hump types") – small, medium, or big challenges
- 📝 **JSON logs** of every tutoring exchange
- 🌐 **Works across popular LLM platforms** (ChatGPT, Bard, etc.)

---

## 🛠️ How It Works

1. **Keyword Detector** in the browser tracks when you write an AI-style question.
2. If the query matches a learning domain (e.g. `"SQL"`), it:
   - Sends the query to your local LLM prompt engine (via OpenAI API)
   - Applies a system prompt like:
     > _"Act as a tutor. Ask me a question about this topic first before answering."_
3. The plugin replaces your request with a quiz, explanation, or suggestion to pause and reflect.

---

## 🧪 Example Use Case

User types:
> *"How do I do a LEFT JOIN in SQL?"*

CamelTutor responds:
> _"Great question. Can you first tell me what a JOIN is and when you’d use LEFT JOIN over INNER JOIN?"_

---

## 🧰 Requirements

- Python 3.8+
- `openai>=1.0.0`
- `python-dotenv`
- Chrome or Chromium-based browser
- `manifest.json`-based browser extension loader

---

## 🚀 Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/CamelTutor.git
cd CamelTutor
```


Made for Forgehack 2025 by Shashwat Bansal, Mahi Gupta, Alexis Manyrath, Jun Park

Presentation[https://www.canva.com/design/DAGuS_HZzqE/3qBnQUgEkx6IcHFpBOdP_g/edit?utm_content=DAGuS_HZzqE&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton]
Notion[https://www.notion.so/Project-Overview-23c76236c50580fdb14bdf83304c6f8e]


