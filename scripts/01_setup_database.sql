-- =============================================
-- Configuración inicial de la base de datos FoodTrack
-- =============================================

-- Crear la base de datos
CREATE DATABASE FoodTrack;
GO

-- Usar la base de datos recién creada
USE FoodTrack;
GO

-- Configurar opciones de la base de datos
ALTER DATABASE FoodTrack SET RECOVERY SIMPLE;
ALTER DATABASE FoodTrack SET AUTO_CREATE_STATISTICS ON;
-- ALTER DATABASE FoodTrack SET AUTO_UPDATE_STATISTICS ON;
GO

-- Crear esquemas para organizar las tablas
CREATE SCHEMA dim; -- Para tablas de dimensiones
CREATE SCHEMA fact; -- Para tablas de hechos
GO

PRINT 'Base de datos FoodTrack configurada exitosamente';