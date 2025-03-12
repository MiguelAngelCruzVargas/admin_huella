#mongo_conecction.py

# FUNCIONA
from pymongo import MongoClient

from dateutil.parser import parse
from datetime import datetime, timedelta
import pytz
from pymongo import errors
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def get_db():
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        # client = MongoClient("mongodb://10.10.52.229:5376/", serverSelectionTimeoutMS=2000)
        # Probar la conexión
        client.admin.command('ismaster')
        db = client["sistemachecador"]
        return db
    except (ConnectionFailure, ServerSelectionTimeoutError):
        print("Base de datos desconectada. Por favor, revise la conexión.")
        return None
    except Exception as e:
        print("Error al conectar con la base de datos. Contacte al administrador.")
        return None


def convertir_a_formato_24hrs(horas):
    horas_24hrs = []
    for hora in horas:
        if isinstance(hora, datetime):
            hora = hora.strftime("%H:%M")
        try:
            horas_24hrs.append(hora)
        except ValueError as e:
            print(f"Error al convertir hora: {hora}. Detalles: {str(e)}")
    return horas_24hrs


def get_info(db, collection_name):
    try:
        if db is None:
            return "Base de datos desconectada. Por favor, revise la conexión."
            
        collection = db[collection_name]
        current_date = datetime.now()

        data = collection.find_one({
            'Fecha_inicial': {'$lte': current_date},
            'Fecha_Final': {'$gte': current_date}
        })
        
        if data and 'mensaje_administrador' in data:
            return data['mensaje_administrador']
        else:
            return "No hay avisos disponibles para hoy."
    except Exception as e:
        return f"Error al obtener la información: {str(e)}"
    


def get_employee_name(db, rfc):
   try:
       employee = db.get_collection('datos_generales').find_one(
           {"RFC": rfc},
           {"nombre": 1, "apellido_paterno": 1, "apellido_materno": 1, "_id": 0}
       )
       if employee:
           nombre_completo = f"{employee.get('nombre', '')} {employee.get('apellido_paterno', '')} {employee.get('apellido_materno', '')}"
           return nombre_completo.strip()
       return rfc
   except Exception as e:
       print(f"Error al obtener nombre: {e}")
       return rfc

def get_admin_message_by_rfc(db, rfc):
    # Si el RFC es vacío o None, no mostrar ningún mensaje
    if not rfc or rfc.strip() == "":
        return None
        
    current_date = datetime.now()
    try:
        # Verificar que el RFC existe en la colección de empleados antes de buscar avisos
        empleado_existe = db.get_collection('datos_generales').find_one({"RFC": rfc})
        if not empleado_existe:
            return None
            
        # Buscar aviso específico para el RFC
        info = db.get_collection('Avisos').find_one({
            "RFC": rfc,
            "Fecha_inicial": {"$lte": current_date},
            "Fecha_Final": {"$gte": current_date}
        })
        if info:
            return info.get('mensaje_administrador', "No hay avisos del administrador.")
        else:
            return None
    except Exception as e:
        return f"Error al obtener el mensaje del administrador: {str(e)}"
    

def get_rfc_by_name(db, name):
    try:
        # Asegúrate de que el nombre del campo que contiene el nombre en tu colección es correcto
        info = db.get_collection('catalogos_horario').find_one({"RFC": name})
        if info:
            return info.get('RFC', None)  # Asegúrate de que el campo 'RFC' está correctamente escrito
        else:
            return None
    except Exception as e:
        return f"Error al buscar el RFC: {str(e)}"


def update_entry_by_rfc(db, rfc):
    current_time = datetime.now()  # Hora actual para registrar la entrada
    fecha_actual_str = current_time.strftime("%Y-%m-%d") + "T00:00.000Z"  # Formato fecha día ISO

    try:
        result = db.get_collection('catalogos_horario').update_one(
            {"RFC": rfc, "Fechas.fecha_dia": fecha_actual_str},
            {"$set": {
                "Fechas.$.HEC.0.hora_entrada": current_time,
                "Fechas.$.HEC.0.estatus_checador": "NORMAL"
            }}
        )
        if result.modified_count > 0:
            return "Actualización exitosa."
        else:
            return "No se encontraron registros para actualizar o fecha no coincide."
    except Exception as e:
        return f"Error al actualizar la entrada: {str(e)}"

def get_employee_schedule_type_and_entry(db, rfc):
    # Esta función necesita ser definida para obtener el tipo de horario y determinar si la próxima acción es una entrada o salida.
    return "abierto", "entrada"

def determine_check_type(db, rfc):
    current_time = datetime.now()
    fecha_actual_str = current_time.strftime("%Y-%m-%d") + "T00:00.000Z"
    documento = db.get_collection('catalogos_horario').find_one(
        {"RFC": rfc, "tipo_horario": "abierto", "Fechas.fecha_dia": fecha_actual_str}
    )
    if documento:
        hec = documento["Fechas"][0].get("HEC", [])
        hsc = documento["Fechas"][0].get("HSC", [])
        if not hec or (len(hec) > len(hsc)):
            return "salida"
    return "entrada"

######################################33




from datetime import datetime, timedelta
import pytz

def add_open_schedule_check(db, rfc, check_type):
    from datetime import datetime, timedelta
    
    current_time1 = datetime.now(pytz.UTC)
    base_time = current_time1.replace(hour=0, minute=0, second=0, microsecond=0)
    
    current_time = datetime.now()
    fecha_actual_str = current_time.strftime("%Y-%m-%d") + "T00:00.000Z"
    end_of_day = current_time.replace(hour=23, minute=59, second=59)
    tiempo_minimo = timedelta(seconds=6)
    message = None

    try:
        # Verificar si el empleado existe
        employee_exists = db.get_collection('catalogos_horario').find_one(
            {"RFC": rfc}
        )
        
        if not employee_exists:
            employee_name = get_employee_name(db, rfc)
            return (f"No se encontró un horario asignado para {employee_name}. Por favor contacte al administrador.", "error")
            
        # Verificar horario abierto
        employee_schedule = db.get_collection('catalogos_horario').find_one(
            {"RFC": rfc, "tipo_horario": "Abierto"}
        )
        
        if not employee_schedule:
            employee_name = get_employee_name(db, rfc)
            return (f"El empleado {employee_name} no tiene un horario abierto asignado. Por favor contacte al administrador.", "error")

        index = next((i for i, f in enumerate(employee_schedule["Fechas"]) if f["fecha_dia"] == fecha_actual_str), None)

        # Si no existe registro para la fecha actual, crearlo
        if index is None:
            initial_data = {
                "fecha_dia": fecha_actual_str,
                "HEC": []
            }
            
            result = db.get_collection('catalogos_horario').update_one(
                {"RFC": rfc, "tipo_horario": "Abierto"},
                {"$push": {"Fechas": initial_data}}
            )
            
            if not result.modified_count > 0:
                return ("Error al crear registro del día.", "error")
            
            employee_schedule = db.get_collection('catalogos_horario').find_one(
                {"RFC": rfc, "tipo_horario": "Abierto"}
            )
            index = len(employee_schedule["Fechas"]) - 1

        # Verificar tiempo desde último registro
        registros_hoy = employee_schedule["Fechas"][index]
        ultimos_registros = (
            [e.get('horario_entrada_r') for e in registros_hoy.get('HEC', []) if e.get('registrado')] +
            [s.get('horario_salida_r') for s in registros_hoy.get('HSC', []) if s.get('registrado')]
        )
        
        if ultimos_registros:
            ultimo_registro = max(ultimos_registros)
            tiempo_transcurrido = current_time - ultimo_registro
            
            if tiempo_transcurrido < tiempo_minimo:
                segundos_restantes = (tiempo_minimo - tiempo_transcurrido).seconds
                return (f"Por favor espere {segundos_restantes} segundos para realizar el siguiente registro", "info")

        hec = registros_hoy.get("HEC", [])
        hsc = registros_hoy.get("HSC", []) if "HSC" in registros_hoy else []

        # Verificar coherencia de registros
        if len(hec) < len(hsc):
            return (f"Error: Hay más salidas ({len(hsc)}) registradas que entradas ({len(hec)}) para el RFC {rfc}.", "error")

        # Verificar fin de día
        if current_time >= end_of_day and len(hec) > len(hsc):
            db.get_collection('catalogos_horario').update_one(
                {"RFC": rfc, "tipo_horario": "Abierto", f"Fechas.{index}.fecha_dia": fecha_actual_str},
                {"$push": {f"Fechas.{index}.HSC": {
                    "hora_salida": end_of_day,
                    "horario_salida_r": end_of_day,
                    "estatus_checador": "FALTA",
                    "registrado": True
                }}}
            )
            return (f"Salida automática registrada a las 23:59:59 con estatus FALTA", "info")

        # Procesar registros pendientes
        if len(hec) == len(hsc):
            # Registrar nueva entrada
            db.get_collection('catalogos_horario').update_one(
                {"RFC": rfc, "tipo_horario": "Abierto", f"Fechas.{index}.fecha_dia": fecha_actual_str},
                {"$push": {f"Fechas.{index}.HEC": {
                    "hora_entrada": base_time,
                    "horario_entrada_r": current_time,
                    "estatus_checador": "NORMAL",
                    "registrado": True
                }}}
            )
            return f"Bienvenido {get_employee_name(db, rfc)}, entrada registrada."
        else:
            # Registrar nueva salida
            db.get_collection('catalogos_horario').update_one(
                {"RFC": rfc, "tipo_horario": "Abierto", f"Fechas.{index}.fecha_dia": fecha_actual_str},
                {"$push": {f"Fechas.{index}.HSC": {
                    "hora_salida": base_time,
                    "horario_salida_r": current_time,
                    "estatus_checador": "NORMAL",
                    "registrado": True
                }}}
            )
            return f"Hasta luego {get_employee_name(db, rfc)}, salida registrada."

    except Exception as e:
        error_msg = f"Error al procesar registro: {str(e)}"
        print(f"Error detallado: {error_msg}")  # Para debugging
        return (error_msg, "error")


########################################################
def determine_next_action(hec, hsc, current_time):
    if not hec or (hec and not hsc):
        # No hay entradas o no hay salidas después de la última entrada
        return "HEC", {"hora_entrada": current_time, "estatus_checador": "NORMAL"}
    else:
        # Hay una entrada, verificamos la última acción
        last_hec = hec[-1] if hec else None
        last_hsc = hsc[-1] if hsc else None
        if last_hec and (not last_hsc or last_hec["hora_entrada"] > last_hsc.get("hora_salida", datetime.min)):
            return "HSC", {"hora_salida": current_time, "estatus_checador": "NORMAL"}
        else:
            return "HEC", {"hora_entrada": current_time, "estatus_checador": "NORMAL"}


    
def get_employee_schedule_type(db, rfc):
    try:
        # Obtener el nombre del empleado primero
        employee_name = get_employee_name(db, rfc)
        
        # Buscar el horario del empleado
        employee_data = db.get_collection('catalogos_horario').find_one({"RFC": rfc})
        
        if employee_data:
            tipo_horario = employee_data.get('tipo_horario', None)
            if tipo_horario:
                return True, tipo_horario
            else:
                return False, f"No se encontró un horario asignado para {employee_name}. Por favor contacte al administrador."
        else:
            return False, f"No se encontró un horario asignado para {employee_name}. Por favor contacte al administrador."
            
    except Exception as e:
        return False, f"Error inesperado al buscar el horario de {employee_name}: {str(e)}"

def obtener_nombre_dia():
    dias_espanol = {
        0: "LUNES",
        1: "MARTES",
        2: "MIERCOLES",
        3: "JUEVES",
        4: "VIERNES",
        5: "SABADO",
        6: "DOMINGO"
    }
    dia_actual = datetime.now().weekday()
    return dias_espanol[dia_actual]


def convertir_a_formato_24hrs(horas):
    horas_24hrs = []
    for hora in horas:
        if isinstance(hora, datetime):
            hora = hora.strftime("%H:%M")
        try:
            horas_24hrs.append(hora)
        except ValueError as e:
            print(f"Error al convertir hora: {hora}. Detalles: {str(e)}")
    return horas_24hrs

def verificar_y_actualizar_horario_fechas(db, rfc):
    tz = pytz.timezone('America/Mexico_City')
    current_time = datetime.now(tz)

    days_map = {
        'Monday': 'LUNES',
        'Tuesday': 'MARTES',
        'Wednesday': 'MIERCOLES',
        'Thursday': 'JUEVES',
        'Friday': 'VIERNES',
        'Saturday': 'SABADO',
        'Sunday': 'DOMINGO'
    }
    weekday = days_map[current_time.strftime("%A")]

    documento = db.get_collection('catalogos_horario').find_one({"RFC": rfc, "tipo_horario": "Cerrado"})
    if not documento:
        empleado_nombre = get_employee_name(db, rfc)
        # Comprobamos si existe el usuario en datos_generales pero no tiene horario asignado
        empleado_existe = db.get_collection('datos_generales').find_one({"RFC": rfc})
        if empleado_existe:
            return f"{empleado_nombre}, usted no tiene horario asignado. Por favor, contacte al administrador.", "error"
        else:
            return f"{empleado_nombre}, NO TIENE UN HORARIO ASIGNADO.", "error"
    
    # Buscar el último horario activo en el array 'Horarios'
    horarios = documento.get('Horarios', [])
    ultimo_horario_activo = None
    for horario in reversed(horarios):
        if horario.get('estatus', '').lower() == 'activo':
            ultimo_horario_activo = horario
            break

    if not ultimo_horario_activo:
        empleado_nombre = get_employee_name(db, rfc)
        return f"El estatus para {empleado_nombre} es inactivo.", "error"

    resultado_secundario = procesar_general(documento, weekday, current_time, db)

    # Evaluar el resultado de la función secundaria
    if isinstance(resultado_secundario, tuple):
        estatus, accion = resultado_secundario
        if estatus != "FALTA":
            # Si el estatus no es FALTA, terminar la ejecución de la función principal
            print(f"Procesado con estatus {estatus}, no es FALTA. Terminando ejecución.")
            return resultado_secundario
        # Si el estatus es FALTA, continuar con la lógica principal
        print("Procesado como FALTA en función secundaria, continua con la función principal.")

    elif resultado_secundario == "No se realizaron actualizaciones para el día actual.":
        print("No se realizaron actualizaciones para el día actual.")

    # Verificar la existencia del día antes de acceder
    if 'DIA' not in ultimo_horario_activo:
        empleado_nombre = get_employee_name(db, rfc)
        return f"No hay horario configurado para {empleado_nombre}.", "error"

    try:
        dia_horarios = ultimo_horario_activo['DIA'].get(weekday)
        if dia_horarios is None:
            empleado_nombre = get_employee_name(db, rfc)
            return f"No hay horario asignado para este día ({weekday}) para {empleado_nombre}.", "error"
        
        if not dia_horarios:
            empleado_nombre = get_employee_name(db, rfc)
            return f"No se encontraron horarios para {empleado_nombre} en el día de hoy.", "error"

    

    except Exception as e:
        print(f"Error procesando horario: {e}")
        empleado_nombre = get_employee_name(db, rfc)
        return f"Error al procesar horario para {empleado_nombre}.", "error"
    try:
        horas_entrada = [hora if isinstance(hora, str) else hora.isoformat() for hora in dia_horarios.get('Hora_entrada', [])]
        horas_salida = [hora if isinstance(hora, str) else hora.isoformat() for hora in dia_horarios.get('Hora_salida', [])]
    except Exception as e:
        return f"Error al convertir horas: {str(e)}"

    try:
        horas_entrada_dt = [datetime.fromisoformat(hora) for hora in horas_entrada]
        horas_salida_dt = [datetime.fromisoformat(hora) for hora in horas_salida]
    except Exception as e:
        return f"Error al convertir horas: {str(e)}"

    horas_entrada_24hrs = convertir_a_formato_24hrs(horas_entrada_dt)
    horas_salida_24hrs = convertir_a_formato_24hrs(horas_salida_dt)

    current_time_str = current_time.strftime("%H:%M")
    current_time_dt = datetime.strptime(current_time_str, "%H:%M").replace(year=current_time.year, month=current_time.month, day=current_time.day)

    formatted_date = current_time.strftime("%Y-%m-%dT00:00.000Z")
    fecha_index = next((i for i, f in enumerate(documento['Fechas']) if f['fecha_dia'] == formatted_date), None)
    if fecha_index is None:
        empleado_nombre = get_employee_name(db, rfc)
        return f"No hay registros disponibles para {empleado_nombre} el día de hoy.", "error"

    estatus = "FALTA"
    update_field = None
    target_index = None

    for idx, hora in enumerate(horas_entrada_dt):
        hora_dt = hora.replace(year=current_time.year, month=current_time.month, day=current_time.day)
        diff = (current_time_dt - hora_dt).total_seconds() / 60

        if -30 <= diff <= 10:
            if documento['Fechas'][fecha_index]['HEC'][idx].get('registrado', False):
                empleado_nombre = get_employee_name(db, rfc)
                return f"Entrada ya registrada para {empleado_nombre}.", None
            estatus = "NORMAL"
            update_field = 'HEC'
            target_index = idx
            print(f"Estatus Entrada: {estatus} para el índice {idx}")
            break
        elif 10 <= diff <= 20:
            if documento['Fechas'][fecha_index]['HEC'][idx].get('registrado', False):
                empleado_nombre = get_employee_name(db, rfc)
                return f"Entrada ya registrada para {empleado_nombre}.", None
            estatus = "RETARDO"
            update_field = 'HEC'
            target_index = idx
            print(f"Estatus Entrada: {estatus} para el índice {idx}")
            break
        elif 20 <= diff <= 30:
            if documento['Fechas'][fecha_index]['HEC'][idx].get('registrado', False):
                empleado_nombre = get_employee_name(db, rfc)
                return f"Entrada ya registrada para {empleado_nombre}.", None
            estatus = "NOTA MALA"
            update_field = 'HEC'
            target_index = idx
            print(f"Estatus Entrada: {estatus} para el índice {idx}")
            break
        elif diff > 30:
            estatus = "FALTA"
            update_field = 'HEC'
            target_index = idx
            print(f"Estatus Entrada: {estatus} para el índice {idx}")
            continue  # No es necesario; podríamos quitarlo

    if estatus == "FALTA":
        for idx, hora in enumerate(horas_salida_dt):
            hora_dt = hora.replace(year=current_time.year, month=current_time.month, day=current_time.day)
            diff = (current_time_dt - hora_dt).total_seconds() / 60

            if diff <= -2:
                if documento['Fechas'][fecha_index]['HSC'][idx].get('registrado', False):
                    empleado_nombre = get_employee_name(db, rfc)
                    return f"Salida ya registrada para {empleado_nombre}.", None
                
                estatus = "FALTA"
                update_field = 'HSC'
                target_index = idx
                print(f"Estatus Salida: {estatus} para el índice {idx}")
                break
            elif -1 < diff <= 30:
                if documento['Fechas'][fecha_index]['HSC'][idx].get('registrado', False):
                    empleado_nombre = get_employee_name(db, rfc)
                    return f"Salida ya registrada para {empleado_nombre}.", None
                estatus = "NORMAL"
                update_field = 'HSC'
                target_index = idx
                print(f"Estatus Salida: {estatus} para el índice {idx}")
                break
            elif diff > 30:
                estatus = "FALTA"
                update_field = 'HSC'
                target_index = idx
                print(f"Estatus Salida: {estatus} para el índice {idx}")
                continue  # No es necesario; podríamos quitarlo

    if estatus != 'FALTA':
        employee_name = get_employee_name(db, rfc)

        if estatus and update_field is not None:
            time_key = "horario_entrada_r" if update_field == 'HEC' else "horario_salida_r"
            action_type = "entrada" if update_field == 'HEC' else "salida"
            update_path = f"Fechas.{fecha_index}.{update_field}.{target_index}"

            update_data = {
                f"{update_path}.estatus_checador": estatus,
                f"{update_path}.{time_key}": current_time_dt.replace(tzinfo=None),
                f"{update_path}.registrado": True
            }

            result = db.get_collection('catalogos_horario').update_one({"_id": documento['_id']}, {"$set": update_data})

            return estatus, action_type

    empleado_nombre = get_employee_name(db, rfc)
    if update_field == 'HEC':
        return f"Entrada fuera de horario para {empleado_nombre}.", "error"
    else:
        return f"Salida fuera de horario para {empleado_nombre}.", "error"


def procesar_general(documento, weekday, current_time, db):
    general_dia_horarios = documento.get('General', {}).get('DIA', {}).get(weekday, {})
    if not general_dia_horarios:
        return "FALTA", None
    
    horas_entrada_dt = []
    horas_salida_dt = []

    # Procesar horas de entrada
    for hora in general_dia_horarios.get('Hora_entrada', []):
        if isinstance(hora, datetime):
            horas_entrada_dt.append(hora)
        elif isinstance(hora, str):
            try:
                horas_entrada_dt.append(datetime.fromisoformat(hora))
            except ValueError as e:
                return f"Error al convertir hora de entrada: {str(e)}", None
            
    if horas_entrada_dt:
        print("Se están usando entradas generales")

    # Procesar horas de salida
    for hora in general_dia_horarios.get('Hora_salida', []):
        if isinstance(hora, datetime):
            horas_salida_dt.append(hora)
        elif isinstance(hora, str):
            try:
                horas_salida_dt.append(datetime.fromisoformat(hora))
            except ValueError as e:
                return f"Error al convertir hora de salida: {str(e)}", None
            
    if horas_salida_dt:
        print("Se están usando salidas generales")

    formatted_date = current_time.strftime("%Y-%m-%dT00:00.000Z")
    fecha_index = next((i for i, f in enumerate(documento['Fechas']) if f['fecha_dia'] == formatted_date), None)
    if fecha_index is None:
        return "No hay registros para actualizar hoy.", None

    estatus = "FALTA"
    action_type = None

    for horas_dt, campo in zip([horas_entrada_dt, horas_salida_dt], ['HEC', 'HSC']):
        for idx, hora_dt in enumerate(horas_dt):
            if hora_dt.date() == current_time.date():
                current_time_str = current_time.strftime("%H:%M")
                current_time_dt = datetime.strptime(current_time_str, "%H:%M").replace(year=current_time.year, month=current_time.month, day=current_time.day)
                diff = (current_time_dt - hora_dt).total_seconds() / 60

                registros = documento['Fechas'][fecha_index][campo]
                target_idx = next((i for i, reg in enumerate(registros) if not reg.get('registrado', False)), None)

                if target_idx is None:
                    continue

                if campo == 'HEC':
                    if -30 <= diff <= 10:
                        estatus = "NORMAL"
                    elif 10 < diff <= 20:
                        estatus = "RETARDO"
                    elif 20 < diff <= 30:
                        estatus = "NOTA MALA"
                    elif diff > 30:
                        estatus = "FALTA"
                    action_type = "entrada"
                elif campo == 'HSC':
                    if -60 <= diff <= 0:
                        estatus = "FALTA"
                    elif 0 < diff <= 30:
                        estatus = "NORMAL"
                    elif diff > 30:
                        estatus = "FALTA"
                    action_type = "salida"

                # if estatus == 'FALTA':
                #     return estatus, action_type  # Terminar con el estatus "FALTA" directamente

                if estatus != 'FALTA':
                    time_key = "horario_entrada_r" if campo == 'HEC' else "horario_salida_r"
                    if not documento['Fechas'][fecha_index][campo][target_idx].get('registrado', False):
                        update_path = f"Fechas.{fecha_index}.{campo}.{target_idx}"
                        update_data = {
                            f"{update_path}.estatus_checador": estatus,
                            f"{update_path}.{time_key}": current_time_dt.replace(tzinfo=None),
                            f"{update_path}.registrado": True
                        }
                        result = db.get_collection('catalogos_horario').update_one({"_id": documento['_id']}, {"$set": update_data})
                        return estatus, action_type
    #return "No se realizaron actualizaciones para el día actual."


    return estatus, action_type

################################################################### 20 DE JUNIO DE 2024