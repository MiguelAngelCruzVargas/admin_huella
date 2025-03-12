// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos
    const loginForm = document.querySelector('form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginButton = document.querySelector('.btn-login');
    const firstRunModal = document.getElementById('first-run-modal');
    const formPrimeraConfig = document.getElementById('form-primera-config');
    const closeModalBtn = document.getElementById('close-modal');
    
    // Enfoque automático en el campo de usuario
    if (usernameInput) {
        usernameInput.focus();
    }
    
    // Funciones de utilidad
    function showFieldError(input, message) {
        // Eliminar error anterior si existe
        clearFieldError(input);
        
        // Crear mensaje de error
        const errorElement = document.createElement('div');
        errorElement.className = 'field-error';
        errorElement.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
        
        // Añadir estilo al campo con error
        input.classList.add('input-error');
        
        // Insertar mensaje después del campo
        input.parentNode.insertAdjacentElement('afterend', errorElement);
    }
    
    function clearFieldError(input) {
        // Remover clase de error del input
        input.classList.remove('input-error');
        
        // Buscar y eliminar mensajes de error
        const parent = input.parentNode.parentNode;
        const errorElement = parent.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
    }
    
    // Validación del formulario de login
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            let isValid = true;
            
            // Validar campo de usuario
            if (!usernameInput.value.trim()) {
                showFieldError(usernameInput, 'El usuario es obligatorio');
                isValid = false;
            } else {
                clearFieldError(usernameInput);
            }
            
            // Validar campo de contraseña
            if (!passwordInput.value) {
                showFieldError(passwordInput, 'La contraseña es obligatoria');
                isValid = false;
            } else {
                clearFieldError(passwordInput);
            }
            
            if (!isValid) {
                event.preventDefault();
                return false;
            }
            
            // Animación del botón durante el envío
            loginButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verificando...';
            loginButton.disabled = true;
            
            // La forma se enviará automáticamente si todos los campos son válidos
            return true;
        });
    }
    
    // Validación del formulario de primera configuración
    if (formPrimeraConfig) {
        formPrimeraConfig.addEventListener('submit', function(event) {
            const configUsername = document.getElementById('config-username');
            const configPassword = document.getElementById('config-password');
            const configConfirmPassword = document.getElementById('config-confirm-password');
            const configNombre = document.getElementById('config-nombre');
            const configApellido = document.getElementById('config-apellido');
            const configEmail = document.getElementById('config-email');
            const submitButton = formPrimeraConfig.querySelector('button[type="submit"]');
            
            let isValid = true;
            
            // Validar todos los campos
            if (!configUsername.value.trim()) {
                showFieldError(configUsername, 'El usuario es obligatorio');
                isValid = false;
            } else {
                clearFieldError(configUsername);
            }
            
            if (!configPassword.value) {
                showFieldError(configPassword, 'La contraseña es obligatoria');
                isValid = false;
            } else if (configPassword.value.length < 6) {
                showFieldError(configPassword, 'Mínimo 6 caracteres');
                isValid = false;
            } else {
                clearFieldError(configPassword);
            }
            
            if (!configConfirmPassword.value) {
                showFieldError(configConfirmPassword, 'Debe confirmar la contraseña');
                isValid = false;
            } else if (configConfirmPassword.value !== configPassword.value) {
                showFieldError(configConfirmPassword, 'Las contraseñas no coinciden');
                isValid = false;
            } else {
                clearFieldError(configConfirmPassword);
            }
            
            if (!configNombre.value.trim()) {
                showFieldError(configNombre, 'El nombre es obligatorio');
                isValid = false;
            } else {
                clearFieldError(configNombre);
            }
            
            if (!configApellido.value.trim()) {
                showFieldError(configApellido, 'El apellido es obligatorio');
                isValid = false;
            } else {
                clearFieldError(configApellido);
            }
            
            if (!configEmail.value.trim()) {
                showFieldError(configEmail, 'El email es obligatorio');
                isValid = false;
            } else if (!isValidEmail(configEmail.value)) {
                showFieldError(configEmail, 'Email no válido');
                isValid = false;
            } else {
                clearFieldError(configEmail);
            }
            
            if (!isValid) {
                event.preventDefault();
                
                // Hacer scroll al primer error
                const firstError = document.querySelector('.field-error');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
                
                return false;
            }
            
            // Animación del botón durante el envío
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
            submitButton.disabled = true;
            
            // La forma se enviará automáticamente si todos los campos son válidos
            return true;
        });
    }
    
    // Validación de email
    function isValidEmail(email) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }
    
    // Manejadores de eventos para campos de entrada del login
    if (usernameInput) {
        usernameInput.addEventListener('input', function() {
            clearFieldError(this);
        });
    }
    
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            clearFieldError(this);
        });
    }
    
    // Cerrar modal de primera configuración
    if (closeModalBtn && firstRunModal) {
        closeModalBtn.addEventListener('click', function() {
            // No permitir cerrar el modal en la primera ejecución
            if (confirm('¿Está seguro que desea cancelar la configuración inicial? El sistema no funcionará correctamente sin un usuario administrador.')) {
                firstRunModal.style.display = 'none';
            }
        });
    }
    
    // Manejadores de eventos para todos los inputs del formulario de primera configuración
    if (formPrimeraConfig) {
        const inputs = formPrimeraConfig.querySelectorAll('input');
        inputs.forEach(function(input) {
            input.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
    }
    
    // Añadir estilos adicionales vía JavaScript
    document.head.insertAdjacentHTML('beforeend', `
        <style>
            .input-error {
                border-color: var(--error-color) !important;
                background-color: rgba(244, 67, 54, 0.05) !important;
            }
            
            .field-error {
                color: var(--error-color);
                font-size: 12px;
                margin-top: 5px;
                display: flex;
                align-items: center;
                gap: 5px;
                animation: slideIn 0.3s ease;
            }
            
            @media (max-width: 480px) {
                .field-error {
                    font-size: 11px;
                }
            }
        </style>
    `);
});