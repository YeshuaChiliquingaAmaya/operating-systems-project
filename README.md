# 🖥️ Monitoreo de Recursos del Sistema Operativo

Este proyecto es una aplicación web que permite monitorear en tiempo real el uso de **CPU, memoria, red, procesos y almacenamiento** del sistema operativo.

## 🚀 Características
✔ Monitoreo en tiempo real del **uso de CPU, memoria y red**  
✔ Visualización de **procesos activos ordenados por consumo**  
✔ **Gráficos interactivos** con actualización automática  
✔ **Interfaz gráfica atractiva** con barra de progreso para almacenamiento  

---

## 👥 Instalación y Configuración

Sigue estos pasos para clonar y ejecutar la aplicación en tu máquina.

### 1️⃣ **Clonar el Repositorio**
Abre la terminal y ejecuta:
```bash
git clone https://github.com/YeshuaChiliquingaAmaya/operating-systems-project.git
cd operating-systems-project
```

### 2️⃣ **Crear un Entorno Virtual**
Para evitar conflictos con otras dependencias, crea un entorno virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows usa: venv\Scripts\activate
```

### 3️⃣ **Instalar las Dependencias**
Instala las bibliotecas necesarias desde `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4️⃣ **Ejecutar la Aplicación**
```bash
python app.py
```
Luego, abre tu navegador en:  
🔗 **http://127.0.0.1:5000/**  

---

## 📆 Dependencias Usadas
- **Flask** → Para crear la aplicación web  
- **psutil** → Para obtener el uso del sistema  
- **Chart.js** → Para visualizar los gráficos en tiempo real  

---

## 🛠️ Mantenimiento
Si necesitas actualizar las dependencias en el futuro, ejecuta:
```bash
pip freeze > requirements.txt
```

---

## 🌟 Autor
📌 **Yeshua Chiliquinga Amaya**  
📧 _[Tu correo o contacto opcional]_  
🔗 _[Tu LinkedIn o sitio web opcional]_  

---

🚀 ¡Ahora puedes clonar el repositorio, instalar las dependencias y empezar a monitorear tu sistema!  
Si tienes dudas o encuentras errores, no dudes en abrir un **Issue** en este repositorio. 😃

