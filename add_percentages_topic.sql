-- =====================================================
-- ADD INTRODUCTION TO PERCENTAGES TOPIC
-- =====================================================
-- This adds a new topic "Introduction to Percentages" to the NUMBER strand
-- Position: Between Decimals and Sets
-- 75 questions total (25 per difficulty level)
-- =====================================================

-- STEP 1: Add the topic to the topics table
-- =====================================================
INSERT INTO topics (name, strand, order_index, description) 
VALUES (
    'Introduction to Percentages',
    'Number',
    9,  -- Position between Decimals (8) and Sets (10)
    'Learn to convert between percentages, decimals and fractions, and solve problems involving percentages, interest, and profit/loss'
);

-- Get the topic_id for the new topic (will be used in questions)
-- The topic_id will be automatically assigned by the database


-- =====================================================
-- STEP 2: Add BEGINNER Questions (25 questions)
-- Focus: Converting decimals/fractions to percents, basic percent calculations
-- =====================================================

INSERT INTO questions (topic, difficulty, question_text, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, hint) VALUES
-- Decimal to Percentage conversions (Questions 1-8)
('Introduction to Percentages', 'Beginner', 'Convert 0.25 to a percentage.', '25%', '2.5%', '0.25%', '250%', 'Multiply the decimal by 100 to convert to a percentage.'),
('Introduction to Percentages', 'Beginner', 'Convert 0.5 to a percentage.', '50%', '5%', '0.5%', '500%', 'Remember: 0.5 means 5 tenths, which is 50 hundredths or 50%.'),
('Introduction to Percentages', 'Beginner', 'Convert 0.75 to a percentage.', '75%', '7.5%', '0.75%', '750%', 'Move the decimal point two places to the right and add the % symbol.'),
('Introduction to Percentages', 'Beginner', 'Convert 0.1 to a percentage.', '10%', '1%', '0.1%', '100%', '0.1 is the same as 10/100 which equals 10%.'),
('Introduction to Percentages', 'Beginner', 'Convert 0.6 to a percentage.', '60%', '6%', '0.6%', '600%', 'Think: 0.6 = 60/100 = 60%.'),
('Introduction to Percentages', 'Beginner', 'Convert 0.35 to a percentage.', '35%', '3.5%', '0.35%', '350%', 'Multiply 0.35 by 100: 0.35 × 100 = 35%.'),
('Introduction to Percentages', 'Beginner', 'Convert 0.9 to a percentage.', '90%', '9%', '0.9%', '900%', '0.9 = 9 tenths = 90 hundredths = 90%.'),
('Introduction to Percentages', 'Beginner', 'Convert 0.05 to a percentage.', '5%', '0.5%', '50%', '500%', '0.05 = 5/100 = 5%.'),

-- Percentage to Decimal conversions (Questions 9-12)
('Introduction to Percentages', 'Beginner', 'Convert 40% to a decimal.', '0.4', '4', '0.04', '40', 'Divide by 100: 40 ÷ 100 = 0.4.'),
('Introduction to Percentages', 'Beginner', 'Convert 15% to a decimal.', '0.15', '1.5', '15', '0.015', 'To convert percentage to decimal, divide by 100.'),
('Introduction to Percentages', 'Beginner', 'Convert 80% to a decimal.', '0.8', '8', '0.08', '80', 'Move the decimal point two places to the left: 80% = 0.80 = 0.8.'),
('Introduction to Percentages', 'Beginner', 'Convert 3% to a decimal.', '0.03', '0.3', '3', '30', '3% means 3 out of 100, which is 0.03.'),

-- Fraction to Percentage conversions (Questions 13-17)
('Introduction to Percentages', 'Beginner', 'Convert 1/2 to a percentage.', '50%', '25%', '2%', '12%', 'Think: 1/2 = 0.5, and 0.5 = 50%.'),
('Introduction to Percentages', 'Beginner', 'Convert 1/4 to a percentage.', '25%', '50%', '4%', '14%', '1/4 = 0.25 = 25%.'),
('Introduction to Percentages', 'Beginner', 'Convert 3/4 to a percentage.', '75%', '34%', '43%', '25%', '3/4 = 0.75 = 75%.'),
('Introduction to Percentages', 'Beginner', 'Convert 1/5 to a percentage.', '20%', '5%', '15%', '50%', 'Divide: 1 ÷ 5 = 0.2 = 20%.'),
('Introduction to Percentages', 'Beginner', 'Convert 1/10 to a percentage.', '10%', '1%', '100%', '0.1%', '1/10 = 0.1 = 10%.'),

-- Basic Percentage Calculations (Questions 18-25)
('Introduction to Percentages', 'Beginner', 'What is 10% of 50?', '5', '10', '50', '500', '10% means 10/100, so calculate (10/100) × 50.'),
('Introduction to Percentages', 'Beginner', 'What is 50% of 80?', '40', '50', '30', '160', '50% is the same as half, so divide 80 by 2.'),
('Introduction to Percentages', 'Beginner', 'What is 25% of 100?', '25', '50', '75', '4', '25% = 1/4, so divide 100 by 4.'),
('Introduction to Percentages', 'Beginner', 'What is 20% of 60?', '12', '20', '40', '3', 'Calculate: (20/100) × 60 = (1/5) × 60.'),
('Introduction to Percentages', 'Beginner', 'What is 10% of 120?', '12', '10', '112', '1200', '10% = 1/10, so divide 120 by 10.'),
('Introduction to Percentages', 'Beginner', 'What is 75% of 40?', '30', '35', '25', '10', '75% = 3/4, so calculate (3/4) × 40.'),
('Introduction to Percentages', 'Beginner', 'Express 12 out of 100 as a percentage.', '12%', '1.2%', '120%', '88%', 'Out of 100 means the number itself is the percentage.'),
('Introduction to Percentages', 'Beginner', 'Express 45 out of 100 as a percentage.', '45%', '4.5%', '450%', '55%', '45 out of 100 = 45/100 = 45%.');


-- =====================================================
-- STEP 3: Add INTERMEDIATE Questions (25 questions)
-- Focus: Simple interest, adding tax, subtracting discount, profit and loss
-- =====================================================

INSERT INTO questions (topic, difficulty, question_text, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, hint) VALUES
-- Simple Interest (Questions 1-7)
('Introduction to Percentages', 'Intermediate', 'Calculate the simple interest on €500 at 5% per year for 2 years.', '€50', '€25', '€100', '€500', 'Use the formula: Interest = Principal × Rate × Time. I = 500 × 0.05 × 2.'),
('Introduction to Percentages', 'Intermediate', 'What is the simple interest on €1000 at 4% per year for 3 years?', '€120', '€40', '€400', '€12', 'I = P × R × T = 1000 × 0.04 × 3.'),
('Introduction to Percentages', 'Intermediate', 'Calculate the simple interest on €800 at 6% per year for 1 year.', '€48', '€6', '€60', '€480', 'For 1 year, just multiply principal by the rate: 800 × 0.06.'),
('Introduction to Percentages', 'Intermediate', 'Find the simple interest on €2000 at 3% per year for 4 years.', '€240', '€24', '€600', '€2400', 'I = 2000 × 0.03 × 4 = 2000 × 0.12.'),
('Introduction to Percentages', 'Intermediate', 'What is the total amount after earning €75 simple interest on €500?', '€575', '€500', '€75', '€425', 'Total Amount = Principal + Interest = 500 + 75.'),
('Introduction to Percentages', 'Intermediate', 'Calculate the simple interest on €600 at 10% per year for 2 years.', '€120', '€60', '€12', '€1200', 'I = 600 × 0.10 × 2 = 600 × 0.20.'),
('Introduction to Percentages', 'Intermediate', 'Find the simple interest rate if €400 grows to €480 in 2 years.', '10%', '5%', '20%', '8%', 'Interest = 480 - 400 = €80. Rate = (80 ÷ 400) ÷ 2 = 0.1 = 10%.'),

-- Adding Tax/VAT (Questions 8-12)
('Introduction to Percentages', 'Intermediate', 'A book costs €20 before tax. What is the total price with 10% tax?', '€22', '€20', '€30', '€2', 'Calculate tax: 20 × 0.10 = €2. Add to original: 20 + 2 = €22.'),
('Introduction to Percentages', 'Intermediate', 'An item costs €50 before VAT. What is the price including 20% VAT?', '€60', '€70', '€50', '€10', 'VAT = 50 × 0.20 = €10. Total = 50 + 10 = €60.'),
('Introduction to Percentages', 'Intermediate', 'A laptop costs €800 before 23% VAT. What is the final price?', '€984', '€800', '€1023', '€184', 'VAT = 800 × 0.23 = €184. Final price = 800 + 184 = €984.'),
('Introduction to Percentages', 'Intermediate', 'Find the total cost of a €45 meal with 15% service charge added.', '€51.75', '€45', '€60', '€6.75', 'Service charge = 45 × 0.15 = €6.75. Total = 45 + 6.75 = €51.75.'),
('Introduction to Percentages', 'Intermediate', 'A phone costs €300. What is the price after adding 12% tax?', '€336', '€312', '€300', '€360', 'Tax = 300 × 0.12 = €36. Total = 300 + 36 = €336.'),

-- Subtracting Discount (Questions 13-17)
('Introduction to Percentages', 'Intermediate', 'A €60 jacket has a 20% discount. What is the sale price?', '€48', '€40', '€50', '€12', 'Discount = 60 × 0.20 = €12. Sale price = 60 - 12 = €48.'),
('Introduction to Percentages', 'Intermediate', 'Find the price of a €80 item after a 25% discount.', '€60', '€55', '€20', '€105', 'Discount = 80 × 0.25 = €20. Final price = 80 - 20 = €60.'),
('Introduction to Percentages', 'Intermediate', 'A TV costs €500. What is the price after a 15% discount?', '€425', '€485', '€75', '€515', 'Discount = 500 × 0.15 = €75. Sale price = 500 - 75 = €425.'),
('Introduction to Percentages', 'Intermediate', 'Calculate the sale price of €120 shoes with 30% off.', '€84', '€90', '€36', '€150', 'Discount = 120 × 0.30 = €36. Sale price = 120 - 36 = €84.'),
('Introduction to Percentages', 'Intermediate', 'An item costing €200 has a 10% discount. What do you pay?', '€180', '€190', '€20', '€220', 'Discount = 200 × 0.10 = €20. You pay 200 - 20 = €180.'),

-- Profit and Loss (Questions 18-25)
('Introduction to Percentages', 'Intermediate', 'An item bought for €50 is sold for €60. What is the profit?', '€10', '€50', '€60', '€110', 'Profit = Selling Price - Cost Price = 60 - 50.'),
('Introduction to Percentages', 'Intermediate', 'Find the profit percentage if an item bought for €100 is sold for €120.', '20%', '10%', '120%', '1.2%', 'Profit = 120 - 100 = €20. Profit % = (20/100) × 100% = 20%.'),
('Introduction to Percentages', 'Intermediate', 'A shopkeeper buys goods for €80 and sells them for €100. What is the profit percentage?', '25%', '20%', '80%', '125%', 'Profit = 100 - 80 = €20. Profit % = (20/80) × 100% = 25%.'),
('Introduction to Percentages', 'Intermediate', 'An item bought for €200 is sold for €180. What is the loss?', '€20', '€180', '€200', '€380', 'Loss = Cost Price - Selling Price = 200 - 180.'),
('Introduction to Percentages', 'Intermediate', 'Find the loss percentage if an item bought for €50 is sold for €40.', '20%', '10%', '25%', '80%', 'Loss = 50 - 40 = €10. Loss % = (10/50) × 100% = 20%.'),
('Introduction to Percentages', 'Intermediate', 'An item is sold at €75 making a 25% profit. What was the cost price?', '€60', '€75', '€50', '€93.75', 'If 125% = €75, then 100% = 75 ÷ 1.25 = €60.'),
('Introduction to Percentages', 'Intermediate', 'A trader bought goods for €150 and sold them for €180. Calculate the profit percentage.', '20%', '30%', '15%', '120%', 'Profit = 180 - 150 = €30. Profit % = (30/150) × 100% = 20%.'),
('Introduction to Percentages', 'Intermediate', 'An article is sold for €90 at a 10% loss. What was the original price?', '€100', '€90', '€99', '€81', 'If 90% = €90, then 100% = 90 ÷ 0.9 = €100.');


-- =====================================================
-- STEP 4: Add ADVANCED Questions (25 questions)
-- Focus: Compound interest, reverse calculations for % increase/decrease
-- =====================================================

INSERT INTO questions (topic, difficulty, question_text, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, hint) VALUES
-- Compound Interest (Questions 1-10)
('Introduction to Percentages', 'Advanced', 'Calculate the compound interest on €1000 at 10% per year for 2 years.', '€210', '€200', '€100', '€1210', 'Year 1: 1000 × 1.10 = €1100. Year 2: 1100 × 1.10 = €1210. Interest = 1210 - 1000.'),
('Introduction to Percentages', 'Advanced', 'Find the amount after 2 years if €500 is invested at 5% compound interest per year.', '€551.25', '€550', '€525', '€500', 'Year 1: 500 × 1.05 = €525. Year 2: 525 × 1.05 = €551.25.'),
('Introduction to Percentages', 'Advanced', 'What is the compound interest on €2000 at 8% per year for 2 years?', '€332.80', '€320', '€160', '€2332.80', 'Use formula: A = P(1 + r)^n. A = 2000 × 1.08² = €2332.80. Interest = 332.80.'),
('Introduction to Percentages', 'Advanced', 'Calculate the total amount for €800 invested at 6% compound interest for 3 years.', '€952.38', '€944', '€800', '€1144', 'A = 800 × 1.06³ = 800 × 1.191016 = €952.38.'),
('Introduction to Percentages', 'Advanced', 'Find the compound interest on €1500 at 12% per year for 2 years.', '€381.60', '€360', '€180', '€1881.60', 'Year 1: 1500 × 1.12 = €1680. Year 2: 1680 × 1.12 = €1881.60. CI = 381.60.'),
('Introduction to Percentages', 'Advanced', 'What is the difference between compound and simple interest on €1000 at 10% for 2 years?', '€10', '€20', '€200', '€210', 'Simple Interest = 1000 × 0.10 × 2 = €200. Compound Interest = €210. Difference = €10.'),
('Introduction to Percentages', 'Advanced', 'Calculate the compound interest on €3000 at 5% per year for 3 years.', '€472.88', '€450', '€150', '€3472.88', 'A = 3000 × 1.05³ = 3000 × 1.157625 = €3472.88. CI = 472.88.'),
('Introduction to Percentages', 'Advanced', 'Find the amount after 2 years if €600 grows at 15% compound interest per year.', '€793.50', '€780', '€600', '€180', 'Year 1: 600 × 1.15 = €690. Year 2: 690 × 1.15 = €793.50.'),
('Introduction to Percentages', 'Advanced', 'Calculate compound interest on €5000 at 4% per year for 2 years.', '€408', '€400', '€200', '€5408', 'A = 5000 × 1.04² = 5000 × 1.0816 = €5408. CI = €408.'),
('Introduction to Percentages', 'Advanced', 'What is the final amount if €1200 is invested at 7% compound interest for 3 years?', '€1470.05', '€1452', '€1200', '€252', 'A = 1200 × 1.07³ = 1200 × 1.225043 = €1470.05.'),

-- Reverse Percentage Calculations - Finding Original Values (Questions 11-17)
('Introduction to Percentages', 'Advanced', 'After a 20% increase, a price is €120. What was the original price?', '€100', '€120', '€96', '€144', 'If 120% = €120, then 100% = 120 ÷ 1.20 = €100.'),
('Introduction to Percentages', 'Advanced', 'After a 25% decrease, a quantity is 60. What was it originally?', '80', '60', '75', '45', 'If 75% = 60, then 100% = 60 ÷ 0.75 = 80.'),
('Introduction to Percentages', 'Advanced', 'A price increased by 15% to become €230. Find the original price.', '€200', '€230', '€195.50', '€264.50', 'If 115% = €230, then 100% = 230 ÷ 1.15 = €200.'),
('Introduction to Percentages', 'Advanced', 'After reducing by 30%, the price is €140. What was the original price?', '€200', '€140', '€98', '€182', 'If 70% = €140, then 100% = 140 ÷ 0.70 = €200.'),
('Introduction to Percentages', 'Advanced', 'A value increased by 50% to reach 180. Find the original value.', '120', '180', '90', '270', 'If 150% = 180, then 100% = 180 ÷ 1.50 = 120.'),
('Introduction to Percentages', 'Advanced', 'After a 10% discount, an item costs €45. What was the original price?', '€50', '€45', '€40.50', '€49.50', 'If 90% = €45, then 100% = 45 ÷ 0.90 = €50.'),
('Introduction to Percentages', 'Advanced', 'A population decreased by 20% to 4000. What was the original population?', '5000', '4000', '4800', '3200', 'If 80% = 4000, then 100% = 4000 ÷ 0.80 = 5000.'),

-- Finding Percentage Increase/Decrease Rate (Questions 18-25)
('Introduction to Percentages', 'Advanced', 'A value increased from 50 to 60. What is the percentage increase?', '20%', '10%', '16.67%', '120%', 'Increase = 60 - 50 = 10. % increase = (10/50) × 100% = 20%.'),
('Introduction to Percentages', 'Advanced', 'A price decreased from 80 to 60. Find the percentage decrease.', '25%', '20%', '33.33%', '75%', 'Decrease = 80 - 60 = 20. % decrease = (20/80) × 100% = 25%.'),
('Introduction to Percentages', 'Advanced', 'Find the percentage increase when a value changes from 40 to 50.', '25%', '20%', '10%', '125%', 'Increase = 50 - 40 = 10. % increase = (10/40) × 100% = 25%.'),
('Introduction to Percentages', 'Advanced', 'A quantity decreased from 200 to 150. Calculate the percentage decrease.', '25%', '50%', '33.33%', '75%', 'Decrease = 200 - 150 = 50. % decrease = (50/200) × 100% = 25%.'),
('Introduction to Percentages', 'Advanced', 'Find the percentage increase from 25 to 30.', '20%', '5%', '16.67%', '120%', 'Increase = 30 - 25 = 5. % increase = (5/25) × 100% = 20%.'),
('Introduction to Percentages', 'Advanced', 'A value went from 120 to 90. What is the percentage decrease?', '25%', '30%', '33.33%', '75%', 'Decrease = 120 - 90 = 30. % decrease = (30/120) × 100% = 25%.'),
('Introduction to Percentages', 'Advanced', 'Calculate the percentage increase when a price rises from €75 to €90.', '20%', '15%', '25%', '120%', 'Increase = 90 - 75 = €15. % increase = (15/75) × 100% = 20%.'),
('Introduction to Percentages', 'Advanced', 'Find the percentage decrease from 500 to 400.', '20%', '25%', '100%', '80%', 'Decrease = 500 - 400 = 100. % decrease = (100/500) × 100% = 20%.');


-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Run these to verify the data was inserted correctly:

-- Check topic was added
-- SELECT * FROM topics WHERE name = 'Introduction to Percentages';

-- Count questions by difficulty
-- SELECT difficulty, COUNT(*) as count 
-- FROM questions 
-- WHERE topic = 'Introduction to Percentages' 
-- GROUP BY difficulty;

-- Total should be 75 questions (25 Beginner, 25 Intermediate, 25 Advanced)
