document.addEventListener('DOMContentLoaded', function() {
    // Selectores de elementos
    const elementos = {
        nombreFiltro: document.getElementById('nombre-filtro'),
        departamentoFiltro: document.getElementById('departamento-filtro'),
        estatusFiltro: document.getElementById('estatus-filtro'),
        aplicarFiltrosBtn: document.getElementById('aplicar-filtros'),
        nuevoEmpleadoBtn: document.getElementById('nuevo-empleado'),
        newEmpleadoModal: document.getElementById('new-empleado-modal'),
        prevPageBtn: document.getElementById('prev-page'),
        nextPageBtn: document.getElementById('next-page'),
        pageInfo: document.getElementById('page-info'),
        menuToggle: document.getElementById('menu-toggle'),
        sidebar: document.querySelector('.sidebar')
    };

    // Configuración de paginación
    const configPaginacion = {
        paginaActual: 1,
        elementosPorPagina: 10
    };

    
    // Función para manejar modales
    function initModalHandlers() {
        const closeModalBtns = elementos.newEmpleadoModal.querySelectorAll('.close, #cancelar-nuevo-empleado');
        const nuevoEmpleadoForm = document.getElementById('nuevo-empleado-form');

        // Abrir modal
        elementos.nuevoEmpleadoBtn.addEventListener('click', () => {
            elementos.newEmpleadoModal.style.display = 'block';
        });

        // Cerrar modal
        closeModalBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                elementos.newEmpleadoModal.style.display = 'none';
            });
        });

        // Cerrar modal al hacer clic fuera
        window.addEventListener('click', (event) => {
            if (event.target === elementos.newEmpleadoModal) {
                elementos.newEmpleadoModal.style.display = 'none';
            }
        });

        // Manejo de formulario de nuevo empleado
        nuevoEmpleadoForm.addEventListener('submit', handleNuevoEmpleadoSubmit);
    }

    // Manejar submit de nuevo empleado
    function handleNuevoEmpleadoSubmit(event) {
        event.preventDefault();

        const formData = new FormData(event.target);

        fetch("{{ url_for('crear_empleado') }}", {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarNotificacion('Empleado creado exitosamente', 'success');
                elementos.newEmpleadoModal.style.display = 'none';
                location.reload();
            } else {
                mostrarNotificacion(`Error al crear empleado: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarNotificacion('Ocurrió un error al crear el empleado', 'error');
        });
    }

    // Inicializar botones de edición y vista
    function initAccionesEmpleado() {
        const editButtons = document.querySelectorAll('.btn-edit');
        const viewButtons = document.querySelectorAll('.btn-view');

        editButtons.forEach(button => {
            button.addEventListener('click', () => {
                const empleadoId = button.getAttribute('data-id');
                fetch(`/empleados/editar/${empleadoId}`)
                    .then(response => response.json())
                    .then(data => {
                        mostrarModalEdicion(data);
                    })
                    .catch(error => {
                        console.error('Error al recuperar datos del empleado:', error);
                        mostrarNotificacion('No se pudieron cargar los datos del empleado', 'error');
                    });
            });
        });

        viewButtons.forEach(button => {
            button.addEventListener('click', () => {
                const empleadoId = button.getAttribute('data-id');
                fetch(`/empleados/ver/${empleadoId}`)
                    .then(response => response.json())
                    .then(mostrarDetallesEmpleado)
                    .catch(error => {
                        console.error('Error al recuperar datos del empleado:', error);
                        mostrarNotificacion('No se pudieron cargar los detalles del empleado', 'error');
                    });
            });
        });
    }

    // Mostrar modal de detalles de empleado
    function mostrarDetallesEmpleado(empleado) {
        const detallesModal = crearModalDinamico({
            titulo: 'Detalles del Empleado',
            contenido: `
                <div class="empleado-detalles">
                    <div class="detalles-grid">
                        <div class="detalles-item">
                            <span class="detalles-label">Nombre:</span>
                            <span>${empleado.nombre} ${empleado.apellidos}</span>
                        </div>
                        <div class="detalles-item">
                            <span class="detalles-label">RFC:</span>
                            <span>${empleado.rfc}</span>
                        </div>
                        <div class="detalles-item">
                            <span class="detalles-label">Departamento:</span>
                            <span>${empleado.departamento}</span>
                        </div>
                        <div class="detalles-item">
                            <span class="detalles-label">Fecha de Ingreso:</span>
                            <span>${empleado.fecha_ingreso}</span>
                        </div>
                        <div class="detalles-item">
                            <span class="detalles-label">Estatus:</span>
                            <span class="${empleado.activo ? 'badge-success' : 'badge-danger'}">
                                ${empleado.activo ? 'Activo' : 'Inactivo'}
                            </span>
                        </div>
                    </div>
                </div>
            `
        });
    }

    // Función para crear modales dinámicamente
    function crearModalDinamico({ titulo, contenido }) {
        const modal = document.createElement('div');
        modal.classList.add('modal');
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${titulo}</h2>
                    <button class="modal-close" aria-label="Cerrar">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                ${contenido}
            </div>
        `;

        document.body.appendChild(modal);
        modal.style.display = 'block';

        // Manejadores de cierre
        const closeBtn = modal.querySelector('.modal-close');
        closeBtn.addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                document.body.removeChild(modal);
            }
        });

        return modal;
    }

    // Mostrar modal de edición
    function mostrarModalEdicion(empleado) {
        const modalEdicion = crearModalDinamico({
            titulo: 'Editar Empleado',
            contenido: `
                <form id="editar-empleado-form">
                    <input type="hidden" name="id" value="${empleado._id}">
                    <div class="form-grid">
                        <div class="form-group">
                            <label for="nombre-editar">Nombre</label>
                            <input type="text" id="nombre-editar" name="nombre" value="${empleado.nombre}" required>
                        </div>
                        <div class="form-group">
                            <label for="apellidos-editar">Apellidos</label>
                            <input type="text" id="apellidos-editar" name="apellidos" value="${empleado.apellidos}" required>
                        </div>
                        <!-- Agregar más campos según sea necesario -->
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">Guardar Cambios</button>
                        <button type="button" class="btn btn-secondary modal-close">Cancelar</button>
                    </div>
                </form>
            `
        });

        const formEditar = modalEdicion.querySelector('#editar-empleado-form');
        formEditar.addEventListener('submit', handleEditarEmpleado);
    }

    // Manejar edición de empleado
    function handleEditarEmpleado(event) {
        event.preventDefault();
        const formData = new FormData(event.target);

        fetch("/empleados/actualizar", {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarNotificacion('Empleado actualizado exitosamente', 'success');
                location.reload();
            } else {
                mostrarNotificacion(`Error al actualizar empleado: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarNotificacion('Ocurrió un error al actualizar el empleado', 'error');
        });
    }

    // Sistema de filtrado
    function initFiltrado() {
        elementos.aplicarFiltrosBtn.addEventListener('click', () => {
            const filtros = {
                nombre: elementos.nombreFiltro.value.toLowerCase(),
                departamento: elementos.departamentoFiltro.value,
                estatus: elementos.estatusFiltro.value
            };

            aplicarFiltrosDinamicos(filtros);
        });
    }

    // Aplicar filtros dinámicamente
    function aplicarFiltrosDinamicos(filtros) {
        const filas = document.querySelectorAll('.data-table tbody tr');
        
        filas.forEach(fila => {
            const nombre = fila.querySelector('td:nth-child(2)').textContent.toLowerCase();
            const departamento = fila.querySelector('td:nth-child(3)').textContent;
            const estatus = fila.querySelector('.badge').textContent.toLowerCase();

            const mostrarFila = 
                (filtros.nombre === '' || nombre.includes(filtros.nombre)) &&
                (filtros.departamento === '' || departamento === filtros.departamento) &&
                (filtros.estatus === '' || estatus === filtros.estatus);

            fila.style.display = mostrarFila ? '' : 'none';
        });

        // Reiniciar paginación
        configPaginacion.paginaActual = 1;
        actualizarPaginacion();
    }

    // Sistema de paginación
    function initPaginacion() {
        function actualizarPaginacion() {
            const filas = document.querySelectorAll('.data-table tbody tr:not([style*="display: none"])');
            const totalPaginas = Math.ceil(filas.length / configPaginacion.elementosPorPagina);

            // Mostrar/ocultar filas según página actual
            filas.forEach((fila, index) => {
                const paginaFila = Math.floor(index / configPaginacion.elementosPorPagina) + 1;
                fila.style.display = paginaFila === configPaginacion.paginaActual ? '' : 'none';
            });

            // Actualizar información de página
            elementos.pageInfo.textContent = `Página ${configPaginacion.paginaActual} de ${totalPaginas}`;

            // Habilitar/deshabilitar botones de navegación
            elementos.prevPageBtn.disabled = configPaginacion.paginaActual === 1;
            elementos.nextPageBtn.disabled = configPaginacion.paginaActual === totalPaginas;
        }

        // Evento página anterior
        elementos.prevPageBtn.addEventListener('click', () => {
            if (configPaginacion.paginaActual > 1) {
                configPaginacion.paginaActual--;
                actualizarPaginacion();
            }
        });

        // Evento página siguiente
        elementos.nextPageBtn.addEventListener('click', () => {
            const filas = document.querySelectorAll('.data-table tbody tr:not([style*="display: none"])');
            const totalPaginas = Math.ceil(filas.length / configPaginacion.elementosPorPagina);
            
            if (configPaginacion.paginaActual < totalPaginas) {
                configPaginacion.paginaActual++;
                actualizarPaginacion();
            }
        });

        // Inicializar paginación
        actualizarPaginacion();
    }

    
    // Función de notificación
    function mostrarNotificacion(mensaje, tipo = 'info') {
        const notificacion = document.createElement('div');
        notificacion.classList.add('notificacion', `notificacion-${tipo}`);
        notificacion.textContent = mensaje;
        
        document.body.appendChild(notificacion);
        
        setTimeout(() => {
            notificacion.classList.add('mostrar');
        }, 10);

        setTimeout(() => {
            notificacion.classList.remove('mostrar');
            setTimeout(() => {
                document.body.removeChild(notificacion);
            }, 300);
        }, 3000);
    }

    // Inicializar funcionalidades
    function init() {
        initModalHandlers();
        initAccionesEmpleado();
        initFiltrado();
        initPaginacion();
    }

 // Nueva función para manejar el menú responsive
 function initMenuResponsive() {
    if (!elementos.menuToggle || !elementos.sidebar) return;

    elementos.menuToggle.addEventListener('click', toggleSidebar);

    // Cerrar menú al hacer clic fuera en móviles
    document.addEventListener('click', function(event) {
        const esMenuToggle = elementos.menuToggle.contains(event.target);
        const esSidebar = elementos.sidebar.contains(event.target);

        if (!esMenuToggle && !esSidebar && window.innerWidth <= 768) {
            cerrarSidebar();
        }
    });

    // Manejar cambios de tamaño de ventana
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            cerrarSidebar();
        }
    });
}

// Función para alternar sidebar
function toggleSidebar() {
    elementos.sidebar.classList.toggle('active');
    crearOverlay();
}

// Función para crear overlay
function crearOverlay() {
    // Eliminar overlay existente
    let overlayExistente = document.querySelector('.sidebar-overlay');
    if (overlayExistente) {
        overlayExistente.remove();
    }

    // Si el sidebar está activo, crear overlay
    if (elementos.sidebar.classList.contains('active')) {
        const overlay = document.createElement('div');
        overlay.classList.add('sidebar-overlay');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 99;
        `;
        
        overlay.addEventListener('click', cerrarSidebar);
        document.body.appendChild(overlay);
    }
}

// Función para cerrar sidebar
function cerrarSidebar() {
    elementos.sidebar.classList.remove('active');
    
    const overlay = document.querySelector('.sidebar-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// Mejoras en tabla responsiva
function initTablaResponsiva() {
    const tabla = document.querySelector('.data-table');
    if (!tabla) return;

    const headers = Array.from(tabla.querySelectorAll('thead th'));
    const filas = tabla.querySelectorAll('tbody tr');

    filas.forEach(fila => {
        const celdas = fila.querySelectorAll('td');
        celdas.forEach((celda, index) => {
            if (headers[index]) {
                const titulo = headers[index].textContent;
                celda.setAttribute('data-title', titulo);
            }
        });
    });
}

// Mejorar formularios en móviles
function initFormulariosResponsivos() {
    const formularios = document.querySelectorAll('form');
    
    formularios.forEach(formulario => {
        // Agregar atributos para mejor experiencia en móviles
        formulario.querySelectorAll('input, select').forEach(campo => {
            campo.setAttribute('autocomplete', 'off');
            
            // Configurar tipos de input para móviles
            if (campo.type === 'date') {
                campo.setAttribute('placeholder', 'AAAA-MM-DD');
            }
        });
    });
}

// Inicialización extendida
function init() {
    // Llamadas a funciones originales
    initModalHandlers();
    initAccionesEmpleado();
    initFiltrado();
    initPaginacion();

    // Nuevas funcionalidades responsivas
    initMenuResponsive();
    initTablaResponsiva();
    initFormulariosResponsivos();

    // Ajustes de accesibilidad
    document.body.addEventListener('touchstart', function() {}, false);
}

    // Ejecutar inicialización
    init();
});

if (!window.fetch) {
    console.warn('Su navegador no soporta todas las características modernas.');
}