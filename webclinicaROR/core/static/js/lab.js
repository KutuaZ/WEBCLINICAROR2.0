document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("reservaForm");

    form.addEventListener("submit", function(e) {
        e.preventDefault();

        const nombre = document.getElementById("reserva-nombre");
        const email = document.getElementById("reserva-email");
        const examen = document.getElementById("reserva-examen");
        const fecha = document.getElementById("reserva-fecha");

        let valid = true;

        // Nombre
        if (!nombre.value.trim()) {
            nombre.classList.add("is-invalid");
            valid = false;
        } else {
            nombre.classList.remove("is-invalid");
            nombre.classList.add("is-valid");
        }

        // Email
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email.value.trim() || !emailPattern.test(email.value.trim())) {
            email.classList.add("is-invalid");
            valid = false;
        } else {
            email.classList.remove("is-invalid");
            email.classList.add("is-valid");
        }

        // Examen
        if (!examen.value) {
            examen.classList.add("is-invalid");
            valid = false;
        } else {
            examen.classList.remove("is-invalid");
            examen.classList.add("is-valid");
        }

        // Fecha
        if (!fecha.value) {
            fecha.classList.add("is-invalid");
            valid = false;
        } else {
            fecha.classList.remove("is-invalid");
            fecha.classList.add("is-valid");
        }

        if (valid) {
            alert("Formulario válido.");
        }
    });
});




    /*pago cuentas*/

function validarRut(rut) {

    rut = rut.replace(/\./g, '').replace(/\s/g, '').toUpperCase();  // Quitar puntos y espacios


    if (!/^(\d+)-([\dkK])$/.test(rut)) return false;

    const [cuerpo, dv] = rut.split('-');
    let suma = 0;
    let multiplo = 2;

    for (let i = cuerpo.length - 1; i >= 0; i--) {
        suma += multiplo * parseInt(cuerpo[i], 10);
        multiplo = multiplo < 7 ? multiplo + 1 : 2;
    }

    let dvEsperado = 11 - (suma % 11);
    if (dvEsperado === 11) dvEsperado = '0';
    else if (dvEsperado === 10) dvEsperado = 'K';
    else dvEsperado = dvEsperado.toString();

    return dv.toUpperCase() === dvEsperado;
}

// Validación al enviar
document.getElementById("pago-form").addEventListener("submit", function(e) {
    e.preventDefault();
    const rutInput = document.getElementById("pago-rut");
    const rut = rutInput.value;
    const errorDiv = document.getElementById("rut-error");

    if (!validarRut(rut)) {
        errorDiv.style.display = "block";
        rutInput.classList.add("is-invalid");
    } else {
        errorDiv.style.display = "none";
        rutInput.classList.remove("is-invalid");
        rutInput.classList.add("is-valid");
        alert(" RUT válido. Redirigiendo a la página de pago...");
    }
});
    /*Fin pago cuentas*/