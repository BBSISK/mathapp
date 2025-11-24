-- ============================================================================
-- WHO AM I? FEATURE - DATABASE SCHEMA
-- ============================================================================
-- Run this file to add the necessary tables for the Who Am I? reveal feature
-- 
-- Usage:
--   cd ~/mathapp
--   sqlite3 instance/mathquiz.db < add_who_am_i_tables.sql
-- ============================================================================

-- Table to store Who Am I images
CREATE TABLE IF NOT EXISTS who_am_i_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    difficulty TEXT CHECK(difficulty IN ('beginner', 'intermediate', 'advanced')),
    image_filename TEXT NOT NULL,
    answer TEXT NOT NULL,
    hint TEXT,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to track user's current reveal session
CREATE TABLE IF NOT EXISTS who_am_i_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    quiz_attempt_id INTEGER,
    image_id INTEGER NOT NULL,
    tiles_revealed TEXT DEFAULT '[]',  -- JSON array of tile indices revealed
    guesses_made INTEGER DEFAULT 0,
    correct_guess INTEGER DEFAULT 0,
    bonus_points_earned INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (image_id) REFERENCES who_am_i_images(id)
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_who_am_i_sessions_user 
    ON who_am_i_sessions(user_id);
    
CREATE INDEX IF NOT EXISTS idx_who_am_i_sessions_quiz 
    ON who_am_i_sessions(quiz_attempt_id);

-- Add bonus_points column to quiz_attempts if it doesn't exist
-- This stores the Who Am I bonus separately from regular quiz points
-- Note: This will error if column already exists, which is fine
ALTER TABLE quiz_attempts ADD COLUMN who_am_i_bonus INTEGER DEFAULT 0;

-- Sample data for testing (optional - comment out if you want to add your own images first)
-- INSERT INTO who_am_i_images (topic, difficulty, image_filename, answer, hint) VALUES
-- ('Descriptive Statistics', 'beginner', 'sample_1.jpg', 'Cristiano Ronaldo', 'Portuguese footballer'),
-- ('Descriptive Statistics', 'intermediate', 'sample_2.jpg', 'Taylor Swift', 'American singer'),
-- ('Descriptive Statistics', 'advanced', 'sample_3.jpg', 'Eiffel Tower', 'Famous landmark');

SELECT 'Who Am I? tables created successfully!' as message;
