import os
import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify, send_from_directory
from pdf_generator import generate_pdf 

app = Flask(__name__)
app.secret_key = "Contraseña123$"

# personalizacion del formato de fechas
def format_time(timestamp):
    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%H:%M")
    except Exception:
        return timestamp

def format_date_divider(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        today = datetime.today()
        if dt.date() == today.date():
            return "Hoy"
        elif dt.date() == (today - timedelta(days=1)).date():
            return "Ayer"
        elif (today - dt).days < 7:
            weekday_map = {
                "Monday": "Lunes",
                "Tuesday": "Martes",
                "Wednesday": "Miércoles",
                "Thursday": "Jueves",
                "Friday": "Viernes",
                "Saturday": "Sábado",
                "Sunday": "Domingo"
            }
            return weekday_map.get(dt.strftime("%A"), dt.strftime("%A"))
        else:
            return dt.strftime("%d/%m/%Y")
    except Exception:
        return date_str

app.jinja_env.filters["format_time"] = format_time
app.jinja_env.filters["format_date_divider"] = format_date_divider

# Base de datos de los usarios
def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def authenticate_user(email, password):
    hashed = hash_password(password)
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed)).fetchone()
    conn.close()
    return user

def store_message(user_id, sender, message):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO conversations (user_id, sender, message)
        VALUES (?, ?, ?)
    """, (user_id, sender, message))
    conn.commit()
    conn.close()

def get_conversation_history(user_id):
    conn = get_db_connection()
    messages = conn.execute("""
        SELECT * FROM conversations
        WHERE user_id = ?
        ORDER BY timestamp ASC
    """, (user_id,)).fetchall()
    conn.close()
    return messages

#base de datos de los documentos
def get_db_documents_connection():
    conn = sqlite3.connect(os.path.join(app.root_path, "documents.db"))
    conn.row_factory = sqlite3.Row
    return conn

#rutas del programa
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = authenticate_user(email, password)
        if user:
            if user["email"].lower() == "admin@test.com":
                session["is_admin"] = True
                session["username"] = user["username"]
                return redirect(url_for("admin_dashboard"))
            else:
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                return redirect(url_for("dashboard"))
        else:
            flash("Credenciales incorrectas. Inténtalo de nuevo.")
    return render_template("login.html")

@app.route("/admin")
def admin_dashboard():
    if not session.get("is_admin"):
        flash("Acceso no autorizado.")
        return redirect(url_for("login"))
    return render_template("admin.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmPassword")
        if password != confirm_password:
            flash("Las contraseñas no coinciden.")
            return render_template("register.html")
        hashed_password = hash_password(password)
        conn = get_db_connection()
        try:
            conn.execute("""
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?)
            """, (username, email, hashed_password))
            conn.commit()
            flash("Usuario registrado exitosamente. Ahora inicia sesión.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Error: El correo ya se encuentra registrado.")
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" in session:
        history = get_conversation_history(session["user_id"])
        return render_template("dashboard.html", history=history)
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/store_message", methods=["POST"])
def store_message_route():
    if "user_id" not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401
    data = request.get_json()
    sender = data.get("sender")
    message = data.get("message")
    if sender and message:
        store_message(session["user_id"], sender, message)
        return jsonify({"success": True}), 200
    return jsonify({"error": "Datos incompletos"}), 400

@app.route("/delete_message", methods=["POST"])
def delete_message():
    if "user_id" not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401
    data = request.get_json()
    msg_id = data.get("msg_id")
    if msg_id:
        conn = get_db_connection()
        conn.execute("DELETE FROM conversations WHERE id = ? AND user_id = ?", (msg_id, session["user_id"]))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    return jsonify({"error": "Mensaje no especificado"}), 400

# generador de pdfs
@app.route("/generate_pdf", methods=["POST"])
def generate_pdf_endpoint():
    if "user_id" not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    data_req = request.get_json()
    document_type = data_req.get("document_type")
    cedula = data_req.get("cedula")
    
    if not all([document_type, cedula]):
        return jsonify({"error": "Faltan datos requeridos"}), 400

    doc_type_query = document_type.capitalize()

    db_path = os.path.join(app.root_path, "documents.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM documents WHERE document_type = ? AND cedula = ? LIMIT 1",
        (doc_type_query, cedula)
    ).fetchone()
    conn.close()
    
    if row is None:
        return jsonify({"error": "Documento no encontrado"}), 404

    details = json.loads(row["details"])

    output_dir = os.path.join(app.root_path, "actas")
    os.makedirs(output_dir, exist_ok=True)
    doc_id = str(int(datetime.now().timestamp()))
    filename = f"{document_type}_{doc_id}.pdf"
    file_path = os.path.join(output_dir, filename)

    generate_pdf(document_type, details, file_path)

    pdf_url = url_for("download_pdf", filename=filename, _external=True)
    return jsonify({"success": True, "url": pdf_url})

# apartado para ingresar documentos
@app.route("/submit_bautizo", methods=["POST"])
def submit_bautizo():
    details = {
        "bautizado": {
            "nombre": request.form.get("nombre"),
            "fecha_nacimiento": request.form.get("Fecha_de_nacimiento"),
            "lugar_nacimiento": request.form.get("Lugar_de_nacimiento"),
            "fecha_bautismo": request.form.get("fecha_de_bautizo"),
            "lugar_bautismo": request.form.get("Lugar_del_bautizo")
        },
        "informacion_familiar": {
            "padre": request.form.get("padre"),
            "madre": request.form.get("Madre"),
            "padrino": request.form.get("padrino"),
            "madrina": request.form.get("madrina"),
            "testigos": request.form.get("testigos")
        },
        "autoridad_religiosa": {
            "ministro": request.form.get("ministro")
        },
        "acta_eclesiastica": {
            "libro": request.form.get("tomo_n°"),
            "folio": request.form.get("folio_n°")
        },
        "acta_civil": {
            "acta": request.form.get("acta_n°"),
            "folio": request.form.get("folio_n°"),
            "tomo": request.form.get("tomo_n°"),
            "fecha": request.form.get("fecha"),
            "lugar": ""  # No se solicita en el formulario; se deja vacío
        }
    }
    document_type = "Bautismo"
    cedula = request.form.get("cédula_de_identidad")
    json_details = json.dumps(details)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = get_db_documents_connection()
    conn.execute("INSERT INTO documents (document_type, cedula, details, created_at) VALUES (?, ?, ?, ?)",
                 (document_type, cedula, json_details, created_at))
    conn.commit()
    conn.close()
    
    flash("Documento de Bautismo registrado exitosamente.")
    return redirect(url_for("index"))

@app.route("/submit_matrimonio", methods=["POST"])
def submit_matrimonio():
    data = {
        "novio": {
            "nombre": request.form.get("nombre_novio"),
            "cedula": request.form.get("cedula_novio"),
            "fecha_nacimiento": request.form.get("Fecha_de_nacimiento_novio"),
            "lugar_nacimiento": request.form.get("Lugar_de_nacimiento_novio"),
            "padre": request.form.get("padre_novio"),
            "madre": request.form.get("Madre_novio")
        },
        "novia": {
            "nombre": request.form.get("nombre_novia"),
            "cedula": request.form.get("cedula_novia"),
            "fecha_nacimiento": request.form.get("Fecha_de_nacimiento_novia"),
            "lugar_nacimiento": request.form.get("Lugar_de_nacimiento_novia"),
            "padre": request.form.get("padre_novia"),
            "madre": request.form.get("Madre_novia")
        },
        "sacramento": {
            "ministro": request.form.get("ministro"),
            "fecha_matrimonio": request.form.get("fecha_de_matrimonio"),
            "lugar_matrimonio": request.form.get("Lugar_del_matrimonio"),
            "testigos": request.form.get("testigos")
        },
        "registro_eclesiastico": {
            "acta": request.form.get("acta_n°"),
            "folio": request.form.get("folio_n°"),
            "libro": request.form.get("libro_n°")
        }
    }
    document_type = "Matrimonio"
    cedula = request.form.get("cedula_novio")
    details = json.dumps(data)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = get_db_documents_connection()
    conn.execute("INSERT INTO documents (document_type, cedula, details, created_at) VALUES (?, ?, ?, ?)",
                 (document_type, cedula, details, created_at))
    conn.commit()
    conn.close()
    
    flash("Documento de Matrimonio registrado exitosamente.")
    return redirect(url_for("index"))

@app.route("/submit_confirmacion", methods=["POST"])
def submit_confirmacion():
    data = {
        "persona": {
            "nombre": request.form.get("nombre"),
            "apellido": request.form.get("Apellido"),
            "cedula": request.form.get("cédula_de_identidad"),
            "fecha_nacimiento": request.form.get("Fecha_de_nacimiento"),
            "lugar_nacimiento": request.form.get("Lugar_de_nacimiento")
        },
        "familiar": {
            "padre": request.form.get("padre"),
            "madre": request.form.get("Madre"),
            "padrino": request.form.get("padrino")
        },
        "sacramento": {
            "ministro": request.form.get("ministro"),
            "fecha_confirmacion": request.form.get("fecha_de_confirmacion"),
            "lugar_confirmacion": request.form.get("Lugar_de_confirmacion")
        },
        "registro_eclesiastico": {
            "acta": request.form.get("acta_n°"),
            "folio": request.form.get("folio_n°"),
            "libro": request.form.get("libro_n°")
        }
    }
    document_type = "Confirmacion"
    cedula = request.form.get("cédula_de_identidad")
    details = json.dumps(data)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = get_db_documents_connection()
    conn.execute("INSERT INTO documents (document_type, cedula, details, created_at) VALUES (?, ?, ?, ?)",
                 (document_type, cedula, details, created_at))
    conn.commit()
    conn.close()
    
    flash("Documento de Confirmación registrado exitosamente.")
    return redirect(url_for("index"))

# rutas de los formulario
@app.route("/bautizo")
def bautizo():
    return render_template("bautizo.html")

@app.route("/confirmacion")
def confirmacion():
    return render_template("confirmacion.html")

@app.route("/matrimonio")
def matrimonio():
    return render_template("matrimonio.html")

@app.route("/actas/<filename>")
def download_pdf(filename):
    output_dir = os.path.join(app.root_path, "actas")
    return send_from_directory(output_dir, filename)

@app.route("/img/<path:filename>")
def serve_img(filename):
    return send_from_directory(os.path.join(app.root_path, "img"), filename)

if __name__ == "__main__":
    app.run(debug=True)
