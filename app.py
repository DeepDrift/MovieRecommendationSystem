import pickle
import streamlit as st
import requests
import json
import time

# --- Custom CSS for background, cards, fonts, headings, and button ---
def local_css(css_text):
    st.markdown(f"<style>{css_text}</style>", unsafe_allow_html=True)

custom_css = '''
body, .stApp {
    background: #000000 !important;
    color: #fff;
}

h1, .stHeader, .stTextInput, .stSelectbox, .stButton {
    font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
}

/* Headings color */
h1, h2, h3, h4, h5, h6 {
    color: #f5c518 !important;
    text-shadow: 1px 1px 8px #232526;
}

/* Recommendation card headings */
.recommend-card h4 {
    color: #f5c518 !important;
    font-weight: 700;
    margin-top: 0.5em;
    text-shadow: 1px 1px 8px #232526;
}

.stButton>button {
    background: linear-gradient(90deg, #1976d2 60%, #f5c518 100%);
    color: #fff;
    border-radius: 8px;
    font-size: 18px;
    padding: 0.5em 2em;
    margin-top: 1em;
    font-weight: 700;
    border: none;
    box-shadow: 0 2px 8px rgba(25,118,210,0.15);
    transition: background 0.3s, box-shadow 0.3s;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #115293 60%, #c9a10a 100%);
    color: #fff;
    box-shadow: 0 4px 16px rgba(245,197,24,0.25);
}

.advanced-search-label {
    font-size: 1.5em;
    color: #f5c518;
    font-weight: 800;
    margin-bottom: 1em;
    letter-spacing: 1px;
    display: flex;
    align-items: center;
    gap: 0.5em;
    text-shadow: 2px 2px 12px #232526;
    justify-content: center;
}
.stSelectbox>div>div {
    background: #232526;
    color: #fff;
    border-radius: 16px !important;
    border: 2px solid #1976d2;
    box-shadow: 0 2px 12px rgba(25,118,210,0.10);
    font-size: 1.1em;
    font-weight: 500;
    transition: border 0.2s, box-shadow 0.2s;
}
.stSelectbox>div>div:focus-within, .stSelectbox>div>div:hover {
    border: 2px solid #f5c518;
    box-shadow: 0 4px 24px rgba(245,197,24,0.15);
}

.recommend-card {
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    padding: 1em;
    margin: 0.5em 0;
    text-align: center;
    transition: transform 0.2s;
}
.recommend-card:hover {
    transform: scale(1.04);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}

/* Make movie images larger using st.image only */
.recommend-card .stImage img {
    width: 100% !important;
    max-width: 270px;
    max-height: 420px;
    min-height: 320px;
    object-fit: cover;
    margin-left: auto;
    margin-right: auto;
    border-radius: 12px;
    box-shadow: 0 2px 16px rgba(25,118,210,0.10);
}
'''

local_css(custom_css)

# --- Load data ---
movies = pickle.load(open('artifacts/movie_list.pkl','rb'))
similarity = pickle.load(open('artifacts/similarity.pkl','rb'))
movie_list = movies['title'].values

# Prepare movie list with a search icon placeholder
movie_list_with_placeholder = ["🔍 Search for a movie..."] + list(movie_list)

# --- Main headline and attractive subtitle above the search bar ---
st.markdown("""
    <div style="text-align:center; margin-bottom:0.5em;">
        <span style="font-size:3.5em; font-weight:900; background: linear-gradient(90deg, #1976d2 30%, #f5c518 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display:inline-block; letter-spacing:2px; text-shadow: 2px 2px 8px rgba(0,0,0,0.25);">
            🎬 Movie Recommender
        </span>
    </div>
    <div style="text-align:center; margin-bottom:2em;">
        <span style="
            font-size:2em;
            font-weight:800;
            background: linear-gradient(90deg, #f5c518 40%, #fffbe7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline-block;
            letter-spacing: 1px;
            white-space: nowrap;
        ">
            Discover films that match your taste, instantly.
        </span>
    </div>
""", unsafe_allow_html=True)

selected_movie = st.selectbox(
    "",
    movie_list_with_placeholder,
    key="movie_select",
)

# Only show recommendations if a real movie is selected
if selected_movie != "🔍 Search for a movie...":
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Recommendation logic ---
    def fetch_poster(movie_id):
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url).json()
        poster_path = data.get('poster_path', None)
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"

    def recommend(movie):
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended_movie_names = []
        recommended_movie_posters = []
        for i in distances[1:9]:  # Get top 8 (excluding the selected movie itself)
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movie_posters.append(fetch_poster(movie_id))
            recommended_movie_names.append(movies.iloc[i[0]].title)
        return recommended_movie_names, recommended_movie_posters

    # --- Show recommendations with spinner and cards ---
    if st.button('Show Recommendations'):
        with st.spinner('Finding the best movies for you...'):
            time.sleep(1)  # Simulate loading
            recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
        st.markdown("""
            <div style='text-align:center; color:#f5c518; font-size:2em; font-weight:700; margin-top:2em; margin-bottom:1em; letter-spacing:1px; text-shadow: 1px 1px 8px #232526;'>
                Top 8 Recommendations
            </div>
        """, unsafe_allow_html=True)
        # First row (first 4 movies)
        cols1 = st.columns(4)
        for idx, col in enumerate(cols1):
            with col:
                st.markdown(f"<div class='recommend-card'>", unsafe_allow_html=True)
                st.image(recommended_movie_posters[idx], use_container_width=True)
                st.markdown(f"<h4 style='color:#f5c518; margin-top:0.5em;'>{recommended_movie_names[idx]}</h4>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        # Second row (next 4 movies)
        cols2 = st.columns(4)
        for idx, col in enumerate(cols2):
            with col:
                st.markdown(f"<div class='recommend-card'>", unsafe_allow_html=True)
                st.image(recommended_movie_posters[idx+4], use_container_width=True)
                st.markdown(f"<h4 style='color:#f5c518; margin-top:0.5em;'>{recommended_movie_names[idx+4]}</h4>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
