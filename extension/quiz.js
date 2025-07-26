// quiz.js - Handles the quiz popup window

document.addEventListener('DOMContentLoaded', async () => {
    const topicBadge = document.getElementById('topic-badge');
    const keywordName = document.getElementById('keyword-name');
    const questionText = document.getElementById('question-text');
    const answerSection = document.getElementById('answer-section');
    const answerText = document.getElementById('answer-text');
    const showAnswerBtn = document.getElementById('show-answer-btn');
    const closeBtn = document.getElementById('close-btn');
    const successMessage = document.querySelector('.success-message');
    
    // Load quiz data
    const storage = await chrome.storage.local.get(['activeQuiz']);
    const quizData = storage.activeQuiz;
    
    if (!quizData || !quizData.questions || quizData.questions.length === 0) {
        questionText.textContent = 'Error loading quiz. Please try again.';
        showAnswerBtn.style.display = 'none';
        return;
    }
    
    // Display quiz information
    const question = quizData.questions[0]; // Use the first question
    topicBadge.textContent = quizData.topic;
    keywordName.textContent = quizData.keyword || question.keyword;
    questionText.textContent = question.question;
    answerText.textContent = question.answer;
    
    // Handle show answer button
    showAnswerBtn.addEventListener('click', () => {
        answerSection.style.display = 'block';
        showAnswerBtn.style.display = 'none';
        successMessage.style.display = 'block';
        
        // Log that the user answered the quiz
        logQuizCompletion(quizData.topic, quizData.keyword);
    });
    
    // Handle close button
    closeBtn.addEventListener('click', () => {
        window.close();
    });
    
    // Allow closing with Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            window.close();
        }
    });
});

// Log quiz completion
async function logQuizCompletion(topic, keyword) {
    const storage = await chrome.storage.local.get(['quizHistory']);
    const history = storage.quizHistory || [];
    
    history.push({
        topic,
        keyword,
        completedAt: new Date().toISOString()
    });
    
    // Keep only the last 100 quiz completions
    if (history.length > 100) {
        history.shift();
    }
    
    await chrome.storage.local.set({ quizHistory: history });
}