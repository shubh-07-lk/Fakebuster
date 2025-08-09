import os
import time
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
from langdetect import detect
from deep_translator import GoogleTranslator
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

# Load environment variables (optional .env support)
load_dotenv()

# -- CONFIG: You can replace these with environment variables or edit config.py --
from config import NYT_API_KEY, NEWS_API_KEY

NYT_ARTICLE_SEARCH_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
NEWSAPI_TOP_HEADLINES_URL = "https://newsapi.org/v2/top-headlines"

app = FastAPI(title="FakeBuster AI - Backend")

# Allow CORS for frontend during development; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load embedding model once (global)
print("Loading sentence-transformers model (this may take a while the first time)...")
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded.")


# Request/response models
class CheckRequest(BaseModel):
    article: str
    top_k: Optional[int] = 10  # how many headlines to return


class MatchItem(BaseModel):
    source: str
    headline: str
    url: Optional[str] = None
    score: float


class CheckResponse(BaseModel):
    verdict: str  # REAL / LIKELY REAL / FAKE
    confidence: float  # best similarity score (0-1)
    detected_language: str
    matches: List[MatchItem] = []


# Helpers
def translate_to_english(text: str):
    try:
        detected = detect(text)
    except Exception:
        detected = "unknown"
    if detected != "en" and detected != "unknown":
        try:
            translated = GoogleTranslator(source=detected, target="en").translate(text)
            return translated, detected
        except Exception:
            return text, detected
    return text, detected


def fetch_nyt_articles(query: str, page: int = 0):
    params = {"q": query, "api-key": NYT_API_KEY, "sort": "newest", "page": page}
    resp = requests.get(NYT_ARTICLE_SEARCH_URL, params=params, timeout=10)
    if resp.status_code == 200:
        return resp.json().get("response", {}).get("docs", [])
    else:
        return []


def fetch_newsapi_headlines(country: str = "in"):
    params = {"country": country, "apiKey": NEWS_API_KEY}
    resp = requests.get(NEWSAPI_TOP_HEADLINES_URL, params=params, timeout=10)
    if resp.status_code == 200:
        return resp.json().get("articles", [])
    else:
        return []


def embed_texts(texts: List[str]):
    return EMBEDDING_MODEL.encode(texts, convert_to_numpy=True, show_progress_bar=False)


@app.post("/check-fake-news", response_model=CheckResponse)
def check_fake_news(req: CheckRequest):
    if not req.article or len(req.article.strip()) == 0:
        raise HTTPException(status_code=400, detail="Article text is required.")

    translated, detected_lang = translate_to_english(req.article)
    text_for_embed = translated[:2000]
    user_embedding = embed_texts([text_for_embed])[0].reshape(1, -1)

    matches = []

    # NYT
    try:
        nyt_docs = fetch_nyt_articles(translated)
    except Exception:
        nyt_docs = []

    nyt_headlines = []
    nyt_meta = []
    for doc in nyt_docs:
        headline = doc.get("headline", {}).get("main") or doc.get("abstract") or ""
        if headline:
            nyt_headlines.append(headline)
            nyt_meta.append({"url": doc.get("web_url")})

    if nyt_headlines:
        nyt_embeddings = embed_texts(nyt_headlines)
        sims = cosine_similarity(user_embedding, nyt_embeddings)[0]
        for idx, score in enumerate(sims):
            if score >= 0.60:
                matches.append(MatchItem(
                    source="NYT",
                    headline=nyt_headlines[idx],
                    url=nyt_meta[idx].get("url"),
                    score=float(score)
                ))

    # NewsAPI
    try:
        newsapi_articles = fetch_newsapi_headlines()
    except Exception:
        newsapi_articles = []

    news_headlines = []
    news_meta = []
    for item in newsapi_articles:
        title = item.get("title") or item.get("description") or ""
        if title:
            news_headlines.append(title)
            news_meta.append({"url": item.get("url"), "source": item.get("source", {}).get("name")})

    if news_headlines:
        news_embeddings = embed_texts(news_headlines)
        sims2 = cosine_similarity(user_embedding, news_embeddings)[0]
        for idx, score in enumerate(sims2):
            if score >= 0.60:
                matches.append(MatchItem(
                    source=news_meta[idx].get("source", "NewsAPI"),
                    headline=news_headlines[idx],
                    url=news_meta[idx].get("url"),
                    score=float(score)
                ))

    matches_sorted = sorted(matches, key=lambda x: x.score, reverse=True)[:req.top_k]
    sources = set([m.source for m in matches_sorted])
    best_score = matches_sorted[0].score if matches_sorted else 0.0

    if "NYT" in sources and any(s.source != "NYT" for s in matches_sorted):
        verdict = "REAL"
    elif "NYT" in sources or len(matches_sorted) > 0:
        verdict = "LIKELY REAL"
    else:
        verdict = "FAKE"

    return CheckResponse(
        verdict=verdict,
        confidence=round(float(best_score), 3),
        detected_language=detected_lang,
        matches=matches_sorted
    )


@app.get("/related-news")
def related_news(query: str):
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter required.")
    translated, detected = translate_to_english(query)
    docs = fetch_nyt_articles(translated)
    results = []
    for doc in docs[:10]:
        results.append({
            "headline": doc.get("headline", {}).get("main"),
            "snippet": doc.get("snippet"),
            "url": doc.get("web_url"),
            "pub_date": doc.get("pub_date")
        })
    return {"query_translated": translated, "detected_language": detected, "results": results}
