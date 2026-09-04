import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Top & Flop Spotify",
    page_icon="🏆",
    layout="wide"
)


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

df_spotify = pd.read_excel("data/Spotify.xlsx")


# ============================================================
# STATISTIQUES
# ============================================================

popularite = df_spotify["track_popularity"].dropna()

moyenne_popularite = np.mean(popularite)
mediane_popularite = np.median(popularite)
ecart_type_popularite = np.std(popularite)


# ============================================================
# STYLE VISUEL
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }

    h1, h2, h3 {
        color: #FFFFFF !important;
    }

    p, li {
        color: #E6E6E6;
    }

    .stat-card {
        padding: 20px;
        border-radius: 14px;
        text-align: center;
        min-height: 120px;
        margin-bottom: 15px;
    }

    .stat-title {
        font-size: 15px;
        margin-bottom: 8px;
        color: #E0E0E0;
    }

    .stat-value {
        font-size: 30px;
        font-weight: bold;
        color: #FFFFFF;
    }

    .green-card {
        background: linear-gradient(
            135deg,
            #1DB954,
            #148A3B
        );
    }

    .blue-card {
        background: linear-gradient(
            135deg,
            #2196F3,
            #1565C0
        );
    }

    .purple-card {
        background: linear-gradient(
            135deg,
            #9C27B0,
            #6A1B9A
        );
    }

    .top-header {
        background-color: #1DB954;
        padding: 12px 20px;
        border-radius: 10px;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    .flop-header {
        background-color: #E53935;
        padding: 12px 20px;
        border-radius: 10px;
        margin-top: 30px;
        margin-bottom: 15px;
    }

    .section-title {
        color: #FFFFFF;
        font-size: 22px;
        font-weight: bold;
        margin: 0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITRE
# ============================================================

st.title("🏆 Top & Flop Spotify")

st.write(
    "Découvrez les titres les plus et les moins populaires "
    "de notre dataset."
)


# ============================================================
# STATISTIQUES CLÉS
# ============================================================

st.subheader("📊 Statistiques de popularité")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="stat-card green-card">
            <div class="stat-title">
                ⭐ Popularité moyenne
            </div>
            <div class="stat-value">
                {moyenne_popularite:.2f}/100
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="stat-card blue-card">
            <div class="stat-title">
                📊 Popularité médiane
            </div>
            <div class="stat-value">
                {mediane_popularite:.2f}/100
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="stat-card purple-card">
            <div class="stat-title">
                📐 Écart-type
            </div>
            <div class="stat-value">
                {ecart_type_popularite:.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TOP 10
# ============================================================

st.markdown(
    """
    <div class="top-header">
        <div class="section-title">
            🟢 Top 10 des titres les plus populaires
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


top_titres = (
    df_spotify
    .sort_values(
        "track_popularity",
        ascending=False
    )
    .head(10)
)


fig_top = px.bar(
    top_titres.sort_values("track_popularity"),
    x="track_popularity",
    y="track_name",
    orientation="h",
    title="",
    labels={
        "track_popularity": "Popularité",
        "track_name": "Titre"
    },
    text="track_popularity"
)


fig_top.update_traces(
    marker_color="#1DB954",
    textposition="outside",
    textfont=dict(
        color="white"
    )
)


fig_top.update_layout(
    plot_bgcolor="#181818",
    paper_bgcolor="#121212",
    font=dict(
        color="white"
    ),
    xaxis=dict(
        gridcolor="#333333",
        color="white",
        tickfont=dict(color="white"),
        title_font=dict(color="white")
    ),
    yaxis=dict(
        color="white",
        tickfont=dict(color="white"),
        title_font=dict(color="white")
    )
)


st.plotly_chart(
    fig_top,
    use_container_width=True
)


# ============================================================
# INFORMATIONS TOP 10
# ============================================================

st.subheader("🎵 Informations sur les titres")

st.dataframe(
    top_titres[
        [
            "track_name",
            "artist_name",
            "album_name",
            "artist_genres",
            "track_duration_min",
            "track_popularity"
        ]
    ],
    use_container_width=True
)


# ============================================================
# FLOP 10
# ============================================================

st.markdown(
    """
    <div class="flop-header">
        <div class="section-title">
            🔴 Flop 10 des titres les moins populaires
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


flop_titres = (
    df_spotify
    .sort_values(
        "track_popularity",
        ascending=True
    )
    .head(10)
)


fig_flop = px.bar(
    flop_titres.sort_values(
        "track_popularity",
        ascending=False
    ),
    x="track_popularity",
    y="track_name",
    orientation="h",
    title="",
    labels={
        "track_popularity": "Popularité",
        "track_name": "Titre"
    },
    text="track_popularity"
)


fig_flop.update_traces(
    marker_color="#E53935",
    textposition="outside",
    textfont=dict(
        color="white"
    )
)


fig_flop.update_layout(
    plot_bgcolor="#181818",
    paper_bgcolor="#121212",
    font=dict(
        color="white"
    ),
    xaxis=dict(
        range=[0, 1],
        gridcolor="#333333",
        color="white",
        tickfont=dict(color="white"),
        title_font=dict(color="white")
    ),
    yaxis=dict(
        color="white",
        tickfont=dict(color="white"),
        title_font=dict(color="white")
    )
)


st.plotly_chart(
    fig_flop,
    use_container_width=True
)


# ============================================================
# CONCLUSION
# ============================================================

st.subheader("💡 Conclusion")

st.write(
    f"La popularité moyenne des titres du dataset est de "
    f"**{moyenne_popularite:.2f}/100**, tandis que la médiane est de "
    f"**{mediane_popularite:.2f}/100**."
)

st.write(
    f"L'écart-type est de **{ecart_type_popularite:.2f}**, "
    "ce qui montre une dispersion importante des niveaux de "
    "popularité entre les titres."
)