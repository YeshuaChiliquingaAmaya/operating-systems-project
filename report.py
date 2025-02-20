import os
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import platform
import psutil
import GPUtil
from datetime import datetime
from database import obtener_historial
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, ListFlowable, ListItem
from reportlab.lib import colors
import re

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

def limpiar_texto(texto):
    """Limpia el texto de caracteres problemáticos y reestructura listas."""
    # Elimina etiquetas HTML mal formateadas y caracteres especiales
    texto = re.sub(r"</?b>", "", texto)  
    texto = re.sub(r"\*\*", "", texto)  
    texto = texto.replace("\n", " ")

    # Reemplaza guiones o asteriscos con formato de lista para ReportLab
    texto = re.sub(r"\s*-\s*", "\n• ", texto)  

    return texto.strip()

def generar_pdf(horas=1, explicacion_ia=""):
    """Genera un informe detallado con análisis de IA con formato mejorado."""

    registros = obtener_historial(horas)
    if not registros:
        return "No hay datos suficientes para generar el reporte."

    reports_dir = os.path.join(os.getcwd(), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    nombre_pdf = os.path.join(reports_dir, f"reporte_completo_{timestamp}.pdf")

    pdf = SimpleDocTemplate(nombre_pdf, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # **Estilos personalizados**
    title_style = styles['Title']
    title_style.textColor = colors.darkblue

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        spaceAfter=10,
        textColor=colors.black
    )

    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        spaceAfter=6,
        textColor=colors.black,
        alignment=TA_JUSTIFY
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        spaceAfter=4,
        textColor=colors.black,
        leftIndent=15
    )

    # **Título del Informe**
    story.append(Paragraph(f"Informe de Monitoreo del Sistema - Últimas {horas} horas", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Generado el: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", normal_style))
    story.append(Spacer(1, 12))

    # **Sección de Análisis Inteligente**
    story.append(Paragraph("<b>Análisis Inteligente del Sistema</b>", subtitle_style))
    story.append(Spacer(1, 12))

    # **Limpieza y formateo de la respuesta de Gemini**
    explicacion_ia = limpiar_texto(explicacion_ia)

    # **Dividir la explicación en secciones**
    secciones = explicacion_ia.split("\n• ")  
    for idx, seccion in enumerate(secciones):
        if idx == 0:  
            story.append(Paragraph(seccion, normal_style))
        else:  
            story.append(ListFlowable([ListItem(Paragraph(seccion, bullet_style))], bulletType='bullet'))

    story.append(Spacer(1, 12))

    # **Información del sistema**
    info_sistema = obtener_info_sistema()
    story.append(Paragraph("<b>Información del Sistema:</b>", subtitle_style))
    for clave, valor in info_sistema.items():
        if clave == "Red":
            story.append(Paragraph(f"<b>{clave}:</b>", normal_style))
            for interfaz, detalles in valor.items():
                story.append(Paragraph(f"{interfaz}: {detalles[0].address}", normal_style))
        else:
            story.append(Paragraph(f"{clave}: {valor}", normal_style))
    story.append(Spacer(1, 12))

    # **Extraer métricas desde la base de datos**
    timestamps = [dato["timestamp"][:19] for dato in registros]
    cpu_uso = [dato["cpu"]["uso_promedio"] for dato in registros]
    memoria_uso = [dato["memoria"]["uso_promedio"] for dato in registros]
    disco_uso = [
        sum(part["used"] for part in dato["disco"]) / len(dato["disco"]) if dato["disco"] else 0
        for dato in registros
    ]
    red_envio = [dato["red"]["envio_total"] for dato in registros]
    red_recepcion = [dato["red"]["recepcion_total"] for dato in registros]

    # **Calcular estadísticas**
    stats = {
        "CPU": {"max": max(cpu_uso), "min": min(cpu_uso), "avg": sum(cpu_uso) / len(cpu_uso)},
        "Memoria": {"max": max(memoria_uso), "min": min(memoria_uso), "avg": sum(memoria_uso) / len(memoria_uso)},
        "Disco": {"max": max(disco_uso), "min": min(disco_uso), "avg": sum(disco_uso) / len(disco_uso)},
        "Red Enviada": {"total": sum(red_envio)},
        "Red Recibida": {"total": sum(red_recepcion)}
    }

    # **Agregar estadísticas al PDF**
    story.append(Paragraph("<b>Análisis de Consumo de Recursos:</b>", subtitle_style))
    for recurso, valores in stats.items():
        detalles = " | ".join([f"{k}: {v:.2f}" for k, v in valores.items()])
        story.append(Paragraph(f"{recurso}: {detalles}", normal_style))
        story.append(Spacer(1, 6))

    # **Crear gráfico de consumo de recursos**
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

    imagen_grafico = os.path.join(reports_dir, f"grafico_{timestamp}.png")
    plt.savefig(imagen_grafico)
    plt.close()

    # **Agregar imagen al PDF**
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Gráficos de Consumo de Recursos:</b>", subtitle_style))
    story.append(Spacer(1, 12))
    story.append(Image(imagen_grafico, width=400, height=200))

    # **Guardar PDF**
    pdf.build(story)

    return nombre_pdf