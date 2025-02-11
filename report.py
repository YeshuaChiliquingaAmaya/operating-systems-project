import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import platform
import psutil
import GPUtil
from datetime import datetime
from database import obtener_historial

def obtener_info_sistema():
    """Obtiene información detallada del sistema."""
    info = {
        "Sistema Operativo": platform.system(),
        "Versión OS": platform.version(),
        "Arquitectura": platform.architecture()[0],
        "Procesador": platform.processor(),
        "Núcleos Físicos": psutil.cpu_count(logical=False),
        "Núcleos Lógicos": psutil.cpu_count(logical=True),
        "RAM Total (GB)": round(psutil.virtual_memory().total / (1024**3), 2),
        "Almacenamiento Total (GB)": round(psutil.disk_usage('/').total / (1024**3), 2),
        "Red": psutil.net_if_addrs()
    }

    # Obtener información de GPU si está disponible
    gpus = GPUtil.getGPUs()
    if gpus:
        info["Tarjeta Gráfica"] = gpus[0].name
        info["Memoria VRAM (GB)"] = round(gpus[0].memoryTotal / 1024, 2)
    else:
        info["Tarjeta Gráfica"] = "No detectada"

    return info

def generar_pdf(horas=1):
    """Genera un informe detallado basado en datos extraídos de MongoDB."""
    
    registros = obtener_historial(horas)
    if not registros:
        return "No hay datos suficientes para generar el reporte."

    # Nombre del archivo PDF
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    nombre_pdf = f"reporte_completo_{timestamp}.pdf"
    
    # Crear el documento PDF
    pdf = SimpleDocTemplate(nombre_pdf, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Título
    story.append(Paragraph(f"Informe de Monitoreo del Sistema - Últimas {horas} horas", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Generado el: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", styles['Normal']))
    story.append(Spacer(1, 12))

    # Información del sistema
    info_sistema = obtener_info_sistema()
    story.append(Paragraph("<b>Información del Sistema:</b>", styles['Heading2']))
    for clave, valor in info_sistema.items():
        if clave == "Red":
            story.append(Paragraph(f"<b>{clave}:</b>", styles['Normal']))
            for interfaz, detalles in valor.items():
                story.append(Paragraph(f"{interfaz}: {detalles[0].address}", styles['Normal']))
        else:
            story.append(Paragraph(f"{clave}: {valor}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Extraer métricas desde la base de datos
    timestamps = [dato["timestamp"][:19] for dato in registros]
    cpu_uso = [dato["cpu"]["uso_promedio"] for dato in registros]
    memoria_uso = [dato["memoria"]["uso_promedio"] for dato in registros]
    disco_uso = [dato["disco"]["porcentaje"] for dato in registros]
    red_envio = [dato["red"]["envio_total"] for dato in registros]
    red_recepcion = [dato["red"]["recepcion_total"] for dato in registros]

    # Calcular estadísticas
    stats = {
        "CPU": {"max": max(cpu_uso), "min": min(cpu_uso), "avg": sum(cpu_uso) / len(cpu_uso)},
        "Memoria": {"max": max(memoria_uso), "min": min(memoria_uso), "avg": sum(memoria_uso) / len(memoria_uso)},
        "Disco": {"max": max(disco_uso), "min": min(disco_uso), "avg": sum(disco_uso) / len(disco_uso)},
        "Red Enviada": {"total": sum(red_envio)},
        "Red Recibida": {"total": sum(red_recepcion)}
    }

    # Agregar estadísticas al PDF
    story.append(Paragraph("<b>Análisis de Consumo de Recursos:</b>", styles['Heading2']))
    for recurso, valores in stats.items():
        detalles = " | ".join([f"{k}: {v:.2f}" for k, v in valores.items()])
        story.append(Paragraph(f"{recurso}: {detalles}", styles['Normal']))
        story.append(Spacer(1, 6))

    # Obtener los procesos más demandantes
    procesos_top_cpu = sorted(
        [proc for dato in registros for proc in dato["procesos"]],
        key=lambda x: x["cpu"], reverse=True
    )[:5]

    procesos_top_memoria = sorted(
        [proc for dato in registros for proc in dato["procesos"]],
        key=lambda x: x["memoria"], reverse=True
    )[:5]

    # Agregar información sobre los procesos
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Procesos con Mayor Consumo de CPU:</b>", styles['Heading2']))
    for proc in procesos_top_cpu:
        story.append(Paragraph(f"{proc['nombre']} - CPU: {proc['cpu']}% - PID: {proc['pid']}", styles['Normal']))

    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Procesos con Mayor Consumo de Memoria:</b>", styles['Heading2']))
    for proc in procesos_top_memoria:
        story.append(Paragraph(f"{proc['nombre']} - Memoria: {proc['memoria']}% - PID: {proc['pid']}", styles['Normal']))

    # Crear gráfico de consumo de recursos
    plt.figure(figsize=(6, 3))
    plt.plot(timestamps, cpu_uso, label="CPU (%)", color="red", marker="o")
    plt.plot(timestamps, memoria_uso, label="Memoria (%)", color="blue", marker="o")
    plt.plot(timestamps, disco_uso, label="Disco (%)", color="green", marker="o")
    plt.xticks(rotation=45, fontsize=8)
    plt.legend()
    plt.grid()
    plt.title("Monitoreo de CPU, Memoria y Disco")
    plt.xlabel("Tiempo")
    plt.ylabel("Uso (%)")
    plt.tight_layout()

    imagen_grafico = f"grafico_{timestamp}.png"
    plt.savefig(imagen_grafico)
    plt.close()

    # Agregar imagen al PDF
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Gráficos de Consumo de Recursos:</b>", styles['Heading2']))
    story.append(Spacer(1, 12))
    story.append(Image(imagen_grafico, width=400, height=200))

    # Guardar PDF
    pdf.build(story)

    return nombre_pdf
