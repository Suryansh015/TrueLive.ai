import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./Dashboard.module.css"; 
import modalStyles from "./Modal.module.css";
import { auth } from "../Login/firebase";
import { useAuthState } from "react-firebase-hooks/auth";
import defaultAvatar from "./media/avatar-icon.png";
import ytfeature1 from "../ExtraStuff/yt-feature-1.png";
import articlefeature2 from "../ExtraStuff/article-feature-2.jpg";
import genAIfeature3 from "../ExtraStuff/genai-feature3.png";
import ocrfeature4 from "../ExtraStuff/ocr-feature4.png";
import dashboardICO from "./media/dashboard-icon.png";
import homeICO from "./media/homepage-icon.png";
import newsICO from "./media/news-icon.png";
import featureICO from "./media/features-icon.png";
import contactICO from "./media/contact-icon.png"

const Dashboard = () => {
  const [user] = useAuthState(auth);
  const navigate = useNavigate();
  const [activeModal, setActiveModal] = useState(null);
  const [youtubeURL, setYoutubeURL] = useState("");
  const [articleURL, setArticleURL] = useState("");
  // const [newsURL, setNewsURL] = useState(""); NEWS SUMMARIZER REMOVED
  const [streamURL, setStreamURL] = useState("");
  const [instaURL, setInstaURL] = useState("");
  const [newsInput, setNewsInput] = useState("");
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
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  // YouTube Analysis Handler
  const handleYouTubeAnalysis = async (file, url) => {
    setIsLoading(true);
    try {
      let response;
      {/*}
      ${data.key_points ? `
        <div class="result-section">
          <p><strong>Key Points:</strong></p>
          <ul>
            ${data.key_points.map(point => `<li>${point}</li>`).join('')}
          </ul>
        </div>
      ` : ''}
      */}
      if (url) {
        // Handle URL-based analysis
        response = await fetch("http://127.0.0.1:5000/videoanalyze", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ url }),
        });
  
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
  
        const data = await response.json();
        
        // Format verification results by replacing asterisks
        const formattedVerification = data.verification_result
          ? data.verification_result
              .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
              .replace(/\*(.*?)\*/g, "<em>$1</em>")
              .replace(/\n/g, "<br>")
          : '';
  
        // Create results window
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
                
                ${data.summary ? `
                  <div class="result-section">
                    <p><strong>Transcription Summary:</strong></p>
                    <div class="summary-box">${data.summary}</div>
                  </div>
                ` : ''}
                
                
              
                ${formattedVerification ? `
                  <div class="result-section">
                    <p><strong>Verification Results:</strong></p>
                    <div class="summary-box">${formattedVerification}</div>
                  </div>
                ` : ''}
                
                ${data.video_id ? `
                  <div class="result-section">
                    <p><strong>Video Preview:</strong></p>
                    <iframe 
                      width="560" 
                      height="315" 
                      src="https://www.youtube.com/embed/${data.video_id}" 
                      frameborder="0" 
                      allowfullscreen>
                    </iframe>
                  </div>
                ` : ''}
              </div>
            </body>
          </html>
        `);
      } else if (file) {
        // Handle file-based analysis
        const formData = new FormData();
        formData.append("video", file);
        response = await fetch("http://127.0.0.1:5000/videoanalyze", {
          method: "POST",
          body: formData,
        });
  
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
  
        const data = await response.json();
        console.log(data); // Handle further as needed
      } else {
        throw new Error("Please provide either a YouTube URL or upload a video file.");
      }
    } catch (error) {
      console.error("Error:", error);
      alert(error.message || "An error occurred while analyzing the video.");
    } finally {
      setIsLoading(false);
    }
  };
  
  
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Article Analysis Handler
const handleArticleAnalysis = async () => {
  setIsLoading(true);
  try {
    const response = await fetch("http://127.0.0.1:5000/verify_article", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: articleURL }),
    });
    const data = await response.json();

    let claimsHTML = "";
    if (data.claims && data.claims.length > 0) {
      claimsHTML = `
        <div class="result-section">
          <p><strong>Extracted Claims:</strong></p>
          ${data.claims.map(claim => `
            <div class="claim-box">
              <p>${claim.text}</p>
              <small>Confidence: ${(claim.confidence * 100).toFixed(2)}%</small>
            </div>
          `).join('')}
        </div>
      `;
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
            .claim-box {
              background-color: #f5f5f5;
              padding: 10px;
              margin: 10px 0;
              border-radius: 5px;
              border-left: 4px solid #2d87f0;
            }
            .claim-box small {
              color: #666;
              display: block;
              margin-top: 5px;
            }
            .source-link {
              color: #2d87f0;
              text-decoration: none;
            }
            .source-link:hover {
              text-decoration: underline;
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
              <p><strong>Confidence:</strong> ${data.claim_verification.confidence}%</p>
              <p><strong>Source:</strong> <a href="${data.claim_verification.source}" class="source-link" target="_blank">${data.claim_verification.source}</a></p>
            </div>

            <!-- Speedometer Animation -->
            <div class="speedometer">
              <svg width="150" height="150">
                <circle class="background" cx="75" cy="75" r="70"></circle>
                <circle class="progress" cx="75" cy="75" r="70"></circle>
              </svg>
              <div class="percentage">0%</div>
            </div>

            ${claimsHTML}

            <div class="result-section">
              <p><strong>Summary:</strong></p>
              <div class="summary-box">${data.article.summary}</div>
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
  } catch (error) {
    console.error("Error:", error);
    alert("An error occurred while verifying the article.");
  } finally {
    setIsLoading(false);
  }
};
{/* OLD NEWS SUMMARIZER REMOVED ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  // News Summary Handler
  const handleSummarize = async () => {
    setIsLoading(true);
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
    } finally {
      setIsLoading(false);
    }
  };
*/}
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  // Stream Analysis Handler
  const handleStreamAnalysis = async (url) => {
    setIsLoading(true);
    try {
      if (!url) {
        throw new Error("Please provide a YouTube livestream URL.");
      }
  
      const response = await fetch("http://127.0.0.1:5000/analyze_stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });
  
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
  
      const data = await response.json();
  
      // Format verification results by replacing asterisks
      const formattedVerification = data.verification
        ? data.verification
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\*(.*?)\*/g, "<em>$1</em>")
            .replace(/\n/g, "<br>")
        : '';
  
      // Create results window
      const streamWindow = window.open("", "_blank", "width=800,height=600");
      streamWindow.document.write(`
        <html>
          <head>
            <title>Livestream Analysis Results</title>
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
              .summary-box {
                padding: 10px;
                background-color: #fafafa;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-style: italic;
              }
              .key-points {
                list-style-type: none;
                padding: 0;
              }
              .key-points li {
                margin: 10px 0;
                padding: 10px;
                background-color: #f5f5f5;
                border-radius: 5px;
                border-left: 4px solid #2d87f0;
              }
            </style>
          </head>
          <body>
            <div class="container">
              <h4>Livestream Analysis Results</h4>
              
              ${data.transcript ? `
                <div class="result-section">
                  <p><strong>Transcript:</strong></p>
                  <div class="summary-box">${data.transcript}</div>
                </div>
              ` : ''}
              
              ${data.key_points ? `
                <div class="result-section">
                  <p><strong>Key Points:</strong></p>
                  <ul class="key-points">
                    ${data.key_points.map(point => `<li>${point}</li>`).join('')}
                  </ul>
                </div>
              ` : ''}
              
              ${formattedVerification ? `
                <div class="result-section">
                  <p><strong>Fact Check Results:</strong></p>
                  <div class="summary-box">${formattedVerification}</div>
                </div>
              ` : ''}
            </div>
          </body>
        </html>
      `);
    } catch (error) {
      console.error("Error:", error);
      alert(error.message || "An error occurred while analyzing the livestream.");
    } finally {
      setIsLoading(false);
    }
  };
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  // gen ai detector
  const handleGenAIAnalysis = async (file) => {
    setIsLoading(true);
    try {
      if (!file) throw new Error("Please upload an image file.");
  
      const formData = new FormData();
      formData.append("file", file);
  
      const response = await fetch("http://127.0.0.1:5000/genAI", {
        method: "POST",
        body: formData,
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
      }
  
      const data = await response.json();
      if (data.error) throw new Error(data.error);
  
      // Determine box color based on claim
      const isHuman = data.prediction.toLowerCase() === "human";
      const claimBoxColor = isHuman ? "#28a745" : "#dc3545"; // Green for human, Red for artificial
      const claimTextColor = "#fff"; // White text for contrast
  
      // Display result in a new window
      const resultWindow = window.open("", "_blank", "width=800,height=600");
      resultWindow.document.write(`
        <html>
          <head>
            <title>Image Analysis Result</title>
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
                text-align: center;
              }
              h4 {
                color: #2d87f0;
                font-size: 1.5rem;
                margin-bottom: 20px;
                margin-top: 20px;
              }
              .claim-box {
                background-color: ${claimBoxColor};
                color: ${claimTextColor};
                font-size: 1.2rem;
                font-weight: bold;
                padding: 15px;
                border-radius: 5px;
                margin: 20px auto;
                width: 60%;
                text-align: center;
              }
              .result-section {
                font-size: 1rem;
                margin-bottom: 20px;
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
              <h4>Image Analysis Result</h4>
              <div class="claim-box">${data.prediction}</div>
              <p class="result-section"><strong>Confidence:</strong> ${data.confidence.toFixed(2)}%</p>
              <div class="speedometer">
                <svg viewBox="0 0 150 150">
                  <circle class="background" cx="75" cy="75" r="70"></circle>
                  <circle class="progress" cx="75" cy="75" r="70"></circle>
                </svg>
                <div class="percentage">${data.confidence.toFixed(2)}%</div>
              </div>
            </div>
            <script>
              const confidence = ${data.confidence};
              const progressCircle = document.querySelector('.progress');
              const percentage = (1 - confidence / 100) * 440;
  
              let currentOffset = 440;
              const animateProgress = () => {
                const step = 10;
                if (currentOffset > percentage) {
                  currentOffset -= step;
                  if (currentOffset < percentage) currentOffset = percentage;
                  progressCircle.style.strokeDashoffset = currentOffset;
                  requestAnimationFrame(animateProgress);
                }
              };
  
              animateProgress();
            </script>
          </body>
        </html>
      `);
    } catch (error) {
      console.error("Error:", error);
      alert(error.message || "An error occurred while analyzing the image.");
    } finally {
      setIsLoading(false);
    }
  };
  
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
  // OCR Analysis 
  const handleOCRAnalysis = async (imageFile) => {
    setIsLoading(true);
    try {
        const formData = new FormData();
        formData.append("image", imageFile);

        const response = await fetch("http://127.0.0.1:5001/OCR", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        // Format verification results like YouTube analysis
        const formattedVerification = data.verification_result
            ? data.verification_result
                .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                .replace(/\*(.*?)\*/g, "<em>$1</em>")
                .replace(/\n/g, "<br>")
            : '';

        let keyPointsHTML = "";
        if (data.key_points && data.key_points.length > 0) {
            keyPointsHTML = `
                <div class="result-section">
                    <p><strong>Key Points:</strong></p>
                    <ul>
                        ${data.key_points.map(point => `<li>${point}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        const analysisWindow = window.open("", "_blank", "width=800,height=600");
        analysisWindow.document.write(`
            <html>
                <head>
                    <title>OCR Verification Results</title>
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
                        <h4>OCR Verification Results</h4>
                        <div class="result-section">
                            <p><strong>Extracted Text:</strong></p>
                            <div class="summary-box">${data.extracted_text}</div>
                        </div>

                        <div class="result-section">
                            <p><strong>Summary:</strong></p>
                            <div class="summary-box">${data.summary}</div>
                        </div>

                        ${keyPointsHTML}

                        ${formattedVerification ? `
                            <div class="result-section">
                                <p><strong>Verification Results:</strong></p>
                                <div class="summary-box">${formattedVerification}</div>
                            </div>
                        ` : ''}
                    </div>
                </body>
            </html>
        `);
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred while processing the image.");
    } finally {
        setIsLoading(false);
    }
};

// Keyword Article Analysis~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
const handleArticleKeywordAnalysis = async () => {
  setIsLoading(true);
  try {
    const response = await fetch("http://127.0.0.1:5000/articlekeyword", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ news_input: newsInput }),
    });

    const data = await response.json();
    console.log("Response status:", response.status);
    console.log("Received from /articlekeyword:", data);

    if (!data.verification || !data.credibility_score) {
      alert("Missing data in response. Please try again.");
      return;
    }

    const articleWindow = window.open("", "_blank", "width=800,height=600");
    articleWindow.document.write(`
      <html>
        <head>
          <title>Verification Analysis</title>
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
              margin-bottom: 30px;
            }
            .section {
              margin-bottom: 20px;
            }
            .score-box {
              background-color: #e0f3ff;
              padding: 10px;
              border-left: 4px solid #2d87f0;
              font-weight: bold;
              border-radius: 4px;
              margin-top: 10px;
              color: #333;
            }
          </style>
        </head>
        <body>
          <div class="container">
            <h4>Verification & Credibility Analysis</h4>

            <div class="section">
              <p><strong>Verification Status:</strong></p>
              <div class="score-box">${data.verification}</div>
            </div>

            <div class="section">
              <p><strong>Credibility Score:</strong></p>
              <div class="score-box">${data.credibility_score} / 100</div>
            </div>
          </div>
        </body>
      </html>
    `);
  } catch (error) {
    console.error("Error during article keyword verification:", error);
    alert("Something went wrong during verification.");
  } finally {
    setIsLoading(false);
  }
};



// Instagram Reels Analysis~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
const handleInstaAnalysis = async () => {
  setIsLoading(true);

  try {
    const response = await fetch("http://127.0.0.1:5000/analyze_reels", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: instaURL }), // make sure reelUrl is in your component state
    });

    const data = await response.json();
    console.log("Response status:", response.status);
    console.log("Received from /analyze_stream:", data);

    if (!data.transcript || !data.verification) {
      alert("Missing data in response. Please try again.");
      return;
    }

    const reelWindow = window.open("", "_blank", "width=800,height=600");
    reelWindow.document.write(`
      <html>
        <head>
          <title>Reel Verification Analysis</title>
          <style>
            body {
              font-family: 'Arial', sans-serif;
              background: linear-gradient(to right, #000, #001f3f);
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
              margin-bottom: 30px;
            }
            .section {
              margin-bottom: 20px;
            }
            .score-box {
              background-color: #e0f3ff;
              padding: 10px;
              border-left: 4px solid #2d87f0;
              font-weight: bold;
              border-radius: 4px;
              margin-top: 10px;
              color: #333;
              white-space: pre-wrap;
            }
          </style>
        </head>
        <body>
          <div class="container">
            <h4>Instagram Reel Analysis</h4>

            <div class="section">
              <p><strong>Transcription:</strong></p>
              <div class="score-box">${data.transcript}</div>
            </div>

            <div class="section">
              <p><strong>Verification Result:</strong></p>
              <div class="score-box">${data.verification}</div>
            </div>
          </div>
        </body>
      </html>
    `);
  } catch (error) {
    console.error("Error during reel analysis:", error);
    alert("Something went wrong during reel analysis.");
  } finally {
    setIsLoading(false);
  }
};

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
            <img
                          src={user?.photoURL || defaultAvatar}
                          alt="Avatar"
                          className={styles.avatar}
                          onError={(e) => (e.target.src = defaultAvatar)} // Fallback if the image fails to load
                        />
            <div className={styles.userName}>{user?.displayName || "Guest"}</div>
          </div>
        </div>

        {/* Feature Cards */}
        <div className={styles.grid}>
          <div className={styles.card} onClick={() => setActiveModal('video')}>
            <img src={ytfeature1} alt="Video Analysis" className={styles.cardImage} />
            <div className={styles.cardContent}>
              <h2 style={{fontSize:"2rem"}}>Youtube Analysis</h2>
              <p>Verify your video content with our AI-powered</p>
              <p>fact-checking system from Youtube Link or Livestream.</p>
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

          <div className={`${styles.card} ${styles.fullWidth}`} onClick={() => setActiveModal('genAI')}>
            <img src={genAIfeature3} alt="AI Gen IMG Det" className={styles.cardImage} />
            <div className={styles.cardContent}>
              <h2 style={{fontSize:"2rem"}}>AI Image Detector</h2>
              <p>Detects whether an image is AI-generated or real.</p>
              <p>Utilizes deep learning models for accurate analysis.</p>
              <p>‎ </p>
              <p className={styles.rightArrow}>→</p>
            </div>
          </div>
          {/*<div className={styles.card} onClick={() => setActiveModal('stream')}>*/}
          <div className={styles.card} onClick={() => setActiveModal('OCR')}>
            <img src={ocrfeature4} alt="OCR" className={styles.cardImage} />
            <div className={styles.cardContent}>
              <h2 style={{fontSize:"2rem"}}>Social Media Analysis</h2>
              <p>Extracts text from images using OCR for news analysis.</p>
              <p>Analyzes Instagram Reels for content authenticity.</p>
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
        placeholder="Paste your YouTube Video URL here"
      />
      <button 
        className={modalStyles.pasteButton} 
        onClick={() => handlePasteClick(setYoutubeURL)}
      >
        Paste
      </button>
    </div>
    <button
      onClick={() => handleYouTubeAnalysis(file, youtubeURL)}
      className={modalStyles.analyzeButton}
      disabled={isLoading}
      style={{ marginTop: "5px" }}
    >
      {isLoading ? <div className={modalStyles.spinner}></div> : "Verify Video"}
    </button>
    <div style={{ marginTop: "40px", marginBottom: "40px" }} className={modalStyles.divider}>
      <span className={modalStyles.orText}>or</span>
    </div>
    <h4>Livestream Analysis</h4>
                  <div style={{ position: "relative" }}>
                    <input
                      type="text"
                      value={streamURL}
                      onChange={(e) => setStreamURL(e.target.value)}
                      placeholder="Paste your Livestream URL here"
                    />
                    <button className={modalStyles.pasteButton} onClick={() => handlePasteClick(setStreamURL)}>
                      Paste
                    </button>
                  </div>
                  <button 
                    onClick={() => handleStreamAnalysis(streamURL)} 
                    className={modalStyles.analyzeButton} 
                    disabled={isLoading}
                    style={{ marginTop: "5px" }}
                  >
                    {isLoading ? <div className={modalStyles.spinner}></div> : "Verify Stream"}
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
                  
                  <button
                    onClick={handleArticleAnalysis}
                    className={modalStyles.analyzeButton}
                    disabled={isLoading}
                    style={{ marginBottom: "-10px", marginTop: "5px" }}
                  >
                    {isLoading ? <div className={modalStyles.spinner}></div> : "Verify Article"}
                  </button>
                  <div style={{ marginTop: "40px", marginBottom: "40px" }} className={modalStyles.divider}>
      <span className={modalStyles.orText}>or</span>
    </div>
    <h4>Keyword Search</h4>
                  <div style={{ position: "relative" }}>
                    <input
                      type="text"
                      value={newsInput}
                      onChange={(e) => setNewsInput(e.target.value)}
                      placeholder="Enter a news statement or keyword"
                    />
                    <button className={modalStyles.pasteButton} onClick={() => handlePasteClick(setNewsInput)}>
                      Paste
                    </button>
                  </div>
                  
                  <button
                    onClick={handleArticleKeywordAnalysis}
                    className={modalStyles.analyzeButton}
                    disabled={isLoading}
                    style={{ marginBottom: "10px", marginTop: "5px" }}
                  >
                    {isLoading ? <div className={modalStyles.spinner}></div> : "Analyze"}
                  </button>
                </div>
              )}      
              {/* OLD NEWS SUMMARIZER ~~~~~~~~~~~
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
                    onClick={handleSummarize}
                    className={modalStyles.analyzeButton}
                    disabled={isLoading}
                    >
                      {isLoading ? <div className={modalStyles.spinner}></div> : "Summarize"}
                  </button>
                </div>
              )}  
              */}

              {/* STREAM SEPERATE MODAL NOW COMBINED W VIDEO ~~~~~~~~~~~~~~~~~~~~~~~
              {activeModal === 'stream' && (
                <div className={modalStyles.window}>
                  <h4>Livestream Analysis</h4>
                  <div style={{ position: "relative" }}>
                    <input
                      type="text"
                      value={streamURL}
                      onChange={(e) => setStreamURL(e.target.value)}
                      placeholder="Paste your Livestream URL here"
                    />
                    <button className={modalStyles.pasteButton} onClick={() => handlePasteClick(setStreamURL)}>
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
                    onClick={() => handleStreamAnalysis(streamURL)} 
                    className={modalStyles.analyzeButton} 
                    disabled={isLoading}
                  >
                    {isLoading ? <div className={modalStyles.spinner}></div> : "Verify Stream"}
                  </button>
                </div>
              )}  
                */}
              {activeModal === 'genAI' && (
  <div className={modalStyles.window}>
    <h4>AI Generated IMG Detector</h4>

    <div className={modalStyles.uploadSection}>
      <input
        type="file"
        accept="image/*"
        className={modalStyles.fileInput}
        onChange={(e) => handleGenAIAnalysis(e.target.files[0])}
      />
      <p>or Drop an Image (jpg, png, jpeg)</p>
    </div>
    <button
      onClick={() => handleGenAIAnalysis(null)}
      className={modalStyles.analyzeButton}
      disabled={isLoading}
    >
      {isLoading ? <div className={modalStyles.spinner}></div> : "Analyze Image"}
    </button>
  </div>
)}
{activeModal === 'OCR' && (
  <div className={modalStyles.window}>
    <h4>Instagram Reels Analysis</h4>
                  <div style={{ position: "relative" }}>
                    <input
                      type="text"
                      value={instaURL}
                      onChange={(e) => setInstaURL(e.target.value)}
                      placeholder="Paste your Livestream URL here"
                    />
                    <button className={modalStyles.pasteButton} onClick={() => handlePasteClick(setInstaURL)}>
                      Paste
                    </button>
                  </div>
                  <button 
                    onClick={() => handleInstaAnalysis(instaURL)} 
                    className={modalStyles.analyzeButton} 
                    disabled={isLoading}
                    style={{ marginTop: "5px", marginBottom: "-10px" }}
                  >
                    {isLoading ? <div className={modalStyles.spinner}></div> : "Verify Reel"}
                  </button>
                  <div style={{ marginTop: "40px", marginBottom: "40px" }} className={modalStyles.divider}>
      <span className={modalStyles.orText}>or</span>
    </div>
    <h4 style={{ marginTop: "-10px" }}>Image Analysis</h4>
    <div className={modalStyles.uploadSection}>
      <input
        type="file"
        accept="image/*"
        className={modalStyles.fileInput}
        onChange={(e) => handleOCRAnalysis(e.target.files[0])}
      />
      <p>or Drop an Image (jpg, png, jpeg)</p>
    </div>
    <button
      onClick={() => handleOCRAnalysis(null)}
      className={modalStyles.analyzeButton}
      disabled={isLoading}
    >
      {isLoading ? <div className={modalStyles.spinner}></div> : "Analyze Image"}
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