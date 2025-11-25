/**
 * WHO AM I? - Mystery Image Reveal System
 * 
 * Features:
 * - 5×5 grid (25 tiles) that gradually reveals an image
 * - Students answer questions correctly to reveal tiles
 * - Guessing system with bonus points
 * - Progress tracking and animations
 * 
 * Updated: November 2025
 * - Changed from 4×4 to 5×5 grid
 * - Removed tile gaps for more obscured image
 * - Fixed "Make a Guess" button functionality
 * - FIXED: loadNextImage() now uses correct HTML structure
 * - FIXED: Hint now displays properly at top of image
 */

// ========================================
// STATE MANAGEMENT
// ========================================

let whoAmIState = {
    quizAttemptId: null,
    sessionId: null,
    imageUrl: null,
    hint: null,
    totalTiles: 25,          // 5×5 grid
    revealedTiles: new Set(),
    guessedNames: new Set(),
    correctGuess: false,
    bonusPoints: 0
};

// ========================================
// INITIALIZATION
// ========================================

/**
 * Initialize Who Am I for a new quiz attempt
 * @param {string} topic - The quiz topic (e.g., 'descriptive_statistics')
 * @param {string} difficulty - The difficulty level (e.g., 'beginner')
 * @param {number} quizAttemptId - The numeric quiz attempt ID
 */
async function initializeWhoAmI(topic, difficulty, quizAttemptId) {
    console.log('🎯 Initializing Who Am I for quiz attempt:', quizAttemptId);
    console.log('   Topic:', topic, '| Difficulty:', difficulty);
    
    // Reset state
    whoAmIState = {
        quizAttemptId: quizAttemptId,
        sessionId: null,
        imageUrl: null,
        hint: null,
        totalTiles: 25,
        revealedTiles: new Set(),
        guessedNames: new Set(),
        correctGuess: false,
        bonusPoints: 0
    };
    
    try {
        // Start a new Who Am I session via the existing API
        const response = await fetch('/api/who-am-i/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topic: topic,
                difficulty: difficulty,
                quiz_attempt_id: quizAttemptId
            })
        });
        
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            console.warn('⚠️ No Who Am I image available:', data.error);
            return;
        }
        
        // Store session data
        whoAmIState.sessionId = data.session_id;
        whoAmIState.imageUrl = data.image_url;
        whoAmIState.hint = data.hint;
        
        console.log('✅ Who Am I session started:', data.session_id);
        console.log('💡 Hint:', whoAmIState.hint || 'No hint available');
        
        // Create the reveal grid
        createRevealGrid();
        
        // Show the container
        const container = document.getElementById('who-am-i-container');
        if (container) {
            container.style.display = 'block';
        }
        
    } catch (error) {
        console.error('❌ Error initializing Who Am I:', error);
    }
}

/**
 * Create the 5×5 reveal grid with hint display
 */
function createRevealGrid() {
    const container = document.getElementById('who-am-i-container');
    if (!container) return;
    
    const imageUrl = whoAmIState.imageUrl;
    if (!imageUrl) {
        console.error('❌ No image URL in state');
        return;
    }
    
    // Build hint HTML if available (trim whitespace from hint)
    console.log('🔍 Creating grid - hint check:');
    console.log('  - Raw hint:', whoAmIState.hint);
    console.log('  - Hint type:', typeof whoAmIState.hint);
    
    const trimmedHint = whoAmIState.hint ? whoAmIState.hint.trim() : '';
    console.log('  - Trimmed hint:', trimmedHint);
    console.log('  - Trimmed length:', trimmedHint.length);
    console.log('  - Will create hint HTML:', !!trimmedHint);
    
    const hintHTML = trimmedHint ? `
        <div class="who-am-i-hint">
            💡 <strong>Hint:</strong> ${trimmedHint}
        </div>
    ` : '';
    
    console.log('  - Hint HTML length:', hintHTML.length);
    if (hintHTML.length > 0) {
        console.log('  - Hint HTML preview:', hintHTML.substring(0, 100));
    }
    
    // Build the grid HTML
    container.innerHTML = `
        <div class="who-am-i-wrapper">
            <div class="who-am-i-header">
                <h3>🎭 Who Am I?</h3>
                <p>Answer correctly to reveal the mystery mathematician!</p>
            </div>
            
            ${hintHTML}
            
            <div class="reveal-grid">
                <!-- Background Image (hidden behind tiles) -->
                <div class="reveal-grid-bg" style="background-image: url('${imageUrl}');"></div>
                
                <!-- Tile Overlay (5×5 grid) -->
                <div class="reveal-grid-overlay">
                    ${generateTileHTML()}
                </div>
            </div>
            
            <div class="who-am-i-progress">
                <p>Progress: <span id="tiles-revealed">0</span>/${whoAmIState.totalTiles} tiles revealed</p>
                <div class="progress-bar">
                    <div class="progress-fill" id="reveal-progress-bar" style="width: 0%;"></div>
                </div>
            </div>
            
            <button class="guess-button" onclick="openGuessModal()">
                🤔 Make a Guess
            </button>
        </div>
    `;
    
    console.log('✅ Grid created with hint:', whoAmIState.hint ? 'Yes' : 'No');
    
    // Check if hint element actually made it into the DOM
    setTimeout(() => {
        const hintElement = document.querySelector('.who-am-i-hint');
        console.log('🔍 DOM check - hint element exists:', !!hintElement);
        if (hintElement) {
            console.log('  - Content:', hintElement.textContent);
            console.log('  - Visible:', hintElement.offsetHeight > 0);
        }
    }, 50);
}

/**
 * Generate HTML for all 25 tiles
 */
function generateTileHTML() {
    let html = '';
    for (let i = 1; i <= whoAmIState.totalTiles; i++) {
        html += `<div class="reveal-tile" data-tile="${i}"><span>${i}</span></div>`;
    }
    return html;
}

// ========================================
// TILE REVEAL LOGIC
// ========================================

/**
 * Called when student answers a question correctly
 */
function onCorrectAnswer() {
    if (!whoAmIState.imageUrl || whoAmIState.correctGuess) {
        return; // No image or already guessed correctly
    }
    
    // Reveal a random unrevealed tile
    revealRandomTile();
}

/**
 * Reveal one random unrevealed tile
 */
function revealRandomTile() {
    // Get all unrevealed tiles
    const unrevealedTiles = [];
    for (let i = 1; i <= whoAmIState.totalTiles; i++) {
        if (!whoAmIState.revealedTiles.has(i)) {
            unrevealedTiles.push(i);
        }
    }
    
    if (unrevealedTiles.length === 0) {
        console.log('🎉 All tiles revealed!');
        return;
    }
    
    // Pick a random tile
    const randomIndex = Math.floor(Math.random() * unrevealedTiles.length);
    const tileNumber = unrevealedTiles[randomIndex];
    
    // Reveal it
    revealTile(tileNumber);
}

/**
 * Reveal a specific tile
 */
function revealTile(tileNumber) {
    if (whoAmIState.revealedTiles.has(tileNumber)) {
        return; // Already revealed
    }
    
    // Mark as revealed
    whoAmIState.revealedTiles.add(tileNumber);
    
    // Update the tile visually
    const tile = document.querySelector(`[data-tile="${tileNumber}"]`);
    if (tile) {
        tile.classList.add('revealed');
    }
    
    // Update progress
    updateProgress();
    
    console.log(`✅ Tile ${tileNumber} revealed (${whoAmIState.revealedTiles.size}/${whoAmIState.totalTiles})`);
}

/**
 * Update progress display
 */
function updateProgress() {
    const revealedCount = whoAmIState.revealedTiles.size;
    const percentage = (revealedCount / whoAmIState.totalTiles) * 100;
    
    // Update text
    const counterElement = document.getElementById('tiles-revealed');
    if (counterElement) {
        counterElement.textContent = revealedCount;
    }
    
    // Update progress bar
    const progressBar = document.getElementById('reveal-progress-bar');
    if (progressBar) {
        progressBar.style.width = `${percentage}%`;
    }
}

// ========================================
// GUESSING SYSTEM
// ========================================

/**
 * Open the guess modal
 */
function openGuessModal() {
    if (!whoAmIState.imageUrl) {
        alert('No mystery image loaded!');
        return;
    }
    
    if (whoAmIState.correctGuess) {
        alert('You already guessed correctly! 🎉');
        return;
    }
    
    // Create modal HTML
    const modalHTML = `
        <div class="guess-modal" id="guess-modal">
            <div class="guess-modal-content">
                <h3>🤔 Who Am I?</h3>
                <p>Think you know? Make your guess!</p>
                
                <input 
                    type="text" 
                    id="guess-input" 
                    placeholder="Type your answer..."
                    autocomplete="off"
                >
                
                <div class="guess-modal-buttons">
                    <button class="guess-modal-submit" onclick="submitGuess()">
                        Submit Guess
                    </button>
                    <button class="guess-modal-cancel" onclick="closeGuessModal()">
                        Cancel
                    </button>
                </div>
                
                <div id="guess-feedback-area"></div>
            </div>
        </div>
    `;
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Focus input
    const input = document.getElementById('guess-input');
    if (input) {
        input.focus();
        
        // Allow Enter key to submit
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                submitGuess();
            }
        });
    }
}

/**
 * Close the guess modal
 */
function closeGuessModal() {
    const modal = document.getElementById('guess-modal');
    if (modal) {
        modal.remove();
    }
}

/**
 * Submit a guess
 */
async function submitGuess() {
    const input = document.getElementById('guess-input');
    if (!input) return;
    
    const guess = input.value.trim();
    
    if (!guess) {
        showGuessFeedback('Please enter a guess!', 'incorrect');
        return;
    }
    
    // Check if already guessed this name
    const normalizedGuess = guess.toLowerCase();
    if (whoAmIState.guessedNames.has(normalizedGuess)) {
        showGuessFeedback('You already tried that name!', 'already-guessed');
        return;
    }
    
    // Add to guessed names
    whoAmIState.guessedNames.add(normalizedGuess);
    
    try {
        // Send guess to server
        const response = await fetch('/api/who-am-i/guess', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: whoAmIState.sessionId,
                guess: guess
            })
        });
        
        const data = await response.json();
        
        if (data.correct) {
            // Correct guess!
            whoAmIState.correctGuess = true;
            whoAmIState.bonusPoints = (whoAmIState.bonusPoints || 0) + (data.bonus_points || 0);  // Accumulate bonus points
            
            const answerName = data.answer || guess;
            
            // Check if there's another image to solve
            if (data.next_session) {
                showGuessFeedback(
                    `🎉 Correct! It's ${answerName}! +${data.bonus_points} bonus points! 
                    <br><strong>🎯 Loading next mystery image...</strong>`, 
                    'correct'
                );
                
                // Reveal all tiles of current image
                revealAllTiles();
                
                // Load next image FIRST (while modal is still open)
                setTimeout(() => {
                    loadNextImage(data.next_session);
                    // THEN close modal after next image is loaded
                    setTimeout(() => {
                        closeGuessModal();
                    }, 500);
                }, 2000);
                
            } else {
                // No more images available
                showGuessFeedback(
                    `🎉 Correct! It's ${answerName}! You earned +${data.bonus_points} bonus points!
                    <br><strong>✨ Amazing! You've solved all available images!</strong>`, 
                    'correct'
                );
                
                // Reveal all remaining tiles
                revealAllTiles();
                
                // Close modal after 3 seconds
                setTimeout(() => {
                    closeGuessModal();
                }, 3000);
            }
            
        } else {
            // Incorrect guess
            const remaining = data.guesses_remaining || 0;
            showGuessFeedback(
                `❌ Not quite! ${remaining} ${remaining === 1 ? 'guess' : 'guesses'} remaining`, 
                'incorrect'
            );
            
            // Clear input for next try
            if (input) {
                input.value = '';
                input.focus();
            }
        }
        
    } catch (error) {
        console.error('❌ Error submitting guess:', error);
        showGuessFeedback('Error submitting guess. Please try again.', 'incorrect');
    }
}

/**
 * Show feedback in the modal
 */
function showGuessFeedback(message, type) {
    const feedbackArea = document.getElementById('guess-feedback-area');
    if (!feedbackArea) return;
    
    feedbackArea.innerHTML = `
        <div class="guess-feedback ${type}">
            ${message}
        </div>
    `;
}

/**
 * Reveal all tiles (when guessed correctly)
 */
function revealAllTiles() {
    for (let i = 1; i <= whoAmIState.totalTiles; i++) {
        revealTile(i);
    }
}

// ========================================
// BONUS POINTS
// ========================================

/**
 * Get the bonus points earned (for results screen)
 */
function getWhoAmIBonusPoints() {
    return whoAmIState.bonusPoints;
}

// ========================================
// UTILITY FUNCTIONS
// ========================================

/**
 * Reset state for a new quiz
 */
function resetWhoAmI() {
    whoAmIState = {
        quizAttemptId: null,
        sessionId: null,
        imageUrl: null,
        hint: null,
        totalTiles: 25,
        revealedTiles: new Set(),
        guessedNames: new Set(),
        correctGuess: false,
        bonusPoints: 0
    };
    
    const container = document.getElementById('who-am-i-container');
    if (container) {
        container.style.display = 'none';
        container.innerHTML = '';
    }
}

// ========================================
// AUTOMATIC NEXT IMAGE LOADING - FIXED!
// ========================================

/**
 * Load the next mystery image automatically after solving one
 * FIXED: Now properly recreates the reveal grid structure WITH HINT
 */
function loadNextImage(nextSessionData) {
    console.log('🔄 Loading next mystery image...');
    console.log('📦 Next session data:', nextSessionData);
    
    // Update state with new session data
    whoAmIState.sessionId = nextSessionData.session_id;
    whoAmIState.imageUrl = nextSessionData.image_url;
    whoAmIState.hint = nextSessionData.hint || '';
    whoAmIState.revealedTiles = new Set();  // Clear revealed tiles
    whoAmIState.correctGuess = false;
    whoAmIState.guessedNames.clear();
    
    console.log('✅ State updated:', {
        sessionId: whoAmIState.sessionId,
        imageUrl: whoAmIState.imageUrl,
        hint: whoAmIState.hint
    });
    
    // Find container
    const container = document.getElementById('who-am-i-container');
    if (!container) {
        console.error('❌ Could not find who-am-i-container!');
        return;
    }
    
    // Make sure container is visible
    container.style.display = 'block';
    
    console.log('🎨 Recreating entire grid structure with hint...');
    
    // FIXED: Recreate the entire grid structure using the same method as initial creation
    // This now includes the hint display!
    createRevealGrid();
    
    console.log('✅ Grid structure recreated with 25 unrevealed tiles and hint');
    
    // Show notification that new image loaded
    const notification = document.createElement('div');
    notification.className = 'who-am-i-notification';
    notification.innerHTML = '🎯 <strong>New Mystery Image!</strong> Keep answering to reveal it!';
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 30px;
        border-radius: 50px;
        font-size: 16px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideDown 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    console.log('✅ Notification shown');
    
    // Remove notification after 2.5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideUp 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 2500);
    
    console.log('✅ Next image loaded successfully!');
}

// ========================================
// EXPORTS (for use in student_app.html)
// ========================================

console.log('✅ Who Am I system loaded (5×5 grid, no gaps, with hints)');
