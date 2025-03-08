import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./Dashboard.module.css";
import modalStyles from "./Modal.module.css";
import { auth } from "../Login/firebase";
import { useAuthState } from "react-firebase-hooks/auth";
import Avatar from "./avatar-icon.png";
import ytfeature1 from "../ExtraStuff/yt-feature-1.png";
import articlefeature2 from "../ExtraStuff/article-feature-2.jpg";
import summarizerfeature3 from "../ExtraStuff/summarizer-feature-3.png";
import dashboardICO from "./dashboard-icon.png";
import homeICO from "./homepage-icon.png";
import newsICO from "./news-icon.png";
import featureICO from "./features-icon.png";
import contactICO from "./contact-icon.png"

const Dashboard = () => {
  const [user] = useAuthState(auth);
  const navigate = useNavigate();
  const [activeModal, setActiveModal] = useState(null);
  const [youtubeURL, setYoutubeURL] = useState("");
  const [articleURL, setArticleURL] = useState("");
  const [newsURL, setNewsURL] = useState("");
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleHomeClick = () => {
    navigate("/");
  };

  const handleSignOut = () => {
    auth.signOut();
    navigate("/");
  };

  const handlePasteClick = async (setter) => {
    try {
      const text = await navigator.clipboard.readText();
      setter(text);
    } catch (error) {
      console.error("Failed to read clipboard contents:", error);
    }
  };

  const handleFileChange = (e) => {
    const uploadedFile = e.target.files[0];
    if (uploadedFile) {
      setFile(uploadedFile);
    }
  };

  // YouTube Analysis Handler
  const handleYouTubeAnalysis = async (file) => {
    setIsLoading(true);
    try {
      if (!file) {
        alert("Please upload a YouTube video file.");
        return;
      }
      
      const formData = new FormData();
      formData.append("video", file);
  
      const response = await fetch("http://127.0.0.1:5000/", {
        method: "POST",
        body: formData,
      });
  
      if (response.ok) {
        const data = await response.json();
        if (data.transcription && data.claim_verification) {
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
                    stroke-dasharray: 440;
                    stroke-dashoffset: 440;
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
                    <p><strong>Claim Status:</strong> <span class="status">${data.claim_verification.status}</span></p>
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
                    <p><strong>Transcription:</strong></p>
                    <div class="summary-box">${data.transcription}</div>
                  </div>
                </div>
                <script>
                  const confidence = ${data.claim_verification.confidence};
                  const status = "${data.claim_verification.status}";
                  
                  const progressCircle = document.querySelector('.progress');
                  const percentageText = document.querySelector('.percentage');
                  const statusElement = document.querySelector('.status');
                  const radius = 70;
                  const circumference = 2 * Math.PI * radius;

                  progressCircle.style.strokeDasharray = circumference;
                  progressCircle.style.strokeDashoffset = circumference;

                  if (status.toLowerCase() === "unverified") {
                    statusElement.style.backgroundColor = "rgb(255, 69, 58)";
                  } else {
                    statusElement.style.backgroundColor = "rgb(50, 176, 36)";
                  }

                  let currentPercentage = 0;
                  const animationDuration = 1500;
                  const intervalTime = 15;
                  const totalSteps = animationDuration / intervalTime;
                  const percentageStep = confidence / totalSteps;

                  const animationInterval = setInterval(() => {
                    if (currentPercentage < confidence) {
                      currentPercentage += percentageStep;
                      const progress = (1 - currentPercentage / 100) * circumference;
                      progressCircle.style.strokeDashoffset = progress;
                      percentageText.textContent = \`\${Math.round(currentPercentage)}%\`;
                    } else {
                      clearInterval(animationInterval);
                      percentageText.textContent = \`\${confidence}%\`;
                      const finalProgress = (1 - confidence / 100) * circumference;
                      progressCircle.style.strokeDashoffset = finalProgress;
                    }
                  }, intervalTime);
                </script>
              </body>
            </html>
          `);
        }
      }
    } catch (error) {
      console.error("Error:", error);
      alert("An error occurred while processing the video.");
    } finally {
      setIsLoading(false);
    }
  };

  // Article Analysis Handler
  const handleArticleVerification = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/verify_article", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: articleURL }),
      });
      const data = await response.json();

      const articlesResponse = await fetch(
        `http://127.0.0.1:5000/guardian-news?query=${encodeURIComponent(data.transcription)}`
      );
      const articlesData = await articlesResponse.json();

      let articlesHTML = "<h4>Related News Articles</h4>";
      if (articlesData.response && articlesData.response.results.length > 0) {
        articlesHTML += articlesData.response.results
          .map(
            (article) =>
              `<div class="article">
                <h5>${article.webTitle}</h5>
                <p>${article.fields.trailText}</p>
                <a href="${article.webUrl}" target="_blank">Read more</a>
              </div>`
          )
          .join("");
      } else {
        articlesHTML += "<p>No relevant articles found.</p>";
      }

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
                stroke-dasharray: 440;
                stroke-dashoffset: 440;
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
              <div class="articles">${articlesHTML}</div>
            </div>
            <script>
              const confidence = ${data.claim_verification.confidence};
              const status = "${data.claim_verification.status}";
              
              const progressCircle = document.querySelector('.progress');
              const percentageText = document.querySelector('.percentage');
              const statusElement = document.querySelector('.status');
              const radius = 70;
              const circumference = 2 * Math.PI * radius;

              progressCircle.style.strokeDasharray = circumference;
              progressCircle.style.strokeDashoffset = circumference;

              if (status.toLowerCase() === "unverified") {
                statusElement.style.backgroundColor = "rgb(255, 69, 58)";
              } else {
                statusElement.style.backgroundColor = "rgb(50, 176, 36)";
              }

              let currentPercentage = 0;
              const animationDuration = 1500;
              const intervalTime = 15;
              const totalSteps = animationDuration / intervalTime;
              const percentageStep = confidence / totalSteps;

              const animationInterval = setInterval(() => {
                if (currentPercentage < confidence) {
                  currentPercentage += percentageStep;
                  const progress = (1 - currentPercentage / 100) * circumference;
                  progressCircle.style.strokeDashoffset = progress;
                  percentageText.textContent = \`\${Math.round(currentPercentage)}%\`;
                } else {
                  clearInterval(animationInterval);
                  percentageText.textContent = \`\${confidence}%\`;
                  const finalProgress = (1 - confidence / 100) * circumference;
                  progressCircle.style.strokeDashoffset = finalProgress;
                }
              }, intervalTime);
            </script>
          </body>
        </html>
      `);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  // News Summary Handler
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
                  <p><strong>Title:</strong> ${data.title}</p>
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
      console.error("Error:", error);
      alert("An error occurred while fetching the summary.");
    }
  };

  return (
    <div className={styles.dashboard}>
      {/* Sidebar */}
      <aside className={styles.sidebar}>
        <div onClick={handleHomeClick} className={styles.logo}>TrueLive.AI</div>
        <hr style={{width:"100%"}}></hr>
        <nav className={styles.nav}>
          <ul>
            <li className={styles.active}>
              <img src={dashboardICO} alt="Dashboard" className={styles.icon} /> Dashboard
            </li>
            <li>
              <a href="/">
                <img style={{ marginTop: "-2px" }} src={homeICO} alt="Homepage" className={styles.icon} /> Homepage
              </a>
            </li>
            <li>
            <a href="/trendingnews">
                <img style={{ marginTop: "-2px" }} src={newsICO} alt="Latest News" className={styles.icon} /> Latest News
              </a>
            </li>
            <li>
              <a href="/extrastuff">
                <img style={{ marginTop: "-2px" }} src={featureICO} alt="Features" className={styles.icon} /> Features
              </a>
            </li>
            <li>
              <a href="/extrastuff">
                <img style={{ marginTop: "-1px" }} src={contactICO} alt="Contact Us" className={styles.icon} /> Contact Us
              </a>
            </li>
          </ul>
        </nav>
        <div style={{marginLeft:"10px"}}><button onClick={handleSignOut} className={styles.signOutButton}>Sign Out</button></div>
      </aside>

      {/* Main Content */}
      <main className={styles.mainContent}>
        <div className={styles.topBar}>
          <h1>Dashboard</h1>
          <div className={styles.userInfo}>
            <img src={user?.photoURL || Avatar} alt="Avatar" className={styles.avatar} />
            <div className={styles.userName}>{user?.displayName || "Guest"}</div>
          </div>
        </div>

        {/* Feature Cards */}
        <div className={styles.grid}>
          <div className={styles.card} onClick={() => setActiveModal('video')}>
            <img src={ytfeature1} alt="Video Analysis" className={styles.cardImage} />
            <div className={styles.cardContent}>
              <h2 style={{fontSize:"2rem"}}>Video Analysis</h2>
              <p>Verify your video content with our AI-powered</p>
              <p>fact-checking system from Youtube Link or Video Upload.</p>
              <p>‎ </p>
              <p className={styles.rightArrow}>→</p>
            </div>
          </div>

          <div className={styles.card} onClick={() => setActiveModal('article')}>
            <img src={articlefeature2} alt="Article Analysis" className={styles.cardImage} />
            <div className={styles.cardContent}>
              <h2 style={{fontSize:"2rem"}}>Article Analysis</h2>
              <p>Analyze and validate articles with our</p>
              <p>AI-driven analysis tool from Article Link.</p>
              <p>‎ </p>
              <p className={styles.rightArrow}>→</p>
            </div>
          </div>

          <div className={`${styles.card} ${styles.fullWidth}`} onClick={() => setActiveModal('news')}>
            <img src={summarizerfeature3} alt="News Summarizer" className={styles.cardImage} />
            <div className={styles.cardContent}>
              <h2 style={{fontSize:"2rem"}}>News Summarizer</h2>
              <p>Get concise summaries of the latest</p>
              <p>news through our AI summarizer.</p>
              <p>‎ </p>
              <p className={styles.rightArrow}>→</p>
            </div>
          </div>
        </div>

        {/* Modals */}
        {activeModal && (
          <div className={modalStyles.modalOverlay} onClick={() => setActiveModal(null)}>
            <div className={modalStyles.modalContent} onClick={(e) => e.stopPropagation()}>
              {activeModal === 'video' && (
                <div className={modalStyles.window}>
                  <h4>Video Analysis</h4>
                  <div style={{ position: "relative" }}>
                    <input
                      type="text"
                      value={youtubeURL}
                      onChange={(e) => setYoutubeURL(e.target.value)}
                      placeholder="Paste your Video URL here"
                    />
                    <button className={modalStyles.pasteButton} onClick={() => handlePasteClick(setYoutubeURL)}>
                      Paste
                    </button>
                  </div>
                  <div className={modalStyles.divider}>
                    <span className={modalStyles.orText}>or</span>
                  </div>
                  <div className={modalStyles.uploadSection}>
                    <input
                      type="file"
                      accept="video/mp4,video/mkv,video/webm,video/mov,audio/*"
                      onChange={handleFileChange}
                      className={modalStyles.fileInput}
                    />
                    <p>or Drop a Video or Audio here (mp3, mp4, mov)</p>
                  </div>
                  <button
                    onClick={() => handleYouTubeAnalysis(file)}
                    className={modalStyles.analyzeButton}
                    disabled={isLoading}
                  >
                    {isLoading ? <div className={modalStyles.spinner}></div> : "Verify Video"}
                  </button>
                </div>
              )}

              {activeModal === 'article' && (
                <div className={modalStyles.window}>
                  <h4>Article Analysis</h4>
                  <div style={{ position: "relative" }}>
                    <input
                      type="text"
                      value={articleURL}
                      onChange={(e) => setArticleURL(e.target.value)}
                      placeholder="Paste your Article URL here"
                    />
                    <button className={modalStyles.pasteButton} onClick={() => handlePasteClick(setArticleURL)}>
                      Paste
                    </button>
                  </div>
                  <div className={modalStyles.divider}>
                    <span className={modalStyles.orText}>or</span>
                  </div>
                  <div className={modalStyles.uploadSection}>
                    <input
                      type="file"
                      accept="video/mp4,video/mkv,video/webm,video/mov,audio/*"
                      className={modalStyles.fileInput}
                    />
                    <p>or Drop a File (pdf, doc, xlsx)</p>
                  </div>
                  <button
                    onClick={handleArticleVerification}
                    className={modalStyles.analyzeButton}
                  >
                    Verify Article
                  </button>
                </div>
              )}      

              {activeModal === 'news' && (
                <div className={modalStyles.window}>
                  <h4>News Summarizer</h4>
                  <div style={{ position: "relative" }}>
                    <input
                      type="text"
                      value={newsURL}
                      onChange={(e) => setNewsURL(e.target.value)}
                      placeholder="Paste your Article URL here"
                    />
                    <button className={modalStyles.pasteButton} onClick={() => handlePasteClick(setNewsURL)}>
                      Paste
                    </button>
                  </div>
                  <div className={modalStyles.divider}>
                    <span className={modalStyles.orText}>or</span>
                  </div>
                  <div className={modalStyles.uploadSection}>
                    <input
                      type="file"
                      accept="video/mp4,video/mkv,video/webm,video/mov,audio/*"
                      className={modalStyles.fileInput}
                    />
                    <p>or Drop a File (pdf, doc, xlsx)</p>
                  </div>
                  <button
                    onClick={handleSummarizeClick}
                    className={modalStyles.analyzeButton}
                  >
                    Summarize
                  </button>
                </div>
              )}  
            </div>
          </div>
        )}

        <footer className={styles.footer}>
          <p>© 2024, Made with Passion ✊ by Digi Dynamos</p>
        </footer>
      </main>
    </div>
  );
};

export default Dashboard;