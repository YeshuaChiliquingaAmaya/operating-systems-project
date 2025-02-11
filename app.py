from flask import Flask, render_template, jsonify
import psutil
import time

app = Flask(__name__)

# Cache de procesos para reducir carga en el sistema
cache_procesos = []
ultimo_tiempo_cache = 0
CACHE_TIEMPO = 5  # Refrescar cada 5 segundos

def obtener_procesos():
    global cache_procesos, ultimo_tiempo_cache

    tiempo_actual = time.time()
    if tiempo_actual - ultimo_tiempo_cache < CACHE_TIEMPO:
        return cache_procesos  # Devolvemos la cache si está reciente

    procesos_lista = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            procesos_lista.append({
                "pid": proc.info["pid"],
                "nombre": proc.info["name"],
                "cpu": round(proc.info["cpu_percent"], 2),
                "memoria": round(proc.info["memory_percent"], 2)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Ordenar los procesos por uso de CPU y Memoria (los más pesados primero)
    procesos_lista.sort(key=lambda x: (x["cpu"], x["memoria"]), reverse=True)

    # Guardar en cache para evitar cálculos repetitivos
    cache_procesos = procesos_lista[:20]  # Devolver solo los 20 más relevantes
    ultimo_tiempo_cache = tiempo_actual
    return cache_procesos

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/monitoreo")
def monitoreo():
    datos = {
        "cpu": {"uso": psutil.cpu_percent(interval=None)},  
        "memoria": {"usada": psutil.virtual_memory().percent},
        "disco": {
            "total": round(psutil.disk_usage('/').total / (1024**3), 2),
            "usado": round(psutil.disk_usage('/').used / (1024**3), 2),
            "libre": round(psutil.disk_usage('/').free / (1024**3), 2),
            "porcentaje": psutil.disk_usage('/').percent
        },
        "red": {
            "envio": round(psutil.net_io_counters().bytes_sent / (1024**2), 2),
            "recepcion": round(psutil.net_io_counters().bytes_recv / (1024**2), 2),
        },
        "procesos_lista": obtener_procesos()
    }
    return jsonify(datos)

if __name__ == "__main__":
    app.run(debug=True)
