// AgentMath.app - Quiz Milestone Celebration System
// Version 2.1 - HIGH CONTRAST FIX for readability

console.log('🎉 LOADING quiz_milestones.js - Version 2.1 with HIGH CONTRAST text fix!');

// Wait for DOM to be ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeMilestoneSystem);
} else {
    initializeMilestoneSystem();
}

function initializeMilestoneSystem() {
    console.log('✅ Milestone System Initialized - Version 2.1 HIGH CONTRAST');
    
    // Make checkQuizMilestones available globally
    window.checkQuizMilestones = checkQuizMilestones;
}

async function checkQuizMilestones(quizData) {
    console.log('🔍 Checking for milestones...', quizData);
    
    try {
        const response = await fetch('/api/check_milestones', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(quizData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('📊 Milestone check response:', data);
        
        if (data.milestone_earned) {
            console.log('🎉 MILESTONE EARNED!', data.milestone);
            showMilestonePopup(data.milestone);
        } else {
            console.log('No milestone earned this time');
        }
        
    } catch (error) {
        console.error('❌ Error checking milestones:', error);
    }
}

function showMilestonePopup(milestone) {
    console.log('🎨 Creating milestone popup with HIGH CONTRAST styling...');
    
    // Create overlay with dark background
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.85);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        animation: fadeIn 0.3s ease-out;
    `;
    
    // Create modal container
    const modal = document.createElement('div');
    modal.style.cssText = `
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 40px;
        max-width: 500px;
        width: 90%;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        text-align: center;
        position: relative;
        animation: slideUp 0.5s ease-out;
        color: #ffffff;
    `;
    
    // Badge emoji based on type
    const badgeEmojis = {
        'first_quiz': '🎯',
        'quiz_streak': '🔥',
        'perfect_score': '💯',
        'topic_master': '👑',
        'quick_learner': '⚡',
        'dedicated_student': '📚',
        'improvement': '📈'
    };
    
    const emoji = badgeEmojis[milestone.badge_type] || '🏆';
    
    // Create confetti effect
    createConfetti(overlay);
    
    // Modal content with explicit white text
    modal.innerHTML = `
        <div style="font-size: 80px; margin-bottom: 20px; animation: bounce 1s ease-in-out infinite;">
            ${emoji}
        </div>
        <h2 style="
            color: #ffffff;
            font-size: 32px;
            font-weight: bold;
            margin: 20px 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        ">
            ${milestone.badge_name}
        </h2>
        <p style="
            color: #ffffff;
            font-size: 18px;
            margin: 15px 0;
            line-height: 1.6;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
        ">
            ${milestone.description}
        </p>
        <div style="
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
        ">
            <div style="
                color: #ffffff;
                font-size: 16px;
                font-weight: 600;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
            ">
                Points Earned
            </div>
            <div style="
                color: #ffd700;
                font-size: 36px;
                font-weight: bold;
                margin-top: 5px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            ">
                +${milestone.points_awarded}
            </div>
        </div>
        <button onclick="this.closest('.milestone-overlay').remove()" style="
            background: rgba(255, 255, 255, 0.9);
            color: #667eea;
            border: none;
            padding: 12px 30px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 25px;
            cursor: pointer;
            margin-top: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        " 
        onmouseover="this.style.background='#ffffff'; this.style.transform='scale(1.05)';"
        onmouseout="this.style.background='rgba(255, 255, 255, 0.9)'; this.style.transform='scale(1)';">
            Awesome! ✨
        </button>
    `;
    
    overlay.className = 'milestone-overlay';
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    
    // Add animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes slideUp {
            from {
                transform: translateY(50px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
        @keyframes confettiFall {
            to {
                transform: translateY(100vh) rotate(360deg);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
    
    console.log('✅ Milestone popup displayed with HIGH CONTRAST text!');
}

function createConfetti(container) {
    const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#ff9ff3'];
    const confettiCount = 50;
    
    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.style.cssText = `
            position: fixed;
            width: 10px;
            height: 10px;
            background: ${colors[Math.floor(Math.random() * colors.length)]};
            top: -10px;
            left: ${Math.random() * 100}%;
            opacity: ${Math.random() * 0.7 + 0.3};
            animation: confettiFall ${Math.random() * 3 + 2}s linear forwards;
            animation-delay: ${Math.random() * 0.5}s;
            border-radius: ${Math.random() > 0.5 ? '50%' : '0'};
            z-index: 9999;
        `;
        container.appendChild(confetti);
        
        // Remove confetti after animation
        setTimeout(() => confetti.remove(), 5000);
    }
}

console.log('✅ quiz_milestones.js loaded successfully - Version 2.1 HIGH CONTRAST!');
