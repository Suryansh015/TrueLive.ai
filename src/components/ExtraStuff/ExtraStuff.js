import React from "react";
import styles from "./ExtraStuff.module.css"; 
import ytfeature1 from "./yt-feature-1.png"
import articlefeature2 from "./article-feature-2.jpg"
import summarizerfeature3 from "./summarizer-feature-3.png"
import genaifeature4 from "./genai-feature3.png"
import ocrfeature5 from "./ocr-feature4.png"
import whyUseTickIco from "./_whyUseIconTick.png"

const ExtraStuff = () => {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className={styles.container}>
      {/* Section 2: Feature 1 - YouTube link transcription and fact-checking */}
      <div className={styles.featureSection}>
        <div className={styles.textLeft}>
          <h4 className={styles.featureTitle}>Feature 1</h4>
          <h2 className={styles.mainHeading}>
            <span className={styles.highlight}>Video Transcription</span> and Fact-Checking with AI:
          </h2>
          <p className={styles.description}>Streamline Video Content Analysis Effortlessly!</p>
          <ul className={styles.featureList}>
            <li>
              <strong>Accurate Transcriptions:</strong> AI efficiently transcribes YouTube video content for easy reference.
            </li>
            <li>
              <strong>Fact Validation:</strong> Analyze video claims, cross-check data, and ensure content reliability.
            </li>
            <li>
              <strong>Reliability Scoring:</strong> Provide a credibility score based on factual consistency and evidence.
            </li>
            <li>
              <strong>Time-Saving Workflow:</strong> Simplify your research and content creation with automated insights.
            </li>
          </ul>
        </div>
        <div className={styles.imageContainer}>
          <img src={ytfeature1} alt="YouTube feature" className={styles.imageRight} />
        </div>
      </div>

      {/* Section 3: Feature 2 - stream analysis */}
      <div className={styles.featureSectionReverse}>
        <div className={styles.imageContainer}>
          <img src={articlefeature2} alt="YouTube feature" className={styles.imageLeft} />
        </div>
        <div className={styles.textRight}>
          <h4 className={styles.featureTitle}>Feature 2</h4>
          <h2 className={styles.mainHeading}>
          <span className={styles.highlight}>Livestream Transcription</span> and Fact-Checking with AI:
          </h2>
          <p className={styles.description}>Analyze Live Content in Real-Time!</p>
          <ul className={styles.featureList}>
            <li>
              <strong>Unmatched Accuracy:</strong> Scan and analyze news articles to validate their authenticity.
            </li>
            <li>
              <strong>Effortless Verification:</strong> Simply paste a link, and let AI do the heavy lifting.
            </li>
            <li>
              <strong>Clarity Guaranteed:</strong> Understand whether the news is fact or fiction instantly.
            </li>
            <li>
              <strong>Empowered Decisions:</strong> Stay informed with credible, reliable content at all times!
            </li>
          </ul>
        </div>
      </div>
      {/* Feature 3 - article analysis */}
      <div className={styles.featureSection}>
        <div className={styles.textLeft}>
          <h4 className={styles.featureTitle}>Feature 3</h4>
          <h2 className={styles.mainHeading}>
          <span className={styles.highlight}>Fact-Checking News Articles</span>, Verify the Truth at Your Fingertips!
          </h2>
          <p className={styles.description}>Streamline Content Analysis Effortlessly!</p>
          <ul className={styles.featureList}>
          <li>
              <strong>Unmatched Accuracy:</strong> Scan and analyze news articles to validate their authenticity.
            </li>
            <li>
              <strong>Effortless Verification:</strong> Simply paste a link, and let AI do the heavy lifting.
            </li>
            <li>
              <strong>Clarity Guaranteed:</strong> Understand whether the news is fact or fiction instantly.
            </li>
            <li>
              <strong>Empowered Decisions:</strong> Stay informed with credible, reliable content at all times!
            </li>
          </ul>
        </div>
        <div className={styles.imageContainer}>
          <img src={summarizerfeature3} style={{maxWidth: "550px"}} alt="YouTube feature" className={styles.imageRight} />
        </div>
      </div>
      {/* Feature 4 - gen ai det */}
      <div className={styles.featureSectionReverse}>
        <div className={styles.imageContainer}>
          <img src={genaifeature4} alt="YouTube feature" className={styles.imageLeft} />
        </div>
        <div className={styles.textRight}>
          <h4 className={styles.featureTitle}>Feature 4</h4>
          <h2 className={styles.mainHeading}>
          <span className={styles.highlight}>AI-Generated Image Detection</span> with Advanced Analysis:
          </h2>
          <ul className={styles.featureList}>
          <li>
        <strong>AI Detection:</strong> Determines whether an image is AI-generated or authentic.
    </li>
    <li>
        <strong>Deep Analysis:</strong> Examines image patterns, metadata, and artifacts for accuracy.
    </li>
    <li>
        <strong>Confidence Score:</strong> Provides a reliability score for the detection result.
    </li>
    <li>
        <strong>Fast & Efficient:</strong> Get results in seconds with advanced AI models.
    </li>
          </ul>
        </div>
      </div>
      {/* Feature 5 - image ocr analysis */}
      <div className={styles.featureSection}>
        <div className={styles.textLeft}>
          <h4 className={styles.featureTitle}>Feature 5</h4>
          <h2 className={styles.mainHeading}>
          <span className={styles.highlight}>AI-Powered Image Analysis</span> for Text Extraction & Verification:
          </h2>
          <p className={styles.description}>Extract, Analyze, and Validate Image Content!</p>
          <ul className={styles.featureList}>
          <li>
        <strong>Text Extraction:</strong> Converts printed or handwritten text from images into digital format.
    </li>
    <li>
        <strong>Content Verification:</strong> Cross-checks extracted text for factual accuracy.
    </li>
    <li>
        <strong>Key Insights:</strong> Highlights important details and potential inconsistencies.
    </li>
    <li>
        <strong>Quick & Accurate:</strong> Fast OCR processing with AI-powered analysis.
    </li>
          </ul>
        </div>
        <div className={styles.imageContainer}>
          <img src={ocrfeature5} style={{maxWidth: "550px"}} alt="YouTube feature" className={styles.imageRight} />
        </div>
      </div>
      
      {/* Section 5: Why use TrueLive.ai*/}
      <div className={styles.whyUseSection}>
      <h2 className={styles.title}>Why Use <span className={styles.highlight}>TrueLive.ai</span> ?</h2>
      <div className={styles.cards}>
        <div className={styles.card}>
          <img src={whyUseTickIco} alt="Placeholder Icon" className={styles.icon} />
          <h3>Fast & Accurate Fact-Checking</h3>
          <p>Quickly verify news articles and videos with precise fact-checking tools.</p>
        </div>
        <div className={styles.card}>
          <img src={whyUseTickIco} alt="Placeholder Icon" className={styles.icon} />
          <h3>Summarizes News Stories</h3>
          <p>Save time with concise summaries of lengthy news stories.</p>
        </div>
        <div className={styles.card}>
          <img src={whyUseTickIco} alt="Placeholder Icon" className={styles.icon} />
          <h3>Real-Time Verification</h3>
          <p>Stay informed with up-to-date news verification in real-time.</p>
        </div>
        <div className={styles.card}>
          <img src={whyUseTickIco} alt="Placeholder Icon" className={styles.icon} />
          <h3>Share Reliable Information</h3>
          <p>Ensure that you only share trustworthy and accurate information.</p>
        </div>
      </div>
      </div>

      {/* Contact Us Section */}
      <div id="contact-section" className={styles.whyUseSection}>
      </div>
      <div style={{
        textAlign: "center",
        padding: "20px",
        marginTop: "-80px",
        marginBottom: "40px",
        background: "linear-gradient(to left, rgb(0, 0, 0), rgb(0, 0, 0), rgb(0, 34, 75))",
        borderRadius: "10px",
        color: "white",
      }}>
        <h2>Contact Us</h2>
        <p>
          We'd love to hear from you! Reach out to us for any queries, feedback, or support.
        </p>
        <div style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "10px",
          marginTop: "10px",
          
        }}>
          <p>Email: <a href="mailto:support@truelive.ai" style={{ color: "#007bff", textDecoration: "none" }}>support@truelive.ai</a></p>
          <p>Phone: <a href="tel:+1234567890" style={{ color: "#007bff", textDecoration: "none" }}>+1 234 567 890</a></p>
          <p>Follow us on: 
            <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" style={{ marginLeft: "5px", color: "#007bff", textDecoration: "none" }}>Twitter</a>, 
            <a href="https://facebook.com" target="_blank" rel="noopener noreferrer" style={{ marginLeft: "5px", color: "#007bff", textDecoration: "none" }}>Facebook</a>
          </p>
        </div>
      </div>
      <h3 style={{
        marginTop: "-10px", 
        marginBottom: "50px", 
        backgroundColor: "rgb(12, 27, 124)", 
        padding: "20px",
        marginLeft: "-20px",
        marginRight: "-20px"
      }}>
        Made with Passion ✊ by <span style={{color: "#ffef3f"}}>Team Digi Dynamos</span></h3>
      <button
        onClick={scrollToTop}
        style={{
          display: "block",
          margin: "20px auto",
          marginTop: "20px",
          padding: "10px 20px",
          fontSize: "16px",
          backgroundColor:" #ffef3f",
          color: "black",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
          transition: "background-color 0.3s, transform 0.3s",
        }}
        onMouseEnter={(e) => {
          e.target.style.backgroundColor = "#9a7400";
          e.target.style.transform = "scale(1.05)";
        }}
        onMouseLeave={(e) => {
          e.target.style.backgroundColor = "#ffef3f";
          e.target.style.transform = "scale(1)";
        }}
      >
        Return to Top
      </button>
    </div>
  );
};

export default ExtraStuff;
