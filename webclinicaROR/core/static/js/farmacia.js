document.addEventListener('DOMContentLoaded', () => {
    // --- LÓGICA PARA AÑADIR AL CARRITO ---
    const productListContainer = document.getElementById('product-list');
    
    if (!productListContainer) {
        console.error("Error: No se encontró el contenedor de productos ('product-list') en el HTML.");
        return;
    }

    productListContainer.addEventListener('click', (e) => {
        // Nos aseguramos de que el clic fue en un botón de "Agregar al carrito"
        if (e.target && e.target.classList.contains('btn-add')) {
            const button = e.target;
            const productoId = button.dataset.productoId;

            // Verificamos que tengamos el token de seguridad
            if (typeof csrftoken === 'undefined') {
                console.error('Error Crítico: El token CSRF (csrftoken) no está definido en la plantilla HTML.');
                alert('Error de seguridad. No se pudo procesar la solicitud.');
                return;
            }

            const url = `/carrito/agregar/${productoId}/`;

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    // Si hay un error en el servidor (ej. 404, 500), lo mostramos
                    throw new Error(`Error del servidor: ${response.status} ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Respuesta del servidor:', data.mensaje);
                
                // Actualizamos el número en el ícono del carrito
                const badge = document.getElementById('carrito-badge');
                if (badge) {
                    let currentCount = parseInt(badge.textContent || 0);
                    badge.textContent = currentCount + 1;
                }

                // Damos feedback visual al usuario
                button.textContent = '¡Agregado!';
                button.disabled = true; // Deshabilitamos para evitar doble clic
                setTimeout(() => {
                    button.textContent = 'Agregar al carrito';
                    button.disabled = false;
                }, 1500);
            })
            .catch(error => {
                console.error('Error al agregar el producto:', error);
                alert('Hubo un problema al agregar el producto. Revisa la consola para más detalles.');
            });
        }
    });

    // --- LÓGICA DEL BUSCADOR ---
    const buscador = document.querySelector('form[role="search"] input');
    if (buscador) {
        const productos = document.querySelectorAll('.producto');
        buscador.addEventListener('keyup', () => {
            const texto = buscador.value.toLowerCase();
            productos.forEach(prod => {
                const nombre = prod.dataset.nombre.toLowerCase();
                // Si el nombre del producto incluye el texto de búsqueda, lo muestra. Si no, lo oculta.
                prod.style.display = nombre.includes(texto) ? '' : 'none';
            });
        });
    }
});