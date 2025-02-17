import React from "react";

const Header = () => {
  return (
    <header style={styles.header}>
      <h1>Monitoreo del Sistema</h1>
    </header>
  );
};

const styles = {
  header: {
    backgroundColor: "#1E1E2E",
    color: "#FF6B6B",
    padding: "15px",
    textAlign: "center",
    fontSize: "1.8rem",
  },
};

export default Header;
