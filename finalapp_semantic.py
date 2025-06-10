
import streamlit as st
import requests
from deep_translator import GoogleTranslator
from langdetect import detect
import time
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# API Keys
NYT_API_KEY = 'YG9qtrG1LvBhf1qZj9wTOnnoeA98EgUm'
NEWS_API_KEY = 'ecca68e4fd89433bbf77ce4f451fa319'

# API Endpoints
NYT_ARTICLE_SEARCH_URL = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'
NEWSAPI_TOP_HEADLINES_URL = 'https://newsapi.org/v2/top-headlines'

# Load Semantic Embedding Model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to detect and translate text
def translate_to_english(text):
    detected_lang = detect(text)
    if detected_lang != "en":
        translated_text = GoogleTranslator(source=detected_lang, target="en").translate(text)
        return translated_text, detected_lang
    return text, "en"

# Function to fetch news from NYT API
def fetch_nyt_articles(query):
    query, detected_lang = translate_to_english(query)
    params = {
        'q': query,
        'api-key': NYT_API_KEY,
        'sort': 'newest'
    }
    response = requests.get(NYT_ARTICLE_SEARCH_URL, params=params)
    if response.status_code == 200:
        return response.json(), detected_lang
    else:
        st.error(f"⚠️ NYT API Failed: {response.status_code}")
        return None, detected_lang

# Function to fetch top headlines from NewsAPI
def fetch_top_headlines():
    params = {'country': 'in', 'apiKey': NEWS_API_KEY}
    response = requests.get(NEWSAPI_TOP_HEADLINES_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"⚠️ NewsAPI Failed: {response.status_code}")
        return None

# Semantic fake news checker
def check_fake_news(article_text):
    translated_text, detected_lang = translate_to_english(article_text[:300])
    nyt_data, _ = fetch_nyt_articles(translated_text)
    news_data = fetch_top_headlines()
    with st.spinner("Analyzing article semantically... 🧠"):
        time.sleep(2)

    user_embedding = embedding_model.encode([translated_text])
    found_match = False
    matched_sources = []

    # Check NYT
    if nyt_data and 'response' in nyt_data and 'docs' in nyt_data['response']:
        for doc in nyt_data['response']['docs']:
            headline = doc['headline']['main']
            sim = cosine_similarity(user_embedding, embedding_model.encode([headline]))[0][0]
            if sim > 0.7:
                found_match = True
                matched_sources.append("NYT")
                break

    # Check NewsAPI
    if news_data and 'articles' in news_data:
        for article in news_data['articles']:
            headline = article['title']
            sim = cosine_similarity(user_embedding, embedding_model.encode([headline]))[0][0]
            if sim > 0.7:
                found_match = True
                matched_sources.append("NewsAPI")
                break

    if "NYT" in matched_sources and "NewsAPI" in matched_sources:
        return f"<p style='color: green; font-size: 22px; font-weight: bold;'>✅ This news is <b>REAL</b>. Semantically matched in both NYT & NewsAPI. (Language: {detected_lang})</p>"
    elif "NYT" in matched_sources or "NewsAPI" in matched_sources:
        return f"<p style='color: yellow; font-size: 22px; font-weight: bold;'>⚠️ This news is <b>LIKELY REAL</b>. Matched in one trusted source. (Language: {detected_lang})</p>"
    else:
        return f"<p style='color: red; font-size: 22px; font-weight: bold;'>🛑 This news is <b>FAKE</b>. No semantic match found. (Language: {detected_lang})</p>"

# Streamlit App UI
def main():
    st.markdown("<h1 style='text-align: center; color: #007bff;'>🧠 FakeBuster AI (with Semantic Search)</h1>", unsafe_allow_html=True)
    st.subheader("🕵️‍♂️ Check If an Article is Fake or Real")
    user_article = st.text_area("Paste the news article (any language):", height=200)
    if st.button("Check Fake News 🧐"):
        if user_article:
            result = check_fake_news(user_article)
            st.markdown(result, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Please enter an article to analyze.")

if __name__ == "__main__":
    main()
