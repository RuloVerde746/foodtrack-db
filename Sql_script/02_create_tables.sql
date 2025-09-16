-- =============================================
-- Creación de tablas para FoodTrack (versión simplificada)
-- =============================================

USE FoodTrack;
-- GO

-- =============================================
-- TABLAS PRINCIPALES
-- =============================================

-- Tabla FoodTrucks
CREATE TABLE foodtrucks (
    foodtruck_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    cuisine_type NVARCHAR(50),
    city NVARCHAR(100),
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE()
);
-- GO

-- Tabla Ubicaciones
CREATE TABLE locations (
    location_id INT IDENTITY(1,1) PRIMARY KEY,
    zone NVARCHAR(100) NOT NULL,
    address NVARCHAR(255),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    capacity INT DEFAULT 1,
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE()
);
-- GO

-- Tabla Productos
CREATE TABLE products (
    product_id INT IDENTITY(1,1) PRIMARY KEY,
    foodtruck_id INT NOT NULL,
    name NVARCHAR(100) NOT NULL,
    description NVARCHAR(500),
    price DECIMAL(10,2) NOT NULL,
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE(),
    
    CONSTRAINT fk_products_foodtruck FOREIGN KEY (foodtruck_id) REFERENCES foodtrucks(foodtruck_id)
);
-- GO

-- Tabla Pedidos
CREATE TABLE orders (
    order_id INT IDENTITY(1,1) PRIMARY KEY,
    foodtruck_id INT NOT NULL,
    location_id INT NOT NULL,
    customer_name NVARCHAR(100),
    customer_phone NVARCHAR(20),
    status NVARCHAR(20) NOT NULL DEFAULT 'pendiente'
        CHECK (status IN ('pendiente', 'confirmado', 'en_preparacion', 'listo', 'entregado', 'cancelado')),
    total DECIMAL(10,2) NOT NULL,
    order_date DATETIME NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    
    CONSTRAINT fk_orders_foodtruck FOREIGN KEY (foodtruck_id) REFERENCES foodtrucks(foodtruck_id),
    CONSTRAINT fk_orders_location FOREIGN KEY (location_id) REFERENCES locations(location_id)
);
-- GO

-- Tabla Detalles de Pedidos
CREATE TABLE order_items (
    order_item_id INT IDENTITY(1,1) PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1 CHECK (quantity > 0),
    price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    
    CONSTRAINT fk_order_items_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) REFERENCES products(product_id)
);
-- GO

-- Tabla FoodTruck Locations (relación muchos a muchos)
CREATE TABLE foodtruck_locations (
    foodtruck_location_id INT IDENTITY(1,1) PRIMARY KEY,
    foodtruck_id INT NOT NULL,
    location_id INT NOT NULL,
    assignment_date DATE NOT NULL,
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE(),
    
    CONSTRAINT fk_foodtruck_locations_foodtruck FOREIGN KEY (foodtruck_id) REFERENCES foodtrucks(foodtruck_id),
    CONSTRAINT fk_foodtruck_locations_location FOREIGN KEY (location_id) REFERENCES locations(location_id)
);
-- GO

PRINT 'Tablas creadas exitosamente con relaciones básicas';