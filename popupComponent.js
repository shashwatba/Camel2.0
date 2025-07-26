// This function creates and displays a popup quiz modal using the given quiz data
function showQuizPopup(quizData) {
  // If the popup is already on the page, don't add another one
  if (document.getElementById("quiz-popup")) return;

  // Create a new <div> element to contain the modal
  const modal = document.createElement("div");
  modal.id = "quiz-popup";

  // Set the HTML for the modal popup
  modal.innerHTML = `
    <div style="
      position: fixed;
      top: 0; left: 0;
      width: 100%; height: 100%;
      background: rgba(0,0,0,0.6);               /* dark overlay background */
      z-index: 9999;
      display: flex;
      align-items: center;
      justify-content: center;">
      
      <div style="
        background: white;
        padding: 28px;
        border-radius: 14px;
        width: 95%;
        max-width: 600px;
        max-height: 80vh;
        overflow-y : auto;
        font-family: 'Segoe UI', sans-serif;
        box-shadow: 0 8px 30px rgba(0,0,0,0.3);">


        <!-- Question text -->
        <h3 style="margin-top: 0; font-size: 18px; line-height: 1.4;">${quizData.question}</h3>

        <!-- Dynamically generate multiple choice options -->
        ${quizData.options.map(option => `
          <label style="display: block; margin-bottom: 8px;">
            <input type="radio" name="quiz-option" value="${option}">
            ${option}
          </label>
        `).join("")}

        <!-- Submit button -->
        <button id="submit-answer" style="
          margin-top: 10px;
          padding: 8px 12px;
          background:rgb(102, 182, 106);
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;">Submit</button>

        <!-- Feedback will be displayed here -->
        <div id="feedback" style="
        margin-top: 20px;
        font-size: 15px;
        line-height: 1.5;
        font-weight: 500;
        white-space: pre-wrap;
        padding: 10px 0;"></div>
      </div>
    </div>
  `;

  // Add the modal to the page
  document.body.appendChild(modal);

  // Add click listener to the submit button
  document.getElementById("submit-answer").addEventListener("click", async () => {
    // Find the selected answer from the radio buttons
    const selected = document.querySelector('input[name="quiz-option"]:checked');
    const feedbackEl = document.getElementById("feedback");

    // If nothing is selected, show an error message
    if (!selected) {
      feedbackEl.textContent = "Please select an answer.";
      feedbackEl.style.color = "red";
      return;
    }

    const userAnswer = selected.value; // Store the selected answer

    try {
      // Send the selected answer to the backend
      const response = await fetch("http://localhost:3000/submit-answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          questionId: quizData.id,    // Unique ID for this question
          answer: userAnswer          // User's selected answer
        })
      });
      
      const data = await response.json(); // Get the response from the backend


      // Show feedback text returned by backend (e.g., "Correct!" or explanation)
      feedbackEl.textContent = data.feedback;
      feedbackEl.style.color = "black";

      // Auto-close the popup after 25 seconds
      setTimeout(() => {
        document.getElementById("quiz-popup")?.remove();
      }, 25000);

    } catch (err) {
      // If the request fails, show an error message
      feedbackEl.textContent = "Error sending answer. Please try again.";
      feedbackEl.style.color = "red";
      console.error("Submit error:", err);
    }
  });
}
