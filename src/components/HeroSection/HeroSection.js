import React, { useState, useEffect } from "react";
import styles from "./HeroSection.module.css";
import bgImage from "./BGimage.jpg";
import { color, motion } from "framer-motion";
import { auth } from "../Login/firebase";
import { useNavigate } from "react-router-dom";

const HeroSection = () => {
  const [isModalOpen, setModalOpen] = useState(false);
  const [isSignedIn, setIsSignedIn] = useState(false);
  const [youtubeURL, setYoutubeURL] = useState("");
  const [articleURL, setArticleURL] = useState("");
  const [newsURL, setNewsURL] = useState("");
  const [youtubeResults, setYoutubeResults] = useState(null);
  const [articleResults, setArticleResults] = useState(null);
  const [summaryData, setSummaryData] = useState(null);
  const [file, setFile] = useState(null);
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false); // Loading state

  const handlePastearticleClick = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setArticleURL(text); 
    } catch (error) {
      console.error("Failed to read clipboard contents:", error);
    }
  };

  const handlePastesummaryClick = async () => {
    try {
      const text = await navigator.clipboard.readText(); // Read from clipboard
      setNewsURL(text); // Set the pasted text into the input field
    } catch (error) {
      console.error("Failed to read clipboard contents:", error);
    }
  };

  const handlePasteytClick = async () => {
    try {
      const text = await navigator.clipboard.readText(); // Read from clipboard
      setYoutubeURL(text); // Set the pasted text into the input field
    } catch (error) {
      console.error("Failed to read clipboard contents:", error);
    }
  };

  const handleFileChange = (e) => {
    const uploadedFile = e.target.files[0]; // Get the first selected file
    if (uploadedFile) {
      setFile(uploadedFile);  // Save the file in state
    }
  };

  const textVariants = {
    hidden: { opacity: 0, y: -50 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
  };

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged((user) => {
      setIsSignedIn(!!user);
    });
    return () => unsubscribe();
  }, []);

  const handleGetStartedClick = () => {
    if (!isSignedIn) {
      navigate("/login"); // Redirect only if the user is not signed in
    } else {
      setModalOpen(true); 
    }
  };

  const closeModal = () => {
    setModalOpen(false);
  };

  const redirectToLogin = () => {
    window.location.href = "/login";
  };

  const handleYouTubeAnalysis = async (file) => {
    setIsLoading(true);
    console.log("Selected File:", file); 
    try {
      if (!file) {
        alert("Please upload a YouTube video file.");
        return;
      }
      
      const formData = new FormData();
      formData.append("video", file); // Append the video file to the form data
  
      const response = await fetch("http://127.0.0.1:5000/", {
        method: "POST",
        body: formData,
      });
  
      if (response.ok) {
        const data = await response.json();
        console.log("Response Data:", data); // Log response data
        
        // Check if the response contains transcription and claim_verification
        if (data.transcription && data.claim_verification) {
          // Open a new window and display the results
          const ytWindow = window.open("", "_blank", "width=800,height=600");
          ytWindow.document.write(`
            <html>
    <head>
      <title>Video Analysis Results</title>
      <style>
        body {
          font-family: 'Arial', sans-serif;
          background: linear-gradient(to left, rgb(0, 0, 0), rgb(0, 0, 0), rgb(0, 34, 75));
          color: #333;
          margin: 0;
          padding: 30px;
        }
        .container {
          width: 80%;
          margin: 0 auto;
          padding: 20px;
          background-color: #fff;
          border-radius: 8px;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        h4 {
          color: #2d87f0;
          font-size: 1.5rem;
          text-align: center;
          margin-bottom: 40px;
          margin-top: 20px;
        }
        .result-section {
          margin-bottom: 20px;
        }
        .result-section p {
          font-size: 1rem;
          line-height: 1.6;
          margin: 10px 0;
        }
        .result-section strong {
          color: #2d87f0;
        }
        .status {
          font-weight: bold;
          padding: 8px 12px;
          background-color:rgb(50, 176, 36);
          color: #fff;
          border-radius: 5px;
          display: inline-block;
        }
        .summary-box {
          padding: 10px;
          background-color: #fafafa;
          border: 1px solid #ddd;
          border-radius: 5px;
          font-style: italic;
        }
        .speedometer {
          position: relative;
          width: 150px;
          height: 150px;
          margin: 20px auto;
        }
        .speedometer svg {
          transform: rotate(-90deg);
        }
        .speedometer circle {
          fill: none;
          stroke-width: 10;
        }
        .speedometer .background {
          stroke: #ddd;
        }
        .speedometer .progress {
          stroke: #2d87f0;
          stroke-dasharray: 440; /* Circumference of the circle (2πr where r=70) */
          stroke-dashoffset: 440; /* Initial offset */
          transition: stroke-dashoffset 1.5s ease;
        }
        .speedometer .percentage {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          font-size: 1.2rem;
          font-weight: bold;
          color: #2d87f0;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h4>Video Analysis Results</h4>
        <div class="result-section">
          <p><strong>Claim Status:</strong> <span class="status"> ${data.claim_verification.status}</span></p>
        </div>
        <div class="result-section">
          <p><strong>Confidence:</strong> ${data.claim_verification.confidence}</p>
        </div>
        <div class="speedometer">
          <svg width="150" height="150">
            <circle class="background" cx="75" cy="75" r="70"></circle>
            <circle class="progress" cx="75" cy="75" r="70"></circle>
          </svg>
          <div class="percentage">0%</div>
        </div>
        <div class="result-section">
          <p><strong>Transcription:</strong></p>
          <div class="summary-box">${data.transcription}</div>
        </div>
      </div>
      <script>
        const claim_status = ${data.claim_verification.status};
        const confidence = ${data.claim_verification.confidence}; 
        
        const progressCircle = document.querySelector('.progress');
        const percentageText = document.querySelector('.percentage');
        const statusElement = document.querySelector('.status'); // Selecting the status element
        const radius = 70; // Radius of the circle
        const circumference = 2 * Math.PI * radius; // Circumference of the circle

        // Set up the initial values for the circle
        progressCircle.style.strokeDasharray = circumference;
        progressCircle.style.strokeDashoffset = circumference;

        if (claim_status == "Unverified") {
          statusElement.style.backgroundColor = "rgb(255, 69, 58)"; // Change background to red
        }

        // Animate the progress circle and percentage
        let currentPercentage = 0;
        const animationDuration = 1500; // Animation duration in milliseconds
        const intervalTime = 15; // Interval time for updating the percentage text
        const totalSteps = animationDuration / intervalTime; // Total steps in the animation
        const percentageStep = confidence / totalSteps; // Step size for percentage increment

        const animationInterval = setInterval(() => {
          if (currentPercentage < confidence) {
            currentPercentage += percentageStep;
            const progress = (1 - currentPercentage / 100) * circumference;
            progressCircle.style.strokeDashoffset = progress;
            percentageText.textContent = \\${Math.round(currentPercentage)}%\;
          } else {
            clearInterval(animationInterval);
            percentageText.textContent = \\${confidence}%\; // Ensure the percentage matches exactly
            progressCircle.style.strokeDashoffset = (1 - confidence / 100) * circumference;
          }
        }, intervalTime);
      </script>
    </body>
  </html>
          `);
        } else {
          alert("Failed to retrieve valid data from the backend.");
        }
      } else {
        alert("Error occurred while analyzing the video.");
      }
      setIsLoading(false); 
    } catch (error) {
      console.error("Error fetching YouTube analysis:", error);
      alert("An error occurred while processing the YouTube video.");
    }
  };
  
  
  const handleArticleVerification = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/verify_article", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: articleURL }),
      });
      const data = await response.json();
      setArticleResults(data);

      const articleWindow = window.open("", "_blank", "width=800,height=600");
articleWindow.document.write(`
  <html>
    <head>
      <title>Article Verification Results</title>
      <style>
        body {
          font-family: 'Arial', sans-serif;
          background: linear-gradient(to left, rgb(0, 0, 0), rgb(0, 0, 0), rgb(0, 34, 75));
          color: #333;
          margin: 0;
          padding: 30px;
        }
        .container {
          width: 80%;
          margin: 0 auto;
          padding: 20px;
          background-color: #fff;
          border-radius: 8px;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        h4 {
          color: #2d87f0;
          font-size: 1.5rem;
          text-align: center;
          margin-bottom: 40px;
          margin-top: 20px;
        }
        .result-section {
          margin-bottom: 20px;
        }
        .result-section p {
          font-size: 1rem;
          line-height: 1.6;
          margin: 10px 0;
        }
        .result-section strong {
          color: #2d87f0;
        }
        .status {
          font-weight: bold;
          padding: 8px 12px;
          background-color:rgb(63, 210, 46);
          color: #fff;
          border-radius: 5px;
          display: inline-block;
        }
        .summary-box {
          padding: 10px;
          background-color: #fafafa;
          border: 1px solid #ddd;
          border-radius: 5px;
          font-style: italic;
        }
        .speedometer {
          position: relative;
          width: 150px;
          height: 150px;
          margin: 20px auto;
        }
        .speedometer svg {
          transform: rotate(-90deg);
        }
        .speedometer circle {
          fill: none;
          stroke-width: 10;
        }
        .speedometer .background {
          stroke: #ddd;
        }
        .speedometer .progress {
          stroke: #2d87f0;
          stroke-dasharray: 440; /* Circumference of the circle (2πr where r=70) */
          stroke-dashoffset: 440; /* Initial offset */
          transition: stroke-dashoffset 1.5s ease;
        }
        .speedometer .percentage {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          font-size: 1.2rem;
          font-weight: bold;
          color: #2d87f0;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h4>Article Verification Results</h4>
        <div class="result-section">
          <p><strong>Status:</strong> <span class="status">${data.claim_verification.status}</span></p>
        </div>
        <div class="result-section">
          <p><strong>Confidence:</strong> ${data.claim_verification.confidence}%</p> 
        </div>
        <div class="speedometer">
          <svg width="150" height="150">
            <circle class="background" cx="75" cy="75" r="70"></circle>
            <circle class="progress" cx="75" cy="75" r="70"></circle>
          </svg>
          <div class="percentage">0%</div>
        </div>
        <div class="result-section">
          <p><strong>Summary:</strong></p>
          <div class="summary-box">${data.article.summary}</div>
        </div>
      </div>
      <script>
        const claim_status = ${data.claim_verification.status};
        const confidence = ${data.claim_verification.confidence}; 
        
        const progressCircle = document.querySelector('.progress');
        const percentageText = document.querySelector('.percentage');
        const statusElement = document.querySelector('.status'); // Selecting the status element
        const radius = 70; // Radius of the circle
        const circumference = 2 * Math.PI * radius; // Circumference of the circle

        // Set up the initial values for the circle
        progressCircle.style.strokeDasharray = circumference;
        progressCircle.style.strokeDashoffset = circumference;

        if (claim_status == "Unverified") {
          statusElement.style.backgroundColor = "rgb(255, 69, 58)"; // Change background to red
        }

        // Animate the progress circle and percentage
        let currentPercentage = 0;
        const animationDuration = 1500; // Animation duration in milliseconds
        const intervalTime = 15; // Interval time for updating the percentage text
        const totalSteps = animationDuration / intervalTime; // Total steps in the animation
        const percentageStep = confidence / totalSteps; // Step size for percentage increment

        const animationInterval = setInterval(() => {
          if (currentPercentage < confidence) {
            currentPercentage += percentageStep;
            const progress = (1 - currentPercentage / 100) * circumference;
            progressCircle.style.strokeDashoffset = progress;
            percentageText.textContent = \\${Math.round(currentPercentage)}%\;
          } else {
            clearInterval(animationInterval);
            percentageText.textContent = \\${confidence}%\; // Ensure the percentage matches exactly
            progressCircle.style.strokeDashoffset = (1 - confidence / 100) * circumference;
          }
        }, intervalTime);
      </script>
    </body>
  </html>
`);


    } catch (error) {
      console.error("Error verifying article:", error);
    }
  };

  const handleSummarizeClick = async () => {
    try {
      if (!newsURL) {
        alert("Please provide a news URL.");
        return;
      }
      
      const response = await fetch("http://127.0.0.1:5000/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: newsURL }),
      });
      const data = await response.json();

      if (response.ok) {
        setSummaryData(data);
        const summaryWindow = window.open("", "_blank", "width=800,height=600");
        summaryWindow.document.write(`
          <html>
            <head>
              <title>News Summary Results</title>
              <style>
                body {
                  font-family: 'Arial', sans-serif;
                  background: linear-gradient(to left, rgb(0, 0, 0), rgb(0, 0, 0), rgb(0, 34, 75));
                  color: #333;
                  margin: 0;
                  padding: 30px;
                }
                .container {
                  width: 80%;
                  margin: 0 auto;
                  padding: 20px;
                  background-color: #fff;
                  border-radius: 8px;
                  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }
                h4 {
                  color: #2d87f0;
                  font-size: 1.5rem;
                  text-align: center;
                  margin-bottom: 40px;
                  margin-top: 20px;
                }
                .result-section {
                  margin-bottom: 20px;
                }
                .result-section p {
                  font-size: 1rem;
                  line-height: 1.6;
                  margin: 10px 0;
                }
                .result-section strong {
                  color: #2d87f0;
                }
                .status {
                  font-weight: bold;
                  padding: 8px 12px;
                  background-color: #2d87f0;
                  color: #fff;
                  border-radius: 5px;
                  display: inline-block;
                }
                .summary-box {
                  padding: 10px;
                  background-color: #fafafa;
                  border: 1px solid #ddd;
                  border-radius: 5px;
                  font-style: italic;
                }
              </style>
            </head>
            <body>
              <div class="container">
                <h4>News Summary Results</h4>
                <div class="result-section">
                  <p ><strong>Title:</strong> ${data.title}</p>
                  <p><strong>Author:</strong> ${data.author}</p>
                </div>
                <div class="result-section">
                  <p><strong>Summary:</strong></p>
                  <div class="summary-box">${data.summary}</div>
                </div>
              </div>
            </body>
          </html>
        `);
      } else {
        alert(data.error || "Error occurred.");
      }

    } catch (error) {
      console.error("Error fetching summary:", error);
      alert("An error occurred while fetching the summary.");
    }
  };

  return (
    <section style={{marginTop: "40px"}}>
      <div
        className={${styles.heroContent} ${isModalOpen ? styles.blurred : ""}}
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
            className={${styles.getStartedBtn} text-white bg-gradient-to-r from-blue-500 via-blue-600 to-blue-700 hover:bg-gradient-to-br focus:ring-4 focus:outline-none focus:ring-blue-300 dark:focus:ring-blue-800 shadow-lg shadow-blue-500/50 dark:shadow-lg dark:shadow-blue-800/80 font-medium}
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
      {isModalOpen && (
        <div className={styles.modalOverlay} onClick={closeModal}>
          <div
            className={`${styles.modalContent} ${
              isSignedIn ? "" : styles.loginWindow
            }`}
            onClick={(e) => e.stopPropagation()}
          >
            {isSignedIn ? (
              <div className={styles.threeWindows}>

{/* Youtube URL Input Section */}

<div className={styles.window}>
  <div style={{ position: "relative" }}>
    <h4 style={{
      fontSize: "20px",
      marginTop: "20px", 
      backgroundColor: "#3e3e5b",
      padding: "10px 15px",
      marginRight: "80px",
      marginLeft: "80px",
      borderRadius: "5px"
    }}>
      Video Analysis</h4>
    <input
      type="text"
      value={youtubeURL}
      onChange={(e) => setYoutubeURL(e.target.value)}
      placeholder="Paste your Video url here"
    />
    <button className={styles.pasteButton} onClick={handlePasteytClick}>Paste</button>
  </div>
  <div className={styles.divider}>
    <span className={styles.orText}>or</span>
  </div>

  <div className={styles.uploadSection}>
    <div className={styles.fileUploadContainer}>
      <input 
        type="file"
        accept="video/mp4,video/mkv,video/webm,video/mov/mp3,audio/"
        onChange={handleFileChange} 
        className={styles.fileInput}
      />
    </div>
    <p>or Drop a Video or Audio here (mp3, mp4, mov).</p>
  </div>
  <button
    onClick={() => handleYouTubeAnalysis(file)}
    className={styles.analyzeButton}
    disabled={isLoading} 
  >
    {isLoading ? (
      <div className={styles.spinner}></div> // Show spinner during loading
    ) : (
      "Verify Video"
    )}
  </button>
</div>

{/* Article Input Section */}

<div className={styles.window}>
  <div style={{ position: "relative" }}>
    <h4 style={{
      fontSize: "20px",
      marginTop: "20px", 
      backgroundColor: "#3e3e5b",
      padding: "10px 15px",
      marginRight: "80px",
      marginLeft: "80px",
      borderRadius: "5px"
    }}>Article Analysis</h4>
    <input
      type="text"
      value={articleURL}
      onChange={(e) => setArticleURL(e.target.value)}
      placeholder="Paste your Article URL here"
    />
    <button className={styles.pasteButton}  onClick={handlePastearticleClick}>Paste</button>
  </div>

  <div className={styles.divider}>
    <span className={styles.orText}>or</span>
  </div>

  <div className={styles.uploadSection}>
    <div className={styles.fileUploadContainer}>
      <input 
        type="file"
        accept="video/mp4,video/mkv,video/webm,video/mov/mp3,audio/"
        className={styles.fileInput}
      />
    </div>
    <p>or Drop a Video or Audio here (mp3, mp4, mov).</p>
  </div>
  <button
    onClick= {handleArticleVerification}
    className={styles.analyzeButton}
  >
    Verify Article
  </button>
</div>

 {/* News Summarizer Input Section */}

              
<div className={styles.window}>
  <div style={{ position: "relative" }}>
    <h4 style={{
      fontSize: "20px",
      marginTop: "20px", 
      backgroundColor: "#3e3e5b",
      padding: "10px 15px",
      marginRight: "80px",
      marginLeft: "80px",
      borderRadius: "5px"
    }}>News Summarizer</h4>
    <input
      type="text"
      value={newsURL}
      onChange={(e) => setNewsURL(e.target.value)}
      placeholder="Paste your Article URL here"
    />
    <button className={styles.pasteButton}  onClick={handlePastesummaryClick}>Paste</button>
  </div>

  <div className={styles.divider}>
    <span className={styles.orText}>or</span>
  </div>

  <div className={styles.uploadSection}>
    <div className={styles.fileUploadContainer}>
      <input 
        type="file"
        accept="video/mp4,video/mkv,video/webm,video/mov/mp3,audio/"
        className={styles.fileInput}
      />
    </div>
    <p>or Drop a Video or Audio here (mp3, mp4, mov).</p>
  </div>
  <button
    onClick={handleSummarizeClick}
    className={styles.analyzeButton}
  >
    Summarize
  </button>
</div>

              </div>
            ) : null}  {/* If not signed in, no modal will be shown */}
          </div>
        </div>
      )}
    </section>
  );
};

export default HeroSection;
