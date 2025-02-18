// src/components/TablesDashboard.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";

const TablesDashboard = () => {
  const [procesos, setProcesos] = useState([]);
  const [discos, setDiscos] = useState([]);
  const [error, setError] = useState(null);

  // Estados para el ordenamiento de cada tabla
  const [procesosSortConfig, setProcesosSortConfig] = useState({
    key: null,
    direction: "desc",
  });
  const [discosSortConfig, setDiscosSortConfig] = useState({
    key: null,
    direction: "desc",
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/monitoreo");
        const data = response.data;
        setProcesos(data.procesos_lista);
        setDiscos(data.disco);
      } catch (err) {
        console.error("Error al obtener datos:", err);
        setError("Error al obtener datos");
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  // Función genérica para ordenar datos
  const sortData = (data, config) => {
    if (!config.key) return data;
    const sortedData = [...data].sort((a, b) => {
      let aValue = a[config.key];
      let bValue = b[config.key];
      // Si son números, compara numéricamente
      if (typeof aValue === "number" && typeof bValue === "number") {
        return config.direction === "asc" ? aValue - bValue : bValue - aValue;
      }
      // Si son cadenas, usa localeCompare
      return config.direction === "asc"
        ? String(aValue).localeCompare(String(bValue))
        : String(bValue).localeCompare(String(aValue));
    });
    return sortedData;
  };

  // Manejadores para actualizar el estado de ordenamiento
  const handleProcesosSort = (key) => {
    let direction = "desc";
    if (procesosSortConfig.key === key && procesosSortConfig.direction === "desc") {
      direction = "asc";
    }
    setProcesosSortConfig({ key, direction });
  };

  const handleDiscosSort = (key) => {
    let direction = "desc";
    if (discosSortConfig.key === key && discosSortConfig.direction === "desc") {
      direction = "asc";
    }
    setDiscosSortConfig({ key, direction });
  };

  // Aplica el ordenamiento a los datos
  const sortedProcesos = sortData(procesos, procesosSortConfig);
  const sortedDiscos = sortData(discos, discosSortConfig);

  // Función para mostrar un indicador de ordenamiento en el encabezado
  const getSortIndicator = (config, key) => {
    if (config.key === key) {
      return config.direction === "asc" ? " ▲" : " ▼";
    }
    return "";
  };

  return (
    <div style={styles.container}>
      {error && <div style={styles.error}>{error}</div>}
      <div style={styles.grid}>
        {/* Tabla de Procesos Activos */}
        <div style={styles.box}>
          <h3>Procesos Activos</h3>
          <div style={styles.tableWrapper}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th} onClick={() => handleProcesosSort("nombre")}>
                    Process Name{getSortIndicator(procesosSortConfig, "nombre")}
                  </th>
                  <th style={styles.th} onClick={() => handleProcesosSort("usuario")}>
                    User{getSortIndicator(procesosSortConfig, "usuario")}
                  </th>
                  <th style={styles.th} onClick={() => handleProcesosSort("cpu")}>
                    %CPU{getSortIndicator(procesosSortConfig, "cpu")}
                  </th>
                  <th style={styles.th} onClick={() => handleProcesosSort("pid")}>
                    PID{getSortIndicator(procesosSortConfig, "pid")}
                  </th>
                  <th style={styles.th} onClick={() => handleProcesosSort("memoria")}>
                    Memory (%) {getSortIndicator(procesosSortConfig, "memoria")}
                  </th>
                  <th style={styles.th} onClick={() => handleProcesosSort("disk_read_total")}>
                    Disk Read Total (MB){getSortIndicator(procesosSortConfig, "disk_read_total")}
                  </th>
                  <th style={styles.th} onClick={() => handleProcesosSort("disk_write_total")}>
                    Disk Write Total (MB){getSortIndicator(procesosSortConfig, "disk_write_total")}
                  </th>
                  <th style={styles.th} onClick={() => handleProcesosSort("disk_read")}>
                    Disk Read (KB){getSortIndicator(procesosSortConfig, "disk_read")}
                  </th>
                  <th style={styles.th} onClick={() => handleProcesosSort("disk_write")}>
                    Disk Write (KB){getSortIndicator(procesosSortConfig, "disk_write")}
                  </th>
                  <th style={styles.th} onClick={() => handleProcesosSort("prioridad")}>
                    Priority{getSortIndicator(procesosSortConfig, "prioridad")}
                  </th>
                </tr>
              </thead>
              <tbody>
                {sortedProcesos.map((proc, index) => (
                  <tr
                    key={index}
                    style={{
                      backgroundColor: index % 2 === 0 ? "#3E3E4E" : "#2E2E3E",
                    }}
                  >
                    <td style={styles.td}>{proc.nombre}</td>
                    <td style={styles.td}>{proc.usuario}</td>
                    <td style={{ ...styles.td, color: proc.cpu > 50 ? "red" : "inherit" }}>
                      {proc.cpu}%
                    </td>
                    <td style={styles.td}>{proc.pid}</td>
                    <td style={{ ...styles.td, color: proc.memoria > 20 ? "blue" : "inherit" }}>
                      {proc.memoria}%
                    </td>
                    <td style={styles.td}>{proc.disk_read_total} MB</td>
                    <td style={styles.td}>{proc.disk_write_total} MB</td>
                    <td style={styles.td}>{proc.disk_read} KB</td>
                    <td style={styles.td}>{proc.disk_write} KB</td>
                    <td style={styles.td}>{proc.prioridad}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Tabla de Sistema de Archivos */}
        <div style={styles.box}>
          <h3>Sistema de Archivos</h3>
          <div style={styles.tableWrapper}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th} onClick={() => handleDiscosSort("used")}>
                    Used (%) {getSortIndicator(discosSortConfig, "used")}
                  </th>
                  <th style={styles.th} onClick={() => handleDiscosSort("device")}>
                    Device {getSortIndicator(discosSortConfig, "device")}
                  </th>
                  <th style={styles.th} onClick={() => handleDiscosSort("directory")}>
                    Directory {getSortIndicator(discosSortConfig, "directory")}
                  </th>
                  <th style={styles.th} onClick={() => handleDiscosSort("type")}>
                    Type {getSortIndicator(discosSortConfig, "type")}
                  </th>
                  <th style={styles.th} onClick={() => handleDiscosSort("total")}>
                    Total (GB) {getSortIndicator(discosSortConfig, "total")}
                  </th>
                  <th style={styles.th} onClick={() => handleDiscosSort("available")}>
                    Available (GB) {getSortIndicator(discosSortConfig, "available")}
                  </th>
                </tr>
              </thead>
              <tbody>
                {sortedDiscos.map((disco, index) => (
                  <tr
                    key={index}
                    style={{
                      backgroundColor: index % 2 === 0 ? "#3E3E4E" : "#2E2E3E",
                    }}
                  >
                    <td style={styles.td}>{disco.used}%</td>
                    <td style={styles.td}>{disco.device}</td>
                    <td style={styles.td}>{disco.directory}</td>
                    <td style={styles.td}>{disco.type}</td>
                    <td style={styles.td}>{disco.total} GB</td>
                    <td style={styles.td}>{disco.available} GB</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    textAlign: "center",
    padding: "20px",
    color: "#E0E0E0",
    backgroundColor: "#1E1E2E",
    minHeight: "100vh",
  },
  error: {
    color: "red",
    marginBottom: "10px",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
    gap: "20px",
    maxWidth: "1200px",
    margin: "auto",
  },
  box: {
    backgroundColor: "#2E2E3E",
    padding: "20px",
    borderRadius: "15px",
    boxShadow: "0px 8px 16px rgba(0, 0, 0, 0.2)",
  },
  tableWrapper: {
    overflowX: "auto",
    marginTop: "10px",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    minWidth: "600px", // Asegura que se muestren todas las columnas
  },
  th: {
    backgroundColor: "#444",
    color: "#fff",
    padding: "10px",
    border: "1px solid #555",
    textAlign: "left",
    cursor: "pointer",
  },
  td: {
    padding: "10px",
    border: "1px solid #555",
    textAlign: "left",
  },
};

export default TablesDashboard;
