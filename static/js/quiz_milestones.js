/**
 * Math Master - Quiz Milestone Celebration System
 * Driver's Education Theme
 * 
 * Automatically celebrates achievements during quizzes:
 * - 10 correct in a row (streak milestone)
 * - 20 total correct answers (total milestone)
 * 
 * Themes by difficulty:
 * - Beginner: Learner stage
 * - Intermediate: Driving test stage
 * - Advanced: Qualified driver stage
 */

class QuizMilestoneSystem {
    constructor() {
        this.milestones = {
            beginner: {
                streak10: {
                    title: "🚗 Got Your Learner's Permit!",
                    subtitle: "10 correct answers in a row!",
                    message: "You're ready to hit the road with a supervisor!",
                    icon: "🎓",
                    color: "#10b981",
                    graphic: "learner"
                },
                total20: {
                    title: "📖 Passed Your Theory Test!",
                    subtitle: "20 total correct answers!",
                    message: "You know the rules of the road!",
                    icon: "📚",
                    color: "#3b82f6",
                    graphic: "theory"
                }
            },
            intermediate: {
                streak10: {
                    title: "📝 Applied for Your Driving Test!",
                    subtitle: "10 correct answers in a row!",
                    message: "Your skills are getting sharper!",
                    icon: "✍️",
                    color: "#f59e0b",
                    graphic: "application"
                },
                total20: {
                    title: "🎉 Passed Your Driving Test!",
                    subtitle: "20 total correct answers!",
                    message: "You're a licensed driver now!",
                    icon: "🚙",
                    color: "#8b5cf6",
                    graphic: "license"
                }
            },
            advanced: {
                streak10: {
                    title: "🔰 Finished Year 1 of Novice Period!",
                    subtitle: "10 correct answers in a row!",
                    message: "One more year to go - stay safe!",
                    icon: "⭐",
                    color: "#ec4899",
                    graphic: "novice"
                },
                total20: {
                    title: "🏆 Fully Qualified Driver!",
                    subtitle: "20 total correct answers!",
                    message: "Congratulations - Drive Safe!",
                    icon: "👑",
                    color: "#ef4444",
                    graphic: "qualified"
                }
            }
        };

        this.currentStreak = 0;
        this.totalCorrect = 0;
        this.achievedMilestones = new Set();
        this.difficulty = 'beginner'; // Will be set from quiz
        this.initialized = false;
    }
    
    // Initialize DOM elements (called lazily when needed)
    ensureInitialized() {
        if (this.initialized) return;
        if (!document.body) return; // Body not ready yet
        
        this.initializeStyles();
        this.createMilestoneContainer();
        this.initialized = true;
    }

    setDifficulty(difficulty) {
        this.ensureInitialized();
        this.difficulty = difficulty.toLowerCase();
    }

    reset() {
        this.currentStreak = 0;
        this.totalCorrect = 0;
        this.achievedMilestones.clear();
    }

    recordAnswer(isCorrect) {
        if (isCorrect) {
            this.currentStreak++;
            this.totalCorrect++;
            this.checkMilestones();
        } else {
            this.currentStreak = 0;
        }
    }

    checkMilestones() {
        const milestones = this.milestones[this.difficulty] || this.milestones.beginner;

        // Check streak milestone (10 in a row)
        if (this.currentStreak === 10 && !this.achievedMilestones.has('streak10')) {
            this.achievedMilestones.add('streak10');
            this.showCelebration(milestones.streak10);
        }

        // Check total milestone (20 total)
        if (this.totalCorrect === 20 && !this.achievedMilestones.has('total20')) {
            this.achievedMilestones.add('total20');
            this.showCelebration(milestones.total20);
        }
    }

    showCelebration(milestone) {
        this.ensureInitialized();
        
        // Create confetti effect
        this.createConfetti();

        // Play celebration sound (optional - silent fail if not available)
        this.playSound();

        // Show milestone popup
        this.displayMilestonePopup(milestone);
    }

    displayMilestonePopup(milestone) {
        const container = document.getElementById('milestone-container');
        
        const popup = document.createElement('div');
        popup.className = 'milestone-popup';
        popup.innerHTML = `
            <div class="milestone-content" style="border-left: 6px solid ${milestone.color};">
                <div class="milestone-graphic">
                    ${this.getGraphicHTML(milestone.graphic)}
                </div>
                <div class="milestone-header">
                    <div class="milestone-icon" style="background: ${milestone.color};">
                        ${milestone.icon}
                    </div>
                    <h2 class="milestone-title">${milestone.title}</h2>
                </div>
                <div class="milestone-subtitle">${milestone.subtitle}</div>
                <p class="milestone-message">${milestone.message}</p>
                <button class="milestone-close" onclick="milestoneSystem.closePopup(this)">
                    Continue Learning! 🚀
                </button>
            </div>
            <div class="milestone-overlay" onclick="milestoneSystem.closePopup(this)"></div>
        `;

        container.appendChild(popup);

        // Trigger animation
        setTimeout(() => {
            popup.classList.add('active');
        }, 10);

        // Auto-close after 8 seconds
        setTimeout(() => {
            this.closePopup(popup.querySelector('.milestone-close'));
        }, 8000);
    }

    closePopup(element) {
        const popup = element.closest('.milestone-popup');
        if (popup) {
            popup.classList.remove('active');
            setTimeout(() => {
                popup.remove();
            }, 300);
        }
    }

    getGraphicHTML(graphic) {
        const graphics = {
            learner: `
                <svg viewBox="0 0 200 200" class="milestone-svg">
                    <!-- Learner's Permit Book -->
                    <rect x="50" y="40" width="100" height="120" rx="5" fill="#3b82f6"/>
                    <rect x="55" y="45" width="90" height="110" rx="3" fill="#60a5fa"/>
                    <circle cx="100" cy="80" r="20" fill="#fff"/>
                    <text x="100" y="90" font-size="24" fill="#3b82f6" text-anchor="middle" font-weight="bold">L</text>
                    <rect x="70" y="110" width="60" height="4" fill="#fff" opacity="0.7"/>
                    <rect x="70" y="120" width="60" height="4" fill="#fff" opacity="0.7"/>
                    <rect x="70" y="130" width="40" height="4" fill="#fff" opacity="0.7"/>
                    <!-- Sparkles -->
                    <text x="40" y="40" font-size="20">✨</text>
                    <text x="155" y="50" font-size="16">⭐</text>
                    <text x="160" y="150" font-size="18">🎓</text>
                </svg>
            `,
            theory: `
                <svg viewBox="0 0 200 200" class="milestone-svg">
                    <!-- Theory Test Paper -->
                    <rect x="40" y="30" width="120" height="140" rx="5" fill="#fff" stroke="#3b82f6" stroke-width="3"/>
                    <circle cx="150" cy="50" r="25" fill="#10b981"/>
                    <path d="M 140 50 L 148 58 L 162 42" stroke="#fff" stroke-width="4" fill="none" stroke-linecap="round"/>
                    <!-- Test lines -->
                    <rect x="55" y="60" width="70" height="6" fill="#e5e7eb" rx="2"/>
                    <rect x="55" y="75" width="70" height="6" fill="#e5e7eb" rx="2"/>
                    <rect x="55" y="90" width="50" height="6" fill="#e5e7eb" rx="2"/>
                    <circle cx="60" cy="110" r="4" fill="#10b981"/>
                    <circle cx="60" cy="125" r="4" fill="#10b981"/>
                    <circle cx="60" cy="140" r="4" fill="#10b981"/>
                    <text x="75" y="114" font-size="12" fill="#666">✓</text>
                    <text x="75" y="129" font-size="12" fill="#666">✓</text>
                    <text x="75" y="144" font-size="12" fill="#666">✓</text>
                    <!-- Stars -->
                    <text x="25" y="45" font-size="18">📚</text>
                    <text x="165" y="170" font-size="18">🎯</text>
                </svg>
            `,
            application: `
                <svg viewBox="0 0 200 200" class="milestone-svg">
                    <!-- Application Form -->
                    <rect x="45" y="35" width="110" height="130" rx="5" fill="#fff" stroke="#f59e0b" stroke-width="3"/>
                    <rect x="55" y="50" width="90" height="8" fill="#fde68a" rx="2"/>
                    <rect x="55" y="70" width="90" height="6" fill="#e5e7eb" rx="2"/>
                    <rect x="55" y="85" width="70" height="6" fill="#e5e7eb" rx="2"/>
                    <rect x="55" y="100" width="80" height="6" fill="#e5e7eb" rx="2"/>
                    <!-- Signature line -->
                    <line x1="55" y1="135" x2="145" y2="135" stroke="#f59e0b" stroke-width="2" stroke-dasharray="2,2"/>
                    <text x="100" y="150" font-size="16" fill="#f59e0b" text-anchor="middle" font-family="cursive">Signature</text>
                    <!-- Pen -->
                    <rect x="150" y="120" width="8" height="40" fill="#1e40af" rx="2" transform="rotate(-30 154 140)"/>
                    <polygon points="150,155 154,165 158,155" fill="#1e40af" transform="rotate(-30 154 160)"/>
                    <!-- Stars -->
                    <text x="20" y="50" font-size="20">✍️</text>
                    <text x="165" y="60" font-size="18">📝</text>
                </svg>
            `,
            license: `
                <svg viewBox="0 0 200 200" class="milestone-svg">
                    <!-- Driver's License Card -->
                    <rect x="30" y="60" width="140" height="90" rx="8" fill="#8b5cf6"/>
                    <rect x="35" y="65" width="130" height="80" rx="6" fill="#a78bfa"/>
                    <!-- Photo placeholder -->
                    <circle cx="65" cy="105" r="25" fill="#fff"/>
                    <text x="65" y="115" font-size="30" text-anchor="middle">😊</text>
                    <!-- License info -->
                    <rect x="105" y="80" width="55" height="5" fill="#fff" opacity="0.8" rx="2"/>
                    <rect x="105" y="95" width="50" height="4" fill="#fff" opacity="0.6" rx="2"/>
                    <rect x="105" y="105" width="45" height="4" fill="#fff" opacity="0.6" rx="2"/>
                    <rect x="105" y="115" width="40" height="4" fill="#fff" opacity="0.6" rx="2"/>
                    <!-- Star badge -->
                    <text x="145" y="135" font-size="20">⭐</text>
                    <!-- Celebration -->
                    <text x="25" y="45" font-size="22">🎉</text>
                    <text x="160" y="50" font-size="22">🚗</text>
                    <text x="170" y="155" font-size="18">🎊</text>
                </svg>
            `,
            novice: `
                <svg viewBox="0 0 200 200" class="milestone-svg">
                    <!-- N Plate -->
                    <rect x="50" y="50" width="100" height="100" rx="10" fill="#fff" stroke="#ec4899" stroke-width="4"/>
                    <text x="100" y="125" font-size="80" fill="#ec4899" text-anchor="middle" font-weight="bold">N</text>
                    <!-- Progress bar -->
                    <rect x="60" y="30" width="80" height="12" fill="#fce7f3" rx="6"/>
                    <rect x="60" y="30" width="40" height="12" fill="#ec4899" rx="6"/>
                    <text x="100" y="25" font-size="10" fill="#ec4899" text-anchor="middle" font-weight="bold">Year 1 ✓</text>
                    <!-- Stars -->
                    <text x="25" y="60" font-size="20">⭐</text>
                    <text x="165" y="70" font-size="18">🔰</text>
                    <text x="35" y="155" font-size="18">💪</text>
                    <text x="160" y="150" font-size="20">🎯</text>
                </svg>
            `,
            qualified: `
                <svg viewBox="0 0 200 200" class="milestone-svg">
                    <!-- Trophy -->
                    <ellipse cx="100" cy="160" rx="50" ry="8" fill="#fbbf24" opacity="0.3"/>
                    <rect x="90" y="140" width="20" height="20" fill="#fbbf24"/>
                    <rect x="85" y="130" width="30" height="10" fill="#fbbf24" rx="2"/>
                    <path d="M 70 130 Q 70 80 100 70 Q 130 80 130 130 Z" fill="#fbbf24"/>
                    <circle cx="100" cy="90" r="15" fill="#fff"/>
                    <text x="100" y="98" font-size="16" fill="#f59e0b" text-anchor="middle" font-weight="bold">1</text>
                    <!-- Handles -->
                    <path d="M 70 100 Q 55 100 55 85 Q 55 75 60 75 L 70 75" stroke="#fbbf24" stroke-width="4" fill="none"/>
                    <path d="M 130 100 Q 145 100 145 85 Q 145 75 140 75 L 130 75" stroke="#fbbf24" stroke-width="4" fill="none"/>
                    <!-- Crown on top -->
                    <text x="100" y="60" font-size="30" text-anchor="middle">👑</text>
                    <!-- Celebration -->
                    <text x="30" y="50" font-size="24">🎉</text>
                    <text x="160" y="55" font-size="24">🎊</text>
                    <text x="25" y="160" font-size="20">✨</text>
                    <text x="165" y="165" font-size="20">⭐</text>
                    <text x="100" y="35" font-size="18" text-anchor="middle">🏆</text>
                </svg>
            `
        };

        return graphics[graphic] || graphics.learner;
    }

    createConfetti() {
        const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
        const container = document.getElementById('milestone-container');

        for (let i = 0; i < 50; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.animationDelay = Math.random() * 0.5 + 's';
            confetti.style.animationDuration = (Math.random() * 1 + 2) + 's';
            
            container.appendChild(confetti);

            setTimeout(() => confetti.remove(), 3000);
        }
    }

    playSound() {
        // Optional: Try to play a celebration sound
        try {
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZSA0PVqzn77JcGAg+ltryxnMpBSuBzvLaiTYIGWm98OScTgwOU6Xh8rJeGgg5j9f0y3ksBS1+zPDdiTwIGWu98OSaSwwOVKbn87BiGQc7ktbrxnIoBSx+zPDdiTwIGWu98OSaSwwOVKbn87BiGQc7ktbrxnIoBSx+zPDdiTwIGWu98OSaSwwOVKbn87BiGQc7ktbrxnIoBSx+zPDdiTwIGWu98OSaSwwOVKbn87BiGQc7ktbrxnIoBSx+zPDdiTwIGWu98OSaSwwOVKbn87BiGQc7ktbrxnIoBSx+zPDdiTwIGWu98OSaSwwOVKbn87BiGQc7ktbrxnIoBSx+zPDdiTwIGWu98OSaSwwOVKbn87BiGQc7ktbrxnIoBSx+zPDdiTwIGWu98OSaSwwOVKbn87BiGQc7ktbrxnIoBSx+zPDdiTwIGWu98OSaSwwOVKbn87BiGQc7ktbrxnIoBSx+zPDdiTwIGWu98OSaSwwOVKbn87BiGQc7ktbrxnIoBSx+zPDdiTwIGWu98OSaSwwOVKbn87BiGQc7ktbrxnIoBSx+zPDdiTwIGWu98OSaSwwOVKbn87BiGQc7ktbrxnIoBSx+zPDdiTwIGWu98OSaSwwOVKbn87BiGQc7ktbrxnIoBSx+zPDdiTwIGWu98OSaSwwOVKbn87BiGQc7ktbrxnIoBSx+zPDdiTwIGWu98OSaSwwOVKbn87BiGQc7ktbrxnIoBSx+zPDdiTwIGWu98OSaSwwOVKbn87BiGQc7ktbrxnIoBSx+zPDdiTwIGWu98OSaSwwOVKbn87BiGQc7ktbrxnIo');
            audio.volume = 0.3;
            audio.play().catch(() => {}); // Silent fail if audio not supported
        } catch (e) {
            // Silent fail - audio is optional
        }
    }

    createMilestoneContainer() {
        if (!document.getElementById('milestone-container')) {
            const container = document.createElement('div');
            container.id = 'milestone-container';
            document.body.appendChild(container);
        }
    }

    initializeStyles() {
        if (document.getElementById('milestone-styles')) return;

        const style = document.createElement('style');
        style.id = 'milestone-styles';
        style.textContent = `
            #milestone-container {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 10000;
            }

            .milestone-popup {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                transition: opacity 0.3s ease;
                pointer-events: all;
            }

            .milestone-popup.active {
                opacity: 1;
            }

            .milestone-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                backdrop-filter: blur(4px);
            }

            .milestone-content {
                position: relative;
                background: white;
                border-radius: 24px;
                padding: 40px;
                max-width: 500px;
                width: 90%;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                transform: scale(0.8);
                transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
                z-index: 1;
            }

            .milestone-popup.active .milestone-content {
                transform: scale(1);
                animation: bounceIn 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
            }

            @keyframes bounceIn {
                0% {
                    transform: scale(0.3);
                    opacity: 0;
                }
                50% {
                    transform: scale(1.05);
                }
                70% {
                    transform: scale(0.9);
                }
                100% {
                    transform: scale(1);
                    opacity: 1;
                }
            }

            .milestone-graphic {
                margin: -60px auto 20px;
                width: 200px;
                height: 200px;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .milestone-svg {
                width: 100%;
                height: 100%;
                filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.1));
                animation: floatGraphic 3s ease-in-out infinite;
            }

            @keyframes floatGraphic {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-10px); }
            }

            .milestone-header {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 16px;
                margin-bottom: 12px;
            }

            .milestone-icon {
                width: 56px;
                height: 56px;
                border-radius: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 32px;
                animation: pulse 2s ease-in-out infinite;
            }

            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }

            .milestone-title {
                font-size: 28px;
                font-weight: 800;
                color: #1f2937;
                margin: 0;
                text-align: center;
            }

            .milestone-subtitle {
                font-size: 18px;
                font-weight: 600;
                color: #6b7280;
                text-align: center;
                margin-bottom: 16px;
            }

            .milestone-message {
                font-size: 16px;
                color: #4b5563;
                text-align: center;
                margin-bottom: 24px;
                line-height: 1.6;
            }

            .milestone-close {
                width: 100%;
                padding: 16px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }

            .milestone-close:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }

            .milestone-close:active {
                transform: translateY(0);
            }

            .confetti {
                position: absolute;
                width: 10px;
                height: 10px;
                top: -10px;
                opacity: 1;
                animation: confettiFall linear forwards;
            }

            @keyframes confettiFall {
                0% {
                    transform: translateY(0) rotate(0deg);
                    opacity: 1;
                }
                100% {
                    transform: translateY(100vh) rotate(720deg);
                    opacity: 0;
                }
            }

            /* Mobile responsive */
            @media (max-width: 768px) {
                .milestone-content {
                    padding: 30px 20px;
                }

                .milestone-graphic {
                    width: 150px;
                    height: 150px;
                    margin: -50px auto 15px;
                }

                .milestone-title {
                    font-size: 22px;
                }

                .milestone-subtitle {
                    font-size: 16px;
                }

                .milestone-message {
                    font-size: 14px;
                }

                .milestone-icon {
                    width: 48px;
                    height: 48px;
                    font-size: 28px;
                }
            }
        `;

        document.head.appendChild(style);
    }
}

// Create global instance (safe to call before DOM ready)
const milestoneSystem = new QuizMilestoneSystem();

// Initialize DOM elements when ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        milestoneSystem.ensureInitialized();
        console.log('✅ Milestone System Ready');
    });
} else {
    // DOM already loaded
    milestoneSystem.ensureInitialized();
    console.log('✅ Milestone System Ready');
}
