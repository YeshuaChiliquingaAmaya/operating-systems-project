import React from "react";
import Header from "./components/Header";
import Dashboard from "./components/Dashboard";
import Terminal from "./components/Terminal";
import Monitor from "./components/TablesDashboard";
import Navbar from "./components/NavBar";

function App() {
  return (
    
    <div>
      <Navbar />
      <Header />
      <Dashboard />
      <Terminal />
      <Monitor />

    </div>
  );
}

export default App;
