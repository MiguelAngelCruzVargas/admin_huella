// Esperar a que el DOM esté cargado


document.addEventListener('DOMContentLoaded', function() {
    // Inicializar reloj
    updateClock();
    
    // Toggle para el menú lateral en dispositivos móviles
    initSidebarToggle();
    
    // Inicializar el dropdown de notificaciones
    initNotificationDropdown();
    
    // Inicializar modal para terminal de asistencia
    initTerminalModal();
});

// Función para actualizar el reloj en tiempo real
function updateClock() {
    const clockElement = document.getElementById('current-time');
    if (!clockElement) return;
    
    function updateTime() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        
        clockElement.textContent = `${hours}:${minutes}:${seconds}`;
    }
    
    // Actualizar inmediatamente
    updateTime();
    
    // Actualizar cada segundo
    setInterval(updateTime, 1000);
}

// Función para inicializar el toggle del sidebar
function initSidebarToggle() {
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (!menuToggle || !sidebar || !mainContent) return;
    
    menuToggle.addEventListener('click', function() {
        sidebar.classList.toggle('active');
        
        // Agregar overlay para cerrar el menú al hacer clic fuera
        if (sidebar.classList.contains('active')) {
            const overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.background = 'rgba(0, 0, 0, 0.3)';
            overlay.style.zIndex = '99';
            document.body.appendChild(overlay);
            
            overlay.addEventListener('click', function() {
                sidebar.classList.remove('active');
                this.remove();
            });
        } else {
            const overlay = document.querySelector('.sidebar-overlay');
            if (overlay) overlay.remove();
        }
    });
    
    // Cerrar automáticamente en pantallas pequeñas al cambiar de tamaño
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768 && sidebar.classList.contains('active')) {
            sidebar.classList.remove('active');
            const overlay = document.querySelector('.sidebar-overlay');
            if (overlay) overlay.remove();
        }
    });
}


// Función para inicializar el dropdown de notificaciones
function initNotificationDropdown() {
    const notificationIcon = document.querySelector('.notification-icon');
    const notificationBadge = notificationIcon.querySelector('.badge');
    if (!notificationIcon) return;
    
    // Verificar si ya existe el dropdown, si no, crearlo
    let dropdown = document.querySelector('.notification-dropdown');
    
    if (!dropdown) {
        dropdown = createNotificationDropdown();
        document.querySelector('.topbar-right').appendChild(dropdown);
    }
    
    // Cargar notificaciones al iniciar
    cargarNotificaciones();
    
    // Alternar dropdown al hacer clic
    notificationIcon.addEventListener('click', function(e) {
        e.stopPropagation();
        dropdown.classList.toggle('show');
        
        // Recargar notificaciones al abrir
        if (dropdown.classList.contains('show')) {
            cargarNotificaciones();
        }
    });
    
    // Cerrar dropdown al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (dropdown.classList.contains('show') && !dropdown.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });
    
    // Evitar que los clics dentro del dropdown lo cierren
    dropdown.addEventListener('click', function(e) {
        e.stopPropagation();
    });

    // Función para cargar notificaciones
    function cargarNotificaciones() {
        fetch('/obtener_notificaciones')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error al obtener notificaciones');
                }
                return response.json();
            })
            .then(notificaciones => {
                const notificationList = dropdown.querySelector('.notification-list');
                notificationList.innerHTML = ''; // Limpiar lista anterior

                // Actualizar contador de notificaciones
                const noLeidas = notificaciones.filter(n => !n.leida);
                notificationBadge.textContent = noLeidas.length;

                if (notificaciones.length === 0) {
                    notificationList.innerHTML = '<p class="no-notifications">No hay notificaciones</p>';
                    return;
                }

                notificaciones.forEach(notificacion => {
                    const item = document.createElement('div');
                    item.className = `notification-item ${notificacion.leida ? '' : 'unread'}`;
                    
                    item.innerHTML = `
                        <div class="notification-content">
                            <div class="notification-icon">
                                <i class="${getIconForNotificationType(notificacion.tipo)}"></i>
                            </div>
                            <div class="notification-text">
                                <div class="notification-title">${notificacion.titulo}</div>
                                <div class="notification-subtitle">${notificacion.mensaje}</div>
                                <div class="notification-time">${formatearFecha(notificacion.fecha)}</div>
                            </div>
                        </div>
                    `;
                    
                    notificationList.appendChild(item);
                });
            })
            .catch(error => {
                console.error('Error al cargar notificaciones:', error);
            });
    }

    // Función para crear el dropdown de notificaciones
    function createNotificationDropdown() {
        const dropdown = document.createElement('div');
        dropdown.className = 'notification-dropdown';
        
        // Encabezado
        const header = document.createElement('div');
        header.className = 'notification-header';
        header.innerHTML = `
            <h3>Notificaciones</h3>
            <span class="mark-all-read">Marcar todo como leído</span>
        `;
        
        // Lista de notificaciones
        const notificationList = document.createElement('div');
        notificationList.className = 'notification-list';
        
        // Enlace para ver todas
        const viewAll = document.createElement('a');
        viewAll.href = '#';
        viewAll.className = 'view-all-link';
        viewAll.textContent = 'Ver todas las notificaciones';
        
        // Agregar todo al dropdown
        dropdown.appendChild(header);
        dropdown.appendChild(notificationList);
        dropdown.appendChild(viewAll);
        
        // Manejar clic en "Marcar todo como leído"
        header.querySelector('.mark-all-read').addEventListener('click', function() {
            fetch('/marcar_todas_notificaciones_leidas', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        cargarNotificaciones();
                    }
                })
                .catch(error => {
                    console.error('Error al marcar notificaciones:', error);
                });
        });
        
        return dropdown;
    }

    // Función para obtener el ícono según el tipo de notificación
    function getIconForNotificationType(tipo) {
        const iconMap = {
            'nuevo_empleado': 'fas fa-user-plus',
            'asistencia': 'fas fa-clipboard-check',
            'sistema': 'fas fa-bell',
            'retardo': 'fas fa-exclamation-triangle',
            'departamento': 'fas fa-building',
            'default': 'fas fa-bell'
        };
        return iconMap[tipo] || iconMap['default'];
    }

    // Función para formatear fecha
    function formatearFecha(fechaISO) {
        const fecha = new Date(fechaISO);
        const ahora = new Date();
        const diferencia = ahora - fecha;
        
        // Intervalos de tiempo
        const minuto = 60 * 1000;
        const hora = 60 * minuto;
        const dia = 24 * hora;

        if (diferencia < minuto) {
            return 'Hace un momento';
        } else if (diferencia < hora) {
            const mins = Math.floor(diferencia / minuto);
            return `Hace ${mins} minuto${mins !== 1 ? 's' : ''}`;
        } else if (diferencia < dia) {
            const horas = Math.floor(diferencia / hora);
            return `Hace ${horas} hora${horas !== 1 ? 's' : ''}`;
        } else {
            return fecha.toLocaleString('es-ES', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }
}

// Inicializar dropdown de notificaciones
document.addEventListener('DOMContentLoaded', initNotificationDropdown);
// Inicializar modal para terminal de asistencia
function initTerminalModal() {
    const terminalBtn = document.getElementById('terminal-btn');
    if (!terminalBtn) return;
    
    // Verificar si ya existe el modal, si no, crearlo
    let modalOverlay = document.querySelector('.modal-overlay');
    
    if (!modalOverlay) {
        modalOverlay = createTerminalModal();
        document.body.appendChild(modalOverlay);
    }
    
    // Mostrar modal al hacer clic en el botón
    terminalBtn.addEventListener('click', function(e) {
        e.preventDefault();
        modalOverlay.classList.add('active');
        
        // Evitar scroll en el body cuando el modal está activo
        document.body.style.overflow = 'hidden';
    });
    
    // Cerrar modal con el botón de cerrar
    const closeBtn = modalOverlay.querySelector('.modal-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            modalOverlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
    
    // Cerrar modal al hacer clic fuera
    modalOverlay.addEventListener('click', function(e) {
        if (e.target === this) {
            this.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
}

// Crear el modal para terminal de asistencia
function createTerminalModal() {
    const modalOverlay = document.createElement('div');
    modalOverlay.className = 'modal-overlay';
    
    const modalContainer = document.createElement('div');
    modalContainer.className = 'modal-container';
    
    // Header del modal
    const modalHeader = document.createElement('div');
    modalHeader.className = 'modal-header';
    modalHeader.innerHTML = `
        <h2><i class="fas fa-desktop"></i> Terminal de Asistencia</h2>
        <button class="modal-close">&times;</button>
    `;
    
    // Body del modal
    const modalBody = document.createElement('div');
    modalBody.className = 'modal-body';
    
    // Contenido del modal
    modalBody.innerHTML = `
        <p>La terminal de asistencia está ejecutándose en segundo plano. Use este panel para ver el estado y configurar opciones.</p>
        
        <div style="margin: 20px 0;">
            <h3>Estado del Servicio</h3>
            <div style="margin-top: 10px; padding: 15px; background-color: #f0f8ff; border-left: 4px solid #1976D2; border-radius: 4px;">
                <div style="display: flex; align-items: center;">
                    <i class="fas fa-circle" style="color: #4CAF50; margin-right: 10px;"></i>
                    <span>Terminal activa y funcionando correctamente</span>
                </div>
                <div style="margin-top: 10px; font-size: 13px; color: #666;">
                    <span>Último registro: </span>
                    <span id="last-checkin-time">Hace 5 minutos</span>
                </div>
            </div>
        </div>
        
        <div style="margin: 25px 0;">
            <h3>Opciones del Terminal</h3>
            
            <div style="margin-top: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <label style="font-weight: 500;">
                        <input type="checkbox" checked> 
                        Mostrar nombre del empleado
                    </label>
                    
                    <div class="toggle-switch">
                        <input type="checkbox" id="toggle-name" class="toggle-checkbox" checked>
                        <label for="toggle-name" class="toggle-label"></label>
                    </div>
                </div>
                
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <label style="font-weight: 500;">
                        <input type="checkbox" checked> 
                        Reproducir sonidos
                    </label>
                    
                    <div class="toggle-switch">
                        <input type="checkbox" id="toggle-sound" class="toggle-checkbox" checked>
                        <label for="toggle-sound" class="toggle-label"></label>
                    </div>
                </div>
                
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <label style="font-weight: 500;">
                        <input type="checkbox" checked> 
                        Modo de pantalla completa
                    </label>
                    
                    <div class="toggle-switch">
                        <input type="checkbox" id="toggle-fullscreen" class="toggle-checkbox">
                        <label for="toggle-fullscreen" class="toggle-label"></label>
                    </div>
                </div>
            </div>
        </div>
        
        <div style="margin: 25px 0;">
            <h3>Acciones Rápidas</h3>
            
            <div style="margin-top: 15px; display: flex; gap: 10px;">
                <button class="action-button" id="restart-terminal-btn">
                    <i class="fas fa-sync-alt"></i> Reiniciar Terminal
                </button>
                
                <button class="action-button" id="open-terminal-btn">
                    <i class="fas fa-external-link-alt"></i> Abrir en Nueva Ventana
                </button>
            </div>
        </div>
        
        <style>
            .toggle-switch {
                position: relative;
                display: inline-block;
                width: 60px;
                height: 30px;
            }
            
            .toggle-checkbox {
                opacity: 0;
                width: 0;
                height: 0;
            }
            
            .toggle-label {
                position: absolute;
                cursor: pointer;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: #ccc;
                transition: .4s;
                border-radius: 34px;
            }
            
            .toggle-label:before {
                position: absolute;
                content: "";
                height: 22px;
                width: 22px;
                left: 4px;
                bottom: 4px;
                background-color: white;
                transition: .4s;
                border-radius: 50%;
            }
            
            .toggle-checkbox:checked + .toggle-label {
                background-color: #1976D2;
            }
            
            .toggle-checkbox:checked + .toggle-label:before {
                transform: translateX(30px);
            }
            
            .action-button {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 5px;
            }
            
            .action-button:hover {
                background-color: #e9e9e9;
            }
            
            #restart-terminal-btn {
                background-color: #FFF8E1;
                border-color: #FFE082;
                color: #FF8F00;
            }
            
            #restart-terminal-btn:hover {
                background-color: #FFECB3;
            }
            
            #open-terminal-btn {
                background-color: #E8F5E9;
                border-color: #A5D6A7;
                color: #2E7D32;
            }
            
            #open-terminal-btn:hover {
                background-color: #C8E6C9;
            }
        </style>
    `;
    
    // Footer del modal
    const modalFooter = document.createElement('div');
    modalFooter.className = 'modal-footer';
    modalFooter.innerHTML = `
        <button class="secondary-btn" id="close-modal-btn">Cerrar</button>
        <button class="primary-btn" id="save-terminal-config-btn">Guardar Configuración</button>
    `;
    
    // Agregar todo al modal
    modalContainer.appendChild(modalHeader);
    modalContainer.appendChild(modalBody);
    modalContainer.appendChild(modalFooter);
    modalOverlay.appendChild(modalContainer);
    
    // Evento para cerrar con el botón de footer
    setTimeout(() => {
        const closeModalBtn = modalOverlay.querySelector('#close-modal-btn');
        if (closeModalBtn) {
            closeModalBtn.addEventListener('click', function() {
                modalOverlay.classList.remove('active');
                document.body.style.overflow = '';
            });
        }
        
        // Evento para guardar configuración
        const saveConfigBtn = modalOverlay.querySelector('#save-terminal-config-btn');
        if (saveConfigBtn) {
            saveConfigBtn.addEventListener('click', function() {
                // Aquí iría la lógica para guardar la configuración
                // Mostrar mensaje de éxito
                showToast('Configuración guardada correctamente', 'success');
                
                // Cerrar el modal
                modalOverlay.classList.remove('active');
                document.body.style.overflow = '';
            });
        }
        
        // Eventos para los botones de acción
        const restartBtn = modalOverlay.querySelector('#restart-terminal-btn');
        if (restartBtn) {
            restartBtn.addEventListener('click', function() {
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Reiniciando...';
                this.disabled = true;
                
                // Simular reinicio
                setTimeout(() => {
                    this.innerHTML = '<i class="fas fa-sync-alt"></i> Reiniciar Terminal';
                    this.disabled = false;
                    
                    // Mostrar mensaje de éxito
                    showToast('Terminal reiniciado correctamente', 'success');
                }, 2000);
            });
        }
        
        const openTerminalBtn = modalOverlay.querySelector('#open-terminal-btn');
        if (openTerminalBtn) {
            openTerminalBtn.addEventListener('click', function() {
                // Abrir terminal en nueva ventana (simulado)
                window.open('/terminal', '_blank', 'width=800,height=600');
            });
        }
    }, 100);
    
    return modalOverlay;
}

// Función para mostrar notificaciones toast
function showToast(message, type = 'info') {
    // Verificar si ya existe el contenedor de toasts
    let toastContainer = document.querySelector('.toast-container');
    
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        toastContainer.style.position = 'fixed';
        toastContainer.style.bottom = '20px';
        toastContainer.style.right = '20px';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // Crear el toast
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.backgroundColor = type === 'success' ? '#4CAF50' : 
                                  type === 'error' ? '#F44336' : 
                                  type === 'warning' ? '#FF9800' : '#2196F3';
    toast.style.color = 'white';
    toast.style.padding = '12px 20px';
    toast.style.borderRadius = '4px';
    toast.style.marginTop = '10px';
    toast.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
    toast.style.display = 'flex';
    toast.style.alignItems = 'center';
    toast.style.justifyContent = 'space-between';
    toast.style.minWidth = '250px';
    toast.style.opacity = '0';
    toast.style.transition = 'all 0.3s ease';
    
    // Icono según el tipo
    const icon = type === 'success' ? 'fas fa-check-circle' : 
                 type === 'error' ? 'fas fa-exclamation-circle' : 
                 type === 'warning' ? 'fas fa-exclamation-triangle' : 'fas fa-info-circle';
    
    toast.innerHTML = `
        <div style="display: flex; align-items: center;">
            <i class="${icon}" style="margin-right: 10px;"></i>
            <span>${message}</span>
        </div>
        <button style="background: none; border: none; color: white; cursor: pointer; margin-left: 10px;">
            &times;
        </button>
    `;
    
    // Agregar al contenedor
    toastContainer.appendChild(toast);
    
    // Mostrar con animación
    setTimeout(() => {
        toast.style.opacity = '1';
    }, 10);
    
    // Configurar cierre automático
    const timeout = setTimeout(() => {
        closeToast(toast);
    }, 5000);
    
    // Evento para cerrar manualmente
    const closeBtn = toast.querySelector('button');
    closeBtn.addEventListener('click', () => {
        clearTimeout(timeout);
        closeToast(toast);
    });
    
    // Función para cerrar el toast
    function closeToast(toastElement) {
        toastElement.style.opacity = '0';
        
        setTimeout(() => {
            toastElement.remove();
            
            // Eliminar el contenedor si no hay más toasts
            if (toastContainer.childNodes.length === 0) {
                toastContainer.remove();
            }
        }, 300);
    }
}

// Inicializar tablas de datos con ordenamiento
function initDataTables() {
    const tables = document.querySelectorAll('.data-table');
    
    tables.forEach(table => {
        const headers = table.querySelectorAll('th');
        
        headers.forEach((header, index) => {
            // Si no debe ser ordenable, saltar
            if (header.classList.contains('no-sort')) return;
            
            // Agregar indicador de ordenamiento
            header.innerHTML += '<span class="sort-indicator"></span>';
            
            // Agregar cursor pointer
            header.style.cursor = 'pointer';
            
            // Evento de clic para ordenar
            header.addEventListener('click', function() {
                const isAscending = !this.classList.contains('sort-asc');
                
                // Eliminar clases de ordenamiento de todos los headers
                headers.forEach(h => {
                    h.classList.remove('sort-asc', 'sort-desc');
                });
                
                // Agregar clase de ordenamiento al header actual
                this.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
                
                // Ordenar la tabla
                sortTable(table, index, isAscending);
            });
        });
    });
}

// Función para ordenar una tabla
function sortTable(table, columnIndex, ascending) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Función para obtener el valor de una celda
    function getCellValue(row, index) {
        const cell = row.querySelector(`td:nth-child(${index + 1})`);
        return cell ? cell.textContent.trim() : '';
    }
    
    // Ordenar las filas
    rows.sort((a, b) => {
        const aValue = getCellValue(a, columnIndex);
        const bValue = getCellValue(b, columnIndex);
        
        // Intentar convertir a números si es posible
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return ascending ? aNum - bNum : bNum - aNum;
        }
        
        // Ordenar como texto
        return ascending
            ? aValue.localeCompare(bValue)
            : bValue.localeCompare(aValue);
    });
    
    // Reordenar el DOM
    rows.forEach(row => tbody.appendChild(row));
}

// Inicializar todo cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    updateClock();
    initSidebarToggle();
    initNotificationDropdown();
    initTerminalModal();
    initDataTables();
    
    // Resaltar la página actual en el menú
    highlightCurrentPage();
});

// Función para resaltar la página actual en el menú
function highlightCurrentPage() {
    const currentPath = window.location.pathname;
    const menuItems = document.querySelectorAll('.sidebar-nav ul li');
    
    menuItems.forEach(item => {
        const link = item.querySelector('a');
        if (link && link.getAttribute('href') === currentPath) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}
document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (!menuToggle || !sidebar) return;
    
    menuToggle.addEventListener('click', function() {
        // Toggle sidebar
        sidebar.classList.toggle('active');
        
        // Create or toggle overlay
        let overlay = document.querySelector('.sidebar-overlay');
        
        if (sidebar.classList.contains('active')) {
            // If no overlay exists, create one
            if (!overlay) {
                overlay = document.createElement('div');
                overlay.classList.add('sidebar-overlay', 'show');
                document.body.appendChild(overlay);
                
                // Close sidebar when clicking overlay
                overlay.addEventListener('click', function() {
                    sidebar.classList.remove('active');
                    this.remove();
                });
            }
        } else {
            // Remove overlay when sidebar is closed
            if (overlay) {
                overlay.remove();
            }
        }
    });
    
    // Responsive handling
    window.addEventListener('resize', function() {
        // Automatically close sidebar on larger screens
        if (window.innerWidth > 768) {
            sidebar.classList.remove('active');
            
            const overlay = document.querySelector('.sidebar-overlay');
            if (overlay) {
                overlay.remove();
            }
        }
    });
});