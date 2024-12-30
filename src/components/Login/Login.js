import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { auth } from "./firebase"; // Correct the import path
import { GoogleAuthProvider, signInWithPopup, onAuthStateChanged } from "firebase/auth"; // Import necessary functions from Firebase
import styles from "./Login.module.css";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  const handleGoogleLogin = async () => {
    const provider = new GoogleAuthProvider();
    try {
      const result = await signInWithPopup(auth, provider);
      const user = result.user;
      setUser(user);
      navigate("/");
    } catch (error) {
      setError(error.message);
    }
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });
    return unsubscribe;
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!username || !password) {
      setError("Please fill in all fields");
    } else {
      setError("");
      alert("Login successful!");
      navigate("/");
    }
  };

  const handleRegister = () => {
    navigate("/register");
  };

  const handleLogout = async () => {
    await auth.signOut();
    setUser(null);
    navigate("/login");
  };

  return (
    <div style={{
      background: "linear-gradient(to left, rgb(0, 0, 0), rgb(0, 0, 0), rgb(0, 34, 75))",
      height: "100vh", // Full viewport height
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
    }}>
    <div className={styles.loginContainer}>
      <h1 style={{ textAlign: "center", marginBottom: "30px", marginLeft: "30px" }}>Log in with</h1>
      {!user ? (
        <>
          <div className={styles.socialLoginContainer}>
            <button onClick={handleGoogleLogin} className={styles.googleLoginBtn}>
              Google
            </button>
            <button className={styles.appleLoginBtn}>Apple</button>
          </div>
          <p style={{ textAlign: "center", margin: "20px 0", fontWeight: "bold", marginLeft: "25px" }}>or</p>
          <form onSubmit={handleSubmit} className={styles.loginForm}>
            <div className={styles.formGroup}>
              <label htmlFor="username"style={{marginLeft: "25px"}}>Email address</label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div className={styles.formGroup}>
              <label htmlFor="password" style={{marginLeft: "25px"}}>Password</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            {error && <p className={styles.error}>{error}</p>}
            <button type="submit" className={styles.submitBtn}>
              Log In
            </button>
          </form>
          <p
            style={{
              textAlign: "center",
              marginTop: "20px",
              marginLeft: "25px"
            }}
          >
            Don't have an account?{" "}
            <span
              style={{
                color: "#007bff",
                cursor: "pointer",
                textDecoration: "underline",
              }}
              onClick={handleRegister}
            >
              Sign up
            </span>
          </p>
        </>
      ) : (
        <div>
          <p>Welcome, {user.email}</p>
          <button onClick={handleLogout} className={styles.submitBtn}>
            Logout
          </button>
        </div>
      )}
    </div>
    </div>
  );
};

export default Login;
