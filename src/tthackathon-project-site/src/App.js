import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header/Header";
import HeroSection from "./components/HeroSection/HeroSection";
import TrendingNews from "./components/TrendingNews/TrendingNews";
import ExtraStuff from "./components/ExtraStuff/ExtraStuff"; // Import the new page
import Login from "./components/Login/Login";
import Register from "./components/Register/Register";
import { auth } from './components/Login/firebase'; // Correct the import path
import { onAuthStateChanged } from "firebase/auth";
import "./App.css";

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser); // Set the user state if signed in
    });

    return unsubscribe; // Clean up the listener when component unmounts
  }, []);

  return (
    <Router>
      <div className="App">
        <Header user={user} />
        <Routes>
          <Route
            path="/"
            element={
              <>
                <HeroSection />
                <TrendingNews />
                <ExtraStuff /> {/* Add ExtraStuff here */}
              </>
            }
          />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
