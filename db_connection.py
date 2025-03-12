# # mongo_connection.py
# import pymongo
# from pymongo import MongoClient
# from bson.objectid import ObjectId
# from datetime import datetime
# import hashlib
# import json
# import os

# # Configuración de la conexión
# CONFIG_FILE = "db_config.json"

# def load_db_config():
#     """Carga la configuración de la base de datos desde un archivo JSON"""
#     try:
#         with open(CONFIG_FILE, 'r') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         # Configuración por defecto
#         default_config = {
#             "host": "localhost",
#             "port": 27017,
#             "database": "sistema_asistencia",
#             "username": "",
#             "password": ""
#         }
        
#         # Guardar configuración por defecto
#         with open(CONFIG_FILE, 'w') as f:
#             json.dump(default_config, f, indent=4)
#         return default_config

# def get_database_connection():
#     """Establece la conexión con MongoDB y devuelve el objeto de base de datos"""
#     config = load_db_config()
    
#     try:
#         # Construir la cadena de conexión
#         if config["username"] and config["password"]:
#             connection_string = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}"
#         else:
#             connection_string = f"mongodb://{config['host']}:{config['port']}"
        
#         # Conectar a MongoDB
#         client = MongoClient(connection_string)
        
#         # Verificar la conexión
#         client.admin.command('ping')
        
#         # Obtener la base de datos
#         db = client[config["database"]]
#         print(f"Conexión establecida a MongoDB: {config['database']}")
#         return db
    
#     except Exception as e:
#         print(f"Error al conectar a MongoDB: {str(e)}")
#         return None

# def initialize_database(db):
#     """Inicializa la base de datos con las colecciones necesarias si no existen"""
#     if db is None:
#         print("No se puede inicializar la base de datos: no hay conexión.")
#         return False
    
#     try:
#         # Lista de colecciones que debe contener la base de datos
#         required_collections = [
#             "usuarios_admin",      # Administradores del sistema
#             "empleados",           # Información de empleados
#             "departamentos",       # Departamentos de la empresa
#             "horarios",            # Definición de horarios
#             "asistencias",         # Registro de entradas/salidas
#             "biometricos",         # Datos biométricos (huellas)
#             "configuracion",       # Configuración general del sistema
#             "imagenes_empleados",  # Fotos de los empleados
#             "nomina",              # Datos para cálculo de nómina
#             "empresa"              # Información de la empresa
#         ]
        
#         # Obtener colecciones existentes
#         existing_collections = db.list_collection_names()
        
#         # Crear colecciones faltantes
#         for collection in required_collections:
#             if collection not in existing_collections:
#                 db.create_collection(collection)
#                 print(f"Colección creada: {collection}")
#             else:
#                 print(f"Colección ya existe: {collection}")
        
#         # Inicializar datos por defecto solo si no existen
#         initialize_default_data(db)
        
#         print("Proceso de inicialización de base de datos completado.")
#         return True
    
#     except pymongo.errors.CollectionInvalid as e:
#         print(f"Error al crear colección: {e}")
#         return False
#     except Exception as e:
#         print(f"Error inesperado al inicializar la base de datos: {str(e)}")
#         return False

# def initialize_default_data(db):
#     """
#     Inicializa datos por defecto en la base de datos de manera segura y extensible.
    
#     Args:
#         db (pymongo.database.Database): Conexión a la base de datos MongoDB
#     """
#     try:
#         # Configuración centralizada de datos por defecto
#         default_data = {
#             "usuarios_admin": {
#                 "condition": lambda collection: collection.count_documents({}) == 0,
#                 "data": {
#                     "username": "admin",
#                     "password": hashlib.sha256("admin123".encode()).hexdigest(),
#                     "nombre": "Administrador",
#                     "apellido": "Sistema",
#                     "email": "admin@sistema.com",
#                     "role": "admin",
#                     "activo": True,
#                     "created_at": datetime.now(),
#                     "last_login": None,
#                     "intentos_fallidos": 0
#                 },
#                 "message": "Usuario administrador por defecto creado."
#             },
#             "departamentos": {
#                 "condition": lambda collection: collection.count_documents({}) == 0,
#                 "data": {
#                     "nombre": "General",
#                     "descripcion": "Departamento general de la empresa",
#                     "activo": True,
#                     "created_at": datetime.now(),
#                     "total_empleados": 0
#                 },
#                 "message": "Departamento General creado."
#             },
#             "configuracion": {
#                 "condition": lambda collection: collection.count_documents({}) == 0,
#                 "data": {
#                     "tolerancia_minutos": 10,
#                     "retardo_minutos": 15,
#                     "falta_automatica_minutos": 30,
#                     "calcular_tiempo_extra": True,
#                     "mostrar_nombre_empleado": True,
#                     "version_configuracion": "1.0",
#                     "ultimo_cambio": datetime.now(),
#                     "configuraciones_adicionales": {}
#                 },
#                 "message": "Configuración inicial creada."
#             },
#             "empresa": {
#                 "condition": lambda collection: collection.count_documents({}) == 0,
#                 "data": {
#                     "nombre": "Mi Empresa",
#                     "direccion": "Calle Principal #123",
#                     "telefono": "555-123-4567",
#                     "email": "contacto@miempresa.com",
#                     "rfc": "EMP123456ABC",
#                     "colores": {
#                         "primary": "#1976D2",
#                         "secondary": "#263238",
#                         "accent": "#4CAF50"
#                     },
#                     "logotipo": None,
#                     "fecha_fundacion": datetime(2023, 1, 1),
#                     "ultimo_cambio": datetime.now()
#                 },
#                 "message": "Información de empresa creada."
#             }
#         }

#         # Registro de operaciones realizadas
#         operaciones_realizadas = []

#         # Iterar sobre las colecciones con datos por defecto
#         for collection_name, config in default_data.items():
#             collection = db[collection_name]
            
#             # Verificar condición para insertar
#             if config["condition"](collection):
#                 try:
#                     # Insertar datos por defecto
#                     result = collection.insert_one(config["data"])
                    
#                     # Agregar a registro de operaciones
#                     operaciones_realizadas.append({
#                         "coleccion": collection_name,
#                         "mensaje": config["message"],
#                         "documento_id": result.inserted_id
#                     })
                    
#                     # Log de operación
#                     print(config["message"])
                
#                 except Exception as e:
#                     print(f"Error al inicializar {collection_name}: {e}")
        
#         # Registro consolidado de operaciones (opcional)
#         if operaciones_realizadas:
#             db["inicializacion_log"].insert_one({
#                 "fecha": datetime.now(),
#                 "operaciones": operaciones_realizadas
#             })
        
#         return True

#     except Exception as error:
#         print(f"Error crítico en inicialización de datos: {error}")
#         return False


# # Función principal para ser usada desde otras partes del sistema
# def get_db():
#     """Obtiene la conexión a la base de datos y la inicializa si es necesario"""
#     db = get_database_connection()
#     if db is not None:
#         initialize_database(db)
#     return db

# # Funciones de utilidad para trabajar con la base de datos

# def get_employee_by_id(db, employee_id):
#     """Obtiene la información de un empleado por su ID"""
#     try:
#         return db["empleados"].find_one({"_id": ObjectId(employee_id)})
#     except Exception as e:
#         print(f"Error al obtener empleado: {str(e)}")
#         return None

# def get_employee_by_rfc(db, rfc):
#     """Obtiene la información de un empleado por su RFC"""
#     try:
#         return db["empleados"].find_one({"rfc": rfc})
#     except Exception as e:
#         print(f"Error al obtener empleado por RFC: {str(e)}")
#         return None

# def register_attendance(db, employee_id, entry_type="entrada", status="NORMAL"):
#     """Registra una entrada o salida en el sistema"""
#     try:
#         # Verificar si es entrada o salida
#         if entry_type.lower() == "entrada":
#             # Registrar entrada
#             result = db["asistencias"].insert_one({
#                 "id_empleado": ObjectId(employee_id),
#                 "fecha_entrada": datetime.now(),
#                 "fecha_salida": None,
#                 "estatus": status,
#                 "observaciones": "",
#                 "created_at": datetime.now()
#             })
#             return str(result.inserted_id)
#         else:
#             # Buscar la última entrada sin salida registrada
#             last_entry = db["asistencias"].find_one(
#                 {"id_empleado": ObjectId(employee_id), "fecha_salida": None},
#                 sort=[("fecha_entrada", pymongo.DESCENDING)]
#             )
            
#             if last_entry:
#                 # Actualizar con la salida
#                 db["asistencias"].update_one(
#                     {"_id": last_entry["_id"]},
#                     {
#                         "$set": {
#                             "fecha_salida": datetime.now(),
#                             "estatus_salida": status
#                         }
#                     }
#                 )
#                 return str(last_entry["_id"])
#             else:
#                 # No hay entrada previa, crear un nuevo registro
#                 result = db["asistencias"].insert_one({
#                     "id_empleado": ObjectId(employee_id),
#                     "fecha_entrada": None,
#                     "fecha_salida": datetime.now(),
#                     "estatus": "IRREGULAR",
#                     "estatus_salida": status,
#                     "observaciones": "Salida sin entrada previa",
#                     "created_at": datetime.now()
#                 })
#                 return str(result.inserted_id)
#     except Exception as e:
#         print(f"Error al registrar asistencia: {str(e)}")
#         return None

# def get_company_info(db):
#     """Obtiene la información de la empresa"""
#     try:
#         return db["empresa"].find_one()
#     except Exception as e:
#         print(f"Error al obtener información de la empresa: {str(e)}")
#         return None

# # Ejecutar esto solo si se ejecuta este archivo directamente
# if __name__ == "__main__":
#     print("Inicializando conexión a la base de datos...")
#     db = get_db()
    
#     if db is not None:
#         print("Conexión exitosa. Base de datos lista para usar.")
#     else:
#         print("No se pudo establecer conexión a la base de datos.")

# mongo_connection.py
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import hashlib
import json
import os

# Configuración de la conexión
CONFIG_FILE = "db_config.json"

def load_db_config():
    """Carga la configuración de la base de datos desde un archivo JSON"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Configuración por defecto
        default_config = {
            "host": "localhost",
            "port": 27017,
            "database": "sistema_asistencia",
            "username": "",
            "password": ""
        }
        
        # Guardar configuración por defecto
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config

def get_database_connection():
    """Establece la conexión con MongoDB y devuelve el objeto de base de datos"""
    config = load_db_config()
    
    try:
        # Construir la cadena de conexión
        if config["username"] and config["password"]:
            connection_string = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}"
        else:
            connection_string = f"mongodb://{config['host']}:{config['port']}"
        
        # Conectar a MongoDB
        client = MongoClient(connection_string)
        
        # Verificar la conexión
        client.admin.command('ping')
        
        # Obtener la base de datos
        db = client[config["database"]]
        print(f"Conexión establecida a MongoDB: {config['database']}")
        return db
    
    except Exception as e:
        print(f"Error al conectar a MongoDB: {str(e)}")
        return None

def initialize_database(db):
    """Inicializa la base de datos con las colecciones necesarias si no existen"""
    if db is None:
        print("No se puede inicializar la base de datos: no hay conexión.")
        return False
    
    try:
        # Lista de colecciones que debe contener la base de datos
        required_collections = [
            "usuarios_admin",      # Administradores del sistema
            "empleados",           # Información de empleados
            "departamentos",       # Departamentos de la empresa
            "horarios",            # Definición de horarios
            "asistencias",         # Registro de entradas/salidas
            "biometricos",         # Datos biométricos (huellas)
            "configuracion",       # Configuración general del sistema
            "imagenes_empleados",  # Fotos de los empleados
            "nomina",              # Datos para cálculo de nómina
            "empresa"              # Información de la empresa
        ]
        
        # Obtener colecciones existentes
        existing_collections = db.list_collection_names()
        
        # Crear colecciones faltantes
        for collection in required_collections:
            if collection not in existing_collections:
                db.create_collection(collection)
                print(f"Colección creada: {collection}")
            else:
                print(f"Colección ya existe: {collection}")
        
        print("Proceso de inicialización de base de datos completado.")
        return True
    
    except pymongo.errors.CollectionInvalid as e:
        print(f"Error al crear colección: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado al inicializar la base de datos: {str(e)}")
        return False

# Función principal para ser usada desde otras partes del sistema
def get_db():
    """Obtiene la conexión a la base de datos y la inicializa si es necesario"""
    db = get_database_connection()
    if db is not None:
        initialize_database(db)
    return db

# Funciones de utilidad para trabajar con la base de datos

def get_employee_by_id(db, employee_id):
    """Obtiene la información de un empleado por su ID"""
    try:
        return db["empleados"].find_one({"_id": ObjectId(employee_id)})
    except Exception as e:
        print(f"Error al obtener empleado: {str(e)}")
        return None

def get_employee_by_rfc(db, rfc):
    """Obtiene la información de un empleado por su RFC"""
    try:
        return db["empleados"].find_one({"rfc": rfc})
    except Exception as e:
        print(f"Error al obtener empleado por RFC: {str(e)}")
        return None
    

def crear_notificacion(db, usuario_id, titulo, mensaje, tipo='sistema'):
    """
    Crea una nueva notificación para un usuario
    
    Args:
        db: Conexión a la base de datos
        usuario_id: ID del usuario que recibe la notificación
        titulo: Título de la notificación
        mensaje: Contenido de la notificación
        tipo: Tipo de notificación (sistema, asistencia, empleado, etc.)
    
    Returns:
        ObjectId de la notificación creada o None si hay un error
    """
    try:
        notificacion = {
            "usuario_id": ObjectId(usuario_id),
            "titulo": titulo,
            "mensaje": mensaje,
            "tipo": tipo,
            "fecha": datetime.now(),
            "leida": False
        }
        
        resultado = db["notificaciones"].insert_one(notificacion)
        return resultado.inserted_id
    except Exception as e:
        print(f"Error al crear notificación: {str(e)}")
        return None

def obtener_notificaciones(db, usuario_id, limite=10, solo_no_leidas=False):
    """
    Obtiene las notificaciones de un usuario
    
    Args:
        db: Conexión a la base de datos
        usuario_id: ID del usuario
        limite: Número máximo de notificaciones a recuperar
        solo_no_leidas: Si es True, devuelve solo notificaciones no leídas
    
    Returns:
        Lista de notificaciones
    """
    try:
        filtro = {"usuario_id": ObjectId(usuario_id)}
        
        if solo_no_leidas:
            filtro["leida"] = False
        
        notificaciones = list(db["notificaciones"].find(filtro)
            .sort("fecha", pymongo.DESCENDING)
            .limit(limite)
        )
        
        return notificaciones
    except Exception as e:
        print(f"Error al obtener notificaciones: {str(e)}")
        return []

def marcar_notificacion_leida(db, notificacion_id):
    """
    Marca una notificación específica como leída
    
    Args:
        db: Conexión a la base de datos
        notificacion_id: ID de la notificación a marcar
    
    Returns:
        True si se marcó con éxito, False en caso de error
    """
    try:
        resultado = db["notificaciones"].update_one(
            {"_id": ObjectId(notificacion_id)},
            {"$set": {"leida": True}}
        )
        return resultado.modified_count > 0
    except Exception as e:
        print(f"Error al marcar notificación como leída: {str(e)}")
        return False

def marcar_todas_notificaciones_leidas(db, usuario_id):
    """
    Marca todas las notificaciones de un usuario como leídas
    
    Args:
        db: Conexión a la base de datos
        usuario_id: ID del usuario
    
    Returns:
        Número de notificaciones marcadas como leídas
    """
    try:
        resultado = db["notificaciones"].update_many(
            {
                "usuario_id": ObjectId(usuario_id),
                "leida": False
            },
            {"$set": {"leida": True}}
        )
        return resultado.modified_count
    except Exception as e:
        print(f"Error al marcar todas las notificaciones como leídas: {str(e)}")
        return 0

def contar_notificaciones_no_leidas(db, usuario_id):
    """
    Cuenta el número de notificaciones no leídas para un usuario
    
    Args:
        db: Conexión a la base de datos
        usuario_id: ID del usuario
    
    Returns:
        Número de notificaciones no leídas
    """
    try:
        return db["notificaciones"].count_documents({
            "usuario_id": ObjectId(usuario_id),
            "leida": False
        })
    except Exception as e:
        print(f"Error al contar notificaciones no leídas: {str(e)}")
        return 0

def register_attendance(db, employee_id, entry_type="entrada", status="NORMAL"):
    """Registra una entrada o salida en el sistema"""
    try:
        # Verificar si es entrada o salida
        if entry_type.lower() == "entrada":
            # Registrar entrada
            result = db["asistencias"].insert_one({
                "id_empleado": ObjectId(employee_id),
                "fecha_entrada": datetime.now(),
                "fecha_salida": None,
                "estatus": status,
                "observaciones": "",
                "created_at": datetime.now()
            })
            return str(result.inserted_id)
        else:
            # Buscar la última entrada sin salida registrada
            last_entry = db["asistencias"].find_one(
                {"id_empleado": ObjectId(employee_id), "fecha_salida": None},
                sort=[("fecha_entrada", pymongo.DESCENDING)]
            )
            
            if last_entry:
                # Actualizar con la salida
                db["asistencias"].update_one(
                    {"_id": last_entry["_id"]},
                    {
                        "$set": {
                            "fecha_salida": datetime.now(),
                            "estatus_salida": status
                        }
                    }
                )
                return str(last_entry["_id"])
            else:
                # No hay entrada previa, crear un nuevo registro
                result = db["asistencias"].insert_one({
                    "id_empleado": ObjectId(employee_id),
                    "fecha_entrada": None,
                    "fecha_salida": datetime.now(),
                    "estatus": "IRREGULAR",
                    "estatus_salida": status,
                    "observaciones": "Salida sin entrada previa",
                    "created_at": datetime.now()
                })
                return str(result.inserted_id)
    except Exception as e:
        print(f"Error al registrar asistencia: {str(e)}")
        return None

def get_company_info(db):
    """Obtiene la información de la empresa"""
    try:
        return db["empresa"].find_one()
    except Exception as e:
        print(f"Error al obtener información de la empresa: {str(e)}")
        return None

# Ejecutar esto solo si se ejecuta este archivo directamente
if __name__ == "__main__":
    print("Inicializando conexión a la base de datos...")
    db = get_db()
    
    if db is not None:
        print("Conexión exitosa. Base de datos lista para usar.")
    else:
        print("No se pudo establecer conexión a la base de datos.")