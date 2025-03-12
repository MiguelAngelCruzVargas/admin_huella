document.addEventListener('DOMContentLoaded', function() {
    // Selectores de elementos
    const elementos = {
        fechaFiltro: document.getElementById('fecha-filtro'),
        departamentoFiltro: document.getElementById('departamento-filtro'),
        estatusFiltro: document.getElementById('estatus-filtro'),
        aplicarFiltrosBtn: document.getElementById('aplicar-filtros'),
        limpiarFiltrosBtn: document.getElementById('limpiar-filtros'),
        prevPageBtn: document.getElementById('prev-page'),
        nextPageBtn: document.getElementById('next-page'),
        pageInfo: document.getElementById('page-info'),
        detallesModal: document.getElementById('detalles-asistencia-modal'),
        detallesContenido: document.getElementById('detalles-contenido'),
        closeModalBtn: document.querySelector('#detalles-asistencia-modal .modal-close')
    };

    // Configuración de paginación
    const configuracion = {
        paginaActual: 1,
        elementosPorPagina: 10
    };

    // Inicialización de eventos
    function inicializarEventos() {
        // Filtros
        elementos.aplicarFiltrosBtn.addEventListener('click', aplicarFiltros);
        elementos.limpiarFiltrosBtn.addEventListener('click', limpiarFiltros);

        // Botones de paginación
        elementos.prevPageBtn.addEventListener('click', irPaginaAnterior);
        elementos.nextPageBtn.addEventListener('click', irPaginaSiguiente);

        // Modal de detalles
        elementos.closeModalBtn.addEventListener('click', cerrarModal);
        elementos.detallesModal.addEventListener('click', function(event) {
            if (event.target === this) {
                cerrarModal();
            }
        });

        // Botones de ver detalles
        const detallesButtons = document.querySelectorAll('.btn-view');
        detallesButtons.forEach(button => {
            button.addEventListener('click', function() {
                const asistenciaId = this.getAttribute('data-id');
                mostrarDetallesAsistencia(asistenciaId);
            });
        });
    }

    // Aplicar filtros
    function aplicarFiltros() {
        const filtros = {
            fecha: elementos.fechaFiltro.value,
            departamento: elementos.departamentoFiltro.value,
            estatus: elementos.estatusFiltro.value
        };

        aplicarFiltrosDinamicos(filtros);
    }

    // Limpiar filtros
    function limpiarFiltros() {
        // Resetear campos de filtro
        elementos.fechaFiltro.value = '';
        elementos.departamentoFiltro.value = '';
        elementos.estatusFiltro.value = '';
        
        // Restaurar vista original
        restaurarVistaOriginal();
    }

    // Función para aplicar filtros dinámicamente
    function aplicarFiltrosDinamicos(filtros) {
        const filas = document.querySelectorAll('.data-table tbody tr');
        
        filas.forEach(fila => {
            const fecha = fila.querySelector('td[data-title="Fecha"]').textContent;
            const departamento = fila.querySelector('td[data-title="Departamento"]').textContent;
            const estatus = fila.querySelector('.badge').textContent;

            const mostrarFila = 
                (!filtros.fecha || fecha.includes(filtros.fecha)) &&
                (!filtros.departamento || departamento.trim() === filtros.departamento.trim()) &&
                (!filtros.estatus || estatus.trim() === filtros.estatus.trim());

            fila.style.display = mostrarFila ? '' : 'none';
        });

        // Reiniciar paginación después de aplicar filtros
        configuracion.paginaActual = 1;
        actualizarPaginacion();
    }

    // Restaurar vista original
    function restaurarVistaOriginal() {
        const filas = document.querySelectorAll('.data-table tbody tr');
        filas.forEach(fila => {
            fila.style.display = '';
        });

        // Reiniciar paginación
        configuracion.paginaActual = 1;
        actualizarPaginacion();
    }

    // Actualizar paginación
    function actualizarPaginacion() {
        const filas = document.querySelectorAll('.data-table tbody tr:not([style*="display: none"])');
        const totalPaginas = Math.ceil(filas.length / configuracion.elementosPorPagina);

        // Mostrar/ocultar filas según página actual
        filas.forEach((fila, index) => {
            const paginaFila = Math.floor(index / configuracion.elementosPorPagina) + 1;
            fila.style.display = paginaFila === configuracion.paginaActual ? '' : 'none';
        });

        // Actualizar información de página
        elementos.pageInfo.textContent = `Página ${configuracion.paginaActual} de ${totalPaginas || 1}`;

        // Habilitar/deshabilitar botones de navegación
        elementos.prevPageBtn.disabled = configuracion.paginaActual === 1;
        elementos.nextPageBtn.disabled = configuracion.paginaActual === totalPaginas;
    }

    // Ir a página anterior
    function irPaginaAnterior() {
        if (configuracion.paginaActual > 1) {
            configuracion.paginaActual--;
            actualizarPaginacion();
        }
    }

    // Ir a página siguiente
    function irPaginaSiguiente() {
        const filas = document.querySelectorAll('.data-table tbody tr:not([style*="display: none"])');
        const totalPaginas = Math.ceil(filas.length / configuracion.elementosPorPagina);
        
        if (configuracion.paginaActual < totalPaginas) {
            configuracion.paginaActual++;
            actualizarPaginacion();
        }
    }

    // Mostrar detalles de asistencia
    function mostrarDetallesAsistencia(asistenciaId) {
        // Simular carga de detalles (reemplazar con fetch real)
        fetch(`/asistencias/detalles/${asistenciaId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }
                return response.json();
            })
            .then(data => {
                // Construir contenido del modal
                const contenidoHTML = `
                    <div class="modal-body">
                        <div class="detalles-grid">
                            <div class="detalles-item">
                                <span class="detalles-label">Empleado</span>
                                <span class="detalles-value">${data.empleado.nombre} ${data.empleado.apellidos}</span>
                            </div>
                            <div class="detalles-item">
                                <span class="detalles-label">Fecha</span>
                                <span class="detalles-value">${data.fecha_entrada}</span>
                            </div>
                            <div class="detalles-item">
                                <span class="detalles-label">Hora Entrada</span>
                                <span class="detalles-value">${data.hora_entrada}</span>
                            </div>
                            <div class="detalles-item">
                                <span class="detalles-label">Hora Salida</span>
                                <span class="detalles-value">${data.hora_salida || 'Pendiente'}</span>
                            </div>
                            <div class="detalles-item">
                                <span class="detalles-label">Estatus</span>
                                <span class="detalles-value">${data.estatus}</span>
                            </div>
                        </div>
                    </div>
                `;

                elementos.detallesContenido.innerHTML = contenidoHTML;
                elementos.detallesModal.style.display = 'block';
            })
            .catch(error => {
                console.error('Error al cargar detalles:', error);
                elementos.detallesContenido.innerHTML = `
                    <div class="modal-body">
                        <p class="error-message">
                            <i class="fas fa-exclamation-circle"></i> 
                            No se pudieron cargar los detalles de la asistencia.
                        </p>
                    </div>
                `;
                elementos.detallesModal.style.display = 'block';
            });
    }

    // Cerrar modal
    function cerrarModal() {
        elementos.detallesModal.style.display = 'none';
    }

    // Inicializar
    function init() {
        inicializarEventos();
        actualizarPaginacion();
    }

    // Ejecutar inicialización
    init();
});