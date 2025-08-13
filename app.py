import streamlit as st
import pickle
import requests

# --- Utility to fetch poster from OMDb ---
def fetch_poster(movie_name, api_key="9515379d"):
    # Properly format the URL with the movie title and safe encoding
    url = f"http://www.omdbapi.com/?apikey={api_key}&t={requests.utils.quote(movie_name)}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        st.error(f"Error contacting OMDb for '{movie_name}': {e}")
        return None

    # OMDb returns Poster = 'N/A' when not available
    poster_path = data.get("Poster")
    if poster_path and poster_path != "N/A":
        return poster_path
    return None

# --- Recommendation logic ---
def recommend(movie, top_n=5):
    # Find index of the selected movie in the original DataFrame
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error(f"Movie '{movie}' not found in dataset.")
        return []

    # Get similarity scores sorted in descending order and skip the first match (itself)
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommendations = []
    for i, _score in distances[1: top_n+1]:
        title = movies.iloc[i].title
        # If you need to use an 'id' column for other APIs, you can read it:
        # movie_id = movies.iloc[i].id   # not used for OMDb which searches by title
        poster = fetch_poster(title)
        recommendations.append((title, poster))

    return recommendations

# --- Load data (ensure these files exist in the working directory) ---
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Titles for selectbox
movie_titles = movies['title'].values

# --- Streamlit UI ---
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title('Movie Recommendation System')

selected_movie_name = st.selectbox('Choose the movie', movie_titles)

if st.button('Recommend'):
    with st.spinner("Finding recommendations..."):
        recs = recommend(selected_movie_name, top_n=5)

    if not recs:
        st.info("No recommendations found.")
    else:
        # Display recommendations in columns
        cols = st.columns(len(recs))
        for col, (title, poster_url) in zip(cols, recs):
            with col:
                if poster_url:
                    st.image(poster_url)
                else:
                    st.write("No poster available")
                st.markdown(f"**{title}**")
