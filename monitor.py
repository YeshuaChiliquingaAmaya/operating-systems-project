import psutil
import time

# Cache de procesos para evitar sobrecarga
cache_procesos = []
ultimo_tiempo_cache = 0
CACHE_TIEMPO = 5  # Segundos para refrescar

def obtener_procesos():
    """Obtiene la lista de procesos en ejecución ordenados por consumo."""
    global cache_procesos, ultimo_tiempo_cache

    tiempo_actual = time.time()
    if tiempo_actual - ultimo_tiempo_cache < CACHE_TIEMPO:
        return cache_procesos  # Retorna la cache si es reciente

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

    # Ordenar procesos por CPU y Memoria (los más pesados primero)
    procesos_lista.sort(key=lambda x: (x["cpu"], x["memoria"]), reverse=True)

    # Guardar en cache solo los 20 más relevantes
    cache_procesos = procesos_lista[:20]
    ultimo_tiempo_cache = tiempo_actual
    return cache_procesos

def obtener_monitoreo():
    """Obtiene los datos actuales del sistema."""
    return {
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
