# Film Taste Analyzer

Analyzes my Letterboxd watch history with film data from TMDb to find out what my film taste actually is.

**Status:** in progress

## Planned
- Load my Letterboxd export with pandas
- Add film details (director, genre, country, year) via the TMDb API
- Stats and charts about my taste
- Streamlit web page
- AI-written taste profile using a local LLM

## Setup
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Create a `.env` file with `TMDB_API_KEY=your_key`.
