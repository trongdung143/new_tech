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
INSERT INTO Orders (customer_id, product_id, quantity) VALUES
(1, 2, 1),
(2, 1, 2),
(1, 3, 3);

