sistema_asistencia/
├── app.py                      # Aplicación principal Flask
├── db_config.json              # Configuración de la base de datos
├── mongo_connection.py         # Conexión a MongoDB (tu archivo existente)
├── static/                     # Archivos estáticos (CSS, JS, imágenes)
│   ├── css/
│   │   ├── login.css           # Estilos para la página de login
│   │   └── dashboard.css       # Estilos para el panel de administración
│   ├── js/
│   │   ├── login.js            # JavaScript para la página de login
│   │   └── dashboard.js        # JavaScript para el panel de administración
│   └── img/
│       ├── logo.png            # Logo de la empresa
│       └── background.jpg      # Fondo para la página de login
├── templates/                  # Plantillas HTML
│   ├── login.html              # Página de login
│   ├── dashboard.html          # Panel de administración principal
│   ├── empleados.html          # Gestión de empleados
│   ├── horarios.html           # Gestión de horarios
│   ├── asistencias.html        # Visualización de asistencias
│   └── reportes.html           # Generación de reportes
└── terminal_asistencia.py      # Aplicación de terminal para el registro biométrico