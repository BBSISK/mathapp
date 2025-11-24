-- WHO AM I: Complete Database Setup
-- Creates all tables needed for multi-topic Who Am I system

-- Step 1: Create main images table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS who_am_i_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic VARCHAR(100),
    difficulty VARCHAR(20) NOT NULL,
    image_filename VARCHAR(255) NOT NULL,
    answer VARCHAR(200) NOT NULL,
    hint TEXT,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 2: Create sessions table for tracking quiz attempts (if it doesn't exist)
CREATE TABLE IF NOT EXISTS who_am_i_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    quiz_attempt_id INTEGER NOT NULL,
    image_id INTEGER NOT NULL,
    tiles_revealed TEXT DEFAULT '[]',
    guesses_made INTEGER DEFAULT 0,
    correct_guess INTEGER DEFAULT 0,
    bonus_points_earned INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (quiz_attempt_id) REFERENCES quiz_attempts(id),
    FOREIGN KEY (image_id) REFERENCES who_am_i_images(id)
);

-- Step 3: Create junction table for multi-topic support
CREATE TABLE IF NOT EXISTS who_am_i_image_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id INTEGER NOT NULL,
    topic VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (image_id) REFERENCES who_am_i_images(id) ON DELETE CASCADE,
    UNIQUE(image_id, topic)
);

-- Step 4: Migrate existing data from who_am_i_images to junction table
-- (Only if there are existing images with topics)
INSERT OR IGNORE INTO who_am_i_image_topics (image_id, topic)
SELECT id, topic FROM who_am_i_images
WHERE topic IS NOT NULL AND topic != '';

-- Step 5: Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_who_am_i_images_topic ON who_am_i_images(topic);
CREATE INDEX IF NOT EXISTS idx_who_am_i_images_difficulty ON who_am_i_images(difficulty);
CREATE INDEX IF NOT EXISTS idx_who_am_i_images_active ON who_am_i_images(active);
CREATE INDEX IF NOT EXISTS idx_who_am_i_sessions_user ON who_am_i_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_who_am_i_sessions_quiz ON who_am_i_sessions(quiz_attempt_id);
CREATE INDEX IF NOT EXISTS idx_image_topics_image_id ON who_am_i_image_topics(image_id);
CREATE INDEX IF NOT EXISTS idx_image_topics_topic ON who_am_i_image_topics(topic);

-- Verification queries (run these manually to check):
-- SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'who_am_i%';
-- SELECT COUNT(*) FROM who_am_i_images;
-- SELECT COUNT(*) FROM who_am_i_image_topics;
