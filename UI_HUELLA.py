
#------------------------------IMPORTANCION DE LIBRERIAS---------------------------------------------#
import tkinter as tk
from tkinter import ttk, Canvas
from PIL import Image, ImageTk
import socket
import threading
import queue
import pygame
from datetime import datetime, timedelta
from mongo_connection1 import *
from collections import deque
import numpy as np
import mediapipe as mp
import subprocess
from concurrent.futures import ThreadPoolExecutor
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from pymongo.errors import PyMongoError
import time
import os
#---------------------------------------------------------------------------------------#




class ConnectionManager:
    def __init__(self):
        self.connection_attempts = {}
        self.max_attempts = 10
        self.block_duration = 300  # 5 minutos de bloqueo

    def check_connection_attempt(self, client_address):
        current_time = time.time()
        
        # Limpiar intentos antiguos
        self.connection_attempts = {
            addr: attempts for addr, (attempts, timestamp) in self.connection_attempts.items()
            if current_time - timestamp < self.block_duration
        }
        
        if client_address in self.connection_attempts:
            attempts, timestamp = self.connection_attempts[client_address]
            
            if attempts > self.max_attempts:
                # Bloquear si supera intentos máximos
                if current_time - timestamp < self.block_duration:
                    return False
        
        # Registrar intento
        self.connection_attempts[client_address] = (
            self.connection_attempts.get(client_address, (0, current_time))[0] + 1,
            current_time
        )
        
        return True
    

"""_create_gradient_
    Crea un gradiente horizontal en un lienzo dado, utilizando los colores RGB de inicio y fin especificados.

    Args:
        canvas (tkinter.Canvas): El lienzo donde se dibujará el gradiente.
        start_color (str): El color de inicio del gradiente en formato hexadecimal (por ejemplo, '#RRGGBB').
        end_color (str): El color de fin del gradiente en formato hexadecimal (por ejemplo, '#RRGGBB').
        width (int): El ancho del lienzo sobre el cual se aplicará el gradiente.

    Returns:
        None: Esta función no retorna ningún valor, modifica el lienzo directamente.

    Raises:
        Exception: Cualquier excepción que ocurra durante la creación del gradiente.
    """

def create_gradient(canvas, start_color, end_color, width):
    """ Create a horizontal gradient with the given start and end RGB colors """
    (r1, g1, b1) = canvas.winfo_rgb(start_color)
    (r2, g2, b2) = canvas.winfo_rgb(end_color)
    
    r_ratio = float(r2 - r1) / width
    g_ratio = float(g2 - g1) / width
    b_ratio = float(b2 - b1) / width

    for i in range(width):
        nr = int(r1 + (r_ratio * i))
        ng = int(g1 + (g_ratio * i))
        nb = int(b1 + (b_ratio * i))
        color = "#%4.4x%4.4x%4.4x" % (nr, ng, nb)
        canvas.create_line(i, 0, i, 10, tags=("gradient",), fill=color)

    canvas.lower("gradient")  


def load_resized_image(path, size):
   
    image = Image.open(path)
    image = image.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(image)

def update_time(time_label, root):
    current_time = datetime.now().strftime('%I:%M:%S %p')
    time_label.config(text=current_time)
    root.after(1000, update_time, time_label, root)
    
dias_espanol = {
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
}


def update_date(date_label):
    day_of_week = datetime.now().strftime("%A")
    date_str = datetime.now().strftime("%d/%m/%Y").upper()
    day_of_week_es = dias_espanol[day_of_week]
    current_date = f"{day_of_week_es}\n\n{date_str}"
    date_label.config(text=current_date)

"""
Funciones de Reproducción de Sonidos

Este módulo contiene funciones para reproducir diferentes sonidos asociados con eventos específicos en una aplicación. 
Cada función utiliza el módulo pygame.mixer para cargar y reproducir un archivo de audio específico.

Funciones:

- play_success_sound(): Reproduce el sonido de éxito.
- play_error_sound(): Reproduce el sonido de error.
- play_notification_sound(): Reproduce el sonido de notificación.
- play_normal_sound(): Reproduce el sonido de entrada normal.
- play_falta_sound(): Reproduce el sonido de falta.
- play_nota_mala_sound(): Reproduce el sonido de nota mala.
- play_retardo_sound(): Reproduce el sonido de retardo.
- play_error_escaneo(): Reproduce el sonido de error de escaneo.
- play_ya_scaneado(): Reproduce el sonido de "ya escaneado".
- play_sa_normal(): Reproduce el sonido de salida normal.
- play_sa_retardo(): Reproduce el sonido de salida con retardo.
- play_sa_notamala(): Reproduce el sonido de salida con nota mala.
- play_sa_falta(): Reproduce el sonido de salida con falta.

Importante:
Asegúrese de que los archivos de audio estén en la ruta correcta 
especificada en cada función. Ya que a veces eso produce que el sistema
no funcione
"""

# sonidos
def play_success_sound():
        success_sound = pygame.mixer.Sound('RECURSOS/audios/correcto.wav')  
        success_sound.play()

   
def play_error_sound():
        error_sound = pygame.mixer.Sound('RECURSOS/audios/Error.wav')  
        error_sound.play()
        
def play_notification_sound():
    notification_sound = pygame.mixer.Sound('RECURSOS/audios/correcto.wav')
    notification_sound.play()
    return notification_sound


# sonidos para los estatus de entrada y salida
def  play_normal_sound():
    normal_sound = pygame.mixer.Sound('RECURSOS/audios/normal.wav')
    normal_sound.play()
    
def play_falta_sound(): 
    falta_sound = pygame.mixer.Sound('RECURSOS/audios/falta.wav')
    falta_sound.play()
    
def play_nota_mala_sound():
    nota_mala_sound = pygame.mixer.Sound('RECURSOS/audios/nota_mala.wav')
    nota_mala_sound.play()

def play_retardo_sound():
    retardo_sound = pygame.mixer.Sound('RECURSOS/audios/retardo.wav')
    retardo_sound.play()

def play_error_escaneo():
    error_escaneo = pygame.mixer.Sound('RECURSOS/audios/error_escanear.wav')
    error_escaneo.play()

def play_ya_scaneado():
    ya_scaneado= pygame.mixer.Sound('RECURSOS/audios/Ya_escaneado.wav')
    ya_scaneado.play()

### SALIDAS ###
def play_sa_normal():
    salida_normal= pygame.mixer.Sound('RECURSOS/audios/SALIDA_NORMAL-.wav')
    salida_normal.play()

def play_sa_retardo():
    salida_retado= pygame.mixer.Sound('RECURSOS/audios/SALIDA_CON_RETARDO.wav')
    salida_retado.play()

def play_sa_notamala():
    salida_notamala= pygame.mixer.Sound('RECURSOS/audios/SALIDA_CON_NOTA_MALA.wav')
    salida_notamala.play()

def play_sa_falta():
    salida_falta= pygame.mixer.Sound('RECURSOS/audios/SALIDA_CON_FALTA.wav')
    salida_falta.play()


import threading
from PIL import Image, ImageDraw, ImageTk, ImageFont
import numpy as np
import cv2
import math
from datetime import datetime

class PickleImageHandler:
    def __init__(self, label):
        self.label = label
        self.images_dict = {}
        self.default_image = None
        self.default_avatar = None
        self.lock = threading.Lock()
        
        
        # Atributos para la animación
        self.animation_frame = 0
        self.animation_frames = []
        self.is_animating = False
        
        # Dimensiones
        self.width = 700
        self.height = 600
        
        # Para imágenes de la base de datos
        self.db_image_width = 500
        self.db_image_height = 400
        
        # Colores para el diseño
        self.background_color = '#E8E8E8'  # Gris claro
        self.frame_color = '#2C3E50'       # Azul oscuro para el marco
        self.frame_width = 10              # Ancho del marco
        
        try:
            self.db = get_db()
            self.coleccion_imagenes = self.db['imagenes_empleados']
            print("Conexión a MongoDB obtenida correctamente")
        except Exception as e:
            print(f"Error al obtener conexión de MongoDB: {str(e)}")
            
        self.load_images_from_mongodb()
        self.create_default_images()
        self.set_default_display()

    def create_default_images(self):
        """Crea las imágenes por defecto"""
        self.create_default_avatar()
        self.create_waiting_image()

    def create_default_avatar(self):
        """Crea un avatar por defecto con ícono de usuario"""
        try:
            # Crear imagen base con fondo gris
            avatar_img = Image.new('RGB', (self.width, self.height), self.background_color)
            draw = ImageDraw.Draw(avatar_img)

            # Calcular tamaño del círculo
            circle_diameter = min(self.width, self.height) - 160
            circle_x0 = (self.width - circle_diameter) // 2
            circle_y0 = (self.height - circle_diameter) // 2
            circle_x1 = circle_x0 + circle_diameter
            circle_y1 = circle_y0 + circle_diameter
            
            # Dibujar círculo blanco con borde
            draw.ellipse([circle_x0, circle_y0, circle_x1, circle_y1], 
                        fill='white', outline=self.frame_color, width=3)

            try:
                font = ImageFont.truetype("arial.ttf", size=40)
            except:
                font = ImageFont.load_default()

            draw.text((self.width//2, self.height//2), "Sin Foto", 
                     fill=self.frame_color, anchor="mm", font=font)
            
            self.default_avatar = ImageTk.PhotoImage(avatar_img)
            print("Avatar por defecto creado correctamente")
        except Exception as e:
            print(f"Error al crear avatar por defecto: {str(e)}")

    def create_waiting_image(self):
        """Crea una imagen de espera animada con efecto de pulso en el ícono"""
        try:
            self.create_animation_frames()
            self.start_animation()
            print("Imagen de espera animada creada correctamente")
        except Exception as e:
            print(f"Error al crear imagen de espera animada: {str(e)}")
            self.create_simple_waiting_image()

    def create_animation_frames(self, num_frames=60):
        """Crea los frames para la animación del ícono con efecto pulso"""
        try:
            self.animation_frames = []
            
            # Cargar el ícono
            try:
                # Intenta cargar el ícono de huella digital
                icon = Image.open('RECURSOS/imagenes/3.png')
                # Convertir a RGBA si no lo está ya
                if icon.mode != 'RGBA':
                    icon = icon.convert('RGBA')
            except Exception as e:
                print(f"No se pudo cargar el ícono: {e}")
                # Crear un círculo como respaldo
                icon = Image.new('RGBA', (250, 250), (0, 0, 0, 0))
                draw = ImageDraw.Draw(icon)
                draw.ellipse([0, 0,249, 249], outline=self.frame_color, width=2)
            
            # Aumentar el tamaño base del ícono
            base_size = 250  # Aumentado de 80 a 150
            
            for frame in range(num_frames):
                # Crear imagen base
                img = Image.new('RGB', (self.width, self.height), self.background_color)
                
                # Calcular el factor de escala para el efecto pulso
                scale_factor = 1.0 + 0.1 * math.sin(2 * math.pi * frame / num_frames)
                
                # Calcular nuevo tamaño
                new_size = int(base_size * scale_factor)
                
                # Redimensionar el ícono
                icon_resized = icon.resize((new_size, new_size), Image.Resampling.LANCZOS)
                
                # Calcular posición para centrar
                paste_x = (self.width - new_size) // 2
                paste_y = (self.height - new_size) // 2 - 30  # -30 para subirlo un poco
                
                # Crear una máscara si la imagen tiene canal alfa
                if icon_resized.mode == 'RGBA':
                    mask = icon_resized.split()[3]
                else:
                    mask = None
                
                # Pegar el ícono
                img.paste(icon_resized, (paste_x, paste_y), mask)
                
                # Añadir textos
                draw = ImageDraw.Draw(img)
                try:
                    title_font = ImageFont.truetype("arial.ttf", size=24)
                    subtitle_font = ImageFont.truetype("arial.ttf", size=16)
                except:
                    title_font = ImageFont.load_default()
                    subtitle_font = ImageFont.load_default()

                # Texto principal
                draw.text(
                    (self.width // 2, paste_y + new_size + 50),
                    "Esperando Identificación...",
                    font=title_font,
                    fill=self.frame_color,
                    anchor="mm"
                )

                # Subtexto
                draw.text(
                    (self.width // 2, paste_y + new_size + 80),
                    "Por favor, coloque su huella dactilar",
                    font=subtitle_font,
                    fill="#666666",
                    anchor="mm"
                )

                # Convertir y guardar el frame
                self.animation_frames.append(ImageTk.PhotoImage(img))

        except Exception as e:
            print(f"Error al crear frames de animación: {str(e)}")
            self.create_simple_waiting_image()


    def create_simple_waiting_image(self):
        """Crea una imagen de espera simple como respaldo"""
        try:
            waiting_img = Image.new('RGB', (self.width, self.height), self.background_color)
            draw = ImageDraw.Draw(waiting_img)
            font = ImageFont.load_default()
            draw.text((self.width//2, self.height//2),
                     "Esperando identificación...",
                     fill=self.frame_color,
                     anchor="mm",
                     font=font)
            self.default_image = ImageTk.PhotoImage(waiting_img)
        except Exception as e:
            print(f"Error al crear imagen de espera simple: {str(e)}")

    def load_images_from_mongodb(self):
        """Carga todas las imágenes desde MongoDB"""
        try:
            documentos = self.coleccion_imagenes.find()
            
            for doc in documentos:
                try:
                    rfc = doc['RFC']
                    imagen_bytes = doc['imagen']
                    
                    # Convertir bytes a imagen
                    nparr = np.frombuffer(imagen_bytes, np.uint8)
                    img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if img_cv2 is None:
                        print(f"No se pudo decodificar la imagen para RFC: {rfc}")
                        continue
                    
                    # Convertir de BGR a RGB
                    img_rgb = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(img_rgb)
                    
                    # Calcular dimensiones manteniendo proporción
                    aspect_ratio = image.width / image.height
                    if aspect_ratio > (self.db_image_width / self.db_image_height):
                        new_width = self.db_image_width
                        new_height = int(self.db_image_width / aspect_ratio)
                    else:
                        new_height = self.db_image_height
                        new_width = int(self.db_image_height * aspect_ratio)
                    
                    # Redimensionar manteniendo proporción
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Crear imagen base con fondo gris
                    final_image = Image.new('RGB', (self.db_image_width, self.db_image_height), self.background_color)
                    
                    # Calcular posición para centrar
                    paste_x = (self.db_image_width - new_width) // 2
                    paste_y = (self.db_image_height - new_height) // 2
                    
                    # Pegar imagen redimensionada centrada
                    final_image.paste(image, (paste_x, paste_y))
                    
                    # Añadir marco
                    final_image = self.add_frame_to_image(final_image)
                    
                    # Convertir a PhotoImage
                    photo_image = ImageTk.PhotoImage(final_image)
                    self.images_dict[rfc] = photo_image
                    
                except Exception as e:
                    print(f"Error al procesar imagen para RFC {rfc}: {str(e)}")

            print(f"Se cargaron {len(self.images_dict)} imágenes desde MongoDB")

        except Exception as e:
            print(f"Error al cargar imágenes desde MongoDB: {str(e)}")

    def add_frame_to_image(self, image):
        """Añade un marco estético a la imagen"""
        try:
            framed_image = Image.new('RGB', 
                                (self.db_image_width + 2*self.frame_width, 
                                    self.db_image_height + 2*self.frame_width), 
                                self.background_color)
            
            draw = ImageDraw.Draw(framed_image)
            draw.rectangle(
                [0, 0, 
                self.db_image_width + 2*self.frame_width - 1, 
                self.db_image_height + 2*self.frame_width - 1],
                outline=self.frame_color,
                width=self.frame_width
            )
            
            framed_image.paste(image, (self.frame_width, self.frame_width))
            return framed_image
        except Exception as e:
            print(f"Error al añadir marco: {str(e)}")
            return image

    def start_animation(self):
        """Inicia la animación de la imagen de espera"""
        if not self.is_animating and self.animation_frames:
            self.is_animating = True
            self.animate_frame()

    def animate_frame(self):
        """Actualiza el frame actual de la animación"""
        if self.is_animating and self.animation_frames:
            self.animation_frame = (self.animation_frame + 1) % len(self.animation_frames)
            with self.lock:
                self.label.configure(image=self.animation_frames[self.animation_frame])
                self.label.image = self.animation_frames[self.animation_frame]
            self.label.after(50, self.animate_frame)  # 50ms para una animación suave

    def stop_animation(self):
        """Detiene la animación"""
        self.is_animating = False

    def set_default_display(self):
        """Muestra la imagen por defecto"""
        self.start_animation()

    def display_employee_image(self, rfc):
        """Muestra la imagen del empleado basado en su RFC"""
        try:
            self.stop_animation()
            with self.lock:
                if rfc in self.images_dict:
                    print(f"Mostrando imagen para RFC: {rfc}")
                    self.label.configure(image=self.images_dict[rfc], bg=self.background_color)
                    self.label.image = self.images_dict[rfc]
                    # Removemos el timer individual
                    # self.label.after(5000, self.display_default)
                else:
                    print(f"No se encontró imagen para el RFC: {rfc}, mostrando avatar")
                    self.label.configure(image=self.default_avatar, bg=self.background_color)
                    self.label.image = self.default_avatar
                    # Removemos el timer individual
                    # self.label.after(5000, self.display_default)
        except Exception as e:
            print(f"Error al mostrar imagen del empleado: {str(e)}")
            self.display_default()

    def display_default(self):
        """Vuelve a mostrar la imagen de espera animada"""
        def do_display():
            self.stop_animation()
            self.start_animation()
        
        # Asegurar que se ejecute en el hilo principal
        if self.label.winfo_exists():
            self.label.after(0, do_display)



# CLASE PRINCIPAL
class App:
    def __init__(self, root, parent_frame, section2_frame, section4_frame):
        self.root = root
    
        self.main_frame = parent_frame
        self.webcam_label = tk.Label(self.main_frame, bg='white')
        self.webcam_label.grid(row=0, column=0, sticky='nswe')
        self.image_handler = PickleImageHandler(self.webcam_label)
        self.message_active = False
        self.section2_frame = section2_frame
        self.section4_frame = section4_frame
        self.lock = threading.Lock()  
       
        
        
        self.db = get_db()
        if self.db is None:
            # Mostrar mensaje en la sección 2 si no hay conexión
            self.update_section2()  # Cambiamos esto para usar update_section2 en lugar de show_db_error_message
        else:
            self.update_section2()
        self.update_section2()
        self.message_queue = queue.Queue()
        self.result_queue = queue.Queue()  
        self.start_socket_server()
        self.metodo_verificacion = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.lock = threading.Lock()  
        self.spoofing_warning_count = 0  


        print(f"Imágenes cargadas: {len(self.image_handler.images_dict)}")
        resized_image1 = load_resized_image('RECURSOS/imagenes/H.png', (90, 100))
        self.image_label1 = tk.Label(self.section4_frame, image=resized_image1, bg='#D3D3D3')
        self.image_label1.grid(row=0, column=0, sticky='nswe')
        self.image_label1.image = resized_image1  

        # resized_image2 = load_resized_image('RECURSOS/imagenes/R.png', (90, 90))
        # self.image_label2 = tk.Label(self.section4_frame, image=resized_image2, bg='#D3D3D3')
        # self.image_label2.grid(row=0, column=2, sticky='nswe')
        # self.image_label2.image = resized_image2  

    
        self.positioning_label = None
        self.log_path = './log.txt'
           
        
       
        """_initialize_attributes_

            Inicializa los atributos necesarios para el funcionamiento de la clase.
            Propósito:
            Configurar e inicializar los parámetros y estados necesarios para las 
            funcionalidades de la clase, tales como la detección facial, el escaneo 
            y el manejo de mensajes.
        """
    def initialize_attributes(self):
            self.is_warning_message_active = False
          
            self.scan_position = 0
            self.scan_direction = 1
            self.scan_speed = 9  # Velocidad del escaneo en píxeles por frame
            self.line_thickness = 2
            self.direction = 1
            self.fade_speed = 0.05  # Velocidad de desvanecimiento
            self.line_color = (0, 255, 0)  # Verde intenso
            self.recognition_error_count=0
            self.error_count = 0 
            self.scan_error_count= 0
            self.message_active = False 
          
            



    """_check_initialized_
        Verifica si los atributos necesarios están inicializados y, si no lo están, los inicializa.

        Propósito:
        Garantizar que los atributos esenciales de la clase estén configurados antes de su uso. 
        Si los atributos no están presentes, los inicializa llamando a `initialize_attributes()`.

        Funcionalidad:
        - Verifica la existencia del atributo 'is_warning_message_active'.
        - Si el atributo no existe, llama a `initialize_attributes()` para inicializar todos los atributos necesarios.
        - Imprime un mensaje de depuración indicando que los atributos no estaban inicializados y que se han inicializado.

    """
    def check_initialized(self):
            if not hasattr(self, 'is_warning_message_active'):
                self.initialize_attributes()
                print("[DEBUG] Attributes were not initialized. Initializing now.")

  
   # ------------------------------------ PARA AVISOS TRABAJADOR 2 MODULOS ------------------------------------ #
    """procesar_rfc_
        Procesa un RFC buscando información relacionada en la base de datos.

        Args:
            rfc (str): El RFC que se va a procesar.

        Funcionalidad:
        - Imprime el RFC a procesar.
        - Busca información relacionada en la colección 'avisos' de la base de datos.
        - Imprime la información encontrada o un mensaje si no se encuentra información.

        Returns:
            None
        """
        # Coloca esto en algún punto del inicio de la aplicación donde db ya esté inicializado

                
    def procesar_rfc(self, rfc):
        try:
            # Aquí va la lógica para procesar el RFC
            print(f"Procesando RFC: {rfc}")

            # Verificar la conexión a la base de datos
            if not self.db:
                print("Conexión a la base de datos no establecida.")
                return

            # Verificar que la colección 'avisos' existe
            if 'Avisos' not in self.db.list_collection_names():
                print("La colección 'avisos' no existe en la base de datos.")
                return

            # Realizar la búsqueda del RFC en la colección 'avisos'
            info_rfc = self.db.get_collection('Avisos').find_one({'RFC': rfc})
            if info_rfc:
                print("Información encontrada:", info_rfc)
            else:
                print("No se encontró información para el RFC proporcionado.")

        except PyMongoError as e:
            print(f"Error al acceder a la base de datos: {str(e)}")
        except Exception as e:
            print(f"Error inesperado: {str(e)}")

    
    
    def show_warning_message(self, message):
        """
        Muestra un mensaje de advertencia en una ventana emergente que se ajusta al tamaño del mensaje
        y se cierra automáticamente después de 7 segundos.
        """
        self.is_warning_message_active = True
        top = tk.Toplevel(self.main_frame)

        # Configurar la ventana emergente
        top.overrideredirect(True)
        top.configure(bg='#333333', padx=0, pady=0)

        # Evitar que se interactúe con la ventana principal mientras esta esté abierta
        top.grab_set()
        top.focus_force()
        top.attributes('-topmost', True)
        
        # Crear un marco dentro de la ventana con borde visible
        frame = tk.Frame(top, bg='#333333', relief='raised', bd=2)
        frame.pack(fill='both', expand=True)
        
        # Añadir un panel superior con el estilo de advertencia
        top_panel = tk.Frame(frame, bg='#333333', height=45)
        top_panel.pack(side='top', fill='x')
        
        # Añadir un contenedor para los botones de control de ventana
        button_container = tk.Frame(top_panel, bg='#333333')
        button_container.pack(side='left', padx=10, pady=8)
        
        # Añadir los botones de "cerrar", "minimizar" y "maximizar" simulados
        for color in ['#FF5F57', '#FEBC2E', '#29C941']:
            btn = tk.Canvas(button_container, width=15, height=15, bg='#333333', highlightthickness=0)
            btn.create_oval(1, 1, 14, 14, fill=color, outline="black", width=1)
            btn.pack(side='left', padx=4)
        
        # Icono de advertencia y título
        warning_icon = tk.Label(
            top_panel, 
            text="⚠", 
            font=('Arial', 18), 
            fg='#FFD700',
            bg='#333333'
        )
        warning_icon.pack(side='left', padx=(15, 5), pady=5)
        
        title_label = tk.Label(
            top_panel, 
            text='AVISO IMPORTANTE', 
            font=('Arial', 16, 'bold'), 
            fg='white', 
            bg='#333333'
        )
        title_label.pack(side='left', pady=5)
        
        # Añadir el contador en la barra superior
        countdown_label = tk.Label(
            top_panel, 
            text="7s", 
            font=('Arial', 14, 'bold'), 
            bg='#333333', 
            fg='#FF5F57'  # Rojo para destacar
        )
        countdown_label.pack(side='right', padx=15, pady=5)
        
        # Contenedor para el mensaje - usando un frame con espacio para padding
        content_frame = tk.Frame(frame, bg='#1E1E1E', padx=0, pady=0)
        content_frame.pack(fill='both', expand=True)
        
        # Marco interior para el padding
        padding_frame = tk.Frame(content_frame, bg='#1E1E1E', padx=25, pady=25)
        padding_frame.pack(fill='both', expand=True)
        
        # Texto de referencia para el tamaño máximo (el que proporcionaste)
        reference_text = """A lo largo de la historia y desde la invención de la escritura, han sido múltiples los ejemplos de autores que a través de esta han dado rienda suelta a su imaginación con el fin de expresar sus sentimientos, emociones y pensamientos. Muchos de ellos han plasmado diferentes creencias, valores y maneras de hacer o vivir, algunos incluso en un corto espacio."""
        
        # Si el mensaje es más largo que el de referencia, lo recortamos 
        # para mostrar solo lo que cabe sin scroll
        if len(message) > len(reference_text) * 1.2:  # Damos un 20% extra de margen
            truncated = True
            display_message = message[:int(len(reference_text) * 1.2)] + "..."
        else:
            truncated = False
            display_message = message
        
        # Usar siempre Label para evitar scrolling
        msg_label = tk.Label(
            padding_frame, 
            text=display_message,
            font=('Arial', 16),
            bg='#1E1E1E', 
            fg='#FFFFFF',
            wraplength=600,  # Ancho fijo amplio
            justify='left',   # Justificación a la izquierda para textos largos
            anchor='nw'       # Alineación arriba-izquierda
        )
        msg_label.pack(fill='both', expand=True)
        
        # Si el mensaje fue truncado, añadir indicación
        if truncated:
            truncate_label = tk.Label(
                padding_frame,
                text="(Mensaje truncado por longitud)",
                font=('Arial', 12, 'italic'),
                bg='#1E1E1E',
                fg='#AAAAAA',
            )
            truncate_label.pack(side='bottom', anchor='se', padx=5, pady=(10, 0))
        
        # Función para actualizar el contador
        def update_countdown(seconds_left):
            if seconds_left > 0:
                countdown_label.config(text=f"{seconds_left}s")
                self.root.after(1000, update_countdown, seconds_left - 1)
            else:
                self.close_message(top)
        
        # Función para ajustar el tamaño de la ventana
        def adjust_window_size():
            # Ventana de tamaño fijo para todos los mensajes
            # Tamaño optimizado para mostrar el texto de referencia completo
            width = 650
            height = 250
            
            # Si el mensaje es muy corto, reducir altura
            if len(message) < 100:
                height = 180
            
            # Centrar en pantalla
            screen_width = top.winfo_screenwidth()
            screen_height = top.winfo_screenheight()
            x_pos = (screen_width - width) // 2
            y_pos = (screen_height - height) // 2
            
            top.geometry(f"{width}x{height}+{x_pos}+{y_pos}")
        
        # Calcular dimensiones y posicionar ventana
        self.root.after(10, adjust_window_size)
        
        # Iniciar cronómetro
        update_countdown(7)




    def close_message(self, top):
        """
        Cierra la ventana emergente con una animación de desvanecimiento.
        """
        def fade_out():
            self.is_warning_message_active = False
            alpha = top.attributes("-alpha")
            if alpha > 0:
                alpha -= 0.1
                top.attributes("-alpha", alpha)
                top.after(50, fade_out)
            else:
                
                top.destroy()

        top.attributes("-alpha", 1)
        fade_out()
    
      # ------------------------------------ TERMINA AVISOS TRABAJADOR ------------------------------------ #
    def show_admin_message(self, message):
         self.show_warning_message(message)


    # ------------------------------------ PARA AVISOS GENERALES 1 MODULO -------------------------------- #
    
    def register_fingerprint_entry(self, name, entry_type, success):
        # Método para registrar la entrada por reconocimiento de huella dactilar
        with open(self.log_path, 'a') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            result = "exitoso" if success else "fallido"
          #  entry_id = str(uuid.uuid4())

            log_entry = f"{timestamp} - Método: Huella Dactilar, Nombre: {name}, Tipo: {entry_type}, Resultado: {result}\n"
            f.write(log_entry)
            
            with open(self.log_path, 'a') as f:
                f.write(log_entry)
        
         # Comprobar si el nombre (que es el RFC) tiene un mensaje de administrador asociado
        admin_message = get_admin_message_by_rfc(self.db, name)
        if admin_message and admin_message != "No se encontró el RFC en la base de datos." and not admin_message.startswith("Error"):
            notification_sound = play_notification_sound()
            pygame.time.wait(int(notification_sound.get_length() * 10))
            
            self.show_admin_message(admin_message)
            


    
    """_ update_section2_
        Actualiza la información mostrada en la sección 2 del marco de la interfaz.

        Funcionalidad:
        - Verifica si hay un mensaje de error activo en la sección 2 y, si es así, no realiza ninguna actualización para evitar sobrescribirlo.
        - Obtiene la información del campo 'Avisogeneral' desde la base de datos.
        - Si no se encuentra información, muestra un mensaje indicando que no hay mensaje disponible.
        - Limpia el contenido actual de la sección 2 y actualiza con la nueva información obtenida.
        - En caso de errores específicos, como falta de campo en la base de datos, muestra un mensaje de error específico.
        - Maneja cualquier otro error genérico mostrando un mensaje de error detallado.

        Excepciones:
        - KeyError: Si el campo requerido no está disponible en la base de datos.
        - Exception: Para manejar cualquier otro error que pueda surgir durante la actualización.

        Returns:
            None
    """

   

    def update_section2(self):
        """
        Versión mejorada que maneja correctamente mensajes cortos y largos
        """
        try:
            # Limpiar contenido anterior primero
            for widget in self.section2_frame.winfo_children():
                widget.destroy()
            
            # Caso 1: No hay conexión a la base de datos
            if self.db is None:
                print("DEBUG: Base de datos no disponible")
                mensaje = "Base de datos desconectada.\nPor favor, revise la conexión y reinicie la aplicación."
                self.mostrar_mensaje_centrado(mensaje, '#FFEBEE', 'red')
                return
            
            # Obtener información
            info = get_info(self.db, 'Avisogeneral')
            
            # Caso 2: La función retorna None o string vacío
            if info is None or info == "":
                print("DEBUG: No hay avisos disponibles (info es None o vacío)")
                mensaje = "No hay avisos disponibles para hoy."
                self.mostrar_mensaje_centrado(mensaje, '#EFEFEF', 'black')
                return
            
            # Caso 3: La función retorna el mensaje predeterminado directamente
            if info == "No hay avisos disponibles para hoy.":
                print("DEBUG: get_info() ya retornó el mensaje predeterminado")
                self.mostrar_mensaje_centrado(info, '#EFEFEF', 'black')
                return
            
            # Caso 4: NUEVO - Mensaje corto que no requiere scroll
            # Verificar si el mensaje es corto (menos de 5 líneas y menos de 200 caracteres)
            lineas = info.count('\n') + 1
            if lineas <= 5 and len(info) < 200:
                print(f"DEBUG: Mensaje corto detectado ({lineas} líneas, {len(info)} caracteres)")
                self.mostrar_mensaje_centrado(info, '#EFEFEF', 'black')
                return
            
            print("DEBUG: Mostrando aviso largo con scroll")
            
            # Si llegamos aquí, tenemos un aviso largo que requiere scroll
            bg_color = '#EFEFEF'
            text_color = 'black'
            
            # Añadir marcador al final
            info_completo = info + "\n\n--- FIN DEL AVISO ---"
            
            # Crear contenedor con tamaño fijo
            container = tk.Frame(self.section2_frame, bg=bg_color, width=600, height=380)
            container.pack_propagate(False)  # Mantener tamaño fijo
            container.pack(fill='both', expand=True)
            
            # Crear un frame interno para el texto y scrollbar
            text_frame = tk.Frame(container, bg=bg_color)
            text_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Crear scrollbar
            scrollbar = tk.Scrollbar(text_frame)
            scrollbar.pack(side='right', fill='y')
            
            # Crear widget Text con enlace a scrollbar
            text_widget = tk.Text(text_frame, 
                                wrap='word',
                                font=('Roboto', 16),
                                bg=bg_color,
                                fg=text_color,
                                padx=15,
                                pady=10)
            
            # Conectar scrollbar y text widget
            scrollbar.config(command=text_widget.yview)
            text_widget.config(yscrollcommand=scrollbar.set)
            
            # Colocar texto a la izquierda de la scrollbar
            text_widget.pack(side='left', fill='both', expand=True)
            
            # Insertar el texto completo
            text_widget.insert('1.0', info_completo)
            
            # Resaltar el marcador final
            start_pos = "1.0"
            while True:
                pos = text_widget.search("--- FIN DEL AVISO ---", start_pos, stopindex="end")
                if not pos:
                    break
                
                # Configurar tags para el marcador
                text_widget.tag_config("marcador_final", foreground="green", font=('Roboto', 16, 'bold'))
                end_pos = f"{pos}+{len('--- FIN DEL AVISO ---')}c"
                text_widget.tag_add("marcador_final", pos, end_pos)
                
                # Guardar la posición del marcador para referencia
                self.posicion_marcador_final = pos
                
                start_pos = end_pos
            
            # Hacer el texto no editable
            text_widget.config(state='disabled')
            
            # Iniciar navegación con scroll suave
            self.iniciar_scroll_suave(text_widget)
            
        except Exception as e:
            print(f"ERROR en update_section2: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
            # Mostrar mensaje de error
            self.mostrar_mensaje_centrado(
                f"Error al mostrar el aviso:\n{str(e)}",
                '#FFEBEE',
                'red'
            )

    def mostrar_mensaje_centrado(self, mensaje, bg_color, text_color):
        """
        Método auxiliar para mostrar un mensaje centrado sin scroll ni marcador
        """
        # Crear contenedor con tamaño fijo
        container = tk.Frame(self.section2_frame, bg=bg_color, width=600, height=380)
        container.pack_propagate(False)  # Mantener tamaño fijo
        container.pack(fill='both', expand=True)
        
        # Crear etiqueta con mensaje centrado con fuente más grande
        mensaje_label = tk.Label(
            container,
            text=mensaje,
            font=('Roboto', 22, 'bold'),  # Fuente más grande y negrita
            bg=bg_color,
            fg=text_color,
            wraplength=550,
            justify='center'
        )
        mensaje_label.place(relx=0.5, rely=0.5, anchor='center')
            
      

    def iniciar_scroll_suave(self, text_widget):
        """
        Implementa un desplazamiento suave que recorre todo el texto
        """
        # Asegurarse de que comenzamos desde el principio
        text_widget.yview_moveto(0.0)
        
        # Variables de control
        self.posicion_scroll = 0.0
        self.incremento_scroll = 0.0003  # Incremento muy pequeño para movimiento ultra suave
        self.pausa_scroll = False
        self.visto_final = False
        
        def realizar_scroll_suave():
            """Realiza un pequeño movimiento de scroll"""
            if not text_widget.winfo_exists() or self.pausa_scroll:
                return
            
            # Obtener información actual
            inicio_visible, fin_visible = text_widget.yview()
            
            # Verificar si el marcador final es visible
            if hasattr(self, 'posicion_marcador_final'):
                try:
                    # Convertir posición del marcador a índice numérico
                    linea_marcador = int(self.posicion_marcador_final.split('.')[0])
                    # Obtener líneas visibles aproximadas
                    linea_inicio = int(float(inicio_visible) * int(text_widget.index('end').split('.')[0]))
                    linea_fin = int(float(fin_visible) * int(text_widget.index('end').split('.')[0]))
                    
                    if linea_inicio <= linea_marcador <= linea_fin:
                        # print(f"¡Marcador final visible! Entre líneas {linea_inicio} y {linea_fin}")
                        self.visto_final = True
                except Exception as e:
                    print(f"Error al verificar marcador: {e}")
            
            # Verificar si hemos llegado al final
            if fin_visible >= 0.99 or self.visto_final:
                # print("Llegando al final del texto - pausando")
                self.pausa_scroll = True
                # Pausa en el final antes de reiniciar
                text_widget.after(4000, reiniciar_scroll)
                return
            
            # Incrementar posición muy gradualmente
            self.posicion_scroll += self.incremento_scroll
            
            # Limitar al rango válido
            self.posicion_scroll = min(self.posicion_scroll, 1.0)
            
            # Aplicar movimiento
            text_widget.yview_moveto(self.posicion_scroll)
            
            # Programar siguiente movimiento (muy frecuente para suavidad)
            text_widget.after(15, realizar_scroll_suave)
        
        def reiniciar_scroll():
            """Vuelve al inicio del texto para reiniciar el ciclo"""
            # Volver al principio
            self.posicion_scroll = 0.0
            self.visto_final = False
            text_widget.yview_moveto(0.0)
            # Desactivar pausa
            self.pausa_scroll = False
            # Pausa inicial antes de reiniciar
            text_widget.after(3000, realizar_scroll_suave)
        
        # Iniciar el scroll con una pausa inicial
        text_widget.after(1000, realizar_scroll_suave)

 # ---------------------------------- MANEJO DE SOCKET PAR LA HUELLA -----------------------------
    """_ start_socket_server_
        Inicia un servidor de socket en un nuevo hilo.

        Funcionalidad:
        - Define la dirección del host y el puerto en los que el servidor de socket escuchará las conexiones entrantes.
        - Inicia un nuevo hilo para ejecutar la función `run_server`, que maneja las operaciones del servidor de socket.
        - El hilo se ejecuta en modo daemon, lo que significa que se cerrará automáticamente cuando el programa principal termine.

        Args:
            None

        Returns:
            None
    """  
    # Añadir este método en la clase App

    def initialize_recovery_system(self):
        """Inicializa el sistema de recuperación automática de la aplicación"""
        
        # Contador de errores consecutivos
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        
        # Tiempo de la última recuperación
        self.last_recovery_time = None
        self.min_recovery_interval = 300  # 5 minutos en segundos
        
        # Iniciar el monitor de estado
        self.check_system_health()
        
        logging.info("Sistema de recuperación automática inicializado")

    def check_system_health(self):
        """Verifica periódicamente el estado general del sistema y toma medidas correctivas si es necesario"""
        try:
            # 1. Verificar conexión a MongoDB
            if self.db is None:
                logging.warning("Conexión a MongoDB perdida, intentando reconectar")
                self.db = get_db()
                if self.db is not None:
                    logging.info("Conexión a MongoDB restablecida")
                    self.update_section2()
                else:
                    self.consecutive_errors += 1
                    logging.error(f"No se pudo reconectar a MongoDB. Error #{self.consecutive_errors}")
            
            # 2. Verificar proceso externo (lector de huella)
            global external_process
            if external_process is None or external_process.poll() is not None:
                logging.warning("Proceso del lector de huella no está en ejecución, reiniciándolo")
                try:
                    if external_process is not None:
                        external_process.terminate()
                        external_process.wait()
                        
                    external_process = subprocess.Popen(["DemoDP4500_k/DemoDP4500/bin/Debug/DemoDP4500.exe", "verificar"])
                    logging.info("Proceso del lector de huella reiniciado correctamente")
                except Exception as e:
                    self.consecutive_errors += 1
                    logging.error(f"Error al reiniciar el lector de huella: {str(e)}. Error #{self.consecutive_errors}")
            
            # 3. Verificar bloqueos de UI
            if self.message_active and hasattr(self, '_message_active_since'):
                time_elapsed = (datetime.now() - self._message_active_since).total_seconds()
                if time_elapsed > 30:  # Si un mensaje lleva activo más de 30 segundos
                    logging.warning(f"Mensaje bloqueado por {time_elapsed} segundos, forzando limpieza")
                    self.clear_message()
            
            # Reinicio del sistema si hay demasiados errores consecutivos
            if self.consecutive_errors >= self.max_consecutive_errors:
                current_time = datetime.now()
                
                # Verificar si ha pasado suficiente tiempo desde la última recuperación
                if (self.last_recovery_time is None or 
                    (current_time - self.last_recovery_time).total_seconds() > self.min_recovery_interval):
                    
                    logging.critical(f"Detectados {self.consecutive_errors} errores consecutivos. Iniciando recuperación de emergencia.")
                    self.perform_emergency_recovery()
                    self.last_recovery_time = current_time
                    self.consecutive_errors = 0
                else:
                    logging.warning("Errores detectados pero la recuperación está en tiempo de espera")
            
            # Si todo está bien, resetear contador de errores
            else:
                self.consecutive_errors = 0
                
        except Exception as e:
            logging.error(f"Error en el monitor de salud del sistema: {str(e)}")
        
        # Programar la siguiente verificación (cada 60 segundos)
        self.root.after(60000, self.check_system_health)

    def perform_emergency_recovery(self):
        """Realiza un proceso de recuperación de emergencia cuando se detectan problemas graves"""
        try:
            logging.info("Iniciando proceso de recuperación de emergencia")
            
            # 1. Liberar recursos y reiniciar componentes críticos
            self.clear_message()  # Limpiar cualquier mensaje activo
            
            # 2. Reiniciar conexión a MongoDB
            self.db = get_db()
            
            # 3. Reiniciar el lector de huella
            global external_process
            try:
                if external_process is not None:
                    external_process.terminate()
                    external_process.wait()
            except:
                pass
                
            try:
                external_process = subprocess.Popen(["DemoDP4500_k/DemoDP4500/bin/Debug/DemoDP4500.exe", "verificar"])
                logging.info("Proceso del lector de huella reiniciado en recuperación de emergencia")
            except Exception as e:
                logging.error(f"Error al reiniciar lector en recuperación: {str(e)}")
            
            # 4. Reiniciar socket server
            self.start_socket_server()
            
            # 5. Actualizar interfaz
            self.update_section2()
            if hasattr(self, 'image_handler'):
                self.image_handler.set_default_display()
                
            # 6. Mostrar mensaje de recuperación
            self.show_error_message(
                "Sistema Recuperado", 
                "El sistema ha detectado y corregido algunos problemas. Si los problemas persisten, contacte al administrador.",
                5000,
                "#FFA500"  # Naranja
            )
            
            logging.info("Proceso de recuperación de emergencia completado")
            
        except Exception as e:
            logging.critical(f"Error en proceso de recuperación de emergencia: {str(e)}")

    def start_socket_server(self):
        host = '127.0.0.1'
        port = 12345
        threading.Thread(target=self.run_server, args=(host, port), daemon=True).start()
        
    """_run_server_
        Ejecuta el servidor de socket y maneja las conexiones entrantes.

        Funcionalidad:
        - Crea y configura un socket del servidor para aceptar conexiones en la dirección y puerto especificados.
        - Configura el socket para reutilizar la dirección, permitiendo reinicios rápidos.
        - En un bucle infinito, escucha y acepta conexiones entrantes.
        - Para cada conexión aceptada, se inicia un nuevo hilo usando `self.executor` para manejar al cliente.

        Args:
            host (str): La dirección del host donde el servidor escuchará.
            port (int): El puerto en el que el servidor escuchará.

        Returns:
            None
    """
    def run_server(self, host, port):
        max_retries = 5
        retry_delay = 2  # segundos
        
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                    # Configuraciones de socket para mayor robustez
                    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    server_socket.settimeout(60)  # Timeout de un minuto para accept()
                    
                    server_socket.bind((host, port))
                    server_socket.listen(10)  # Aumentar cola de conexiones
                    
                    logging.info(f'Servidor seguro escuchando en {host}:{port}')
                    
                    while True:
                        try:
                            client_socket, addr = server_socket.accept()
                            
                            # Configurar socket del cliente
                            client_socket.settimeout(30)  # Timeout de 30 segundos
                            
                            # Usar ThreadPoolExecutor para manejar conexiones
                            self.executor.submit(self.handle_client, client_socket, addr)
                        
                        except socket.timeout:
                            logging.info('Esperando conexiones...')
                            continue
                        except Exception as e:
                            logging.error(f'Error en conexión de cliente: {e}')
            
            except Exception as e:
                logging.critical(f'Error crítico en servidor: {e}')
                time.sleep(retry_delay)

    """
        Maneja la comunicación con un cliente conectado.

        Funcionalidad:
        - Recibe datos del cliente, decodifica y procesa los mensajes recibidos.
        - Mantiene un contador de toques del lector para determinar si se necesita una acción adicional.
        - Encola mensajes recibidos para su procesamiento posterior.
        - Envía una respuesta de confirmación al cliente después de recibir un mensaje.
        - Gestiona los errores y excepciones de la conexión del socket.
        - Finaliza cualquier proceso externo asociado y cierra el socket del cliente cuando se termina la conexión.

        Args:
            client_socket (socket.socket): El socket del cliente conectado.
            addr (tuple): La dirección del cliente (IP, puerto).

        Returns:
            None
    """
    def handle_client(self, client_socket, addr):
        # Convertir addr a un formato manejable si es un entero inesperado
        if isinstance(addr, int):
            addr = ('unknown', addr)
        
        # Si addr no es una tupla, establecer valores por defecto
        if not isinstance(addr, tuple):
            addr = ('unknown', 0)
        
        logging.info(f'Nueva conexión intentada desde {addr}')
        
        try:
            client_socket.settimeout(35)  
            
            def cleanup():
                try:
                    if client_socket:
                        client_socket.close()
                    logging.info(f'Conexión con el cliente {addr} cerrada')
                except Exception as e:
                    logging.error(f'Error al limpiar recursos para {addr}: {e}')

            try:
                while True:
                    try:
                        # Usar recv con un tamaño de búfer más seguro
                        datos = client_socket.recv(1024)
                        
                        # Verificar si hay datos
                        if not datos:
                            logging.info(f'Conexión cerrada por el cliente {addr}')
                            break
                            
                        try:
                            mensaje_completo = datos.decode("ascii").strip()
                        except UnicodeDecodeError:
                            # Manejar posibles problemas de decodificación
                            logging.warning(f'Error decodificando datos de {addr}')
                            continue

                        logging.debug(f'Mensaje recibido de {addr}: {mensaje_completo}')

                        if mensaje_completo == "CERRAR_CONEXION":
                            logging.info(f'Cerrando conexión con {addr}')
                            break

                        # Encolar el mensaje para su procesamiento
                        self.message_queue.put(mensaje_completo)

                        # Enviar respuesta al cliente
                        try:
                            response = "Mensaje recibido"
                            client_socket.sendall(response.encode("ascii"))
                        except Exception as e:
                            logging.warning(f'Error al enviar respuesta a {addr}: {e}')
                            break

                    except socket.timeout:
                        logging.warning(f'Timeout en la conexión con {addr}')
                        break
                    except ConnectionResetError:
                        logging.warning(f'Conexión reiniciada por el cliente {addr}')
                        break

            except Exception as e:
                logging.error(f'Error procesando datos del cliente {addr}: {e}')
                # Imprimir el tipo de error y el traceback para más información
                logging.error(f'Tipo de error: {type(e)}')
                import traceback
                logging.error(traceback.format_exc())

        finally:
            try:
                client_socket.close()
            except Exception as e:
                logging.error(f'Error al cerrar socket para {addr}: {e}')

    
    """_check_for_messages_
        Verifica y procesa mensajes de la cola de mensajes.

        Funcionalidad:
        - Establece el método de verificación como 'huella'.
        - Procesa todos los mensajes en la cola de mensajes.
        - Muestra un cuadro de mensaje en caso de error en la captura de huella.
        - Procesa otros mensajes de acuerdo a la acción recibida y el ID de huella.

        Lógica de Mensajes:
        - Si el mensaje es "FalloCapturaHuella", muestra un mensaje de error, reproduce un sonido de error y registra la entrada fallida.
        - Para otros mensajes, divide el mensaje en acción e ID de huella y llama a `self.process_message` para procesarlo.

        Programación:
        - Utiliza `self.root.after(100, self.check_for_messages)` para verificar la cola de mensajes cada 100 ms.

        Returns:
            None
    """
    def check_for_messages(self):
        self.metodo_verificacion = 'huella'
        while not self.message_queue.empty():
            mensaje_completo = self.message_queue.get_nowait()
            
            # Ignorar mensajes de keep-alive silenciosamente
            if mensaje_completo == "KEEP_ALIVE":
                continue
                
            print(f"Mensaje recibido: {mensaje_completo}")  # Solo imprime mensajes no keep-alive

            # Procesar otros mensajes
            partes = mensaje_completo.split(": ")
            accion = partes[0]
            idHuella = partes[1] if len(partes) > 1 else ""

            # Procesar el mensaje de acuerdo a la acción recibida
            self.process_message(accion, idHuella)

        # Programar la siguiente verificación
        self.root.after(100, self.check_for_messages)

    """_ process_message_
        Procesa mensajes de acciones relacionadas con la asistencia de empleados usando huella digital.

        Args:
            accion (str): La acción recibida para procesar (por ejemplo, "Asistencia tomada", "Escaneo fallido").
            idHuella (str): El identificador de la huella digital del empleado.

        Funcionalidad:
        - Procesa diferentes tipos de acciones basadas en el tipo de horario (abierto o cerrado) del empleado.
        - Muestra mensajes de éxito o error basados en la acción y estado del proceso de asistencia.
        - Reproduce sonidos asociados a cada estado del proceso de asistencia.
        - Registra la entrada o el fallo en el sistema.

        Nota:
        - Esta función solo procesará el mensaje si no hay otro mensaje activo.
    """

  
    
    def process_message(self, accion, idHuella):
        try:

            
            employee_name = get_employee_name(self.db, idHuella)
            
            print(f"Procesando mensaje: Acción: {accion}, ID de Huella: {idHuella}")
            if not self.message_active:
                if accion == "Asistencia tomada":
                    self.image_handler.display_employee_image(idHuella)
                    
                    # Comprobar si hay mensaje administrativo
                    admin_message = get_admin_message_by_rfc(self.db, idHuella)
                    has_admin_message = admin_message and admin_message != "No se encontró el RFC en la base de datos." and not admin_message.startswith("Error")
                    
                    # Primero verificar si el empleado existe en la colección catalogos_horario
                    horario_exists = self.db.get_collection('catalogos_horario').find_one({"RFC": idHuella})
                    
                    if not horario_exists:
                        # Si no existe, mostrar mensaje específico de que no tiene horario asignado
                        self.msg_box_huella(
                            'Aviso de Sistema', 
                            f"{employee_name}, usted no tiene horario asignado. Por favor, contacte al administrador.",
                            'error',
                            f"{employee_name}",
                            "ESTATUS: ERROR",
                            "TIPO: SIN HORARIO"
                        )
                        self.root.after(100, play_error_sound)
                        
                        # Mostrar mensaje administrativo inmediatamente si existe
                        if has_admin_message:
                            notification_sound = play_notification_sound()
                            pygame.time.wait(int(notification_sound.get_length() * 10))
                            self.show_admin_message(admin_message)
                        else:
                            self.register_fingerprint_entry(idHuella, 'Error: Sin Horario Asignado', False)
                        return
                    
                    # Si existe horario, continuar con la verificación del tipo
                    success, schedule_type = get_employee_schedule_type(self.db, idHuella)
                    
                    # Si no se encuentra ningún horario, mostrar error
                    if not success:
                        self.msg_box_huella(
                            'Error de Horario', 
                            schedule_type, 
                            'error',
                            f"{employee_name}",
                            "ESTATUS: ERROR",
                            "TIPO: VERIFICACIÓN"
                        )
                        self.root.after(50, play_error_sound)
                        
                        # Mostrar mensaje administrativo inmediatamente si existe
                        if has_admin_message:
                            notification_sound = play_notification_sound()
                            pygame.time.wait(int(notification_sound.get_length() * 10))
                            self.show_admin_message(admin_message)
                        else:
                            self.register_fingerprint_entry(idHuella, 'Error de Horario', False)
                        return
                    
                    if schedule_type == 'Abierto':
                        mensaje = add_open_schedule_check(self.db, idHuella, "entrada")
                        
                        # Si el mensaje es una tupla (mensaje, estado)
                        if isinstance(mensaje, tuple):
                            message_text, state = mensaje
                            self.msg_box_huella(
                                'Aviso de Sistema', 
                                message_text,
                                'error' if state == "error" else 'éxito',
                                f"{employee_name}",
                                "ESTATUS: ERROR" if state == "error" else "ESTATUS: NORMAL",
                                "TIPO: VERIFICACIÓN"
                            )
                            if state == "error":
                                self.root.after(100, play_error_sound)
                                
                                # Mostrar mensaje administrativo inmediatamente si existe
                                if has_admin_message:
                                    notification_sound = play_notification_sound()
                                    pygame.time.wait(int(notification_sound.get_length() * 10))
                                    self.show_admin_message(admin_message)
                                else:
                                    self.register_fingerprint_entry(idHuella, 'Verificación Fallida', False)
                            return
                        
                        # Si es un string, proceder con la lógica normal
                        mensaje_str = str(mensaje)
                        
                        # Verificar si es un registro duplicado
                        if "ya registrada" in mensaje_str.lower():
                            self.msg_box_huella('Registro de Asistencia', mensaje_str, "error")
                            self.root.after(100, play_ya_scaneado)
                            
                            # Mostrar mensaje administrativo inmediatamente si existe
                            if has_admin_message:
                                notification_sound = play_notification_sound()
                                pygame.time.wait(int(notification_sound.get_length() * 10))
                                self.show_admin_message(admin_message)
                            return
                        
                        # Determinar tipo de acción
                        if "Entrada" in mensaje_str or "Bienvenido" in mensaje_str:
                            tipo_accion = "ENTRADA"
                            sound_func = play_normal_sound
                        else:
                            tipo_accion = "SALIDA"
                            sound_func = play_sa_normal
                            
                        # Configurar y mostrar mensaje de éxito
                        name_label = f"{employee_name}"
                        status_label = "ESTATUS: NORMAL"
                        type_label = f"TIPO: {tipo_accion}"
                        
                        self.msg_box_huella(
                            'Registro de Asistencia',
                            mensaje_str,
                            'éxito',
                            name_label,
                            status_label,
                            type_label
                        )
                        
                        # Reproducir sonido después de mostrar el mensaje
                        self.root.after(100, sound_func)
                        
                        # Si hay mensaje administrativo, mostrarlo inmediatamente
                        if has_admin_message:
                            notification_sound = play_notification_sound()
                            pygame.time.wait(int(notification_sound.get_length() * 10))
                            self.show_admin_message(admin_message)
                            # Registrar la entrada sin mostrar otro mensaje
                            with open(self.log_path, 'a') as f:
                                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                log_entry = f"{timestamp} - Método: Huella Dactilar, Nombre: {idHuella}, Tipo: {tipo_accion} Exitosa, Resultado: exitoso\n"
                                f.write(log_entry)
                        else:
                            self.register_fingerprint_entry(idHuella, f'{tipo_accion} Exitosa', True)
                        
                    elif schedule_type == 'Cerrado':
                        result = verificar_y_actualizar_horario_fechas(self.db, idHuella)
                        if isinstance(result, tuple):
                            if isinstance(result[0], str) and result[1] == "error":
                                # Es un mensaje de error personalizado
                                self.msg_box_huella(
                                    'Registro de Asistencia', 
                                    result[0], 
                                    'error',
                                    f"{employee_name}",
                                    "ESTATUS: ERROR",
                                    "TIPO: VERIFICACIÓN"
                                )
                                self.root.after(100, play_error_sound)
                                
                                # Mostrar mensaje administrativo inmediatamente si existe
                                if has_admin_message:
                                    notification_sound = play_notification_sound()
                                    pygame.time.wait(int(notification_sound.get_length() * 10))
                                    self.show_admin_message(admin_message)
                                return
                            else:
                                # Es un estatus normal (NORMAL, RETARDO, etc)
                                estatus, tipo_accion = result
                                # Verificar registro duplicado
                                if "ya registrada" in str(estatus).lower():
                                    self.msg_box_huella('Registro de Asistencia', estatus, "error")
                                    self.root.after(100, play_ya_scaneado)
                                    
                                    # Mostrar mensaje administrativo inmediatamente si existe
                                    if has_admin_message:
                                        notification_sound = play_notification_sound()
                                        pygame.time.wait(int(notification_sound.get_length() * 10))
                                        self.show_admin_message(admin_message)
                                    return
                                
                                # Procesar normalmente el mensaje de status
                                self.handle_status_messages(idHuella, estatus, tipo_accion)
                                entry_success = estatus in ["NORMAL", "RETARDO"]
                                entry_type = f'{tipo_accion} Exitosa' if entry_success else f'{tipo_accion} Fallida'
                                
                                # Si hay mensaje administrativo, mostrarlo inmediatamente
                                if has_admin_message:
                                    notification_sound = play_notification_sound()
                                    pygame.time.wait(int(notification_sound.get_length() * 10))
                                    self.show_admin_message(admin_message)
                                    # Registrar sin mostrar mensaje administrativo
                                    with open(self.log_path, 'a') as f:
                                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        result = "exitoso" if entry_success else "fallido"
                                        log_entry = f"{timestamp} - Método: Huella Dactilar, Nombre: {idHuella}, Tipo: {entry_type}, Resultado: {result}\n"
                                        f.write(log_entry)
                                else:
                                    self.register_fingerprint_entry(idHuella, entry_type, entry_success)
                    
                    else:
                        self.msg_box_huella(
                            'Error', 
                            f'Tipo de horario no reconocido: {schedule_type}. Por favor, contacte al administrador.', 
                            'error',
                            f"{employee_name}",
                            "ESTATUS: ERROR",
                            "TIPO: VERIFICACIÓN"
                        )
                        self.root.after(100, play_error_sound)
                        
                        # Mostrar mensaje administrativo inmediatamente si existe
                        if has_admin_message:
                            notification_sound = play_notification_sound()
                            pygame.time.wait(int(notification_sound.get_length() * 10))
                            self.show_admin_message(admin_message)
                
                elif accion == "Escaneo fallido":
                    self.msg_box_huella('Error', 'El escaneo ha fallido. Por favor, intenta nuevamente.', 'error')
                    self.root.after(100, play_error_sound)
                    self.register_fingerprint_entry(idHuella, 'Entrada Fallida', False)
                    
                elif accion == "Usuario no registrado, o int?ntelo de nuevo":
                    self.show_error_message('Usuario no registrado', 'Por favor, regístrese o intente nuevamente.', 'error')
                    self.root.after(100, play_error_sound)
                    self.register_fingerprint_entry(idHuella, 'Usuario no registrado', False)
                    
                else:
                    print("Acción no reconocida.")
                    
        except Exception as e:
            print(f"Error en process_message: {str(e)}")
            logging.error(f"Error en process_message: {str(e)}")
            self.msg_box_huella(
                'Error de Sistema',
                f'Error en el procesamiento: {str(e)}',
                'error'
            )
            self.root.after(100, play_error_sound)



    """_ handle_status_messages_
        Maneja los mensajes de estado y reproduce los sonidos correspondientes basados en el estatus y tipo de acción.

        Args:
            idHuella (str): El identificador de la huella digital del empleado.
            estatus (str): El estatus de la asistencia (por ejemplo, "NORMAL", "RETARDO").
            action_type (str): El tipo de acción realizada (por ejemplo, "entrada", "salida").

        Funcionalidad:
        - Muestra mensajes específicos para cada combinación de estatus y tipo de acción.
        - Reproduce sonidos específicos para cada combinación de estatus y tipo de acción.
        - Registra la entrada en el sistema basada en el éxito del proceso.

        Nota:
        - Utiliza un mapa de mensajes y tipos de mensajes para determinar el contenido y tipo de mensaje a mostrar.
    """
    
    def handle_status_messages(self, idHuella, estatus, action_type):
        employee_name = get_employee_name(self.db, idHuella)
        
        status_messages = {
            "NORMAL": {
                "entrada": f"Bienvenido {employee_name}, llegaste a tiempo, asistencia tomada.",
                "salida": f"Hasta luego {employee_name}, salida registrada a tiempo."
            },
            "RETARDO": {
                "entrada": f"¡CASI! {employee_name}, llegaste un poco tarde, asistencia tomada con retardo.",
                "salida": f"¡CUIDADO! {employee_name}, has salido tarde."
            },
            "NOTA MALA": {
                "entrada": f"¡UPSS! {employee_name}, esta vez tienes nota mala, llegaste tarde.", 
                "salida": f"¡ALERTA! {employee_name}, has salido mucho más tarde de lo previsto."
            }
        }
        
        message_types = {
            "NORMAL": "éxito",
            "RETARDO": "retardo",
            "NOTA MALA": "fueraderango"
        }

        if estatus in status_messages:
            message = status_messages[estatus][action_type]
            message_type = message_types[estatus]
            
            # Reproducir sonido correspondiente
            if estatus == "NORMAL":
                play_normal_sound() if action_type == "entrada" else play_sa_normal()
            elif estatus == "RETARDO":
                play_retardo_sound() if action_type == "entrada" else play_sa_retardo()
            elif estatus == "NOTA MALA":
                play_nota_mala_sound() if action_type == "entrada" else play_sa_notamala()
            
            # Mostrar mensaje con formato completo
            name_label = f"{employee_name}"
            status_label = f"ESTATUS: {estatus}"
            type_label = f"TIPO: {action_type.upper()}"
            self.msg_box_huella('Registro de Asistencia', message, message_type, name_label, status_label, type_label)
            
        # Si es un mensaje de error
        else:
            message = estatus  # Usar el mensaje de error original
            message_type = "error"
            play_error_sound()
            # Mostrar mensaje simple sin formato adicional
            self.msg_box_huella('Registro de Asistencia', message, message_type)

        if "ya registrada" in estatus.lower():
            play_ya_scaneado()  # Reproducir el sonido de ya escaneado
            self.msg_box_huella('Registro de Asistencia', estatus, "error")
            return

        entry_success = estatus in ["NORMAL", "RETARDO"]
        entry_type = 'Entrada Exitosa' if entry_success else 'Entrada Fallida'
        self.register_fingerprint_entry(idHuella, entry_type, entry_success)
        
#-----------------------------MANEJO DE MENSAJES DEL LECTOR DE HUELLA ----------------------
    """
    Muestra un mensaje en una ventana emergente dentro de la sección 2 de la interfaz de usuario, con un fondo 
    de color correspondiente al tipo de mensaje, y reproduce un sonido si es necesario.

    Args:
        title (str): El título del mensaje.
        message (str): El contenido del mensaje.
        message_type (str): El tipo de mensaje ('error', 'éxito', 'retardo', 'fueraderango').

    Returns:
        None

    Detalles:
        - La función verifica si ya hay un mensaje activo para evitar superposiciones.
        - Se asigna un color de fondo basado en el tipo de mensaje.
        - Si el mensaje es de tipo 'error', se reproduce un sonido de error.
        - Se limpia el contenido actual de `section2_frame` antes de mostrar el nuevo mensaje.
        - El mensaje se muestra en un contenedor configurado para no cambiar de tamaño y se posiciona en el centro de la sección.
        - El fondo del `image_label1` se cambia al color correspondiente y se restablece después de 5 segundos.
        - Se programa una llamada para limpiar el mensaje después de 5 segundos.
    """
    def msg_box_huella(self, title, message, message_type, name_label=None, status_label=None, type_label=None):
        """
        Muestra un mensaje de asistencia con información detallada y manejo mejorado de errores.
        """
        # Verificar que la sección del frame existe
        if not self.section2_frame.winfo_exists():
            logging.error("Error: section2_frame no existe")
            return

        # Verificar si ya hay un mensaje activo
        if self.message_active:
            logging.warning(f"Mensaje descartado: {title} - {message}")
            return

        # Marcar que hay un mensaje activo
        self.message_active = True
        logging.info(f"Mostrando mensaje: {title} - {message_type}")

        try:
            # Función de limpieza mejorada con mejor gestión de errores
            def synchronized_cleanup():
                def do_cleanup():
                    try:
                        # Restaurar el color del indicador
                        if hasattr(self, 'image_label1') and self.image_label1.winfo_exists():
                            self.image_label1.config(bg='#D3D3D3')
                        
                        # Restaurar la imagen por defecto
                        if hasattr(self, 'image_handler'):
                            self.image_handler.stop_animation()
                            self.image_handler.set_default_display()
                        
                        # Limpiar el mensaje
                        if self.section2_frame.winfo_exists():
                            for widget in self.section2_frame.winfo_children():
                                if widget.winfo_exists():
                                    widget.destroy()
                            self.update_section2()
                        
                        self.message_active = False
                        logging.info("Mensaje limpiado correctamente")
                        
                    except Exception as e:
                        logging.error(f"Error en cleanup: {e}")
                        # Asegurar que el flag se resetea aún en caso de error
                        self.message_active = False

                # Ejecutar la limpieza en el hilo principal
                if self.root.winfo_exists():
                    self.root.after(0, do_cleanup)
                else:
                    logging.warning("La ventana principal no existe, no se puede programar limpieza")
                    self.message_active = False

            # Limpiar widgets existentes de forma segura
            for widget in self.section2_frame.winfo_children():
                if widget.winfo_exists():
                    widget.destroy()

            # Crear el contenedor con manejo de excepciones
            try:
                msg_container = tk.Frame(
                    self.section2_frame,
                    bg='white',
                    width=800,
                    height=380
                )
                msg_container.pack_propagate(False)
                
                if not msg_container.winfo_exists():
                    raise tk.TclError("No se pudo crear el contenedor de mensajes")
                    
                msg_container.pack(expand=True, fill=tk.BOTH)
                
                # Definir colores según el tipo de mensaje
                colors = {
                    'error': '#FF0000',       # Rojo
                    'éxito': '#008000',       # Verde
                    'retardo': '#FFFF00',     # Amarillo
                    'fueraderango': '#8A2BE2' # Violeta
                }
                background_color = colors.get(message_type, '#D3D3D3')  # Gris por defecto

                # Crear widgets según la información disponible
                try:
                    if name_label and status_label and type_label:
                        # Crear layout completo con toda la información
                        self._create_full_message_layout(
                            msg_container, message, name_label, 
                            status_label, type_label
                        )
                    else:
                        # Crear layout simple solo con el mensaje
                        self._create_simple_message_layout(msg_container, message)

                    # Añadir fecha y hora en todos los casos
                    self._add_datetime_to_message(msg_container)

                    # Cambiar color del indicador visual y programar la limpieza
                    if hasattr(self, 'image_label1') and self.image_label1.winfo_exists():
                        self.image_label1.config(bg=background_color)
                        # Programar limpieza automática después de 5 segundos
                        self.root.after(5000, synchronized_cleanup)
                    else:
                        # Si no hay indicador, aún programar la limpieza
                        self.root.after(5000, synchronized_cleanup)

                except tk.TclError as e:
                    logging.error(f"Error al crear widgets: {e}")
                    self.message_active = False
                    synchronized_cleanup()
                    return
                    
            except Exception as e:
                logging.error(f"Error al crear contenedor: {e}")
                self.message_active = False
                return

        except Exception as e:
            logging.error(f"Error mostrando el mensaje: {e}")
            self.message_active = False
            
            # Intentar mostrar mensaje de error
            try:
                if 'msg_container' in locals() and msg_container.winfo_exists():
                    error_label = tk.Label(
                        msg_container,
                        text="Error mostrando el mensaje",
                        bg='white',
                        font=('Arial', 18),
                        wraplength=480,
                        justify=tk.CENTER
                    )
                    error_label.pack(expand=True, fill='both', padx=20, pady=20)
            except:
                pass
                
            # Restaurar color del indicador
            if hasattr(self, 'image_label1') and self.image_label1.winfo_exists():
                self.image_label1.config(bg='#D3D3D3')

    # Métodos auxiliares para mejorar la organización
    def _create_full_message_layout(self, container, message, name_label, status_label, type_label):
        """Crea el layout completo de un mensaje con toda la información del empleado"""
        # Nombre del empleado
        name_label_widget = tk.Label(
            container,
            text=name_label,
            bg='white',
            fg='black',
            font=('Arial', 19, 'bold')
        )
        name_label_widget.pack(pady=(30, 20))

        # Estatus del registro
        status_label_widget = tk.Label(
            container,
            text=status_label,
            bg='white',
            fg='black',
            font=('Arial', 17, 'bold')
        )
        status_label_widget.pack(pady=10)

        # Tipo de operación
        type_label_widget = tk.Label(
            container,
            text=type_label,
            bg='white',
            fg='black',
            font=('Arial', 17, 'bold')
        )
        type_label_widget.pack(pady=10)

        # Mensaje principal
        message_label = tk.Label(
            container,
            text=message,
            bg='white',
            fg='black',
            font=('Arial', 16),
            wraplength=700,
            justify='center'
        )
        message_label.place(relx=0.5, rely=0.6, anchor='center')
        
        # Línea separadora
        separator_frame = tk.Frame(
            container, 
            bg='#E0E0E0',
            height=1
        )
        separator_frame.place(relx=0.05, rely=0.75, relwidth=0.9)

    def _create_simple_message_layout(self, container, message):
        """Crea un layout simple solo con el mensaje principal"""
        message_label = tk.Label(
            container,
            text=message,
            bg='white',
            fg='black',
            font=('Arial', 19, 'bold'),
            pady=20,
            wraplength=700,
            justify='center'
        )
        message_label.place(relx=0.5, rely=0.3, anchor='center')
        
        # Línea separadora
        separator_frame = tk.Frame(
            container, 
            bg='#E0E0E0',
            height=1
        )
        separator_frame.place(relx=0.05, rely=0.6, relwidth=0.9)

    def _add_datetime_to_message(self, container):
        """Añade fecha y hora al mensaje"""
        # Marco para fecha y hora
        time_date_frame = tk.Frame(container, bg='white')
        time_date_frame.place(relx=0, rely=0.85, relwidth=1)

        # Hora
        time_label = tk.Label(
            time_date_frame,
            text=f"🕒 Hora: {datetime.now().strftime('%H:%M:%S')}",
            bg='white',
            fg='black',
            font=('Arial', 20, 'bold')
        )
        time_label.pack(side='left', padx=(20, 0))

        # Fecha
        date_label = tk.Label(
            time_date_frame,
            text=f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y')}",
            bg='white',
            fg='black',
            font=('Arial', 20, 'bold')
        )
        date_label.pack(side='right', padx=(0, 20))

    def clear_message(self):
        """Limpia los mensajes de manera segura"""
        try:
            with self.lock:
                if self.section2_frame.winfo_exists():
                    for widget in self.section2_frame.winfo_children():
                        if widget.winfo_exists():
                            widget.destroy()
                    self.update_section2()
                self.message_active = False
        except Exception as e:
            print(f"Error al limpiar mensaje: {e}")
            self.message_active = False


  #--------------------- MANEJO DE ERRORES DE LA HUELLA BIOMETRICA --------------------


    def show_error_message(self, title, message, duration=2000, background_color='#FF0000'):
        if self.message_active:
            return  # Si ya hay un mensaje activo, no hacer nada

        # Asegurarse de que la duración sea un entero positivo
        if not isinstance(duration, int) or duration <= 0:
            duration = 2000  # Valor predeterminado si la duración proporcionada no es válida

        self.message_active = True  # Establecer el flag de mensaje activo

        try:
            # Detener la animación de la huella si está en ejecución
            if hasattr(self, 'image_handler'):
                self.image_handler.stop_animation()

            # Limpiar los widgets existentes en section2_frame
            for widget in self.section2_frame.winfo_children():
                widget.destroy()

            # Configurar el contenedor de mensajes de manera similar a msg_box_huella()
            msg_container = tk.Frame(self.section2_frame, bg='white', width=800, height=380)
            msg_container.pack_propagate(False)  # Asegurar que el tamaño no cambie
            msg_container.pack(expand=True, fill=tk.BOTH, padx=0, pady=0)

            # Formatear y mostrar el mensaje
            current_time = datetime.now().strftime("%H:%M:%S")
            current_day = datetime.now().strftime("%A")
            current_date = datetime.now().strftime("%d / %m / %Y")

            # Traducir el día al español utilizando el diccionario `dias_espanol`
            current_day_es = dias_espanol.get(current_day, current_day)

            full_message = f"{title}\n{message}\n\nHora: {current_time}\nDía: {current_day_es}\nFecha: {current_date}"

            message_label = tk.Label(msg_container, text=full_message, bg='white', font=('Arial', 18), wraplength=480, justify=tk.CENTER)
            message_label.pack(expand=True, fill='both', padx=20, pady=20)

            # Cambiar el color de fondo de image_label1 si existe
            if hasattr(self, 'image_label1'):
                self.image_label1.config(bg=background_color)

            # Restablecer la imagen predeterminada después de mostrar el mensaje
            def restore_default_image():
                # Restaurar el fondo de image_label1
                if hasattr(self, 'image_label1'):
                    self.image_label1.config(bg='#D3D3D3')
                    
                # Restaurar la animación de la huella
                if hasattr(self, 'image_handler'):
                    self.image_handler.set_default_display()

                # Limpiar el mensaje y restablecer el flag
                for widget in self.section2_frame.winfo_children():
                    widget.destroy()
                self.update_section2()
                self.message_active = False

            # Programar la limpieza después del tiempo especificado
            self.root.after(duration, restore_default_image)

        except Exception as e:
            print(f"Error mostrando el mensaje: {e}")
            self.message_active = False
            if 'msg_container' in locals():
                error_label = tk.Label(
                    msg_container,
                    text="Error mostrando el mensaje",
                    bg='white',
                    font=('Arial', 18),
                    wraplength=480,
                    justify=tk.CENTER
                )
                error_label.pack(expand=True, fill='both', padx=20, pady=20)
            
            if hasattr(self, 'image_label1'):
                self.image_label1.config(bg='#D3D3D3')




    def clear_error_message(self):
        # Limpiar los widgets existentes en section2_frame
        for widget in self.section2_frame.winfo_children():
            widget.destroy()

        # Restaurar el color de fondo de image_label1 si existe
        if hasattr(self, 'image_label1'):
            self.image_label1.config(bg='#D3D3D3')

        # Llamar a update_section2 para actualizar la sección
        self.update_section2()

        self.message_active = False  # Restablecer el flag de mensaje activo
#----------------------------------------------------------------------------------------------------------#
"""_create_window_
    Inicializa la ventana principal para la aplicación del Instituto Tecnológico de Tuxtepec.
    Configura el diseño, el encabezado, la alimentación de video y las secciones para mostrar mensajes.
"""
def create_window():
    global external_process
    
    # Create the main window
    root = tk.Tk()
    root.state('zoomed')  
    root.title("Instituto Tecnológico de Tuxtepec")
    root.attributes('-topmost', True)

    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()


    window_width = int(screen_width * 0.8)
    window_height = int(screen_height * 0.8)

 
    position_x = int((screen_width - window_width) / 2)
    position_y = int((screen_height - window_height) / 2)


    root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")


    root.grid_rowconfigure(1, weight=1) 
    root.grid_columnconfigure(0, weight=45, minsize=window_width*0.45)  # Reducido de 0.45 a 0.25
    root.grid_columnconfigure(1, weight=75, minsize=window_width*0.75)  # Ajustado el resto


   
    header_frame = tk.Frame(root, bg='white', height=50) 
    header_frame.grid(row=0, column=0, columnspan=2, sticky='ew')
    header_frame.grid_propagate(False)

     
    logo_image_left = load_resized_image('RECURSOS/imagenes/logo_ittux.png', (50, 50))
    logo_image_right = load_resized_image('RECURSOS/imagenes/LOGO_TECNM.png', (50, 50))

    # Logo izquierdo
    logo_label_left = tk.Label(header_frame, image=logo_image_left, bg='white')
    logo_label_left.pack(side='left', padx=10)

    # Logo derecho
    logo_label_right = tk.Label(header_frame, image=logo_image_right, bg='white')
    logo_label_right.pack(side='right', padx=10)

    # Institute name label - centrado en el medio
    name_label = tk.Label(header_frame, text='TECNOLÓGICO NACIONAL DE MÉXICO  CAMPUS TUXTEPEC ', bg='white', fg='black', font=('Roboto', 20))
    name_label.pack(expand=True)

    def redraw_gradient(canvas, start_color, end_color):
        canvas.delete("gradient") 
        width = canvas.winfo_width()  
        create_gradient(canvas, start_color, end_color, width)  

   
    gradient_canvas = Canvas(header_frame, bg='white', height=10, bd=0, highlightthickness=0)
    gradient_canvas.pack(fill='x', side='bottom')

   
    create_gradient(gradient_canvas, 'green', 'blue', gradient_canvas.winfo_reqwidth())


    gradient_canvas.bind("<Configure>", lambda event, canvas=gradient_canvas, start_color='green', end_color='blue': redraw_gradient(canvas, start_color, end_color))

    logo_label_left.image = logo_image_left
    logo_label_right.image = logo_image_right
#--------------   CONFIGURACION DEL FRAME DE LA IMAGEN-----
    # Central Frame Configuration
    
    background_color = '#E8E8E8' 
    central_frame = tk.Frame(root, bg=background_color, bd=2, relief='groove')
    central_frame.grid(row=1, column=0, sticky='nswe', padx=0)  # Añadido padx=0
    central_frame.grid_propagate(False)

    # Establecer un tamaño más pequeño
    width = 450  # Reducido de 400 a 350
    height = 750
    central_frame.configure(width=width, height=height)

    # Resto de la configuración
    central_frame.grid_columnconfigure(0, weight=1)
    central_frame.grid_rowconfigure(0, weight=9)
    central_frame.grid_rowconfigure(1, weight=1)

    # Frame para la cámara (top_left_frame)
    top_left_frame = tk.Frame(central_frame, bg=background_color, bd=2, relief='groove')
    top_left_frame.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
    top_left_frame.grid_propagate(False)  # Importante mantener esto
    top_left_frame.grid_rowconfigure(0, weight=1)
    top_left_frame.grid_columnconfigure(0, weight=1)

    # Label para mostrar el video de la cámara
    webcam_label = tk.Label(top_left_frame, bg=background_color)
    webcam_label.grid(row=0, column=0, sticky='nsew')  # Removido pack() para evitar conflictos

    # Frame para la sección inferior (bottom_left_frame)
    bottom_left_frame = tk.Frame(central_frame, bg=background_color, bd=2, relief='groove')
    bottom_left_frame.grid(row=1, column=0, sticky='nswe', padx=2, pady=2)
    bottom_left_frame.grid_propagate(False)  # Importante mantener esto
    bottom_left_frame.grid_columnconfigure(0, weight=1)
    bottom_left_frame.grid_rowconfigure(0, minsize=70)
    bottom_left_frame.grid_rowconfigure(1, minsize=40)
#--------------------------------------------------------------------------------
    font_style = ('bold', 60)  
   # font_style = ('DS-digital', 70)  
    
    time_label = tk.Label(bottom_left_frame, font=font_style, fg='black', bg=background_color)
    time_label.pack(side='top', fill='x', expand=False, pady=(10, 0))  
    
    date_font_style = ('Helvetica', 22,'bold') 
    date_label = tk.Label(bottom_left_frame, font=date_font_style, fg='black', bg=background_color)
    date_label.pack(side='top', fill='x', expand=True, pady=(5, 5))  

 
    update_time(time_label, root)
    update_date(date_label)

 
    right_frame = tk.Frame(root, bg='white', bd=2, relief='groove')
    right_frame.grid(row=1, column=1, sticky='nswe')
    right_frame.grid_propagate(False)

    right_frame = tk.Frame(root, bg='white', bd=2, relief='groove')
    right_frame.grid(row=1, column=1, sticky='nswe')
    right_frame.grid_columnconfigure(0, weight=1)  

    """# Configura las filas del right_frame para las secciones y los separadores
    right_frame.grid_rowconfigure(0, weight=10)  # 10% altura para la primera sección
    right_frame.grid_rowconfigure(1, weight=1)   # Pequeño peso para el primer separador
    right_frame.grid_rowconfigure(2, weight=55)  # 55% altura para la segunda sección
    right_frame.grid_rowconfigure(3, weight=1)   # Pequeño peso para el segundo separador
    right_frame.grid_rowconfigure(4, weight=10)  # 10% altura para la tercera sección
    right_frame.grid_rowconfigure(5, weight=1)   # Pequeño peso para el tercer separador
    right_frame.grid_rowconfigure(6, weight=25)  # 25% altura para la cuarta sección"""

    # Configuración de la fila para Sección 1
    right_frame.grid_rowconfigure(0, minsize=50, weight=10)  # Tamaño fijo para Sección 1

    # Configuración de la fila para el Separador 1
    right_frame.grid_rowconfigure(1, minsize=2, weight=0)  # Altura fija para el separador

    # Configuración de la fila para Sección 2
    right_frame.grid_rowconfigure(2, minsize=250, weight=55)  # Tamaño fijo para Sección 2

    # Configuración de la fila para el Separador 2
    right_frame.grid_rowconfigure(3, minsize=2, weight=0)  # Altura fija para el separador

    # Configuración de la fila para Sección 3
    right_frame.grid_rowconfigure(4, minsize=50, weight=10)  # Tamaño fijo para Sección 3

    # Configuración de la fila para el Separador 3
    right_frame.grid_rowconfigure(5, minsize=2, weight=0)  # Altura fija para el separador

    # Configuración de la fila para Sección 4
    right_frame.grid_rowconfigure(6, minsize=150, weight=25)  # Tamaño fijo para Sección 4

    # Añade los separadores
    separator1 = ttk.Separator(right_frame, orient='horizontal')
    separator1.grid(row=1, column=0, sticky='ew')
    

    separator2 = ttk.Separator(right_frame, orient='horizontal')
    separator2.grid(row=3, column=0, sticky='ew')

    separator3 = ttk.Separator(right_frame, orient='horizontal')
    separator3.grid(row=5, column=0, sticky='ew')


    section1_frame = tk.Frame(right_frame, bg='#079073') 
    section1_frame.grid(row=0, column=0, sticky='nswe')
    section1_label = tk.Label(section1_frame, text='AVISOS', bg='#079073', fg='black', anchor='center', font=('Roboto', 20))  
    section1_label.pack(expand=True, fill='both')  


    section2_frame = tk.Frame(right_frame, bg='#EFEFEF')  
    section2_frame.grid(row=2, column=0, sticky='nswe')
    #section2_label = tk.Label(section2_frame, text='SIN NOVEDAD', bg='#EFEFEF', fg='black', anchor='center', font=('Roboto', 20))  
    #section2_label.pack(expand=True, fill='both')  


    section3_frame = tk.Frame(right_frame, bg='#CFF2EA') 
    section3_frame.grid(row=4, column=0, sticky='nswe')
    section3_label = tk.Label(section3_frame, text='ORGULLOSAMENTE TECNM', bg='#CFF2EA', fg='black', anchor='center', font=('Roboto', 20)) 
    section3_label.pack(expand=True, fill='both') 


    section4_frame = tk.Frame(right_frame, bg='#EFEFEF')
    section4_frame.grid(row=6, column=0, sticky='nswe')
    

    section4_frame.grid_columnconfigure(0, weight=1)
    section4_frame.grid_columnconfigure(1, weight=0)  
    section4_frame.grid_columnconfigure(2, weight=1)
    section4_frame.grid_rowconfigure(0, weight=1)


    separator4 = ttk.Separator(section4_frame, orient='vertical')
    separator4.grid(row=0, column=1, sticky='ns')
    """
    Maneja el evento de cierre de la ventana principal.
    Termina cualquier proceso externo en ejecución y libera los recursos de
    la cámara antes de destruir la ventana.
    """
    
    def on_close():
        global external_process

        if external_process is not None:
            external_process.terminate()
            external_process.wait()

    
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)


    app_instance = App(root, top_left_frame, section2_frame, section4_frame)
   # app_instance.check_result_queue() 
    
    app_instance.check_for_messages()


    try:
      external_process = subprocess.Popen(["DemoDP4500_k/DemoDP4500/bin/Debug/DemoDP4500.exe", "verificar"])
        
    except Exception as e:
        print(f"Failed to start external process: {e}")
        external_process = None
   
    root.mainloop()

if __name__ == "__main__":
    pygame.mixer.init()
    create_window()