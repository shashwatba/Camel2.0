// content.js - Runs on every webpage to track keywords

let isTracking = false;
let trackingData = {};

// Initialize tracking when the page loads
initializeTracking();

async function initializeTracking() {
    // Check if we're tracking any topics
    const response = await chrome.runtime.sendMessage({ action: 'checkTracking' });
    
    if (response && response.isTracking) {
        isTracking = true;
        trackingData = response.topics;
        
        console.log('Tracking initialized with topics:', trackingData);
        
        // Start scanning the page
        scanPageForKeywords();
        
        // Set up mutation observer to track dynamic content
        observePageChanges();
    }
}

// Scan the page for keywords
function scanPageForKeywords() {
    if (!isTracking) return;
    
    // Get all text content from the page
    const textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th, span, div, article, section');
    
    textElements.forEach(element => {
        const text = element.textContent || '';
        checkTextForKeywords(text);
    });
}

// Check text for tracked keywords
function checkTextForKeywords(text) {
    if (!text || text.length < 3) return;
    
    const lowerText = text.toLowerCase();
    
    // Fix: trackingData is an array, and each item has 'name' property
    trackingData.forEach(topicData => {
        topicData.keywords.forEach(keyword => {
            // Create a regex for whole word matching
            const keywordLower = keyword.toLowerCase();
            const regex = new RegExp(`\\b${escapeRegex(keywordLower)}\\b`, 'gi');
            
            const matches = lowerText.match(regex);
            if (matches && matches.length > 0) {
                console.log(`Found keyword "${keyword}" ${matches.length} times in topic "${topicData.name}"`);
                
                // Get quiz format from storage
                chrome.storage.local.get(['quizFormat'], (result) => {
                    const selectedFormat = result.quizFormat || 'multiple-choice';
                    
                    // Notify background script about keyword found
                    chrome.runtime.sendMessage({
                        action: 'keywordFound',
                        topic: topicData.name, // Now this will work correctly
                        keyword: keyword,
                        count: matches.length,
                        format: selectedFormat
                    });
                });
            }
        });
    });
}

// Escape special regex characters
function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Observe page changes for dynamic content
function observePageChanges() {
    if (!isTracking) return;
    
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === Node.TEXT_NODE) {
                        checkTextForKeywords(node.textContent);
                    } else if (node.nodeType === Node.ELEMENT_NODE) {
                        const textElements = node.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th, span, div');
                        textElements.forEach(element => {
                            checkTextForKeywords(element.textContent);
                        });
                    }
                });
            }
        });
    });
    
    // Start observing the document body for changes
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'updateTracking') {
        // Re-initialize tracking with new data
        initializeTracking();
    }
});

// Re-check tracking status when the page becomes visible
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        initializeTracking();
    }
});