// background.js - Service worker for the extension

const API_BASE_URL = 'http://localhost:8000';

// Keep track of active quiz popups to prevent duplicates per topic-keyword
const activeQuizzes = new Set();

// Listen for messages from popup and content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'startTracking') {
    console.log('Started tracking:', request.topic);
  } else if (request.action === 'keywordFound') {
    const tabId = sender?.tab?.id;
    const inc = (typeof request.count === 'number' && Number.isFinite(request.count)) ? request.count : 1;
    handleKeywordFound(request.topic, request.keyword, tabId, inc);
  } else if (request.action === 'checkTracking') {
    checkTrackingStatus().then(sendResponse);
    return true; // respond asynchronously
  }
});

/**
 * Handle when a keyword is found on a page.
 */
async function handleKeywordFound(topic, keyword, tabId, inc = 1) {
  const storage = await chrome.storage.local.get(['learningTopics']);
  const topics = storage.learningTopics || {};

  if (!topics[topic]) return;

  // Increment the count for this keyword by the number of matches on the page
  const prev = topics[topic].keywordCounts[keyword] || 0;
  topics[topic].keywordCounts[keyword] = prev + inc;

  const count = topics[topic].keywordCounts[keyword];
  const threshold = topics[topic].threshold || 5;

  // Persist updated counts
  await chrome.storage.local.set({ learningTopics: topics });

  // If threshold reached (on multiples) and no active quiz for this keyword, generate quiz
  const quizKey = `${topic}-${keyword}`;
  if (count >= threshold && count % threshold === 0 && !activeQuizzes.has(quizKey)) {
    activeQuizzes.add(quizKey);
    await generateAndShowQuiz(topic, keyword, tabId);
  }
}

/**
 * Generate quiz and show it to the user.
 * Resets the keyword counter AFTER quiz data is stored to preserve difficulty logic.
 */
async function generateAndShowQuiz(topic, keyword, tabId) {
  try {
    // Determine difficulty using the pre‑reset count
    const storage = await chrome.storage.local.get(['learningTopics']);
    const topics = storage.learningTopics || {};
    const count = topics[topic]?.keywordCounts?.[keyword] || 0;

    let difficulty = 'medium';
    if (count >= 15) {
      difficulty = 'big';      // hard
    } else if (count <= 5) {
      difficulty = 'small';    // easy
    }

    // Call the FastAPI backend to generate a quiz
    const response = await fetch(`${API_BASE_URL}/generate-quiz`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic,
        keywords: [keyword],
        difficulty
      })
    });

    if (!response.ok) throw new Error('Failed to generate quiz');

    const quizData = await response.json();

    // Store quiz data so quiz.html can render it
    await chrome.storage.local.set({
      activeQuiz: {
        ...quizData,
        topic,
        keyword,
        tabId
      }
    });

    // 🔄 Reset this keyword's count now that a quiz was generated
    if (topics[topic]?.keywordCounts) {
      topics[topic].keywordCounts[keyword] = 0;
      await chrome.storage.local.set({ learningTopics: topics });
    }

    // Open the quiz window
    chrome.windows.create(
      {
        url: chrome.runtime.getURL('quiz.html'),
        type: 'popup',
        width: 500,
        height: 600,
        focused: true
      },
      (window) => {
        // Remove from active set when window closes
        chrome.windows.onRemoved.addListener(function listener(windowId) {
          if (windowId === window.id) {
            activeQuizzes.delete(`${topic}-${keyword}`);
            chrome.windows.onRemoved.removeListener(listener);
          }
        });
      }
    );
  } catch (error) {
    console.error('Error generating quiz:', error);
    activeQuizzes.delete(`${topic}-${keyword}`);
  }
}

/**
 * Check if we're actively tracking any topics.
 */
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
