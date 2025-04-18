import streamlit as st
import requests
from deep_translator import GoogleTranslator
from langdetect import detect
import time

# API Keys
NYT_API_KEY = 'YG9qtrG1LvBhf1qZj9wTOnnoeA98EgUm'
NEWS_API_KEY = 'ecca68e4fd89433bbf77ce4f451fa319'

# API Endpoints
NYT_ARTICLE_SEARCH_URL = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'
NEWSAPI_TOP_HEADLINES_URL = 'https://newsapi.org/v2/top-headlines'

# Custom CSS for Dark Mode Styling
st.markdown("""
    <style>
        .main {
            background: linear-gradient(270deg, #121212, #1e1e1e);
            background-size: 400% 400%;
            padding: 20px;
            border-radius: 10px;
            color: white !important;
        }
        .stTextArea label, .stTextInput label {
            color: white !important;
            font-size: 16px;
            font-weight: bold;
        }
        .stTextArea textarea, .stTextInput input {
            background-color: #333;
            color: white;
            border-radius: 10px;
            padding: 10px;
            border: 1px solid #555;
        }
        .stButton>button {
            background-color: #007bff;
            color: white;
            font-size: 18px;
            padding: 10px 20px;
            border-radius: 5px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #0056b3;
            transform: scale(1.05);
        }
        .footer {
            text-align: center;
            padding: 10px;
            margin-top: 20px;
            font-size: 14px;
            color: #bbb;
        }
    </style>
""", unsafe_allow_html=True)

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
    params = {
        'country': 'in',
        'apiKey': NEWS_API_KEY
    }
    
    response = requests.get(NEWSAPI_TOP_HEADLINES_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"⚠️ NewsAPI Failed: {response.status_code}")
        return None

# Function to check if an article is fake by comparing with NYT & NewsAPI
def check_fake_news(article_text):
    translated_text, detected_lang = translate_to_english(article_text[:50])
    
    # Fetch news from NYT & NewsAPI
    nyt_data, _ = fetch_nyt_articles(translated_text)
    news_data = fetch_top_headlines()
    
    with st.spinner("Analyzing article... 🧐"):
        time.sleep(2)

    # Check in NYT
    found_in_nyt = False
    if nyt_data and 'response' in nyt_data and 'docs' in nyt_data['response']:
        articles = nyt_data['response']['docs']
        if articles:
            found_in_nyt = True

    # Check in NewsAPI
    found_in_newsapi = False
    if news_data and 'articles' in news_data:
        headlines = [article['title'].lower() for article in news_data['articles']]
        if any(translated_text.lower() in headline for headline in headlines):
            found_in_newsapi = True

    # Final verdict
    if found_in_nyt and found_in_newsapi:
        return f"<p style='color: green; font-size: 22px; font-weight: bold;'>✅ This news is <b>REAL</b>. Found in both NYT & NewsAPI. (Detected Language: {detected_lang})</p>"
    elif found_in_nyt:
        return f"<p style='color: yellow; font-size: 22px; font-weight: bold;'>⚠️ This news is <b>LIKELY REAL</b>. Found in NYT but not in NewsAPI. (Detected Language: {detected_lang})</p>"
    elif found_in_newsapi:
        return f"<p style='color: yellow; font-size: 22px; font-weight: bold;'>⚠️ This news is <b>LIKELY REAL</b>. Found in NewsAPI but not in NYT. (Detected Language: {detected_lang})</p>"
    else:
        return f"<p style='color: red; font-size: 22px; font-weight: bold;'>🛑 This news is <b>FAKE</b>. No matching articles found in NYT or NewsAPI. (Detected Language: {detected_lang})</p>"

# Streamlit App with Sidebar Input Selection
def main():
    # Sidebar for Input Type Selection
    st.sidebar.title("🌐 Choose Input Type")
    input_type = st.sidebar.radio(
        "Select an option:",
        ("🔍 Search for Related News", "🕵️‍♂️ Check Fake News")
    )

    # Main Content
    st.markdown("<h1 style='text-align: center; color: #007bff;'>🌍 FakeBuster (Multilingual Fake News Detector)</h1>", unsafe_allow_html=True)
    st.markdown("<div class='main'>", unsafe_allow_html=True)

    if input_type == "🔍 Search for Related News":
        # Search for related news
        st.subheader("🔍 Search for Related News")
        query = st.text_input("Enter a search term (any language):")

        if st.button("Search 🔎"):
            if query:
                st.write("Translating and searching for:", query)
                nyt_data, detected_lang = fetch_nyt_articles(query)

                if nyt_data and 'response' in nyt_data:
                    articles = nyt_data['response']['docs']
                    if articles:
                        st.subheader(f"Results (Language: {detected_lang} → Translated to English)")
                        for article in articles:
                            st.write(f"**{article['headline']['main']}**")
                            st.write(f"[Read more]({article['web_url']})")
                            st.write("---")
                    else:
                        st.warning("⚠️ No articles found in NYT.")
                else:
                    st.error("❌ Failed to fetch articles from NYT.")
            else:
                st.warning("⚠️ Please enter a search term.")

    elif input_type == "🕵️‍♂️ Check Fake News":
        # Check if an article is fake or real
        st.subheader("🕵️‍♂️ Check If an Article is Fake or Real")
        user_article = st.text_area("Paste the news article (any language):", height=200)

        if st.button("Check Fake News 🧐"):
            if user_article:
                result = check_fake_news(user_article)
                st.markdown(result, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Please enter an article to analyze.")

    st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("""
        <div class='footer'>
            <p>Developed with ❤️ by [Shubh] | Powered by NYT API & NewsAPI</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
