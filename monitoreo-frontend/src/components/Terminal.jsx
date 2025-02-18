// src/components/TerminalBash.jsx
import React, { useState, useRef } from "react";
import axios from "axios";

const TerminalBash = () => {
  const [command, setCommand] = useState("");
  const [output, setOutput] = useState([]);
  const terminalRef = useRef(null);

  const handleKeyDown = async (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      await executeCommand();
    }
  };

  const executeCommand = async () => {
    if (!command.trim()) return;

    // Definir el prompt (puedes personalizar el usuario y la ruta)
    const promptUser = "GRUPOJYA";
    const promptPath = "~/proyecto";

    // Agregar la línea del comando ejecutado
    setOutput((prev) => [
      ...prev,
      <div key={prev.length} style={{ textAlign: "left" }}>
        <span style={styles.promptUser}>{promptUser}</span>
        <span style={styles.promptPath}> {promptPath}</span>
        <span style={styles.promptSymbol}> $</span> {command}
      </div>,
    ]);

    // Guardamos el comando y luego limpiamos el input
    const currentCommand = command;
    setCommand("");

    try {
      const response = await axios.post("http://127.0.0.1:5000/ejecutar_comando", {
        comando: currentCommand.trim(),
      });

      if (response.data.error) {
        setOutput((prev) => [
          ...prev,
          <div key={prev.length} style={{ color: "red", textAlign: "left" }}>
            {response.data.error}
          </div>,
        ]);
      } else {
        // Separa la salida por líneas y agrega cada línea en el terminal
        const stdoutLines = response.data.salida.split("\n").map((line, idx) => (
          <div key={`stdout-${idx}`} style={{ textAlign: "left" }}>
            {line}
          </div>
        ));
        const stderrLines = response.data.error.split("\n").map((line, idx) => (
          <div key={`stderr-${idx}`} style={{ textAlign: "left", color: "red" }}>
            {line}
          </div>
        ));

        setOutput((prev) => [...prev, ...stdoutLines, ...stderrLines]);
      }
    } catch (error) {
      setOutput((prev) => [
        ...prev,
        <div key={prev.length} style={{ color: "red", textAlign: "left" }}>
          Error de conexión con el servidor
        </div>,
      ]);
    }

    // Auto-scroll al final del terminal
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  };

  return (
    <div style={styles.container}>
      <h3>Terminal Bash</h3>
      <div ref={terminalRef} style={styles.terminalContainer}>
        <div style={styles.terminalOutput}>{output}</div>
        <div style={styles.terminalPrompt}>
          <span style={styles.promptUser}>yeshua@linux</span>
          <span style={styles.promptPath}> ~/proyecto</span>
          <span style={styles.promptSymbol}> $</span>
          <input
            type="text"
            style={styles.commandInput}
            placeholder="Escribe un comando..."
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            onKeyDown={handleKeyDown}
            autoFocus
          />
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: "600px",
    margin: "20px auto",
    textAlign: "center",
  },
  terminalContainer: {
    width: "100%",
    background: "black",
    color: "white",
    padding: "10px",
    fontFamily: '"Fira Code", monospace',
    fontSize: "14px",
    borderRadius: "5px",
    boxShadow: "inset 0px 0px 10px rgba(0, 255, 0, 0.5)",
    height: "250px",
    overflowY: "auto",
    position: "relative",
    textAlign: "left",
  },
  terminalOutput: {
    whiteSpace: "pre-wrap",
    wordWrap: "break-word",
    color: "#33ff33",
    padding: "5px",
    maxHeight: "180px",
    overflowY: "auto",
    textAlign: "left",
  },
  terminalPrompt: {
    display: "flex",
    alignItems: "center",
    padding: "5px",
    textAlign: "left",
  },
  promptUser: {
    color: "#33ff33",
    fontWeight: "bold",
  },
  promptPath: {
    color: "#66ccff",
    marginLeft: "5px",
  },
  promptSymbol: {
    color: "#ffcc00",
    marginLeft: "5px",
  },
  commandInput: {
    background: "transparent",
    border: "none",
    color: "white",
    fontFamily: '"Fira Code", monospace',
    fontSize: "14px",
    width: "80%",
    outline: "none",
    marginLeft: "5px",
    textAlign: "left",
  },
};

export default TerminalBash;
