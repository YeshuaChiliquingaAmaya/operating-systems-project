import React, { useState, useEffect } from "react";
import axios from "axios";

const VirusTotalScanner = () => {
  const [procesos, setProcesos] = useState([]);
  const [analisis, setAnalisis] = useState(null);
  const [analizando, setAnalizando] = useState(false);
  const [procesoActual, setProcesoActual] = useState(null);

  useEffect(() => {
    const fetchProcesos = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/monitoreo");
        setProcesos(response.data.procesos_lista);
      } catch (error) {
        console.error("Error al obtener procesos:", error);
      }
    };

    fetchProcesos();
    const interval = setInterval(fetchProcesos, 5000);
    return () => clearInterval(interval);
  }, []);

  const analizarProceso = async (ruta) => {
    try {
      setAnalizando(true);
      setProcesoActual(ruta);
      setAnalisis(null);

      const response = await axios.post("http://127.0.0.1:5000/analizar_proceso", { ruta });
      const analysisId = response.data.analysis_id;

      if (!analysisId) {
        setAnalisis({ error: "No se pudo iniciar el análisis." });
        setAnalizando(false);
        return;
      }

      // Consultar el resultado después de unos segundos
      setTimeout(() => obtenerResultado(analysisId), 10000);
    } catch (error) {
      console.error("Error al analizar archivo:", error);
      setAnalisis({ error: "No se pudo analizar el archivo" });
      setAnalizando(false);
    }
  };

  const obtenerResultado = async (analysisId) => {
    try {
      const response = await axios.get(`http://127.0.0.1:5000/resultado_analisis/${analysisId}`);
      setAnalisis(response.data);
    } catch (error) {
      console.error("Error al obtener resultados:", error);
      setAnalisis({ error: "No se pudo obtener el resultado del análisis" });
    } finally {
      setAnalizando(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2>Escaneo de VirusTotal</h2>
      <table style={styles.table}>
        <thead>
          <tr>
            <th>PID</th>
            <th>Nombre</th>
            <th>Ruta</th>
            <th>CPU (%)</th>
            <th>Memoria (%)</th>
            <th>VirusTotal</th>
          </tr>
        </thead>
        <tbody>
          {procesos.map((proceso) => (
            <tr key={proceso.pid}>
              <td>{proceso.pid}</td>
              <td>{proceso.nombre}</td>
              <td>{proceso.ruta}</td>
              <td>{proceso.cpu}</td>
              <td>{proceso.memoria}</td>
              <td>
                {proceso.ruta !== "Desconocido" ? (
                  <button
                    style={styles.button}
                    onClick={() => analizarProceso(proceso.ruta)}
                    disabled={analizando}
                  >
                    {analizando && procesoActual === proceso.ruta ? "Analizando..." : "Analizar"}
                  </button>
                ) : (
                  "No disponible"
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {analisis && (
        <div style={styles.result}>
          <h3>Resultado del Análisis</h3>
          <pre>{JSON.stringify(analisis, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

// Estilos en línea
const styles = {
  container: {
    textAlign: "center",
    padding: "20px",
    color: "#E0E0E0",
    backgroundColor: "#1E1E2E",
    borderRadius: "10px",
    boxShadow: "0px 4px 8px rgba(0, 0, 0, 0.3)",
    maxWidth: "900px",
    margin: "auto",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    backgroundColor: "#2A2A3E",
    color: "#E0E0E0",
    borderRadius: "5px",
    overflow: "hidden",
  },
  button: {
    backgroundColor: "#4CAF50",
    color: "white",
    border: "none",
    padding: "8px 12px",
    cursor: "pointer",
    borderRadius: "5px",
    fontSize: "14px",
  },
  result: {
    marginTop: "20px",
    backgroundColor: "#333",
    padding: "15px",
    borderRadius: "8px",
    textAlign: "left",
    color: "#FFD700",
  },
};

export default VirusTotalScanner;
