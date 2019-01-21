DROP TABLE IF EXISTS products;
CREATE TABLE products(
    product_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    price FLOAT NOT NULL,
    inventory_count INT NOT NULL
);

DROP TABLE IF EXISTS shopping_carts;
CREATE TABLE shopping_carts(
    shopping_cart_id SERIAL PRIMARY KEY
);

DROP TABLE IF EXISTS shopping_cart_products;
CREATE TABLE shopping_cart_products(
    id SERIAL PRIMARY KEY,
    shopping_cart_id BIGINT UNSIGNED NOT NULL,
    product_id BIGINT UNSIGNED NOT NULL,
    FOREIGN KEY(product_id) REFERENCES products(product_id),
    FOREIGN KEY(shopping_cart_id) REFERENCES shopping_carts(shopping_cart_id)
);