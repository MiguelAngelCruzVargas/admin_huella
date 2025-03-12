import os
import sys
import pymongo
from bson import decode_all
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFileDialog, QTextEdit, 
                             QGroupBox, QMessageBox, QProgressBar)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPalette, QColor

class BSONUploaderThread(QThread):
    """Hilo para cargar colecciones BSON en segundo plano"""
    progress_update = pyqtSignal(str)
    upload_complete = pyqtSignal(bool, str)

    def __init__(self, directory_path, mongodb_uri, database_name, exclude_patterns):
        super().__init__()
        self.directory_path = directory_path
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        self.exclude_patterns = exclude_patterns

    def run(self):
        try:
            # Establecer conexión a MongoDB
            client = pymongo.MongoClient(self.mongodb_uri)
            db = client[self.database_name]
            
            # Encontrar archivos BSON
            bson_files = [f for f in os.listdir(self.directory_path) 
                          if f.endswith('.bson') and 
                          not any(pattern in f for pattern in self.exclude_patterns)]
            
            # Contadores
            total_collections = 0
            total_documents = 0
            
            # Procesar cada archivo BSON
            for bson_filename in bson_files:
                collection_name = os.path.splitext(bson_filename)[0]
                file_path = os.path.join(self.directory_path, bson_filename)
                
                try:
                    with open(file_path, 'rb') as bson_file:
                        bson_data = bson_file.read()
                        
                        try:
                            documents = decode_all(bson_data)
                            collection = db[collection_name]
                            
                            # Insertar solo si la colección está vacía
                            if collection.count_documents({}) == 0:
                                if documents:
                                    # Eliminar _id para evitar errores
                                    for doc in documents:
                                        doc.pop('_id', None)
                                    
                                    collection.insert_many(documents)
                                    
                                    # Actualizar progreso
                                    self.progress_update.emit(
                                        f"Cargados {len(documents)} documentos en la colección {collection_name}"
                                    )
                                    
                                    total_collections += 1
                                    total_documents += len(documents)
                            else:
                                self.progress_update.emit(
                                    f"La colección {collection_name} ya contiene documentos. Saltando."
                                )
                        
                        except Exception as decode_error:
                            self.progress_update.emit(
                                f"Error al decodificar {bson_filename}: {decode_error}"
                            )
                
                except IOError as file_error:
                    self.progress_update.emit(
                        f"Error al leer el archivo {bson_filename}: {file_error}"
                    )
            
            # Mensajes de resumen
            self.progress_update.emit("\n--- Resumen de Carga ---")
            self.progress_update.emit(f"Colecciones procesadas: {total_collections}")
            self.progress_update.emit(f"Total de documentos insertados: {total_documents}")
            self.progress_update.emit("Carga de colecciones BSON completada.")
            
            # Notificar éxito
            self.upload_complete.emit(True, "Carga completada exitosamente")
        
        except pymongo.errors.ConnectionFailure as conn_error:
            # Notificar error de conexión
            self.upload_complete.emit(False, f"No se pudo conectar a MongoDB: {conn_error}")
        except Exception as e:
            # Notificar error inesperado
            self.upload_complete.emit(False, f"Ocurrió un error: {e}")
        finally:
            # Cerrar conexión de MongoDB
            if 'client' in locals():
                client.close()

class BSONUploaderApp(QMainWindow):
    """Aplicación principal para cargar colecciones BSON"""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """Inicializar la interfaz de usuario"""
        self.setWindowTitle('Cargador de Colecciones BSON a MongoDB')
        self.setGeometry(300, 300, 700, 800)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Estilo oscuro moderno
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c2c2c;
                color: #ffffff;
            }
            QLabel, QLineEdit, QTextEdit {
                color: #ffffff;
                background-color: #3c3f41;
                border: 1px solid #5a5a5a;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #4a6984;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a7f9e;
            }
            QGroupBox {
                color: #ffffff;
                border: 2px solid #5a5a5a;
                border-radius: 4px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)

        # Sección de Configuración de MongoDB
        mongodb_group = QGroupBox("Configuración de MongoDB")
        mongodb_layout = QVBoxLayout()
        mongodb_group.setLayout(mongodb_layout)

        # URI de MongoDB
        uri_layout = QHBoxLayout()
        uri_label = QLabel("URI de MongoDB:")
        self.uri_input = QLineEdit()
        self.uri_input.setText("mongodb://localhost:27017")
        uri_layout.addWidget(uri_label)
        uri_layout.addWidget(self.uri_input)
        mongodb_layout.addLayout(uri_layout)

        # Nombre de Base de Datos
        db_layout = QHBoxLayout()
        db_label = QLabel("Nombre de Base de Datos:")
        self.db_input = QLineEdit()
        self.db_input.setText("sistemachecador")
        db_layout.addWidget(db_label)
        db_layout.addWidget(self.db_input)
        mongodb_layout.addLayout(db_layout)

        # Sección de Directorio BSON
        directory_group = QGroupBox("Directorio BSON")
        directory_layout = QHBoxLayout()
        directory_group.setLayout(directory_layout)

        # Entrada de directorio
        self.directory_input = QLineEdit()
        browse_btn = QPushButton("Examinar")
        browse_btn.clicked.connect(self.browse_directory)
        directory_layout.addWidget(self.directory_input)
        directory_layout.addWidget(browse_btn)

        # Sección de Patrones de Exclusión
        exclusion_group = QGroupBox("Patrones de Exclusión")
        exclusion_layout = QVBoxLayout()
        exclusion_group.setLayout(exclusion_layout)

        self.exclusion_input = QTextEdit()
        self.exclusion_input.setPlainText("temp\nbackup\nold")
        exclusion_layout.addWidget(self.exclusion_input)

        # Botón de Carga
        self.upload_btn = QPushButton("Cargar Colecciones BSON")
        self.upload_btn.clicked.connect(self.start_upload)

        # Área de Registro
        log_group = QGroupBox("Registro de Carga")
        log_layout = QVBoxLayout()
        log_group.setLayout(log_layout)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        log_layout.addWidget(self.log_area)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()

        # Agregar todos los componentes al diseño principal
        main_layout.addWidget(mongodb_group)
        main_layout.addWidget(directory_group)
        main_layout.addWidget(exclusion_group)
        main_layout.addWidget(self.upload_btn)
        main_layout.addWidget(log_group)
        main_layout.addWidget(self.progress_bar)

    def browse_directory(self):
        """Abrir diálogo para seleccionar directorio"""
        directory = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio")
        if directory:
            self.directory_input.setText(directory)

    def start_upload(self):
        """Iniciar proceso de carga"""
        # Validar entradas
        uri = self.uri_input.text().strip()
        db_name = self.db_input.text().strip()
        directory = self.directory_input.text().strip()
        exclusions = [line.strip() for line in self.exclusion_input.toPlainText().split('\n') if line.strip()]

        # Validar campos
        if not uri or not db_name or not directory:
            QMessageBox.critical(self, "Error", "Por favor complete todos los campos")
            return

        # Limpiar registro anterior
        self.log_area.clear()

        # Mostrar barra de progreso
        self.progress_bar.show()
        self.upload_btn.setEnabled(False)

        # Crear y comenzar hilo de carga
        self.upload_thread = BSONUploaderThread(directory, uri, db_name, exclusions)
        self.upload_thread.progress_update.connect(self.update_log)
        self.upload_thread.upload_complete.connect(self.upload_finished)
        self.upload_thread.start()

    def update_log(self, message):
        """Actualizar área de registro"""
        self.log_area.append(message)
        # Desplazar hasta el final
        self.log_area.verticalScrollBar().setValue(
            self.log_area.verticalScrollBar().maximum()
        )

    def upload_finished(self, success, message):
        """Manejar finalización de carga"""
        # Ocultar barra de progreso
        self.progress_bar.hide()
        self.upload_btn.setEnabled(True)

        # Mostrar mensaje de resultado
        if success:
            QMessageBox.information(self, "Éxito", message)
        else:
            QMessageBox.critical(self, "Error", message)

def main():
    """Iniciar la aplicación"""
    app = QApplication(sys.argv)
    uploader = BSONUploaderApp()
    uploader.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()