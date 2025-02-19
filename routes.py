from flask import Blueprint, jsonify, render_template
from monitor import obtener_monitoreo
from database import guardar_monitoreo, obtener_historial
from report import generar_pdf
from flask import send_file
import subprocess
from flask import Blueprint, request, jsonify
import requests
from config import API_KEY, VT_FILE_SCAN, VT_ANALYSIS_RESULT
from monitor import obtener_monitoreo

routes = Blueprint("routes", __name__)
headers = {"x-apikey": API_KEY}
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

# Lista de comandos peligrosos que queremos bloquear
COMANDOS_PROHIBIDOS = ["rm", "shutdown", "reboot", "poweroff", "halt", "kill", "pkill", "mkfs", "dd", "fdisk", "mkpart", "wipefs"]

@routes.route('/ejecutar_comando', methods=['POST'])
def ejecutar_comando():
    """Ejecuta un comando Bash y devuelve la salida, bloqueando comandos peligrosos."""
    data = request.json
    comando = data.get("comando", "").strip()

    if not comando:
        return jsonify({"error": "No se proporcionó ningún comando"}), 400

    # Bloquear comandos prohibidos
    for prohibido in COMANDOS_PROHIBIDOS:
        if comando.startswith(prohibido) or f" {prohibido} " in comando:
            return jsonify({"error": f"Comando '{prohibido}' no permitido por seguridad"}), 403

    try:
        # Ejecutar el comando en Bash y capturar la salida
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)

        return jsonify({
            "salida": resultado.stdout,
            "error": resultado.stderr
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@routes.route("/analizar_proceso", methods=["POST"])
def analizar_proceso():
    """Envía un archivo a VirusTotal y devuelve el ID del análisis."""
    data = request.json
    ruta_archivo = data.get("ruta", "")

    if not ruta_archivo:
        return jsonify({"error": "Ruta de archivo no proporcionada"}), 400

    try:
        with open(ruta_archivo, "rb") as file:
            files = {"file": file}
            response = requests.post(VT_FILE_SCAN, headers=headers, files=files)
            result = response.json()
            
            # Extraer ID del análisis
            analysis_id = result.get("data", {}).get("id", None)
            if not analysis_id:
                return jsonify({"error": "No se obtuvo un ID de análisis"}), 500
            
            return jsonify({"analysis_id": analysis_id})
    except FileNotFoundError:
        return jsonify({"error": "Archivo no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route("/resultado_analisis/<analysis_id>", methods=["GET"])
def resultado_analisis(analysis_id):
    """Obtiene los resultados de un análisis de VirusTotal."""
    url = f"{VT_ANALYSIS_RESULT}/{analysis_id}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return jsonify({"error": "No se pudo obtener el resultado"}), response.status_code

    return response.json()