import streamlit as st
import pandas as pd
import numpy as np


# ============================================================
# CONFIGURATION DE LA PAGE
# ============================================================

st.set_page_config(
    page_title="Spotify Analysis",
    page_icon="🎵",
    layout="wide"
)


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

df_spotify = pd.read_excel("data/Spotify.xlsx")


# ============================================================
# STATISTIQUES GÉNÉRALES
# ============================================================

nombre_titres = len(df_spotify)

nombre_artistes = df_spotify["artist_name"].nunique()

popularite_moyenne = np.mean(
    df_spotify["track_popularity"].dropna()
)

duree_moyenne = np.mean(
    df_spotify["track_duration_min"].dropna()
)


# ============================================================
# STYLE VISUEL
# ============================================================

st.markdown(
    """
    <style>

    /* Fond général */
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }

    /* Texte général */
    .stApp p,
    .stApp li {
        color: #E6E6E6;
    }

    /* Titres */
    .stApp h1,
    .stApp h2,
    .stApp h3 {
        color: #FFFFFF;
    }

    /* Titre principal */
    .main-title {
        font-size: 48px;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 5px;
    }

    /* Sous-titre */
    .subtitle {
        font-size: 20px;
        color: #B3B3B3;
        margin-bottom: 30px;
    }

    /* Cartes statistiques */
    .stat-card {
        background-color: #1E1E1E;
        padding: 22px;
        border-radius: 12px;
        border: 1px solid #333333;
        text-align: center;
        min-height: 130px;
    }

    .stat-title {
        color: #B3B3B3;
        font-size: 15px;
        margin-bottom: 8px;
    }

    .stat-value {
        color: #FFFFFF;
        font-size: 30px;
        font-weight: 700;
    }

    /* Blocs d'analyse */
    .analysis-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #333333;
        min-height: 150px;
        margin-bottom: 15px;
    }

    .analysis-card h3 {
        color: #FFFFFF;
        margin-top: 0;
    }

    .analysis-card p {
        color: #D0D0D0;
    }

    /* Texte secondaire Streamlit */
    .stCaption {
        color: #AFAFAF;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# EN-TÊTE
# ============================================================

col_titre, col_logo = st.columns([4, 1])

with col_titre:
    st.markdown(
        '<div class="main-title">🎵 Spotify Analysis</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        "Exploration et analyse des données musicales Spotify"
        "</div>",
        unsafe_allow_html=True
    )

with col_logo:
    st.image(
        "images/spotify_logo.png",
        width=180
    )
# ============================================================
# PRÉSENTATION
# ============================================================

st.markdown("## 🎧 Notre projet")

st.write(
    """
    Bienvenue dans notre analyse du dataset Spotify.

    L'objectif de ce projet est d'explorer les données afin
    d'identifier les tendances et caractéristiques des titres,
    des artistes et des genres musicaux présents dans notre dataset.
    """
)


st.divider()


# ============================================================
# INDICATEURS CLÉS
# ============================================================

st.markdown("## 📊 Quelques chiffres clés")


col1, col2, col3, col4 = st.columns(4)


with col1:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-title">🎵 Titres analysés</div>
            <div class="stat-value">{nombre_titres:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-title">👨‍🎤 Artistes</div>
            <div class="stat-value">{nombre_artistes:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-title">⭐ Popularité moyenne</div>
            <div class="stat-value">{popularite_moyenne:.1f}/100</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col4:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-title">⏱️ Durée moyenne</div>
            <div class="stat-value">{duree_moyenne:.2f} min</div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


# ============================================================
# NOS ANALYSES
# ============================================================

st.markdown("## 🔎 Nos analyses")

st.write(
    "Utilisez le menu à gauche pour explorer les différentes analyses."
)


col1, col2 = st.columns(2)


with col1:

    st.markdown(
        """
        <div class="analysis-card">

        <h3>🏆 Top & Flop</h3>

        <p>
        Découvrez les titres les plus populaires et les titres
        les moins populaires de notre dataset.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="analysis-card">

        <h3>👥 Followers & popularité</h3>

        <p>
        Découvrez si le nombre de followers d'un artiste
        est lié à la popularité de ses titres.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="analysis-card">

        <h3>🎸 Genres musicaux</h3>

        <p>
        Identifiez les genres musicaux les plus représentés
        dans notre dataset.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        """
        <div class="analysis-card">

        <h3>👨‍🎤 Artistes populaires et suivis</h3>

        <p>
        Identifiez les artistes combinant une forte popularité
        et un grand nombre de followers.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="analysis-card">

        <h3>⏱️ Caractéristiques des titres</h3>

        <p>
        Analysez certaines caractéristiques des titres
        les plus populaires, notamment leur durée et leurs genres.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


# ============================================================
# SOURCE DES DONNÉES
# ============================================================

st.caption(
    "📁 Source des données : Spotify.xlsx • "
    f"{nombre_titres:,} titres analysés"
)