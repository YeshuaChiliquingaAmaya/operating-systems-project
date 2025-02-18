// src/components/Navbar.jsx
import React, { useState } from "react";

const Navbar = () => {
  const [horas, setHoras] = useState(1);

  const handleHorasChange = (e) => {
    setHoras(e.target.value);
  };

  return (
    <nav style={styles.navbar}>
      <div style={styles.navContent}>
        <a href="/" style={styles.logo}>
          Monitoreo Sistema
        </a>
        <div style={styles.links}>
          <label style={styles.label}>
            Horas:
            <input
              type="number"
              value={horas}
              onChange={handleHorasChange}
              style={styles.input}
              min="1"
            />
          </label>
          <a
            href={`http://127.0.0.1:5000/historial/${horas}`}
            style={styles.navLink}
          >
            Historial
          </a>
          <a
            href={`http://127.0.0.1:5000/informe/${horas}`}
            style={styles.navLink}
          >
            Informe
          </a>
        </div>
      </div>
    </nav>
  );
};

const styles = {
  navbar: {
    backgroundColor: "#2E2E3E",
    padding: "10px 20px",
    color: "#E0E0E0",
  },
  navContent: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  logo: {
    color: "#E0E0E0",
    textDecoration: "none",
    fontSize: "20px",
    fontWeight: "bold",
  },
  links: {
    display: "flex",
    alignItems: "center",
  },
  label: {
    display: "flex",
    alignItems: "center",
    marginRight: "20px",
  },
  input: {
    marginLeft: "5px",
    width: "50px",
    padding: "5px",
    borderRadius: "4px",
    border: "1px solid #ccc",
  },
  navLink: {
    marginLeft: "20px",
    color: "#E0E0E0",
    textDecoration: "none",
    fontWeight: "bold",
  },
};

export default Navbar;
