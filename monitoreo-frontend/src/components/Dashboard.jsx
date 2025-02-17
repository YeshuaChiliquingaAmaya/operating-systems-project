import React, { useEffect, useState } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";
import "chart.js/auto";

const Dashboard = () => {
  const [data, setData] = useState({
    cpu: [],
    memoria: [],
    redEnvio: [],
    redRecepcion: [],
    timestamps: [],
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/monitoreo");
        const { cpu, memoria, red } = response.data;
        const timestamp = new Date().toLocaleTimeString();

        setData((prev) => ({
          cpu: [...prev.cpu, cpu.uso].slice(-10),
          memoria: [...prev.memoria, memoria.usada].slice(-10),
          redEnvio: [...prev.redEnvio, red.envio].slice(-10),
          redRecepcion: [...prev.redRecepcion, red.recepcion].slice(-10),
          timestamps: [...prev.timestamps, timestamp].slice(-10),
        }));
      } catch (error) {
        console.error("Error al obtener datos:", error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={styles.container}>
      <h2>Estadísticas en Tiempo Real</h2>
      <div style={styles.grid}>
        <div style={styles.box}>
          <h3>Uso de CPU</h3>
          <Line data={getChartData(data.cpu, "Uso CPU (%)", "#FF6B6B")} options={chartOptions} />
        </div>
        <div style={styles.box}>
          <h3>Memoria</h3>
          <Line data={getChartData(data.memoria, "Memoria (%)", "#6BCB77")} options={chartOptions} />
        </div>
        <div style={styles.box}>
          <h3>Red (Networking)</h3>
          <Line
            data={{
              labels: data.timestamps,
              datasets: [
                { label: "Envío (MB)", data: data.redEnvio, borderColor: "#4D96FF", backgroundColor: "rgba(77, 150, 255, 0.2)" },
                { label: "Recepción (MB)", data: data.redRecepcion, borderColor: "#FFD93D", backgroundColor: "rgba(255, 217, 61, 0.2)" },
              ],
            }}
            options={chartOptions}
          />
        </div>
      </div>
    </div>
  );
};

const getChartData = (data, label, color) => ({
  labels: Array(data.length).fill(""),
  datasets: [{ label, data, borderColor: color, backgroundColor: `${color}33` }],
});

const chartOptions = {
  responsive: true,
  scales: { y: { beginAtZero: true } },
};

const styles = {
  container: {
    textAlign: "center",
    padding: "20px",
    color: "#E0E0E0",
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
};

export default Dashboard;
