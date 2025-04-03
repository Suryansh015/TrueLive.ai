import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, useLocation } from "react-router-dom";
import Header from "./components/Header/Header";
import HeroSection from "./components/HeroSection/HeroSection";
import TrendingNews from "./components/TrendingNews/TrendingNews";
import ExtraStuff from "./components/ExtraStuff/ExtraStuff"; // Import the new page
import Login from "./components/Login/Login";
import Register from "./components/Register/Register";
import Dashboard from "./components/Dashboard/Dashboard";
import { auth } from "./components/Login/firebase"; // Correct the import path
import { onAuthStateChanged } from "firebase/auth";
import "./App.css";

const AppContent = () => {
  const [user, setUser] = useState(null);
  const location = useLocation(); // Get current route
  const showHeader = location.pathname !== "/dashboard"; // Hide Header on Dashboard

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser); // Set user state if signed in
    });

    return unsubscribe; // Clean up listener on unmount
  }, []);

  return (
    <div className="App">
      {showHeader && <Header user={user} />} {/* Show header on all pages except dashboard */}
      <Routes>
        <Route
          path="/"
          element={
            <>
              <HeroSection />
              <TrendingNews />
              <ExtraStuff />
            </>
          }
        />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/herosection" element={<HeroSection />} />
        <Route path="/trendingnews" element={<TrendingNews />} />
        <Route path="/extrastuff" element={<ExtraStuff />} />
        <Route path="/contactus" element={<ExtraStuff />} />
      </Routes>
    </div>
  );
};

const App = () => (
  <Router>
    <AppContent />
  </Router>
);

export default App;
