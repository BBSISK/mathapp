-- WHO AM I: Multi-Topic Support Migration
-- This adds support for assigning images to multiple topics

-- Step 1: Create junction table for image-topic relationships
CREATE TABLE IF NOT EXISTS who_am_i_image_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id INTEGER NOT NULL,
    topic VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (image_id) REFERENCES who_am_i_images(id) ON DELETE CASCADE,
    UNIQUE(image_id, topic)
);

-- Step 2: Migrate existing topic data to junction table
-- This copies the single topic from each image to the new table
INSERT INTO who_am_i_image_topics (image_id, topic)
SELECT id, topic FROM who_am_i_images
WHERE topic IS NOT NULL AND topic != '';

-- Step 3: Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_image_topics_image_id ON who_am_i_image_topics(image_id);
CREATE INDEX IF NOT EXISTS idx_image_topics_topic ON who_am_i_image_topics(topic);

-- Step 4: Add topic_enabled flag to track which topics have Who Am I enabled
-- (We'll keep this simple - store as JSON in a settings table or check if images exist)

-- Verification queries (run these to check migration worked):
-- SELECT COUNT(*) FROM who_am_i_image_topics; -- Should match count of who_am_i_images
-- SELECT i.answer, GROUP_CONCAT(t.topic) as topics 
-- FROM who_am_i_images i 
-- LEFT JOIN who_am_i_image_topics t ON i.id = t.image_id 
-- GROUP BY i.id;

-- Note: The 'topic' column in who_am_i_images is kept for backward compatibility
-- and can be used as the "primary" topic for display purposes
