
/* Validación del formulario html reserva */
document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("reservaForm");

    const campos = {
        "reserva-nombre": {
            regex: /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]{3,50}$/,
            required: true,
            error: {
                required: "El nombre es obligatorio.",
                format: "Solo se permiten letras y espacios (3-50 caracteres)."
            }
        },
        "reserva-email": {
            regex: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            required: true,
            error: {
                required: "El correo es obligatorio.",
                format: "Formato de correo inválido."
            }
        },
        "reserva-telefono": {
            regex: /^\+?[0-9\s\-()]{7,15}$/,
            required: true,
            error: {
                required: "El teléfono es obligatorio.",
                format: "Formato de teléfono inválido."
            }
        },
        "reserva-rut": {
            regex: /^\d{1,2}\.\d{3}\.\d{3}-[\dKk\d]$/,
            required: true,
            error: {
                required: "El RUT es obligatorio.",
                format: "Formato de RUT inválido. X.XXX.XXX-X"
            }
        },
        "reserva-fecha": {
            required: true,
            error: { required: "La fecha es obligatoria." }
        },
        "reserva-tiempo": {
            required: true,
            error: { required: "Debe seleccionar una hora." }
        },
        "reserva-specialty": {
            required: true,
            error: { required: "Debe seleccionar una especialidad." }
        }
    };

    // Llenar opciones de hora
    const tiempoSelect = document.getElementById("reserva-tiempo");
    const horarios = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00"];
    horarios.forEach(h => {
        const opt = document.createElement("option");
        opt.value = h;
        opt.text = h;
        tiempoSelect.appendChild(opt);
    });

    function mostrarError(id, mensaje) {
        const input = document.getElementById(id);
        limpiarError(id);
        const errorElem = document.createElement("div");
        errorElem.className = "text-danger";
        errorElem.innerText = mensaje;
        input.parentNode.appendChild(errorElem);
        input.classList.add("is-invalid");
    }

    function limpiarError(id) {
        const input = document.getElementById(id);
        const error = input.parentNode.querySelector(".text-danger");
        if (error) error.remove();
        input.classList.remove("is-invalid");
    }

    form.addEventListener("submit", function(e) {
        e.preventDefault();
        let valido = true;

        Object.keys(campos).forEach(id => {
            const input = document.getElementById(id);
            const valor = input.value.trim();

            if (campos[id].required) {
                if (input.tagName === "SELECT") {
                    if (!valor) {
                        mostrarError(id, campos[id].error.required);
                        valido = false;
                        return;
                    }
                } else if (!valor) {
                    mostrarError(id, campos[id].error.required);
                    valido = false;
                    return;
                }
            }

            if (valor && campos[id].regex && !campos[id].regex.test(valor)) {
                mostrarError(id, campos[id].error.format);
                valido = false;
            } else {
                limpiarError(id);
            }
        });

        if (valido) {
            alert("¡Formulario válido! Datos enviados.");
            form.reset();
        }
    });

    // Validación en tiempo real
    Object.keys(campos).forEach(id => {
        const input = document.getElementById(id);
        if (input.tagName === "SELECT") {
            input.addEventListener("change", () => limpiarError(id));
        } else {
            input.addEventListener("input", () => limpiarError(id));
        }
    });
});


/* Acordeón en especialidades */
document.querySelectorAll('.acordeon-boton').forEach(boton => {
    boton.addEventListener('click', () => {
    const item = boton.parentElement;
    item.classList.toggle('activo');
    });
});

/* flechas cambio acordeon */
const botones = document.querySelectorAll(".acordeon-boton");

botones.forEach(boton => {
    boton.addEventListener("click", function () {
    this.classList.toggle("active");

    const contenido = this.nextElementSibling;
    if (contenido.style.maxHeight) {
        contenido.style.maxHeight = null;
    } else {
        contenido.style.maxHeight = contenido.scrollHeight + "px";
        }
    });
});


/* Validación del formulario contacto */
(() => {
    'use strict';

    const form = document.getElementById('contactForm');

    form.addEventListener('submit', function(event) {
    event.preventDefault(); // evitar envío por defecto
    event.stopPropagation();

    // Validación de campos requeridos
    let isValid = form.checkValidity();

    // Validación del mensaje: máximo 50 palabras
    const message = document.getElementById('contact-message').value.trim();
    const wordCount = message.split(/\s+/).filter(word => word.length > 0).length;
    if (wordCount > 50) {
        isValid = false;
        document.getElementById('contact-message').classList.add('is-invalid');
        document.getElementById('contact-message').nextElementSibling.textContent = 
        `El mensaje excede el límite de 50 palabras (${wordCount} actuales).`;
    } else {
        document.getElementById('contact-message').classList.remove('is-invalid');
    }

    form.classList.add('was-validated');

    if (isValid) {
        alert('Formulario enviado correctamente');
        form.reset();
        form.classList.remove('was-validated');
        }
    });
})();

    //*fin de validacion contactos*/


    //*validar formulario iniciar sesion

document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("loginForm");

    form.addEventListener("submit", function(e) {
        e.preventDefault();

        const email = document.getElementById("login-email");
        const password = document.getElementById("login-password");
        let valid = true;

        // Validar email
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email.value.trim() || !emailPattern.test(email.value.trim())) {
            email.classList.add("is-invalid");
            email.classList.remove("is-valid");
            valid = false;
        } else {
            email.classList.remove("is-invalid");
            email.classList.add("is-valid");
        }

        // Validar contraseña mínimo 6 caracteres
        if (!password.value.trim() || password.value.trim().length < 6) {
            password.classList.add("is-invalid");
            password.classList.remove("is-valid");
            valid = false;
        } else {
            password.classList.remove("is-invalid");
            password.classList.add("is-valid");
        }

        if (valid) {
            alert("Formulario válido \n.");
        }
    });
});


