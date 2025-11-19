-- ═══════════════════════════════════════════════════════════════════════
-- PATTERNS QUESTIONS - SQL FIX SCRIPT
-- Fixes incorrect correct_answer values across all difficulty levels
-- Total fixes: 43 critical questions
-- ═══════════════════════════════════════════════════════════════════════

-- ADVANCED LEVEL FIXES (10 questions)
-- ═══════════════════════════════════════════════════════════════════════

-- Question 1889: Exponential sequence (was B, should be C)
UPDATE questions SET correct_answer = 2 WHERE id = 1889;

-- Question 1890: Next square number 36 (was B, should be C)
UPDATE questions SET correct_answer = 2 WHERE id = 1890;

-- Question 1891: Square numbers pattern (was B, should be C)
UPDATE questions SET correct_answer = 2 WHERE id = 1891;

-- Question 1892: Multiply by 3 pattern (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1892;

-- Question 1893: 2n² = 72 (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1893;

-- Question 1894: Cube number 125 (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1894;

-- Question 1895: n(n+1) pattern (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1895;

-- Question 1896: 7² = 49 (was B, should be C)
UPDATE questions SET correct_answer = 2 WHERE id = 1896;

-- Question 1897: 2⁵ = 32 (was C, should be D)
UPDATE questions SET correct_answer = 3 WHERE id = 1897;

-- Question 1898: 3n² = 75 (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1898;


-- BEGINNER LEVEL FIXES (19 questions)
-- ═══════════════════════════════════════════════════════════════════════

-- Question 1809: Moon comes after star (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1809;

-- Question 1810: Blue comes after red (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1810;

-- Question 1811: 4 stars next (was C, should be D)
UPDATE questions SET correct_answer = 3 WHERE id = 1811;

-- Question 1812: Smiley alternates (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1812;

-- Question 1813: Banana completes pattern (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1813;

-- Question 1814: 8+2=10 (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1814;

-- Question 1815: 20+5=25 (was B, should be C)
UPDATE questions SET correct_answer = 2 WHERE id = 1815;

-- Question 1816: 7+2=9 (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1816;

-- Question 1817: 40+10=50 (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1817;

-- Question 1818: 12+3=15 (was B, should be C)
UPDATE questions SET correct_answer = 2 WHERE id = 1818;

-- Question 1819: Circle comes next (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1819;

-- Question 1820: Circle completes pattern (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1820;

-- Question 1821: Down triangle alternates (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1821;

-- Question 1822: Common difference is 3 (was B, should be C)
UPDATE questions SET correct_answer = 2 WHERE id = 1822;

-- Question 1823: Common difference is 3 (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1823;

-- Question 1824: Common difference is 5 (was B, should be C)
UPDATE questions SET correct_answer = 2 WHERE id = 1824;

-- Question 1825: Common difference is 5 (was B, should be C)
UPDATE questions SET correct_answer = 2 WHERE id = 1825;

-- Question 1826: Common difference is 4 (was B, should be C)
UPDATE questions SET correct_answer = 2 WHERE id = 1826;

-- Question 1827: 28+7=35 (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1827;


-- INTERMEDIATE LEVEL FIXES (14 questions)
-- ═══════════════════════════════════════════════════════════════════════

-- Question 1849: 15+4=19 (was B, should be C)
UPDATE questions SET correct_answer = 2 WHERE id = 1849;

-- Question 1850: nth term is 2n (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1850;

-- Question 1851: nth term is 5n (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1851;

-- Question 1852: 3(10)+1=31 (was B, should be C)
UPDATE questions SET correct_answer = 2 WHERE id = 1852;

-- Question 1853: 2(7)-1=13 (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1853;

-- Question 1854: nth term is 3n+1 (was B, should be C)
UPDATE questions SET correct_answer = 2 WHERE id = 1854;

-- Question 1855: 3(6)-2=16 (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1855;

-- Question 1857: 6×20=120 (was B, should be C)
UPDATE questions SET correct_answer = 2 WHERE id = 1857;

-- Question 1858: nth term is 4n+5 (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1858;

-- Question 1859: 3(8)-1=23 (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1859;

-- Question 1860: 5(12)-2=58 (was B, should be C)
UPDATE questions SET correct_answer = 2 WHERE id = 1860;

-- Question 1861: nth term is 5n+2 (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1861;

-- Question 1862: 4(15)+3=63 (was B, should be C)
UPDATE questions SET correct_answer = 2 WHERE id = 1862;

-- Question 1863: nth term is 7n+3 (was A, should be B)
UPDATE questions SET correct_answer = 1 WHERE id = 1863;


-- ═══════════════════════════════════════════════════════════════════════
-- VERIFICATION QUERY
-- Run this after applying fixes to verify all corrections
-- ═══════════════════════════════════════════════════════════════════════

SELECT 
    id, 
    difficulty, 
    SUBSTR(question_text, 1, 50) as question,
    CASE correct_answer
        WHEN 0 THEN 'A'
        WHEN 1 THEN 'B'
        WHEN 2 THEN 'C'
        WHEN 3 THEN 'D'
    END as correct_option,
    correct_answer as correct_index
FROM questions
WHERE id IN (
    1889, 1890, 1891, 1892, 1893, 1894, 1895, 1896, 1897, 1898,
    1809, 1810, 1811, 1812, 1813, 1814, 1815, 1816, 1817, 1818,
    1819, 1820, 1821, 1822, 1823, 1824, 1825, 1826, 1827,
    1849, 1850, 1851, 1852, 1853, 1854, 1855, 1857, 1858, 1859,
    1860, 1861, 1862, 1863
)
ORDER BY difficulty, id;


-- ═══════════════════════════════════════════════════════════════════════
-- SUMMARY
-- ═══════════════════════════════════════════════════════════════════════
-- Total questions fixed: 43
-- Advanced level: 10 fixes
-- Beginner level: 19 fixes  
-- Intermediate level: 14 fixes
--
-- All fixes align correct_answer index with explanations
-- Ready to apply to production database
-- ═══════════════════════════════════════════════════════════════════════
