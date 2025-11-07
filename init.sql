-- Create the transactions table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    description VARCHAR(255) NOT NULL,
    amount REAL NOT NULL,
    category VARCHAR(100) DEFAULT 'Uncategorized'
);

-- Insert some realistic sample data
INSERT INTO transactions (date, description, amount, category) VALUES
('2025-09-01', 'Salary Deposit', -5500.00, 'Income'),
('2025-09-02', 'WHOLE FOODS MARKET', 154.32, 'Groceries'),
('2025-09-03', 'NETFLIX.COM', 15.99, 'Subscriptions'),
('2025-09-04', 'STARBUCKS COFFEE', 5.75, 'Restaurants'),
('2025-09-05', 'AMAZON.COM AMZN.COM/BILL WA', 45.99, 'Shopping'),
('2025-09-06', 'SHELL OIL', 55.20, 'Transport'),
('2025-09-07', 'UBER EATS', 25.50, 'Restaurants'),
('2025-09-10', 'PG&E UTILITIES', 112.80, 'Utilities'),
('2025-09-12', 'SPOTIFY', 10.99, 'Subscriptions'),
('2025-09-15', 'TRADER JOES #123', 88.45, 'Groceries'),
('2025-09-18', 'DELTA AIRLINES TICKET', 432.50, 'Travel'),
('2025-09-20', 'CHEVRON GAS', 62.30, 'Transport'),
('2025-09-22', 'ZARA CLOTHING', 120.00, 'Uncategorized'),
('2025-09-25', 'COMCAST CABLE', 85.00, 'Utilities'),
('2025-09-26', 'Freelance Project Payment', -1200.00, 'Income'),
('2025-09-28', 'THE CHEESECAKE FACTORY', 75.68, 'Uncategorized'),
('2025-09-30', 'RENT PAYMENT', 1800.00, 'Housing');
