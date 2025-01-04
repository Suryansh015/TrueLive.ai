import React from "react";
import { useNavigate } from "react-router-dom";
import { auth } from "../Login/firebase"; // Correct the import path
import styles from "./Header.module.css";

const Header = ({ user }) => {
  const navigate = useNavigate();

  const handleLoginClick = () => {
    navigate("/login");
  };

  const handleHomeClick = () => {
    navigate("/");
  };

  const handleLogout = async () => {
    await auth.signOut(); // Sign out
    navigate("/login");
  };

  // Function to truncate email
  const truncateEmail = (email) => {
    const [name, domain] = email.split("@");
    const truncatedName = name.length > 5 ? `${name.substring(0, 5)}...` : name;
    return `${truncatedName}@${domain}`;
  };

  const handleContactClick = () => {
    // Scroll to the Contact Us section in ExtraStuff component
    const contactSection = document.getElementById("contact-section");
    if (contactSection) {
      contactSection.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <header className={styles.header}>
      <div
        className={`${styles.logo} ${styles.clickable}`}
        onClick={handleHomeClick}
      >
        TrueLive.AI
      </div>
      <nav>
        <ul className={styles.navList}>
          <li onClick={handleHomeClick}>Home</li>
          <li>Pages</li>
          <li>Blog</li>
          <li onClick={handleContactClick} className={styles.contactLink}>Contact</li>
        </ul>
      </nav>
      {user ? (
        <div className={styles.userInfo}>
          <img
            src={user.photoURL} // User's profile picture URL
            alt="User Profile"
            className={styles.profilePic}
          />
          <button className={styles.logoutBtn} onClick={handleLogout}>
            Logout
          </button>
        </div>
      ) : (
        <button className={styles.loginBtn} onClick={handleLoginClick}>
          Register / Login
        </button>
      )}
    </header>
  );
};

export default Header;
