import pyodbc
import pandas as pd
import os
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('carga_datos.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class CargadorDatosFoodTrack:
    def __init__(self, server, database, username='', password=''):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.conn = None
        self.cursor = None
        
    def conectar(self):
        """Establece conexión con SQL Server usando Windows Authentication"""
        try:
            if self.username and self.password:
                # SQL Authentication
                connection_string = (
                    f'DRIVER={{SQL Server}};'
                    f'SERVER={self.server};'
                    f'DATABASE={self.database};'
                    f'UID={self.username};'
                    f'PWD={self.password}'
                )
            else:
                # Windows Authentication
                connection_string = (
                    f'DRIVER={{SQL Server}};'
                    f'SERVER={self.server};'
                    f'DATABASE={self.database};'
                    f'Trusted_Connection=yes;'
                )
            
            self.conn = pyodbc.connect(connection_string)
            self.cursor = self.conn.cursor()
            logging.info("Conexión exitosa a SQL Server")
            return True
            
        except pyodbc.Error as e:
            logging.error(f"Error de conexión: {str(e)}")
            return False
    
    def crear_tabla_errores(self):
        """Crea tabla auxiliar para registrar errores si no existe"""
        try:
            create_table_query = '''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='failed_inserts' AND xtype='U')
            CREATE TABLE failed_inserts (
                id INT IDENTITY(1,1) PRIMARY KEY,
                tabla VARCHAR(100),
                datos NVARCHAR(MAX),
                error NVARCHAR(500),
                fecha DATETIME DEFAULT GETDATE()
            )
            '''
            self.cursor.execute(create_table_query)
            self.conn.commit()
            logging.info("Tabla de errores verificada/creada exitosamente")
            return True
        except pyodbc.Error as e:
            logging.error(f"Error al crear tabla de errores: {str(e)}")
            return False
    
    def registrar_error(self, tabla, datos, error):
        """Registra un error en la tabla de errores"""
        try:
            # Limitar el tamaño del mensaje de error para evitar truncamiento
            error_msg = str(error)[:500] if error else 'Error desconocido'
            datos_str = str(datos)[:1000] if datos else 'Sin datos'
            
            insert_error_query = '''
            INSERT INTO failed_inserts (tabla, datos, error)
            VALUES (?, ?, ?)
            '''
            self.cursor.execute(insert_error_query, tabla, datos_str, error_msg)
            self.conn.commit()
            logging.warning(f"Error registrado en failed_inserts: {error_msg}")
            return True
        except pyodbc.Error as e:
            logging.error(f"Error crítico al registrar error: {str(e)}")
            return False
    
    def cargar_csv(self, nombre_tabla, archivo_csv, columnas):
        """
        Carga datos desde un CSV a la tabla especificada
        nombre_tabla: Nombre de la tabla destino
        archivo_csv: Nombre del archivo CSV en la carpeta 'data'
        columnas: String con nombres de columnas separados por coma
        """
        try:
            # Leer CSV
            ruta_archivo = os.path.join('data', archivo_csv)
            if not os.path.exists(ruta_archivo):
                logging.error(f"Archivo no encontrado: {ruta_archivo}")
                return 0, 0
            
            df = pd.read_csv(ruta_archivo)
            total_registros = len(df)
            exitosos = 0
            fallidos = 0
            
            logging.info(f"Leyendo {archivo_csv} - {total_registros} registros")
            
            # Preparar query de inserción
            placeholders = ', '.join(['?' for _ in range(len(df.columns))])
            insert_query = f"INSERT INTO {nombre_tabla} ({columnas}) VALUES ({placeholders})"
            
            # Insertar datos
            for index, row in df.iterrows():
                try:
                    self.cursor.execute(insert_query, tuple(row))
                    self.conn.commit()
                    exitosos += 1
                    
                except pyodbc.Error as e:
                    self.registrar_error(nombre_tabla, tuple(row), str(e))
                    fallidos += 1
                    # Hacer rollback para limpiar la transacción fallida
                    self.conn.rollback()
            
            logging.info(f"{nombre_tabla} - {exitosos} exitosos, {fallidos} fallidos")
            return exitosos, fallidos
            
        except Exception as e:
            logging.error(f"Error procesando {archivo_csv}: {str(e)}")
            return 0, 0
    
    def generar_reporte_final(self):
        """Genera un reporte con las estadísticas de carga"""
        try:
            query = '''
            SELECT 'foodtrucks' as tabla, COUNT(*) as registros FROM foodtrucks
            UNION ALL SELECT 'products', COUNT(*) FROM products
            UNION ALL SELECT 'orders', COUNT(*) FROM orders
            UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
            UNION ALL SELECT 'locations', COUNT(*) FROM locations
            UNION ALL SELECT 'failed_inserts', COUNT(*) FROM failed_inserts
            '''
            
            self.cursor.execute(query)
            resultados = self.cursor.fetchall()
            
            logging.info("\nRESULTADOS FINALES:")
            for tabla, registros in resultados:
                logging.info(f"   {tabla}: {registros} registros")
                
            return resultados
            
        except pyodbc.Error as e:
            logging.error(f"Error generando reporte: {str(e)}")
            return None
    
    def cerrar_conexion(self):
        """Cierra la conexión a la base de datos"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            logging.info("Conexión cerrada correctamente")
        except pyodbc.Error as e:
            logging.error(f"Error al cerrar conexión: {str(e)}")

# Función principal
def main():
    # Configuración
    config = {
        'server': 'localhost\\SQLEXPRESS',
        'database': 'FoodTrackDB',
        'username': '',  # Vacío para Windows Auth
        'password': ''   # Vacío para Windows Auth
    }
    
    # Orden de carga (respetando relaciones)
    carga_config = [
        {'tabla': 'foodtrucks', 'archivo': 'foodtrucks.csv', 'columnas': 'foodtruck_id, name, cuisine_type, city'},
        {'tabla': 'products', 'archivo': 'products.csv', 'columnas': 'product_id, foodtruck_id, name, price, stock'},
        {'tabla': 'orders', 'archivo': 'orders.csv', 'columnas': 'order_id, foodtruck_id, order_date, status, total'},
        {'tabla': 'locations', 'archivo': 'locations.csv', 'columnas': 'location_id, foodtruck_id, location_date, zone'},
        {'tabla': 'order_items', 'archivo': 'order_items.csv', 'columnas': 'order_item_id, order_id, product_id, quantity'}
    ]
    
    # Crear instancia del cargador
    cargador = CargadorDatosFoodTrack(
        config['server'],
        config['database'],
        config['username'],
        config['password']
    )
    
    try:
        # Conectar a la base de datos
        if not cargador.conectar():
            return
        
        # Crear tabla de errores
        if not cargador.crear_tabla_errores():
            logging.warning("Continuando sin tabla de errores")
        
        # Cargar datos en orden
        total_exitosos = 0
        total_fallidos = 0
        
        for config_carga in carga_config:
            exitosos, fallidos = cargador.cargar_csv(
                config_carga['tabla'],
                config_carga['archivo'],
                config_carga['columnas']
            )
            total_exitosos += exitosos
            total_fallidos += fallidos
        
        # Generar reporte final
        cargador.generar_reporte_final()
        
        # Resumen general
        logging.info(f"\nRESUMEN GENERAL:")
        logging.info(f"   Total exitosos: {total_exitosos}")
        logging.info(f"   Total fallidos: {total_fallidos}")
        logging.info(f"   Tasa de éxito: {(total_exitosos/(total_exitosos+total_fallidos)*100 if (total_exitosos+total_fallidos) > 0 else 0):.2f}%")
        
    except Exception as e:
        logging.error(f"Error general en la ejecución: {str(e)}")
    
    finally:
        # Cerrar conexión
        cargador.cerrar_conexion()

if __name__ == "__main__":
    main()