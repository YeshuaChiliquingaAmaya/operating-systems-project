import React, { useEffect, useState } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";
import "chart.js/auto";

const SystemMonitor = () => {
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
    <div style={{ textAlign: "center" }}>
      <h2>Monitoreo del Sistema</h2>
      <div style={{ width: "600px", margin: "auto" }}>
        <Line
          data={{
            labels: data.timestamps,
            datasets: [
              { label: "Uso CPU (%)", data: data.cpu, borderColor: "red" },
              { label: "Memoria Usada (%)", data: data.memoria, borderColor: "blue" },
              { label: "Red Envío (MB)", data: data.redEnvio, borderColor: "green" },
              { label: "Red Recepción (MB)", data: data.redRecepcion, borderColor: "purple" },
            ],
          }}
          options={{ responsive: true }}
        />
      </div>
    </div>
  );
};

export default SystemMonitor;
