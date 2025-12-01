-- Product
CREATE TABLE Product (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    price NUMERIC NOT NULL,
    stock INT NOT NULL
);

-- Customer
CREATE TABLE Customer (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL
);

-- Orders
CREATE TABLE Orders (
    id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES Customer(id),
    order_date TIMESTAMP NOT NULL DEFAULT NOW()
);

-- OrderItem
CREATE TABLE OrderItem (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES Orders(id),
    product_id INT NOT NULL REFERENCES Product(id),
    quantity INT NOT NULL
);





-- Product
INSERT INTO Product (name, price, stock) VALUES
('Laptop', 1200, 10),
('Mouse', 25, 100),
('Keyboard', 50, 50),
('Monitor', 300, 20);

-- Customer
INSERT INTO Customer (name, email) VALUES
('Alice', 'alice@example.com'),
('Bob', 'bob@example.com'),
('Charlie', 'charlie@example.com');

-- Orders
INSERT INTO Orders (customer_id, order_date) VALUES
(1, '2025-11-20'),
(2, '2025-11-21'),
(1, '2025-11-22');

-- OrderItem
INSERT INTO OrderItem (order_id, product_id, quantity) VALUES
(1, 1, 1),  
(1, 2, 2),  
(2, 3, 1),  
(3, 4, 2);  
