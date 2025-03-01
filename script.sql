CREATE TABLE IF NOT EXISTS refund_requests (
    id SERIAL PRIMARY KEY,
    order_id INT UNIQUE,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, approved, rejected
    approved_by TEXT DEFAULT NULL,
    customer_telegram_id BIGINT
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,    -- delivered, returned, damaged
    payment VARCHAR(20) NOT NULL,   -- online, cod (cash on delivery)
    return_period VARCHAR(20) NOT NULL,  -- within, expired
    amount DECIMAL(10,2) NOT NULL   -- Refundable amount
);
INSERT INTO orders (customer, status, payment, return_period, amount) VALUES
    ('customer_1', 'delivered', 'online', 'within', 120.00),  -- Eligible for full refund
    ('customer_2', 'delivered', 'cod', 'within', 200.00),    -- COD: Not eligible
    ('customer_3', 'returned', 'online', 'within', 150.00),  -- Eligible for partial refund
    ('customer_4', 'delivered', 'online', 'expired', 300.00),-- Return period expired
    ('customer_5', 'damaged', 'online', 'within', 180.00),   -- Damaged: Always eligible
    ('customer_6', 'returned', 'online', 'within', 600.00);  -- High value: Needs manager approval
