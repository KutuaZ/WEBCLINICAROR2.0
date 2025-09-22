/* /core/static/js/login.js */

document.addEventListener("DOMContentLoaded", function () {
    
    // --- SCRIPT PARA EL FORMULARIO DE INICIO DE SESIÓN ---
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        const email = document.getElementById("login-email");
        const password = document.getElementById("login-password");

        loginForm.addEventListener("submit", function (e) {
            let valid = true;
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!email.value.trim() || !emailPattern.test(email.value.trim())) {
                valid = false;
            }
            if (!password.value.trim() || password.value.trim().length < 6) {
                valid = false;
            }
            // Si la validación en JavaScript falla, se previene el envío.
            // Si es válida, el formulario se envía normalmente.
            if (!valid) {
                e.preventDefault(); 
            }
        });
    }

    // --- SCRIPT PARA EL FORMULARIO DE TELEMEDICINA ---
    const telemedForm = document.getElementById("telemedForm");
    if (telemedForm) {
        const messageInput = document.getElementById("telemed-message");
        const wordCount = document.getElementById("telemedWordCount");
        const maxWords = 50;

        function countWords(text) {
            if (!text.trim()) return 0;
            return text.trim().split(/\s+/).length;
        }

        messageInput.addEventListener("input", function() {
            let words = countWords(this.value);
            if (words > maxWords) {
                let trimmed = this.value.split(/\s+/).slice(0, maxWords).join(" ");
                this.value = trimmed;
                words = maxWords;
            }
            wordCount.textContent = `${words} / ${maxWords} palabras`;
        });
    }

    // --- SCRIPT PARA EL FORMULARIO DE ARANCELES ---
    const arancelForm = document.getElementById("arancelForm");
    if (arancelForm) {
        arancelForm.addEventListener("submit", function(e) {
            if (!arancelForm.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            } else {
                alert("Solicitud enviada. Se enviará el presupuesto a tu correo.");
                e.preventDefault(); 
            }
            arancelForm.classList.add("was-validated");
        }, false);
    }
});