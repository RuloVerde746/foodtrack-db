-- =============================================
-- Inserción de datos de ejemplo en las tablas
-- =============================================

USE FoodTrack;
-- GO

-- Insertar foodtrucks
INSERT INTO foodtrucks (name, cuisine_type, city) 
VALUES 
('Taco Loco', 'Mexicana', 'Ciudad de México'),
('Burger Bros', 'Americana', 'Buenos Aires');
-- GO

-- Insertar ubicaciones
INSERT INTO locations (zone, address, latitude, longitude, capacity)
VALUES
('Centro', 'Av. Principal 123', -34.603722, -58.381592, 5),
('Parque', 'Calle Secundaria 456', -34.554742, -58.437257, 3);
-- GO

-- Insertar productos
INSERT INTO products (foodtruck_id, name, description, price)
VALUES
(1, 'Taco al pastor', 'Tacos con carne adobada y piña', 50.00),
(1, 'Quesadilla', 'Tortilla de harina con queso derretido', 40.00),
(2, 'Cheeseburger', 'Hamburguesa con queso y vegetales frescos', 70.00),
(2, 'Papas fritas', 'Papas fritas crujientes con sal', 30.00);
-- GO

-- Asignar foodtrucks a ubicaciones
INSERT INTO foodtruck_locations (foodtruck_id, location_id, assignment_date)
VALUES
(1, 1, '2023-09-01'),
(2, 2, '2023-09-01');
-- GO

-- Insertar pedidos
INSERT INTO orders (foodtruck_id, location_id, customer_name, customer_phone, status, total, order_date)
VALUES
(1, 1, 'Juan Pérez', '555-1234', 'entregado', 90.00, '2023-09-01 12:30:00'),
(2, 2, 'María García', '555-5678', 'pendiente', 100.00, '2023-09-01 13:15:00');
-- GO

-- Insertar items de pedidos
INSERT INTO order_items (order_id, product_id, quantity, price, subtotal)
VALUES
(1, 1, 1, 50.00, 50.00),
(1, 2, 1, 40.00, 40.00),
(2, 3, 1, 70.00, 70.00),
(2, 4, 1, 30.00, 30.00);
-- GO

PRINT 'Datos de ejemplo insertados correctamente';