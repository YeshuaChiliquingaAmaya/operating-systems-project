import psutil
import time

# Cache de procesos para evitar sobrecarga
cache_procesos = []
cache_io = {}  # Para calcular diferencia de lectura/escritura
ultimo_tiempo_cache = 0
CACHE_TIEMPO = 5  # Segundos para refrescar

def obtener_procesos():
    """Obtiene la lista de procesos en ejecución ordenados por consumo, incluyendo la ruta del ejecutable."""
    global cache_procesos, cache_io, ultimo_tiempo_cache

    tiempo_actual = time.time()
    if tiempo_actual - ultimo_tiempo_cache < CACHE_TIEMPO:
        return cache_procesos  # Retorna la cache si es reciente

    procesos_lista = []
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cpu_percent', 'memory_percent', 'username', 'nice', 'io_counters']):
        try:
            io_counters = proc.info.get('io_counters', None)
            user = proc.info.get('username', 'Desconocido')
            priority = proc.info.get('nice', 0)
            ruta_exe = proc.info.get('exe', 'Desconocido')  # Obtener ruta del ejecutable

            # Obtener lectura/escritura total
            disk_read_total = io_counters.read_bytes if io_counters else 0
            disk_write_total = io_counters.write_bytes if io_counters else 0

            # Calcular lectura/escritura por intervalo
            pid = proc.info["pid"]
            prev_io = cache_io.get(pid, (0, 0))
            disk_read = max(0, disk_read_total - prev_io[0]) / 1024  # KB
            disk_write = max(0, disk_write_total - prev_io[1]) / 1024  # KB
            cache_io[pid] = (disk_read_total, disk_write_total)

            procesos_lista.append({
                "pid": pid,
                "nombre": proc.info["name"],
                "ruta": ruta_exe,  # Agregamos la ruta del ejecutable
                "usuario": user,
                "cpu": round(proc.info["cpu_percent"], 2),
                "memoria": round(proc.info["memory_percent"], 2),
                "disk_read_total": round(disk_read_total / (1024**2), 2),  # MB
                "disk_write_total": round(disk_write_total / (1024**2), 2),  # MB
                "disk_read": round(disk_read, 2),  # KB
                "disk_write": round(disk_write, 2),  # KB
                "prioridad": priority
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Ordenar procesos por CPU y Memoria (los más pesados primero)
    procesos_lista.sort(key=lambda x: (x["cpu"], x["memoria"]), reverse=True)

    # Guardar en cache solo los 20 más relevantes
    cache_procesos = procesos_lista[:20]
    ultimo_tiempo_cache = tiempo_actual
    return cache_procesos
def obtener_sistema_archivos():
    """Obtiene información detallada del sistema de archivos, excluyendo dispositivos loop."""
    particiones = psutil.disk_partitions(all=False)
    info_discos = []

    for part in particiones:
        # Excluir dispositivos tipo loop (ejemplo: /dev/loop1, /dev/loop2, etc.)
        if "loop" in part.device:
            continue

        try:
            uso = psutil.disk_usage(part.mountpoint)
            info_discos.append({
                "used": round(uso.percent, 1),  # Porcentaje de uso
                "device": part.device,  # Nombre del dispositivo (ej: /dev/sda1)
                "directory": part.mountpoint,  # Punto de montaje (ej: /)
                "type": part.fstype,  # Tipo de sistema de archivos (ej: ext4)
                "total": round(uso.total / (1024**3), 2),  # Tamaño total en GB
                "available": round(uso.free / (1024**3), 2)  # Espacio disponible en GB
            })
        except PermissionError:
            continue  # Saltar particiones sin permisos

    return info_discos

def obtener_monitoreo():
    """Obtiene los datos actuales del sistema junto con los procesos detallados."""
    return {
        "cpu": {"uso": psutil.cpu_percent(interval=None)},
        "memoria": {"usada": psutil.virtual_memory().percent},
        "disco": obtener_sistema_archivos(),
        "red": {
            "envio": round(psutil.net_io_counters().bytes_sent / (1024**2), 2),
            "recepcion": round(psutil.net_io_counters().bytes_recv / (1024**2), 2),
        },
        "procesos_lista": obtener_procesos()  # Llamamos la nueva versión con más detalles
    }