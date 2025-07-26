// quiz.js - Handles the multiple choice quiz popup window

let currentQuestion = null;
let selectedChoice = null;
let isAnswered = false;
let score = 0;
let totalQuestions = 0;
let currentQuestionIndex = 0;
let allQuestions = [];

document.addEventListener('DOMContentLoaded', async () => {
    const topicBadge = document.getElementById('topic-badge');
    const keywordName = document.getElementById('keyword-name');
    const questionText = document.getElementById('question-text');
    const choicesContainer = document.getElementById('choices-container');
    const feedbackSection = document.getElementById('feedback-section');
    const feedbackText = document.getElementById('feedback-text');
    const submitBtn = document.getElementById('submit-btn');
    const nextBtn = document.getElementById('next-btn');
    const closeBtn = document.getElementById('close-btn');
    const scoreSpan = document.getElementById('score');
    const totalSpan = document.getElementById('total');
    const scoreBadge = document.getElementById('score-badge');
    
    // Load quiz data
    const storage = await chrome.storage.local.get(['activeQuiz']);
    const quizData = storage.activeQuiz;
    
    if (!quizData || !quizData.questions || quizData.questions.length === 0) {
        questionText.textContent = 'Error loading quiz. Please try again.';
        submitBtn.style.display = 'none';
        return;
    }
    
    // Initialize quiz
    allQuestions = quizData.questions;
    totalQuestions = allQuestions.length;
    totalSpan.textContent = totalQuestions;
    
    // Display quiz information
    topicBadge.textContent = quizData.topic;
    keywordName.textContent = quizData.keyword || allQuestions[0].keyword;
    
    // Load first question
    loadQuestion(0);
    
    // Handle choice selection
    choicesContainer.addEventListener('click', (e) => {
        const choice = e.target.closest('.choice');
        if (!choice || isAnswered) return;
        
        // Remove previous selection
        document.querySelectorAll('.choice').forEach(c => c.classList.remove('selected'));
        
        // Add selection to clicked choice
        choice.classList.add('selected');
        selectedChoice = choice.dataset.choice;
        submitBtn.disabled = false;
    });
    
    // Handle submit button
    submitBtn.addEventListener('click', () => {
        if (!selectedChoice || isAnswered) return;
        
        checkAnswer();
    });
    
    // Handle next button
    nextBtn.addEventListener('click', () => {
        currentQuestionIndex++;
        if (currentQuestionIndex < totalQuestions) {
            loadQuestion(currentQuestionIndex);
        } else {
            // Quiz completed
            showFinalScore();
        }
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
        
        // Allow keyboard selection (A, B, C, D or 1, 2, 3, 4)
        if (!isAnswered) {
            if (e.key.toLowerCase() === 'a' || e.key === '1') selectChoiceByLetter('A');
            if (e.key.toLowerCase() === 'b' || e.key === '2') selectChoiceByLetter('B');
            if (e.key.toLowerCase() === 'c' || e.key === '3') selectChoiceByLetter('C');
            if (e.key.toLowerCase() === 'd' || e.key === '4') selectChoiceByLetter('D');
            
            // Submit on Enter
            if (e.key === 'Enter' && selectedChoice) {
                checkAnswer();
            }
        } else if (e.key === 'Enter' && nextBtn.style.display !== 'none') {
            // Go to next question on Enter
            nextBtn.click();
        }
    });
});

function loadQuestion(index) {
    currentQuestion = allQuestions[index];
    selectedChoice = null;
    isAnswered = false;
    
    // Reset UI
    const questionText = document.getElementById('question-text');
    const choicesContainer = document.getElementById('choices-container');
    const feedbackSection = document.getElementById('feedback-section');
    const submitBtn = document.getElementById('submit-btn');
    const nextBtn = document.getElementById('next-btn');
    const scoreBadge = document.getElementById('score-badge');
    
    questionText.textContent = currentQuestion.question;
    feedbackSection.style.display = 'none';
    submitBtn.style.display = 'block';
    submitBtn.disabled = true;
    nextBtn.style.display = 'none';
    
    // Show score after first question
    if (index > 0) {
        scoreBadge.style.display = 'block';
    }
    
    // Create choice elements
    choicesContainer.innerHTML = '';
    const choices = [
        { letter: 'A', text: currentQuestion.choice1 },
        { letter: 'B', text: currentQuestion.choice2 },
        { letter: 'C', text: currentQuestion.choice3 },
        { letter: 'D', text: currentQuestion.choice4 }
    ];
    
    choices.forEach(choice => {
        const choiceElement = document.createElement('button');
        choiceElement.className = 'choice';
        choiceElement.dataset.choice = choice.letter;
        choiceElement.innerHTML = `
            <span class="choice-label">${choice.letter}.</span>
            <span>${choice.text}</span>
        `;
        choicesContainer.appendChild(choiceElement);
    });
}

function selectChoiceByLetter(letter) {
    const choice = document.querySelector(`.choice[data-choice="${letter}"]`);
    if (choice) {
        choice.click();
    }
}

function checkAnswer() {
    isAnswered = true;
    const isCorrect = selectedChoice === currentQuestion.correct;
    
    // Update score
    if (isCorrect) {
        score++;
        document.getElementById('score').textContent = score;
    }
    
    // Disable all choices
    document.querySelectorAll('.choice').forEach(choice => {
        choice.classList.add('disabled');
        
        // Mark correct and incorrect choices
        if (choice.dataset.choice === currentQuestion.correct) {
            choice.classList.add('correct');
        } else if (choice.dataset.choice === selectedChoice) {
            choice.classList.add('incorrect');
        }
    });
    
    // Show feedback
    const feedbackSection = document.getElementById('feedback-section');
    const feedbackText = document.getElementById('feedback-text');
    const submitBtn = document.getElementById('submit-btn');
    const nextBtn = document.getElementById('next-btn');
    
    feedbackSection.style.display = 'block';
    feedbackSection.className = `feedback-section ${isCorrect ? 'correct' : 'incorrect'}`;
    
    if (isCorrect) {
        feedbackText.innerHTML = `
            <strong>✅ Correct!</strong><br>
            Great job! You clearly understand this concept.
        `;
    } else {
        const correctChoice = currentQuestion[`choice${currentQuestion.correct.charCodeAt(0) - 64}`];
        feedbackText.innerHTML = `
            <strong>❌ Not quite right.</strong><br>
            The correct answer is <strong>${currentQuestion.correct}. ${correctChoice}</strong><br>
            Take a moment to understand why this is the correct answer.
        `;
    }
    
    // Update buttons
    submitBtn.style.display = 'none';
    
    // Show next button if there are more questions
    if (currentQuestionIndex < totalQuestions - 1) {
        nextBtn.style.display = 'block';
    }
    
    // Log quiz progress
    logQuizProgress(isCorrect);
}

function showFinalScore() {
    const quizContainer = document.querySelector('.quiz-container');
    const percentage = Math.round((score / totalQuestions) * 100);
    
    let message = '';
    let emoji = '';
    
    if (percentage === 100) {
        message = 'Perfect score! You have mastered this topic!';
        emoji = '🎉';
    } else if (percentage >= 80) {
        message = 'Great job! You have a strong understanding.';
        emoji = '🌟';
    } else if (percentage >= 60) {
        message = 'Good effort! Keep practicing to improve.';
        emoji = '👍';
    } else {
        message = 'Keep learning! Review the material and try again.';
        emoji = '📚';
    }
    
    quizContainer.innerHTML = `
        <div style="text-align: center;">
            <h1 style="font-size: 48px; margin-bottom: 20px;">${emoji}</h1>
            <h2>Quiz Complete!</h2>
            <div style="font-size: 36px; color: #667eea; margin: 20px 0;">
                ${score}/${totalQuestions}
            </div>
            <p style="font-size: 18px; color: #666; margin-bottom: 30px;">
                ${message}
            </p>
            <button class="close-btn" onclick="window.close()" style="width: auto; padding: 12px 40px;">
                Close
            </button>
        </div>
    `;
}

// Log quiz progress
async function logQuizProgress(isCorrect) {
    const storage = await chrome.storage.local.get(['activeQuiz', 'quizHistory']);
    const quizData = storage.activeQuiz;
    const history = storage.quizHistory || [];
    
    history.push({
        topic: quizData.topic,
        keyword: quizData.keyword || currentQuestion.keyword,
        question: currentQuestion.question,
        selectedAnswer: selectedChoice,
        correctAnswer: currentQuestion.correct,
        isCorrect: isCorrect,
        completedAt: new Date().toISOString()
    });
    
    // Keep only the last 100 quiz attempts
    if (history.length > 100) {
        history.shift();
    }
    
    await chrome.storage.local.set({ quizHistory: history });
}