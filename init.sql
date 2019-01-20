DROP TABLE IF EXISTS products;
CREATE TABLE products(
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    price FLOAT NOT NULL,
    inventory_count INT NOT NULL
);