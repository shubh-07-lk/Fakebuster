# FakeBuster AI

FakeBuster AI is a multilingual fake news detection tool that uses semantic search to find and verify news articles across trusted sources like the New York Times API and NewsAPI. The system uses sentence embeddings and cosine similarity to identify related news articles and determine credibility.

## 🚀 Features
- Multilingual support (auto-translate to English)
- Semantic search using Sentence-Transformers
- Integration with NYT API and NewsAPI
- User-friendly frontend with modern design
- Backend API for processing and validation

## 🛠️ Technologies Used
- **Frontend:** React.js
- **Backend:** FastAPI (Python)
- **ML/NLP:** Sentence-Transformers (`all-MiniLM-L6-v2`), Scikit-learn
- **APIs:** NYT API, NewsAPI
- **Other:** Google Translator API, Language Detection

## 📦 Installation

### Clone the repository
```bash
git clone https://github.com/yourusername/FakeBuster-AI.git
cd FakeBuster-AI
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## ⚙️ Configuration
Create a `.env` file in the `backend` folder with:
```
NYT_API_KEY=your_new_york_times_api_key
NEWS_API_KEY=your_newsapi_key
```

## 📌 Usage
- Enter a news article in any language to check its authenticity.
- The system fetches related news from multiple trusted sources and performs semantic similarity checks.
- Displays whether the news is REAL, LIKELY REAL, or FAKE.

## 📄 License
This project is licensed under the MIT License.
