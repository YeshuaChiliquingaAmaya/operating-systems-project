from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, COLLECTION_NAME
from datetime import datetime, timedelta
from bson.objectid import ObjectId

# Conectar a MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
coleccion = db[COLLECTION_NAME]

def guardar_monitoreo(datos):
    """Guarda datos agregados en MongoDB cada 5 minutos."""
    timestamp_actual = datetime.utcnow()
    timestamp_bloque = timestamp_actual.replace(second=0, microsecond=0, minute=(timestamp_actual.minute // 5) * 5)

    # Buscar si ya hay un bloque de 5 minutos en la base de datos
    documento_existente = coleccion.find_one({"timestamp": timestamp_bloque})

    if documento_existente:
        # Actualizar valores agregados
        coleccion.update_one(
            {"_id": documento_existente["_id"]},
            {"$set": {
                "cpu.uso_promedio": (documento_existente["cpu"]["uso_promedio"] + datos["cpu"]["uso"]) / 2,
                "cpu.uso_max": max(documento_existente["cpu"]["uso_max"], datos["cpu"]["uso"]),
                "cpu.uso_min": min(documento_existente["cpu"]["uso_min"], datos["cpu"]["uso"]),
                "memoria.uso_promedio": (documento_existente["memoria"]["uso_promedio"] + datos["memoria"]["usada"]) / 2,
                "red.envio_total": documento_existente["red"]["envio_total"] + datos["red"]["envio"],
                "red.recepcion_total": documento_existente["red"]["recepcion_total"] + datos["red"]["recepcion"],
                "procesos": datos["procesos_lista"]  # Actualizar lista de procesos
            }}
        )
    else:
        # Crear un nuevo documento si no existe
        coleccion.insert_one({
            "timestamp": timestamp_bloque,
            "cpu": {
                "uso_promedio": datos["cpu"]["uso"],
                "uso_max": datos["cpu"]["uso"],
                "uso_min": datos["cpu"]["uso"]
            },
            "memoria": {
                "uso_promedio": datos["memoria"]["usada"]
            },
            "disco": datos["disco"],
            "red": {
                "envio_total": datos["red"]["envio"],
                "recepcion_total": datos["red"]["recepcion"]
            },
            "procesos": datos["procesos_lista"]
        })

def obtener_historial(horas=1):
    """Obtiene los últimos registros de monitoreo en las últimas N horas."""
    tiempo_limite = datetime.utcnow() - timedelta(hours=horas)
    registros = list(coleccion.find({"timestamp": {"$gte": tiempo_limite}}).sort("timestamp", -1))
    
    for registro in registros:
        registro["_id"] = str(registro["_id"])  # Convertir ObjectId a string
        registro["timestamp"] = registro["timestamp"].isoformat()
    
    return registros
