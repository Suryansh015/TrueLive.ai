import React from "react";
import { useNavigate } from "react-router-dom";
import styles from "./Dashboard.module.css";
import { auth } from "../Login/firebase"; // Import Firebase auth
import { useAuthState } from "react-firebase-hooks/auth"; // Firebase auth hook
import Avatar from "./avatar-icon.png"; // Default avatar image
import ytfeature1 from "../ExtraStuff/yt-feature-1.png"
import articlefeature2 from "../ExtraStuff/article-feature-2.jpg"
import summarizerfeature3 from "../ExtraStuff/summarizer-feature-3.png"

const Dashboard = () => {
  const [user] = useAuthState(auth); // Get logged-in user
  const navigate = useNavigate();
  
  const handleHomeClick = () => {
    navigate("/");
  };
  
  return (
    <div className={styles.dashboard}>
      {/* Sidebar */}
      <aside className={styles.sidebar}>
        <div onClick={handleHomeClick} className={styles.logo}>TrueLive.AI</div>
        <nav className={styles.nav}>
          <ul>
            <li className={styles.active}>Dashboard</li>
            <li><a href="/">Homepage</a></li>
            <li><a href="/trendingnews">Latest News</a></li>
            <li><a href="/extrastuff">Features</a></li>
          </ul>

          <div className={styles.sectionTitle}>ACCOUNT PAGES</div>
          <ul>
            <li>Signed In ✅</li>
            <li><button className={styles.signOutButton}>Sign Out</button></li>
          </ul>
        </nav>
      </aside>

      {/* Main Content */}
      <main className={styles.mainContent}>
        {/* Top Bar */}
        <div className={styles.topBar}>
          <h1>Dashboard</h1>
          <div className={styles.userInfo}>
            <img src={user?.photoURL || Avatar} alt="Avatar" className={styles.avatar} />
            <div className={styles.userName}>{user?.displayName || "Guest"}</div>
          </div>
        </div>

        {/* Dashboard Cards */}
        <div className={styles.grid}>
          <div className={styles.card}>
            <img src={ytfeature1} alt="News Analysis" className={styles.cardImage} />
            <div className={styles.cardContent}>
              <h2 style={{fontSize:"2rem"}} >Video Analysis</h2>
              <p>Verify your video content with our AI-powered</p><p>fact-checking system from Youtube Link or Video Upload.</p>
              <p>‎ </p>
              <p className={styles.rightArrow}>→</p>
            </div>
          </div>

          <div className={styles.card}>
            <img src={articlefeature2} alt="Article Analysis" className={styles.cardImage} />
            <div className={styles.cardContent}>
              <h2 style={{fontSize:"2rem"}}>Article Analysis</h2>
              <p>Analyze and validate articles with our</p><p>AI-driven analysis tool from Article Link.</p>
              <p>‎ </p>
              <p className={styles.rightArrow}>→</p>
            </div>
          </div>

          <div className={`${styles.card} ${styles.fullWidth}`}>
            <img src={summarizerfeature3} alt="Welcome Back" className={styles.cardImage} />
            <div className={styles.cardContent}>
              <h2 style={{fontSize:"2rem"}}>News Summarizer</h2>
              <p>Get concise summaries of the latest</p><p>news through our AI summarizer.</p>
              <p>‎ </p>
              <p className={styles.rightArrow}>→</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className={styles.footer}>
          <p>© 2024, Made with Passion ✊ by Digi Dynamos</p>
        </footer>
      </main>
    </div>
  );
};

export default Dashboard;
