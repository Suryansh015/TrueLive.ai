import React from "react";
import styles from "./HeroSection.module.css";
import { motion } from "framer-motion";
import { auth } from "../Login/firebase";
import { useNavigate } from "react-router-dom";
import { useAuthState } from "react-firebase-hooks/auth";

const HeroSection = () => {
  const [isSignedIn] = useAuthState(auth);
  const navigate = useNavigate();

  const handleGetStartedClick = () => {
    if (!isSignedIn) {
      navigate("/login");
    } else {
      navigate("/dashboard");
    }
  };

  return (
    <section style={{marginTop: "40px"}}>
      <div
        className={styles.heroContent}
        style={{
          background: "linear-gradient(to left, rgb(0, 0, 0), rgb(0, 0, 0), rgb(0, 34, 75))",
          backgroundPosition: "center",
          height: "500px",
          marginTop: "-40px",
          backgroundSize: "cover",
          position: "relative",
        }}
      >   
        <h9 style={{
          color:"#ffef3f",
          marginBottom: "40px"
        }}>The Future of Fact Checking is Here
        </h9>
        <div className={styles.typingWrapper}>
          <motion.h1 style={{ color: "white", fontSize: "3rem", marginTop: "-10px", textShadow: "2px 2px 8px rgba(0, 0, 0, 0.8)",}}>
            Transforming Misinformation
          </motion.h1>
          <h1 className={styles.typingAnimation} style={{ 
            background: "linear-gradient(to left,rgb(53, 230, 253),rgb(131, 237, 143),rgb(213, 247, 76))",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            fontSize: "3rem", 
            marginTop: "0px",  
          }}>
            Into Awareness
          </h1>
          <motion.button
            className={`${styles.getStartedBtn} text-white bg-gradient-to-r from-blue-500 via-blue-600 to-blue-700 hover:bg-gradient-to-br focus:ring-4 focus:outline-none focus:ring-blue-300 dark:focus:ring-blue-800 shadow-lg shadow-blue-500/50 dark:shadow-lg dark:shadow-blue-800/80 font-medium`}
            onClick={handleGetStartedClick}
            style={{
              color: "white",
              textShadow: "2px 2px 8px rgba(0, 0, 0, 0.8)",
            }}
          >
            Get Started
          </motion.button>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;