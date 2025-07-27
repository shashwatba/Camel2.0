# 🐪 Camel - Smart Learning While Browsing

Transform your everyday web browsing into a personalized learning experience! Camel Tutor is an intelligent Chrome extension that tracks keywords as you browse and generates AI-powered quizzes to reinforce your learning.

## 🌟 Why Camel Tutor is Super Useful

**Stop forgetting what you learn online.** We've all been there - you read an amazing article about machine learning, watch a JavaScript tutorial, or browse through documentation, but a week later you can barely remember the key concepts. Camel Tutor solves this by:

- **🎯 Automatically tracking** important keywords while you browse any website
- **🧠 Testing your knowledge** with AI-generated quizzes when you've encountered enough content
- **📈 Reinforcing learning** through spaced repetition without any extra effort
- **🎮 Making learning engaging** with interactive multiple-choice questions

**Perfect for developers, students, and lifelong learners** who want to retain more of what they read online without changing their browsing habits.

## ✨ Key Features

### 🔍 Smart Keyword Tracking
- Enter any topic you want to learn (e.g., "React", "Machine Learning", "Photography")
- AI generates relevant keywords to track across all websites you visit
- Invisible tracking - browse normally while building knowledge

### 🎯 Intelligent Quiz Generation
- Automatically triggers quizzes when you've encountered keywords multiple times
- AI-powered questions that test real understanding, not just memorization
- Adjustable difficulty levels (Small, Medium, Large "humps")
- Beautiful, distraction-free quiz interface

### 📊 Learning Analytics
- Track your progress across different topics
- See how many times you've encountered each keyword
- Review quiz history and performance
- Identify knowledge gaps

### 🎨 Seamless Experience
- Works on any website
- Non-intrusive popup quizzes
- Clean, modern interface
- Keyboard shortcuts for power users

## 🚀 Getting Started

### Prerequisites
- Chrome browser
- Python 3.8+ (for the backend server)
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd camel-tutor
   ```

2. **Set up the backend server**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure OpenAI API**
   ```bash
   # Create a .env file in the project root
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

4. **Start the backend server**
   ```bash
   python fastapiserver.py
   ```

5. **Load the Chrome extension**
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the project folder
   - The Camel Tutor icon should appear in your toolbar!

### Quick Start

1. **Click the Camel Tutor icon** in your Chrome toolbar
2. **Enter a topic** you want to learn (e.g., "JavaScript", "Digital Marketing")
3. **Start browsing** websites related to that topic
4. **Get quizzed** automatically when you've seen enough content!

## 🛠️ How It Works

Camel Tutor uses a sophisticated three-step process:

1. **Keyword Generation**: When you enter a learning topic, our AI generates 10-15 relevant keywords that are essential for understanding that subject.

2. **Passive Tracking**: As you browse the web, the extension quietly scans page content for those keywords, counting how many times you encounter each one.

3. **Active Learning**: When you've seen a keyword enough times (default: 5), Camel Tutor generates a personalized quiz to test your understanding and reinforce the concepts.

## 🎯 Example Use Cases

**For Developers:**
- Track "React Hooks", "API Design", "Docker" while reading documentation
- Get quizzed on concepts as you encounter them in tutorials and Stack Overflow

**For Students:**
- Learn "Statistics", "European History", "Organic Chemistry" while researching
- Reinforce textbook concepts with real-world examples from the web

**For Professionals:**
- Master "Digital Marketing", "Project Management", "Data Analysis" during work
- Stay sharp on industry trends and best practices

**For Hobbyists:**
- Learn "Photography", "Cooking Techniques", "Guitar Theory" while exploring
- Turn casual browsing into structured learning

## 🔧 Configuration

### Quiz Settings We are Adding Soon
- **Hump Size**: Adjust difficulty from Small (easy) to Large (challenging)
- **Quiz Format**: Choose between multiple-choice and free-response
- **Trigger Threshold**: Modify how many keyword encounters trigger a quiz

### Data Management
- Clear all tracking data anytime
- Export quiz history
- Review performance analytics


## 🔒 Privacy & Data

- **All tracking happens locally** - keywords are only stored in your browser
- **Quiz data is saved locally** in the `quiz_data/` folder
- **OpenAI API** is only used for generating keywords and quiz questions
- **No personal browsing data** is sent to external servers

## 🆘 Support

Having issues? Email me at shashwat2152001@gmail.com

I would love to hear any thoughts!

**Common Issues:**
- Server not starting: Make sure Python 3.8+ is installed and your OpenAI API key is set
- Extension not tracking: Check that the backend server is running on `localhost:8000`
- No quizzes appearing: Try browsing more content related to your chosen topic

---

**Ready to learn smarter, not harder?** Install Camel today and turn your web browsing into a powerful learning tool! 🐪✨