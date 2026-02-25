from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import os
from datetime import datetime

# Configurar la aplicación Flask
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "clave-por-defecto-cambiar")

# Configurar la URL de la API
API_URL = os.getenv("API_URL", "http://api:8000")


def api_request(endpoint, method="GET", data=None, headers=None):
    """Función helper para hacer requests a la API"""
    url = f"{API_URL}{endpoint}"
    default_headers = {"Content-Type": "application/json"}

    if headers:
        default_headers.update(headers)

    # Incluir cookies de sesión si existen
    if "session_token" in session:
        default_headers["Authorization"] = f"Bearer {session.get('session_token')}"

    try:
        if method == "GET":
            response = requests.get(url, headers=default_headers, timeout=10)
        elif method == "POST":
            response = requests.post(
                url, json=data, headers=default_headers, timeout=10
            )
        elif method == "PUT":
            response = requests.put(url, json=data, headers=default_headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=default_headers, timeout=10)
        else:
            return None, f"Método {method} no soportado"

        return response, None
    except requests.exceptions.RequestException as e:
        return None, str(e)


def is_logged_in():
    """Función para verificar si el usuario está logueado"""
    return "user_id" in session and "username" in session


@app.route("/")
def index():
    """Página principal"""
    # Obtener productos destacados de la API
    response, error = api_request("/api/v1/products/")

    if error:
        flash(f"Error al conectar con la API: {error}", "danger")
        products = []
    else:
        products = response.json() if response.status_code == 200 else []

    return render_template("index.html", products=products[:4])


@app.route("/products")
def products():
    """Página de productos"""
    # Obtener lista de productos de la API
    response, error = api_request("/api/v1/products/")

    if error:
        flash(f"Error al conectar con la API: {error}", "danger")
        products = []
    else:
        products = response.json() if response.status_code == 200 else []

    return render_template("products.html", products=products)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Página de login"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Enviar datos a la API de autenticación
        data = {"username": username, "password": password}
        response, error = api_request("/api/v1/users/login", method="POST", data=data)

        if error:
            flash(f"Error de conexión: {error}", "danger")
        elif response.status_code == 200:
            user_data = response.json().get("user", {})
            session["user_id"] = user_data.get("id")
            session["username"] = user_data.get("username")
            session["email"] = user_data.get("email")
            flash("¡Login exitoso!", "success")
            return redirect(url_for("index"))
        else:
            flash(response.json().get("detail", "Error en el login"), "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Página de registro"""
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Las contraseñas no coinciden", "danger")
            return render_template("register.html")

        # Enviar datos a la API de registro
        data = {"username": username, "email": email, "password": password}
        response, error = api_request(
            "/api/v1/users/register", method="POST", data=data
        )

        if error:
            flash(f"Error de conexión: {error}", "danger")
        elif response.status_code == 201:
            flash("¡Registro exitoso! Por favor, inicia sesión.", "success")
            return redirect(url_for("login"))
        else:
            flash(response.json().get("detail", "Error en el registro"), "danger")

    return render_template("register.html")


@app.route("/cart")
def cart():
    """Página del carrito"""
    if not is_logged_in():
        flash("Debes iniciar sesión para ver el carrito", "warning")
        return redirect(url_for("login"))

    # Obtener carrito del usuario de la API
    user_id = session.get("user_id")
    response, error = api_request(f"/api/v1/carts/?user_id={user_id}")

    if error:
        flash(f"Error al conectar con la API: {error}", "danger")
        cart_data = {"items": []}
    elif response.status_code == 200:
        cart_data = response.json()
    else:
        cart_data = {"items": []}

    return render_template("cart.html", cart=cart_data)


@app.route("/add-to-cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    """Agregar producto al carrito"""
    if not is_logged_in():
        flash("Debes iniciar sesión para agregar al carrito", "warning")
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    quantity = int(request.form.get("quantity", 1))

    # Enviar request a la API
    data = {"user_id": user_id, "product_id": product_id, "quantity": quantity}
    response, error = api_request("/api/v1/carts/items", method="POST", data=data)

    if error:
        flash(f"Error de conexión: {error}", "danger")
    elif response.status_code in [200, 201]:
        flash("Producto agregado al carrito", "success")
    else:
        detail = response.json().get("detail", "Error al agregar al carrito")
        flash(detail, "danger")

    return redirect(url_for("products"))


@app.route("/update-cart-item/<int:item_id>", methods=["POST"])
def update_cart_item(item_id):
    """Actualizar cantidad de un item en el carrito"""
    if not is_logged_in():
        flash("Debes iniciar sesión", "warning")
        return redirect(url_for("login"))

    quantity = int(request.form.get("quantity", 1))

    data = {"quantity": quantity}
    response, error = api_request(
        f"/api/v1/carts/items/{item_id}", method="PUT", data=data
    )

    if error:
        flash(f"Error de conexión: {error}", "danger")
    elif response.status_code == 200:
        flash("Carrito actualizado", "success")
    else:
        flash(response.json().get("detail", "Error al actualizar"), "danger")

    return redirect(url_for("cart"))


@app.route("/remove-cart-item/<int:item_id>", methods=["POST"])
def remove_cart_item(item_id):
    """Remover item del carrito"""
    if not is_logged_in():
        flash("Debes iniciar sesión", "warning")
        return redirect(url_for("login"))

    response, error = api_request(f"/api/v1/carts/items/{item_id}", method="DELETE")

    if error:
        flash(f"Error de conexión: {error}", "danger")
    elif response.status_code == 204:
        flash("Item eliminado del carrito", "success")
    else:
        flash(response.json().get("detail", "Error al eliminar"), "danger")

    return redirect(url_for("cart"))


@app.route("/clear-cart", methods=["POST"])
def clear_cart():
    """Limpiar el carrito"""
    if not is_logged_in():
        flash("Debes iniciar sesión", "warning")
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    response, error = api_request(f"/api/v1/carts/?user_id={user_id}", method="DELETE")

    if error:
        flash(f"Error de conexión: {error}", "danger")
    else:
        flash("Carrito vaciado", "success")

    return redirect(url_for("cart"))


@app.route("/logout")
def logout():
    """Logout del usuario"""
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
