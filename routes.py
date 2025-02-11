from flask import Blueprint, jsonify, render_template
from monitor import obtener_monitoreo
from database import guardar_monitoreo, obtener_historial
from report import generar_pdf
from flask import send_file

routes = Blueprint("routes", __name__)

@routes.route("/")
def home():
    return render_template("index.html")

@routes.route("/monitoreo")
def monitoreo():
    """Obtiene datos del sistema y los guarda en la base de datos."""
    datos = obtener_monitoreo()
    guardar_monitoreo(datos)
    return jsonify(datos)

@routes.route("/historial/<int:horas>")
def historial(horas):
    """Obtiene registros históricos de las últimas N horas."""
    return jsonify(obtener_historial(horas))

@routes.route("/informe/<int:horas>")
def descargar_informe(horas):
    """Genera y descarga un informe detallado en PDF basado en la base de datos."""
    nombre_pdf = generar_pdf(horas)
    return send_file(nombre_pdf, as_attachment=True)