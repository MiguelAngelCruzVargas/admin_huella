document.addEventListener('DOMContentLoaded', () => {
    // Elementos de filtrado
    const tipoReporteSelect = document.getElementById('tipo-reporte');
    const fechaInicioInput = document.getElementById('fecha-inicio');
    const fechaFinInput = document.getElementById('fecha-fin');
    const departamentoSelect = document.getElementById('departamento');
    const generarReporteBtn = document.getElementById('generar-reporte');
    const exportarReporteBtn = document.getElementById('exportar-reporte');

    // Contenedores de visualización
    const reporteContainer = document.getElementById('reporte-container');
    const graficoAsistencias = document.getElementById('grafico-asistencias');
    const graficoHoras = document.getElementById('grafico-horas');

    // Modal de configuración
    const configuracionReporteModal = document.getElementById('configuracion-reporte-modal');
    const closeModalBtn = configuracionReporteModal.querySelector('.close');
    const configuracionReporteForm = document.getElementById('configuracion-reporte-form');

    // Variables globales para almacenar datos de reporte
    let datosReporte = null;
    let configuracionReporte = {
        columnas: ['nombre', 'departamento', 'fecha'],
        formato: 'pdf'
    };

    // Establecer fechas por defecto
    const hoy = new Date();
    const primerDiaDelMes = new Date(hoy.getFullYear(), hoy.getMonth(), 1);
    fechaInicioInput.valueAsDate = primerDiaDelMes;
    fechaFinInput.valueAsDate = hoy;

    // Evento para generar reporte
    generarReporteBtn.addEventListener('click', async () => {
        const filtros = {
            tipoReporte: tipoReporteSelect.value,
            fechaInicio: fechaInicioInput.value,
            fechaFin: fechaFinInput.value,
            departamento: departamentoSelect.value
        };

        // Validar fechas
        if (!validarFechas(filtros.fechaInicio, filtros.fechaFin)) {
            return;
        }

        try {
            const response = await fetch('/reportes/generar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(filtros)
            });

            const data = await response.json();

            if (data.success) {
                // Almacenar datos del reporte
                datosReporte = data.datos;
                
                // Mostrar tabla de reporte
                mostrarTablaReporte(data.datos);
                
                // Generar gráficos
                generarGraficos(data.datos);
                
                // Habilitar botón de exportación
                exportarReporteBtn.disabled = false;
            } else {
                mostrarMensajeError(data.message);
            }
        } catch (error) {
            console.error('Error al generar reporte:', error);
            mostrarMensajeError('Ocurrió un error al generar el reporte');
        }
    });

    // Evento de exportación
    exportarReporteBtn.addEventListener('click', () => {
        if (!datosReporte) {
            alert('Primero debe generar un reporte');
            return;
        }

        // Abrir modal de configuración de exportación
        configuracionReporteModal.style.display = 'block';
    });

    // Cerrar modal de configuración
    closeModalBtn.addEventListener('click', () => {
        configuracionReporteModal.style.display = 'none';
    });

    // Envío de configuración de exportación
    configuracionReporteForm.addEventListener('submit', (event) => {
        event.preventDefault();

        // Recoger configuración
        const columnas = Array.from(
            document.querySelectorAll('input[name="columnas"]:checked')
        ).map(input => input.value);
        const formato = document.getElementById('formato-exportacion').value;

        // Actualizar configuración
        configuracionReporte = { columnas, formato };

        // Exportar reporte
        exportarReporte(datosReporte, configuracionReporte);

        // Cerrar modal
        configuracionReporteModal.style.display = 'none';
    });

    // Función para validar fechas
    function validarFechas(fechaInicio, fechaFin) {
        if (!fechaInicio || !fechaFin) {
            alert('Debe seleccionar tanto fecha de inicio como de fin');
            return false;
        }

        const inicio = new Date(fechaInicio);
        const fin = new Date(fechaFin);

        if (inicio > fin) {
            alert('La fecha de inicio no puede ser posterior a la fecha de fin');
            return false;
        }

        return true;
    }

    // Función para mostrar tabla de reporte
    function mostrarTablaReporte(datos) {
        // Limpiar contenedor
        reporteContainer.innerHTML = '';

        // Crear tabla
        const tabla = document.createElement('table');
        tabla.classList.add('tabla-reporte');

        // Crear encabezado
        const thead = document.createElement('thead');
        const encabezados = ['Nombre', 'Departamento', 'Fecha', 'Estatus'];
        const trEncabezados = document.createElement('tr');
        encabezados.forEach(encabezado => {
            const th = document.createElement('th');
            th.textContent = encabezado;
            trEncabezados.appendChild(th);
        });
        thead.appendChild(trEncabezados);
        tabla.appendChild(thead);

        // Crear cuerpo de tabla
        const tbody = document.createElement('tbody');
        datos.forEach(item => {
            const tr = document.createElement('tr');
            
            // Crear celdas
            const celdas = [
                item.nombre,
                item.departamento,
                item.fecha,
                item.estatus
            ];

            celdas.forEach(texto => {
                const td = document.createElement('td');
                td.textContent = texto;
                tr.appendChild(td);
            });

            tbody.appendChild(tr);
        });
        tabla.appendChild(tbody);

        // Añadir tabla al contenedor
        reporteContainer.appendChild(tabla);
    }

    // Función para generar gráficos
    function generarGraficos(datos) {
        // Verificar si Chart está disponible
        if (typeof Chart === 'undefined') {
            console.error('Chart.js no está cargado');
            return;
        }

        // Gráfico de Asistencias
        graficoAsistencias.innerHTML = '';
        const ctxAsistencias = document.createElement('canvas');
        graficoAsistencias.appendChild(ctxAsistencias);

        new Chart(ctxAsistencias, {
            type: 'bar',
            data: {
                labels: ['Normal', 'Retardo', 'Falta'],
                datasets: [{
                    label: 'Estatus de Asistencia',
                    data: [
                        datos.filter(d => d.estatus === 'Normal').length,
                        datos.filter(d => d.estatus === 'Retardo').length,
                        datos.filter(d => d.estatus === 'Falta').length
                    ],
                    backgroundColor: ['#4CAF50', '#FFC107', '#F44336']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Distribución de Asistencias'
                    }
                }
            }
        });

        // Gráfico de Horas
        graficoHoras.innerHTML = '';
        const ctxHoras = document.createElement('canvas');
        graficoHoras.appendChild(ctxHoras);

        new Chart(ctxHoras, {
            type: 'pie',
            data: {
                labels: ['Horas Trabajadas', 'Horas Extra', 'Horas No Trabajadas'],
                datasets: [{
                    data: [40, 5, 3],
                    backgroundColor: ['#2196F3', '#FF9800', '#9C27B0']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Distribución de Horas'
                    }
                }
            }
        });
    }

    // Función para exportar reporte
    async function exportarReporte(datos, configuracion) {
        try {
            // Filtrar columnas según configuración
            const datosExportar = datos.map(item => {
                const nuevoItem = {};
                configuracion.columnas.forEach(columna => {
                    nuevoItem[columna] = item[columna];
                });
                return nuevoItem;
            });

            // Llamada al backend para exportar
            const response = await fetch('/reportes/exportar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    datos: datosExportar,
                    formato: configuracion.formato
                })
            });

            const blob = await response.blob();

            // Crear enlace de descarga
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `reporte.${configuracion.formato}`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        } catch (error) {
            console.error('Error al exportar reporte:', error);
            mostrarMensajeError('Ocurrió un error al exportar el reporte');
        }
    }

    // Función para mostrar mensajes de error
    function mostrarMensajeError(mensaje) {
        reporteContainer.innerHTML = `
            <div class="mensaje-error">
                <p>${mensaje}</p>
            </div>
        `;
    }

    // Eventos de cierre de modal
    window.addEventListener('click', (event) => {
        if (event.target === configuracionReporteModal) {
            configuracionReporteModal.style.display = 'none';
        }
    });
});