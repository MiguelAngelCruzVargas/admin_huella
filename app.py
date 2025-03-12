# Importaciones estándar de Python
import os
import io
import csv
import json
import hashlib
from datetime import datetime, timedelta
import secrets

# Importaciones de Flask
from flask import (
    Flask, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash, 
    session, 
    jsonify, 
    send_file, 
    Response
)

# Importaciones de seguridad y manejo de archivos
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# Importaciones para manejo de datos y reportes
import pandas as pd
import xlsxwriter
from fpdf import FPDF

# Importaciones de base de datos (ajusta según tu configuración)
from db_connection import*

# Importaciones para manejo de tipos de datos
from bson.objectid import ObjectId
from typing import Dict, List, Any

# Importaciones para manejo de fechas (más modernas)
import pytz

# Opcional: para logging mejorado
import logging
from logging.handlers import RotatingFileHandler

# Opcional: para validaciones
import re  # Para validaciones de formato
from email_validator import validate_email, EmailNotValidError



base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, 
            template_folder=template_dir,
            static_folder=static_dir)
app.secret_key = secrets.token_hex(16)  # o cualquier definición de clave secreta que tengas

# Diagnóstico
print(f"Ruta base: {base_dir}")
print(f"Directorio de templates: {template_dir}")
print(f"¿El directorio de templates existe? {os.path.exists(template_dir)}")
if os.path.exists(template_dir):
    print(f"Archivos en {template_dir}: {os.listdir(template_dir)}")

# Clave secreta - genera una clave más segura
import secrets
app.secret_key = secrets.token_hex(16)  # Genera una clave secreta aleatoria


# Configuración de la sesión
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
# Desactivar requisito de HTTPS para las cookies de sesión (solo en desarrollo)
app.config['SESSION_COOKIE_SECURE'] = False  
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Conectar a la base de datos
db = None
try:
    db = get_db()
    if db is not None:
        db.command('ping')
        print("Conexión a la base de datos establecida correctamente")
        initialize_database(db)
    else:
        print("No se pudo establecer la conexión a la base de datos")
except Exception as e:
    print(f"Error crítico al conectar a la base de datos: {e}")
    db = None



###################################################


# Modificación a la ruta index para redirigir a setup si es necesario
@app.route('/')
def index():
    # Verificar si el sistema está configurado (existe al menos un usuario admin)
    if db is not None and db.usuarios_admin.count_documents({}) == 0:
        return redirect(url_for('setup'))
        
    # Si está configurado, proceder normalmente
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Nueva ruta para configuración inicial
@app.route('/setup', methods=['GET', 'POST'])
def setup():
    # Verificar si ya existe un administrador
    if db is not None and db.usuarios_admin.count_documents({}) > 0:
        flash('El sistema ya ha sido configurado')
        return redirect(url_for('login'))
    
    # Variable para mostrar mensajes de error
    error = None
    
    if request.method == 'POST':
        try:
            # 1. Datos de la empresa
            empresa_data = {
                'nombre': request.form.get('empresa_nombre'),
                'direccion': request.form.get('empresa_direccion'),
                'telefono': request.form.get('empresa_telefono'),
                'email': request.form.get('empresa_email'),
                'rfc': request.form.get('empresa_rfc'),
                'colores': {
                    'primary': '#1976D2',
                    'secondary': '#263238',
                    'accent': '#4CAF50'
                },
                'configurado': True,
                'fecha_configuracion': datetime.now()
            }
            
            # 2. Datos del administrador
            username = request.form.get('admin_username')
            password = request.form.get('admin_password')
            confirm_password = request.form.get('admin_confirm_password')
            nombre = request.form.get('admin_nombre')
            apellido = request.form.get('admin_apellido')
            email = request.form.get('admin_email')
            
            # Validaciones básicas
            if not all([username, password, confirm_password, nombre, apellido, email]):
                error = 'Todos los campos del administrador son obligatorios'
                return render_template('setup.html', error=error)
            
            if password != confirm_password:
                error = 'Las contraseñas no coinciden'
                return render_template('setup.html', error=error)
            
            if len(password) < 6:
                error = 'La contraseña debe tener al menos 6 caracteres'
                return render_template('setup.html', error=error)
            
            # Encriptar contraseña
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # 3. Datos de configuración general
            config_data = {
                'tolerancia_minutos': int(request.form.get('config_tolerancia', 10)),
                'retardo_minutos': int(request.form.get('config_retardo', 15)),
                'falta_automatica_minutos': int(request.form.get('config_falta', 30)),
                'calcular_tiempo_extra': request.form.get('config_tiempo_extra') == 'on',
                'mostrar_nombre_empleado': request.form.get('config_mostrar_nombre') == 'on',
                'ultimo_cambio': datetime.now()
            }
            
            # Guardar en la base de datos
            if db is not None:
                # Guardar información de la empresa
                db.empresa.insert_one(empresa_data)
                
                # Guardar configuración
                db.configuracion.insert_one(config_data)
                
                # Crear administrador
                db.usuarios_admin.insert_one({
                    'username': username,
                    'password': password_hash,
                    'nombre': nombre,
                    'apellido': apellido,
                    'email': email,
                    'role': 'admin',
                    'activo': True,
                    'created_at': datetime.now()
                })
                
                # Crear departamento general
                db.departamentos.insert_one({
                    'nombre': 'General',
                    'descripcion': 'Departamento general de la empresa',
                    'activo': True,
                    'created_at': datetime.now()
                })
                
                flash('Configuración inicial completada correctamente')
                return redirect(url_for('login'))
            else:
                error = 'Error de conexión a la base de datos'
        
        except Exception as e:
            print(f"Error en configuración inicial: {str(e)}")
            error = f'Error al crear configuración inicial: {str(e)}'
    
    # Para solicitudes GET o en caso de error
    return render_template('setup.html', error=error)

####################### LOGIN ##########################
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Imprimir estado actual de la sesión para depuración
    print("Current session before login:", dict(session))
    
    # Verificar si el sistema ya está configurado
    if db is not None and db.usuarios_admin.count_documents({}) == 0:
        # Sistema no configurado, redirigir a la página de configuración
        return redirect(url_for('setup'))
    
    # Añadir diagnóstico de rutas
    import os
    print("Directorio de trabajo actual:", os.getcwd())
    print("Ruta absoluta del script:", os.path.abspath(__file__))
    print("Contenido de la carpeta templates:", os.listdir('templates'))
    
    # Añadir soporte para el año actual en el template
    current_year = datetime.now().year

    error = None
    first_run = False
    max_intentos = 5

    try:
        # Verificación de primera ejecución
        if db is not None:
            usuarios_count = db.usuarios_admin.count_documents({})
            first_run = usuarios_count == 0
        else:
            error = 'Error crítico: Base de datos no disponible'
            return render_template('login.html', 
                                   error=error, 
                                   first_run=False, 
                                   now=type('obj', (object,), {'year': current_year}))

    except Exception as e:
        print(f"Error al verificar usuarios iniciales: {e}")
        error = 'Error al verificar configuración inicial'
        return render_template('login.html', 
                               error=error, 
                               first_run=False, 
                               now=type('obj', (object,), {'year': current_year}))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validaciones de entrada
        if not username or not password:
            error = 'Por favor ingrese usuario y contraseña'
            return render_template('login.html', 
                                   error=error, 
                                   first_run=first_run, 
                                   now=type('obj', (object,), {'year': current_year}))

        try:
            # Encriptar la contraseña de manera segura
            password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
            
            # Verificación de usuario
            if db is not None:
                usuario = db.usuarios_admin.find_one({
                    'username': username,
                    'password': password_hash
                })
                
                if usuario:
                    # Imprimir información del usuario encontrado para depuración
                    print(f"Usuario encontrado: {username}")
                    print(f"ID del usuario: {usuario['_id']}")
                    
                    # Verificar estado del usuario
                    if not usuario.get('activo', True):
                        error = 'Usuario inactivo. Contacte al administrador.'
                        return render_template('login.html', 
                                               error=error, 
                                               first_run=first_run, 
                                               now=type('obj', (object,), {'year': current_year}))
                    
                    # Reiniciar intentos fallidos
                    db.usuarios_admin.update_one(
                        {'username': username},
                        {'$set': {'intentos_fallidos': 0}}
                    )

                    # Guardar información de sesión
                    session.clear()  # Limpiar sesión previa
                    session['usuario_id'] = str(usuario['_id'])
                    session['nombre'] = usuario.get('nombre', '')
                    session['apellido'] = usuario.get('apellido', '')
                    session['username'] = usuario['username']
                    session['role'] = usuario.get('role', 'user')
                    session['login_time'] = datetime.now().isoformat()
                    session.permanent = True
                    
                    # Imprimir estado de la sesión después de guardar
                    print("Session after login:", dict(session))
                    print("usuario_id in session:", session.get('usuario_id'))
                    
                    # Registrar inicio de sesión
                    try:
                        db.usuarios_admin.update_one(
                            {'_id': usuario['_id']},
                            {'$set': {
                                'ultimo_inicio_sesion': datetime.now(),
                                'ip_ultimo_inicio': request.remote_addr
                            }}
                        )
                    except Exception as log_error:
                        print(f"Error al registrar inicio de sesión: {log_error}")

                    # Registro de auditoría
                    try:
                        db.auditoria_sesiones.insert_one({
                            'usuario_id': str(usuario['_id']),
                            'username': usuario['username'],
                            'fecha_inicio': datetime.now(),
                            'ip': request.remote_addr,
                            'tipo_evento': 'inicio_sesion_exitoso'
                        })
                    except Exception as audit_error:
                        print(f"Error en registro de auditoría: {audit_error}")
                    
                    # Redireccionar al dashboard con flash message para verificar
                    flash('Inicio de sesión exitoso', 'success')
                    return redirect(url_for('dashboard'))
                
                else:
                    # Manejar intentos fallidos
                    intentos_usuario = db.usuarios_admin.find_one({'username': username})
                    intentos_actuales = intentos_usuario.get('intentos_fallidos', 0) + 1 if intentos_usuario else 1
                    
                    if intentos_actuales >= max_intentos:
                        # Bloquear usuario
                        db.usuarios_admin.update_one(
                            {'username': username},
                            {'$set': {
                                'activo': False, 
                                'fecha_bloqueo': datetime.now(),
                                'intentos_fallidos': intentos_actuales
                            }}
                        )
                        error = 'Cuenta bloqueada. Contacte al administrador.'
                    else:
                        # Incrementar intentos fallidos
                        db.usuarios_admin.update_one(
                            {'username': username},
                            {'$set': {'intentos_fallidos': intentos_actuales}}
                        )
                        error = 'Usuario o contraseña incorrectos'
                    
                    # Registro de intento fallido
                    try:
                        db.auditoria_sesiones.insert_one({
                            'username': username,
                            'fecha_intento': datetime.now(),
                            'ip': request.remote_addr,
                            'tipo_evento': 'inicio_sesion_fallido'
                        })
                    except Exception as audit_error:
                        print(f"Error en registro de auditoría: {audit_error}")

            else:
                error = 'Error crítico: Base de datos no disponible'

        except Exception as e:
            print(f"Error durante el proceso de login: {e}")
            error = 'Error interno del sistema'

    # Obtener información de la empresa para personalizar la página de login
    empresa_info = None
    try:
        if db is not None:
            empresa_info = db.empresa.find_one()
    except Exception as e:
        print(f"Error al obtener información de empresa: {e}")

    return render_template('login.html', 
                           error=error, 
                           first_run=first_run, 
                           now=type('obj', (object,), {'year': current_year}),
                           empresa=empresa_info)
#############################################################

@app.route('/marcar_todas_notificaciones_leidas', methods=['POST'])
def marcar_todas_notificaciones_leidas_route():
    if 'usuario_id' not in session:
        return jsonify({"error": "No autenticado"}), 401
    
    db = get_db()
    if db is None:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        resultado = marcar_todas_notificaciones_leidas(db, session['usuario_id'])
        return jsonify({
            "success": True, 
            "marcadas": resultado
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/obtener_notificaciones', methods=['GET'])
def obtener_notificaciones_route():
    if 'usuario_id' not in session:
        return jsonify({"error": "No autenticado"}), 401
    
    db = get_db()
    if db is None:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    notificaciones = obtener_notificaciones(db, session['usuario_id'])
    
    # Convertir ObjectId a string para serialización JSON
    for notificacion in notificaciones:
        notificacion['_id'] = str(notificacion['_id'])
        notificacion['usuario_id'] = str(notificacion['usuario_id'])
        notificacion['fecha'] = notificacion['fecha'].isoformat()
    
    return jsonify(notificaciones)

# Corrección en la ruta primera-configuracion
@app.route('/primera-configuracion', methods=['POST'])
def primera_configuracion():
    if db is not None and db.usuarios_admin.count_documents({}) == 0:
        # Validar datos
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('email')
        
        # Validaciones básicas
        if not all([username, password, confirm_password, nombre, apellido, email]):
            flash('Todos los campos son obligatorios')
            return redirect(url_for('login'))
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden')
            return redirect(url_for('login'))
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres')
            return redirect(url_for('login'))
        
        # Encriptar contraseña
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Crear usuario administrador
        try:
            db.usuarios_admin.insert_one({
                'username': username,
                'password': password_hash,
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'role': 'admin',
                'activo': True,
                'created_at': datetime.now()  # Corregido datetime.datetime.now() a datetime.now()
            })
            flash('Configuración inicial completada correctamente')
        except Exception as e:
            flash(f'Error al crear usuario: {str(e)}')
    
    return redirect(url_for('login'))

#################################################

###################################3

@app.route('/dashboard')
def dashboard():
    print("Session in dashboard:", dict(session))
    print("usuario_id in dashboard:", session.get('usuario_id'))
    
    # Verificar primero si hay usuario en sesión
    if 'usuario_id' not in session:
        print("No usuario_id in session, redirecting to login")
        flash('Por favor inicie sesión para acceder', 'warning')
        return redirect(url_for('login'))
    
    # Obtener la conexión a la base de datos
    db = get_db()
    
    if db is None:
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('login'))
    
    # Contar notificaciones no leídas
    try:
        notificaciones_no_leidas = contar_notificaciones_no_leidas(db, session['usuario_id'])
    except Exception as e:
        print(f"Error al contar notificaciones: {e}")
        notificaciones_no_leidas = 0
    
    # Obtener estadísticas básicas
    stats = {
        'total_empleados': db.empleados.count_documents({}),
        'asistencias_hoy': db.asistencias.count_documents({
            'fecha_entrada': {'$gte': datetime.now().replace(hour=0, minute=0, second=0)}
        }),
        'departamentos': db.departamentos.count_documents({})
    }
    
    # Obtener asistencias recientes con detalles de empleados
    asistencias_recientes = list(db.asistencias.aggregate([
        {
            '$match': {
                'fecha_entrada': {'$gte': datetime.now().replace(hour=0, minute=0, second=0)}
            }
        },
        {
            '$lookup': {
                'from': 'empleados',
                'localField': 'id_empleado',  # Corregido de 'empleado_id'
                'foreignField': '_id',
                'as': 'empleado_info'
            }
        },
        {
            '$unwind': '$empleado_info'
        },
        {
            '$project': {
                'empleado': {
                    'nombre': '$empleado_info.nombre',
                    'apellido': '$empleado_info.apellidos'
                },
                'hora_entrada': '$fecha_entrada',
                'hora_salida': '$fecha_salida',
                'estado': {
                    '$cond': [
                        {'$eq': ['$fecha_salida', None]}, 'pendiente',
                        {'$cond': [
                            {'$lt': ['$fecha_entrada', datetime.now().replace(hour=8, minute=0, second=0)]}, 
                            'normal', 
                            'retardo'
                        ]}
                    ]
                }
            }
        },
        {
            '$limit': 4  # Limitar a 4 registros
        }
    ]))
    
    # Añadir la fecha actual para la plantilla
    current_datetime = datetime.now()
    
    return render_template('dashboard.html', 
                           stats=stats, 
                           usuario=session,
                           now=current_datetime,
                           notificaciones_no_leidas=notificaciones_no_leidas,
                           asistencias_recientes=asistencias_recientes)
############ crear empleados
@app.route('/empleados/crear', methods=['POST'])
def crear_empleado():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        # Manejar archivo de foto
        foto = request.files.get('foto')
        foto_filename = None
        if foto:
            # Guardar foto en directorio de imágenes de empleados
            foto_filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{foto.filename}")
            foto.save(os.path.join('static/img/empleados', foto_filename))
        
        # Preparar datos del empleado
        nuevo_empleado = {
            'nombre': request.form.get('nombre'),
            'apellidos': request.form.get('apellidos'),
            'rfc': request.form.get('rfc'),
            'curp': request.form.get('curp'),
            'departamento': request.form.get('departamento'),
            'horario_id': request.form.get('horario'),
            'fecha_ingreso': datetime.strptime(request.form.get('fecha_ingreso'), '%Y-%m-%d'),
            'direccion': request.form.get('direccion'),
            'foto': foto_filename,
            'activo': True,
            'created_at': datetime.now(),
            'created_by': session['usuario_id']
        }
        
        # Guardar en base de datos
        if db is not None:
            resultado = db.empleados.insert_one(nuevo_empleado)
            
            return jsonify({
                'success': True, 
                'message': 'Empleado creado exitosamente',
                'empleado_id': str(resultado.inserted_id)
            }), 201
        else:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
    
    except Exception as e:
        print(f"Error al crear empleado: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500

@app.route('/empleados/ver/<empleado_id>', methods=['GET'])
def ver_empleado(empleado_id):
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        from bson.objectid import ObjectId
        
        if db is not None:
            # Buscar empleado con información de departamento
            pipeline = [
                {'$match': {'_id': ObjectId(empleado_id)}},
                {
                    '$lookup': {
                        'from': 'departamentos',
                        'localField': 'departamento',
                        'foreignField': '_id',
                        'as': 'dept_info'
                    }
                },
                {
                    '$lookup': {
                        'from': 'horarios',
                        'localField': 'horario_id',
                        'foreignField': '_id',
                        'as': 'horario_info'
                    }
                }
            ]
            
            empleado = list(db.empleados.aggregate(pipeline))
            
            if empleado:
                empleado = empleado[0]
                # Convertir ObjectId a string
                empleado['_id'] = str(empleado['_id'])
                empleado['departamento'] = empleado['dept_info'][0]['nombre'] if empleado['dept_info'] else 'Sin departamento'
                empleado['horario'] = empleado['horario_info'][0]['nombre'] if empleado['horario_info'] else 'Sin horario'
                
                return jsonify(empleado), 200
            else:
                return jsonify({'success': False, 'message': 'Empleado no encontrado'}), 404
        else:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
    
    except Exception as e:
        print(f"Error al ver empleado: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500
    
########################
@app.route('/empleados')
def empleados():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    # Obtener lista de empleados
    empleados_list = []
    if db is not None:  # Usar "is not None" en lugar de "if db:"
        empleados_cursor = db.empleados.find().sort('apellidos', 1)
        for emp in empleados_cursor:
            emp['_id'] = str(emp['_id'])  # Convertir ObjectId a string
            empleados_list.append(emp)
    
    return render_template('empleados.html', 
                          usuario=session,
                          empleados=empleados_list)


@app.route('/horarios')
def horarios():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    # Obtener lista de horarios
    horarios_list = []
    if db is not None:  # Usar "is not None" en lugar de "if db:"
        horarios_cursor = db.horarios.find()
        for horario in horarios_cursor:
            horario['_id'] = str(horario['_id'])
            horarios_list.append(horario)
    
    return render_template('horarios.html', 
                          usuario=session,
                          horarios=horarios_list)


@app.route('/horarios/crear', methods=['POST'])
def crear_horario():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        # Obtener datos del horario desde la solicitud JSON
        horario_data = request.get_json()
        
        # Validaciones básicas
        if not horario_data.get('nombre'):
            return jsonify({'success': False, 'message': 'El nombre del horario es obligatorio'}), 400
        
        if not horario_data.get('hora_entrada'):
            return jsonify({'success': False, 'message': 'La hora de entrada es obligatoria'}), 400
        
        if not horario_data.get('hora_salida'):
            return jsonify({'success': False, 'message': 'La hora de salida es obligatoria'}), 400
        
        if not horario_data.get('dias_laborales') or len(horario_data.get('dias_laborales', [])) == 0:
            return jsonify({'success': False, 'message': 'Debe seleccionar al menos un día laboral'}), 400
        
        # Preparar datos para guardar en la base de datos
        nuevo_horario = {
            'nombre': horario_data.get('nombre'),
            'hora_entrada': horario_data.get('hora_entrada'),
            'hora_salida': horario_data.get('hora_salida'),
            'tolerancia_minutos': int(horario_data.get('tolerancia_minutos', 0)),
            'dias_laborales': horario_data.get('dias_laborales', []),
            'created_at': datetime.now(),
            'created_by': session['usuario_id']
        }
        
        # Guardar en la base de datos
        if db is not None:
            resultado = db.horarios.insert_one(nuevo_horario)
            
            # Devolver respuesta
            return jsonify({
                'success': True, 
                'message': 'Horario creado exitosamente',
                'horario_id': str(resultado.inserted_id)
            }), 201
        else:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
    
    except Exception as e:
        print(f"Error al crear horario: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500

@app.route('/horarios/editar/<horario_id>', methods=['GET', 'POST'])
def editar_horario(horario_id):
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        # Convertir el ID de string a ObjectId
        from bson.objectid import ObjectId
        
        # Verificar si es una solicitud GET (obtener datos) o POST (actualizar)
        if request.method == 'GET':
            # Buscar el horario en la base de datos
            if db is not None:
                horario = db.horarios.find_one({'_id': ObjectId(horario_id)})
                
                if horario:
                    # Convertir ObjectId a string
                    horario['_id'] = str(horario['_id'])
                    return jsonify(horario), 200
                else:
                    return jsonify({'success': False, 'message': 'Horario no encontrado'}), 404
            else:
                return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        # Para método POST (actualización)
        elif request.method == 'POST':
            # Obtener datos de actualización
            datos_actualizacion = request.get_json()
            
            # Validaciones
            if not datos_actualizacion.get('nombre'):
                return jsonify({'success': False, 'message': 'El nombre del horario es obligatorio'}), 400
            
            # Preparar datos para actualizar
            actualizacion = {
                '$set': {
                    'nombre': datos_actualizacion.get('nombre'),
                    'hora_entrada': datos_actualizacion.get('hora_entrada'),
                    'hora_salida': datos_actualizacion.get('hora_salida'),
                    'tolerancia_minutos': int(datos_actualizacion.get('tolerancia_minutos', 0)),
                    'dias_laborales': datos_actualizacion.get('dias_laborales', []),
                    'updated_at': datetime.now(),
                    'updated_by': session['usuario_id']
                }
            }
            
            # Actualizar en la base de datos
            if db is not None:
                resultado = db.horarios.update_one(
                    {'_id': ObjectId(horario_id)}, 
                    actualizacion
                )
                
                if resultado.modified_count > 0:
                    return jsonify({
                        'success': True, 
                        'message': 'Horario actualizado exitosamente'
                    }), 200
                else:
                    return jsonify({
                        'success': False, 
                        'message': 'No se encontró el horario o no hubo cambios'
                    }), 404
            else:
                return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
    
    except Exception as e:
        print(f"Error al editar horario: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500

#-----------
@app.route('/horarios/eliminar/<horario_id>', methods=['DELETE'])
def eliminar_horario(horario_id):
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        # Convertir el ID de string a ObjectId
        from bson.objectid import ObjectId
        
        # Verificar si el horario está en uso
        if db is not None:
            # Verificar si hay empleados con este horario
            empleados_con_horario = db.empleados.count_documents({'horario_id': horario_id})
            
            if empleados_con_horario > 0:
                return jsonify({
                    'success': False, 
                    'message': f'No se puede eliminar. Hay {empleados_con_horario} empleados asignados a este horario.'
                }), 400
            
            # Eliminar el horario
            resultado = db.horarios.delete_one({'_id': ObjectId(horario_id)})
            
            if resultado.deleted_count > 0:
                return jsonify({
                    'success': True, 
                    'message': 'Horario eliminado exitosamente'
                }), 200
            else:
                return jsonify({
                    'success': False, 
                    'message': 'Horario no encontrado'
                }), 404
        else:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
    
    except Exception as e:
        print(f"Error al eliminar horario: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500
    
@app.route('/asistencias')
def asistencias():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    # Obtener asistencias del día actual
    fecha_inicio = datetime.now().replace(hour=0, minute=0, second=0)  # Corregido datetime.datetime a datetime
    
    asistencias_list = []
    if db is not None:  # Usar "is not None" en lugar de "if db:"
        pipeline = [
            {
                '$match': {
                    'fecha_entrada': {'$gte': fecha_inicio}
                }
            },
            {
                '$lookup': {
                    'from': 'empleados',
                    'localField': 'id_empleado',
                    'foreignField': '_id',
                    'as': 'empleado'
                }
            },
            {
                '$unwind': {
                    'path': '$empleado',
                    'preserveNullAndEmptyArrays': True
                }
            },
            {
                '$sort': {
                    'fecha_entrada': -1
                }
            }
        ]
        
        asistencias_cursor = db.asistencias.aggregate(pipeline)
        for asistencia in asistencias_cursor:
            asistencia['_id'] = str(asistencia['_id'])
            if 'id_empleado' in asistencia:
                asistencia['id_empleado'] = str(asistencia['id_empleado'])
            if 'empleado' in asistencia and '_id' in asistencia['empleado']:
                asistencia['empleado']['_id'] = str(asistencia['empleado']['_id'])
            asistencias_list.append(asistencia)
    
    return render_template('asistencias.html', 
                          usuario=session,
                          asistencias=asistencias_list)

#------------------ REPORTES--------------
@app.route('/reportes')
def reportes():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('reportes.html', usuario=session)


@app.route('/reportes/generar', methods=['POST'])
def generar_reporte():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        # Obtener filtros de la solicitud
        data = request.get_json()
        tipo_reporte = data.get('tipoReporte')
        fecha_inicio = datetime.strptime(data.get('fechaInicio'), '%Y-%m-%d') if data.get('fechaInicio') else None
        fecha_fin = datetime.strptime(data.get('fechaFin'), '%Y-%m-%d') if data.get('fechaFin') else None
        departamento = data.get('departamento')
        
        # Construir pipeline de agregación
        pipeline = []
        
        # Filtro de fechas
        if fecha_inicio and fecha_fin:
            pipeline.append({
                '$match': {
                    'fecha_entrada': {
                        '$gte': fecha_inicio,
                        '$lte': fecha_fin
                    }
                }
            })
        
        # Filtro de departamento
        if departamento:
            pipeline.extend([
                {
                    '$lookup': {
                        'from': 'empleados',
                        'localField': 'id_empleado',
                        'foreignField': '_id',
                        'as': 'empleado'
                    }
                },
                {
                    '$unwind': '$empleado'
                },
                {
                    '$match': {
                        'empleado.departamento': departamento
                    }
                }
            ])
        
        # Agregar etapas según tipo de reporte
        if tipo_reporte == 'asistencias':
            pipeline.append({
                '$group': {
                    '_id': '$id_empleado',
                    'total_asistencias': {'$sum': 1},
                    'estatus': {'$first': '$estatus'}
                }
            })
        elif tipo_reporte == 'retardos':
            pipeline.append({
                '$match': {
                    'estatus': 'RETARDO'
                }
            })
        elif tipo_reporte == 'faltas':
            pipeline.append({
                '$match': {
                    'estatus': 'FALTA'
                }
            })
        
        # Ejecutar agregación
        if db is not None:
            resultados = list(db.asistencias.aggregate(pipeline))
            
            return jsonify({
                'success': True,
                'datos': resultados
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
    
    except Exception as e:
        print(f"Error al generar reporte: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500

@app.route('/reportes/exportar', methods=['POST'])
def exportar_reporte():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        # Obtener datos y formato de exportación
        data = request.get_json()
        datos = data.get('datos', [])
        formato = data.get('formato', 'pdf')
        
        if formato == 'pdf':
            # Generar PDF con FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Escribir encabezados
            if datos:
                encabezados = list(datos[0].keys())
                for encabezado in encabezados:
                    pdf.cell(40, 10, str(encabezado), 1)
                pdf.ln()
                
                # Escribir datos
                for fila in datos:
                    for valor in fila.values():
                        pdf.cell(40, 10, str(valor), 1)
                    pdf.ln()
            
            # Guardar en buffer
            buffer = io.BytesIO()
            pdf.output(buffer, 'F')
            buffer.seek(0)
            
            return send_file(
                buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name='reporte.pdf'
            )
        
        elif formato == 'excel':
            # Usar pandas para Excel
            df = pd.DataFrame(datos)
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Reporte')
            buffer.seek(0)
            
            return send_file(
                buffer,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='reporte.xlsx'
            )
        
        elif formato == 'csv':
            # Generar CSV directamente
            buffer = io.StringIO()
            if datos:
                writer = csv.DictWriter(buffer, fieldnames=list(datos[0].keys()))
                writer.writeheader()
                writer.writerows(datos)
            
            return Response(
                buffer.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=reporte.csv'}
            )
        
    except Exception as e:
        print(f"Error al exportar reporte: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500
#---------------------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Manejo de errores
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)