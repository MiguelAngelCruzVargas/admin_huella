document.addEventListener('DOMContentLoaded', function() {
    // Modal de nuevo horario
    const newHorarioBtn = document.querySelector('[data-modal="new-horario"]');
    const newHorarioModal = document.getElementById('new-horario-modal');
    const closeModalBtn = newHorarioModal.querySelector('.modal-close');
    const cancelModalBtn = document.getElementById('cancelar-nuevo-horario');

    // Función para cerrar el modal
    function closeModal() {
        newHorarioModal.style.display = 'none';
    }

    // Abrir modal de nuevo horario
    if (newHorarioBtn) {
        newHorarioBtn.addEventListener('click', function() {
            newHorarioModal.style.display = 'block';
        });
    }

    // Cerrar modal con botón de cierre (x)
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }

    // Cerrar modal con botón de cancelar
    if (cancelModalBtn) {
        cancelModalBtn.addEventListener('click', closeModal);
    }

    // Cerrar modal si se hace clic fuera de él
    window.addEventListener('click', function(event) {
        if (event.target === newHorarioModal) {
            closeModal();
        }
    });

    // Manejo del formulario de nuevo horario
    const nuevoHorarioForm = document.getElementById('nuevo-horario-form');
    if (nuevoHorarioForm) {
        nuevoHorarioForm.addEventListener('submit', function(event) {
            event.preventDefault();

            // Validar que al menos un día laboral esté seleccionado
            const diasLaborales = document.querySelectorAll('input[name="dias_laborales"]:checked');
            if (diasLaborales.length === 0) {
                alert('Debe seleccionar al menos un día laboral');
                return;
            }

            // Recoger datos del formulario
            const formData = new FormData(nuevoHorarioForm);
            const horarioData = {};

            // Convertir FormData a objeto
            for (let [key, value] of formData.entries()) {
                // Manejar días laborales como array
                if (key === 'dias_laborales') {
                    if (!horarioData[key]) {
                        horarioData[key] = [];
                    }
                    horarioData[key].push(value);
                } else {
                    horarioData[key] = value;
                }
            }

            // Enviar datos al servidor mediante fetch
            fetch("{{ url_for('crear_horario') }}", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(horarioData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Mostrar mensaje de éxito
                    alert('Horario creado exitosamente');
                    
                    // Cerrar modal
                    closeModal();
                    
                    // Recargar la página o actualizar la tabla dinámicamente
                    location.reload();
                } else {
                    // Mostrar mensaje de error
                    alert('Error al crear horario: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Ocurrió un error al crear el horario');
            });
        });
    }

    // Manejo de botones de edición
    const editButtons = document.querySelectorAll('.btn-edit');
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const horarioId = this.getAttribute('data-id');
            
            // Recuperar datos del horario
            fetch(`/horarios/editar/${horarioId}`)
                .then(response => response.json())
                .then(data => {
                    // Rellenar modal de edición con datos
                    // (Este código se implementaría en un modal de edición)
                })
                .catch(error => {
                    console.error('Error al recuperar datos del horario:', error);
                });
        });
    });

    // Manejo de botones de eliminación
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const horarioId = this.getAttribute('data-id');
            
            // Confirmar eliminación
            if (confirm('¿Está seguro de eliminar este horario?')) {
                fetch(`/horarios/eliminar/${horarioId}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Eliminar fila de la tabla
                        this.closest('tr').remove();
                        alert('Horario eliminado exitosamente');
                    } else {
                        alert('Error al eliminar horario: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Ocurrió un error al eliminar el horario');
                });
            }
        });
    });
});