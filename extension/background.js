// background.js - Service worker for the extension

const API_BASE_URL = 'http://localhost:8000';

// Keep track of active quiz popups to prevent duplicates
const activeQuizzes = new Set();

// Listen for messages from popup and content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'startTracking') {
        console.log('Started tracking:', request.topic);
    } else if (request.action === 'keywordFound') {
        handleKeywordFound(request.topic, request.keyword, sender.tab.id);
    } else if (request.action === 'checkTracking') {
        checkTrackingStatus().then(sendResponse);
        return true; // Will respond asynchronously
    }
});

// Handle when a keyword is found on a page
async function handleKeywordFound(topic, keyword, tabId) {
    const storage = await chrome.storage.local.get(['learningTopics']);
    const topics = storage.learningTopics || {};
    
    if (!topics[topic]) return;
    
    // Increment the count for this keyword
    topics[topic].keywordCounts[keyword] = (topics[topic].keywordCounts[keyword] || 0) + 1;
    
    // Check if we've reached the threshold
    const count = topics[topic].keywordCounts[keyword];
    const threshold = topics[topic].threshold || 5;
    
    // Save updated counts
    await chrome.storage.local.set({ learningTopics: topics });
    
    // If threshold reached and no active quiz for this keyword
    const quizKey = `${topic}-${keyword}`;
    if (count >= threshold && count % threshold === 0 && !activeQuizzes.has(quizKey)) {
        activeQuizzes.add(quizKey);
        await generateAndShowQuiz(topic, keyword, tabId);
    }
}

// Generate quiz and show it to the user
async function generateAndShowQuiz(topic, keyword, tabId) {
    try {
        // Call the FastAPI backend to generate a quiz
        const response = await fetch(`${API_BASE_URL}/generate-quiz`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                topic: topic,
                keywords: [keyword]
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate quiz');
        }
        
        const quizData = await response.json();
        
        // Store quiz data temporarily
        await chrome.storage.local.set({
            activeQuiz: {
                ...quizData,
                keyword: keyword,
                tabId: tabId
            }
        });
        
        // Create a new window for the quiz
        chrome.windows.create({
            url: chrome.runtime.getURL('quiz.html'),
            type: 'popup',
            width: 500,
            height: 600,
            focused: true
        }, (window) => {
            // Remove from active quizzes when window closes
            chrome.windows.onRemoved.addListener(function listener(windowId) {
                if (windowId === window.id) {
                    activeQuizzes.delete(`${topic}-${keyword}`);
                    chrome.windows.onRemoved.removeListener(listener);
                }
            });
        });
        
    } catch (error) {
        console.error('Error generating quiz:', error);
        activeQuizzes.delete(`${topic}-${keyword}`);
    }
}

// Check if we're actively tracking any topics
async function checkTrackingStatus() {
    const storage = await chrome.storage.local.get(['learningTopics']);
    const topics = storage.learningTopics || {};
    
    const activeTopics = Object.entries(topics).map(([name, data]) => ({
        name,
        keywords: data.keywords,
        keywordCounts: data.keywordCounts
    }));
    
    return {
        isTracking: activeTopics.length > 0,
        topics: activeTopics
    };
}

// Initialize on install
chrome.runtime.onInstalled.addListener(() => {
    console.log('Learning Tracker Extension installed');
});