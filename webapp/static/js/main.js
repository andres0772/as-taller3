// Funcionalidad JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto-ocultar alertas después de 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Función para agregar productos al carrito con AJAX
function addToCart(productId, quantity = 1) {
    fetch(`/add-to-cart/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `quantity=${quantity}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Producto agregado al carrito', 'success');
        } else {
            showAlert(data.message || 'Error al agregar al carrito', 'danger');
        }
    })
    .catch(error => {
        showAlert('Error de conexión', 'danger');
    });
}

// Función para actualizar cantidad en el carrito
function updateCartQuantity(itemId, quantity) {
    fetch(`/update-cart-item/${itemId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `quantity=${quantity}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            showAlert(data.message || 'Error al actualizar', 'danger');
        }
    })
    .catch(error => {
        showAlert('Error de conexión', 'danger');
    });
}

// Función para remover items del carrito
function removeFromCart(itemId) {
    if (confirm('¿Estás seguro de que quieres eliminar este producto?')) {
        fetch(`/remove-cart-item/${itemId}`, {
            method: 'POST'
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                showAlert('Error al eliminar el producto', 'danger');
            }
        })
        .catch(error => {
            showAlert('Error de conexión', 'danger');
        });
    }
}

// Función para mostrar alertas
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}
