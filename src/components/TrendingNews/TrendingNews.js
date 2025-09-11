import React, { useState, useEffect } from "react";
import styles from "./TrendingNews.module.css";

const TrendingNews = () => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const keywords = ["technology", "health", "sports", "business", "science"];

  useEffect(() => {
    const fetchNews = async () => {
      try {
        setLoading(true);
        const randomKeyword = keywords[Math.floor(Math.random() * keywords.length)];
        const response = await fetch(
          `https://gnews.io/api/v4/search?q=${randomKeyword}&lang=en&max=8&apikey=${process.env.REACT_APP_GNEWS_API_KEY}`
        );

        if (!response.ok) {
          throw new Error("Network response was not ok");
        }

        const data = await response.json();

        if (!data.articles || data.articles.length === 0) {
          setNews([]);
        } else {
          setNews(data.articles); // Already max=8
        }
      } catch (error) {
        console.error("Error fetching news:", error);
        setNews([]);
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, []);

  return (
    <section className={styles.newsSection}>
      <h3 style={{ fontSize: 30 }}>Trending News</h3>
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
                  {article.image && (
                    <img
                      src={article.image}
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
