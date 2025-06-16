# 🧠 FakeBuster AI – Multilingual Fake News Detection with Semantic Search

FakeBuster is an intelligent Streamlit-based web app that helps users check whether a news article is **real** or **fake** using **semantic search**. It fetches trusted articles from **The New York Times** and **NewsAPI**, supports **multiple languages**, and uses **AI-based similarity** instead of keyword matching.

---

## ✨ Features

- 🔍 Multilingual input support (auto-translates to English)
- 🧠 Semantic search with Sentence Transformers (MiniLM)
- ✅ Compares input with NYT & NewsAPI to detect fake news
- 💡 Clear visual feedback (REAL / LIKELY REAL / FAKE)
- 🎨 Dark-themed, responsive Streamlit interface

---

## 🗂 Project Structure

```
FakeBuster-AI/
├── finalapp.py              # Basic keyword matching version
├── finalapp_semantic.py     # AI-powered semantic search version (recommended)
├── LICENSE
├── README.md
├── requirements.txt
└── assets/                  # Optional image folder
    └── preview.png
```

---

## 🖥️ How to Run the App

### 1. Clone the repository
```bash
git clone https://github.com/your-username/FakeBuster-AI.git
cd FakeBuster-AI
```

### 2. Install required libraries
```bash
pip install -r requirements.txt
```

### 3. Add your API keys  
Open `finalapp_semantic.py` and replace:

```python
NYT_API_KEY = 'your_nyt_api_key'
NEWS_API_KEY = 'your_newsapi_key'
```

Get your keys from:  
🔗 https://developer.nytimes.com/  
🔗 https://newsapi.org/

### 4. Run the app
```bash
streamlit run finalapp_semantic.py
```

---

## 🧠 Semantic Search Powered By:
- `sentence-transformers` – for computing embeddings
- `all-MiniLM-L6-v2` – lightweight & effective semantic model

---

## 📸 UI Preview

> *(Add this to the README once your screenshot is saved in `assets/`)*

```
![App Screenshot](assets/preview.png)
```

---

## 🔐 License
This project is licensed under the MIT License – see [LICENSE](LICENSE) for details.

---

## 👨‍💻 Developed by
**Shubham Kalashetty**  
B.Tech CSE (AI & ML) | Alliance University  
[LinkedIn](https://linkedin.com/in/shubham-kalashetty-b02941272) • [GitHub](https://github.com/shubh-07-lk)