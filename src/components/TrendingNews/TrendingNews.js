import React, { useState, useEffect } from "react";
import styles from "./TrendingNews.module.css";

const TrendingNews = () => {
  const [news, setNews] = useState([]); // State to store news data
  const [loading, setLoading] = useState(true); // State to handle loading
  const keywords = ["technology", "health", "sports", "business", "science"]; // List of random keywords

  useEffect(() => {
    const fetchNews = async () => {
      try {
        setLoading(true); // Ensure loading state is reset
        const randomKeyword = keywords[Math.floor(Math.random() * keywords.length)]; // Pick a random keyword
        const response = await fetch(
          `https://newsapi.org/v2/everything?q=${randomKeyword}&apiKey=f2b9f8a68aea4a5dacd81bc2615c96c3`
        );

        if (!response.ok) {
          throw new Error("Network response was not ok");
        }

        const data = await response.json();

        if (!data.articles || data.articles.length === 0) {
          setNews([]); // Set to empty if no articles are found
        } else {
          setNews(data.articles.slice(0, 8)); // Limit to 8 articles
        }
      } catch (error) {
        console.error("Error fetching news:", error);
        setNews([]); // Reset news on error
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, []); // Run only once when the component mounts

  return (
    <section className={styles.newsSection}>
      <h3 style={{
        fontSize: 30
      }}>Trending News</h3>
      {loading ? (
        <p>Loading news...</p>
      ) : (
        <div className={styles.newsList}>
          {news.length === 0 ? (
            <p>No news found.</p>
          ) : (
            news.map((article, index) => (
              <div key={index} className={styles.newsItem}>
                <div className={styles.imageContainer}>
                  {article.urlToImage && (
                    <img
                      src={article.urlToImage}
                      alt={article.title}
                      className={styles.newsImage}
                    />
                  )}
                </div>
                <h4>{article.title}</h4>
                <p>{article.description}</p>
                <a href={article.url} target="_blank" rel="noopener noreferrer">
                  Read more
                </a>
              </div>
            ))
          )}
        </div>
      )}
    </section>
  );
};

export default TrendingNews;
