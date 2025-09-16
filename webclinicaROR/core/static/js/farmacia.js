// --- BUSCADOR ---
const buscador = document.querySelector('form[role="search"] input');
const productos = document.querySelectorAll('.producto');

buscador.addEventListener('keyup', () => {
    const texto = buscador.value.toLowerCase();
    productos.forEach(prod => {
        const nombre = prod.dataset.nombre.toLowerCase();
        prod.style.display = nombre.includes(texto) ? '' : 'none';
    });
});

// --- CARRITO ---
let carrito = [];
const botones = document.querySelectorAll('.btn-add');
const badge = document.querySelector('.badge');
const listaCarrito = document.getElementById('lista-carrito');
const totalCarrito = document.getElementById('total-carrito');

// agregar producto al carrito
botones.forEach(btn => {
    btn.addEventListener('click', (e) => {
        const card = e.target.closest('.producto-card');
        const nombre = card.querySelector('.producto-nombre').textContent.trim();
        const precioText = card.querySelector('.producto-precio').textContent.trim();
        const precio = parseInt(precioText.replace(/[^0-9]/g, ''), 10);

        carrito.push({ nombre, precio });
        renderizarCarrito();
    });
});

// eliminar producto del carrito
function eliminarDelCarrito(index) {
    carrito.splice(index, 1); 
    renderizarCarrito();
}

// renderizar carrito
function renderizarCarrito() {
    listaCarrito.innerHTML = "";
    let total = 0;

    carrito.forEach((item, index) => {
        total += item.precio;

        const li = document.createElement("li");
        li.className = "list-group-item d-flex justify-content-between align-items-center";

        li.innerHTML = `
        <span>${item.nombre} - $${item.precio.toLocaleString()}</span>
        <button class="btn btn-sm btn-Success">❌</button>
    `;

        li.querySelector("button").addEventListener("click", () => eliminarDelCarrito(index));
        listaCarrito.appendChild(li);
    });

    // contador carrito
    badge.textContent = carrito.length;

    // total carrito
    totalCarrito.textContent = `$${total.toLocaleString()}`;
}
