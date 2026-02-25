-- Tabla de usuarios
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de productos
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    stock INTEGER DEFAULT 0,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de carritos
CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de items del carrito
CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER REFERENCES carts(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_carts_user_id ON carts(user_id);
CREATE INDEX idx_cart_items_cart_id ON cart_items(cart_id);
CREATE INDEX idx_cart_items_product_id ON cart_items(product_id);

-- Datos de prueba
INSERT INTO products (name, description, price, stock, image_url) VALUES
('Laptop HP Pavilion', 'Laptop de 15 pulgadas con procesador Intel Core i5', 1299.99, 10, 'https://via.placeholder.com/300'),
('Mouse Inalámbrico', 'Mouse ergonómico inalámbrico con receptor USB', 29.99, 50, 'https://via.placeholder.com/300'),
('Teclado Mecánico', 'Teclado RGB mecánico con switches azules', 89.99, 25, 'https://via.placeholder.com/300'),
('Monitor 24"', 'Monitor Full HD de 24 pulgadas', 199.99, 15, 'https://via.placeholder.com/300'),
('Auriculares Bluetooth', 'Auriculares con cancelación de ruido', 149.99, 30, 'https://via.placeholder.com/300'),
('Webcam HD', 'Cámara web 1080p con micrófono integrado', 59.99, 40, 'https://via.placeholder.com/300'),
('Disco SSD 500GB', 'Disco sólido interno de 500GB', 79.99, 20, 'https://via.placeholder.com/300'),
('USB Flash 64GB', 'Memoria USB 3.0 de 64GB', 12.99, 100, 'https://via.placeholder.com/300');
