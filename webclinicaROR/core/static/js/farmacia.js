document.addEventListener('DOMContentLoaded', () => {
    // --- LÓGICA  CARRITO ---
    const productListContainer = document.getElementById('product-list');
    
    if (!productListContainer) {
        console.error("Error: No se encontró el contenedor de productos ('product-list') en el HTML.");
        return;
    }

    productListContainer.addEventListener('click', (e) => {
        if (e.target && e.target.classList.contains('btn-add')) {
            const button = e.target;
            const productoId = button.dataset.productoId;

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

                    throw new Error(`Error del servidor: ${response.status} ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Respuesta del servidor:', data.mensaje);
                
                const badge = document.getElementById('carrito-badge');
                if (badge) {
                    let currentCount = parseInt(badge.textContent || 0);
                    badge.textContent = currentCount + 1;
                }


                button.textContent = '¡Agregado!';
                button.disabled = true; 
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
                prod.style.display = nombre.includes(texto) ? '' : 'none';
            });
        });
    }
});