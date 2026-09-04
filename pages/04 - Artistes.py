import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Artistes populaires",
    page_icon="👨‍🎤",
    layout="wide"
)


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

df_spotify = pd.read_excel("data/Spotify.xlsx")


# ============================================================
# PRÉPARATION DES DONNÉES
# ============================================================

# Regroupement des informations par artiste.
# On conserve uniquement les artistes présents sur au moins
# 3 titres dans notre dataset.

artistes_analyse = (
    df_spotify
    .groupby("artist_name")
    .agg(
        nombre_titres=("track_name", "count"),
        popularite=("artist_popularity", "max"),
        followers=("artist_followers", "max")
    )
    .query("nombre_titres >= 3")
    .copy()
)


# ============================================================
# NORMALISATION AVEC NUMPY
# ============================================================

# Normalisation de la popularité entre 0 et 1

popularite_min = artistes_analyse["popularite"].min()
popularite_max = artistes_analyse["popularite"].max()

artistes_analyse["popularite_normalisee"] = (
    (artistes_analyse["popularite"] - popularite_min)
    / (popularite_max - popularite_min)
)


# Normalisation du nombre de followers entre 0 et 1

followers_min = artistes_analyse["followers"].min()
followers_max = artistes_analyse["followers"].max()

artistes_analyse["followers_normalises"] = (
    (artistes_analyse["followers"] - followers_min)
    / (followers_max - followers_min)
)


# ============================================================
# CALCUL DU SCORE COMBINÉ
# ============================================================

# Les deux critères ont le même poids :
# 50 % popularité + 50 % followers

artistes_analyse["score"] = np.mean(
    [
        artistes_analyse["popularite_normalisee"],
        artistes_analyse["followers_normalises"]
    ],
    axis=0
)


# ============================================================
# CLASSEMENT
# ============================================================

top_artistes = (
    artistes_analyse
    .sort_values("score", ascending=False)
    .head(10)
    .copy()
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

    /* Titres */
    h1, h2, h3 {
        color: #FFFFFF !important;
    }

    /* Texte */
    p, li {
        color: #E6E6E6;
    }

    /* Métriques */
    [data-testid="stMetric"] {
        background-color: #1E1E1E;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #333333;
    }

    [data-testid="stMetricLabel"] {
        color: #BDBDBD !important;
    }

    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }

    /* Section */
    .section-header {
        background: linear-gradient(
            135deg,
            #7B1FA2,
            #C2185B
        );
        padding: 12px 20px;
        border-radius: 10px;
        margin-top: 25px;
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

st.title("👨‍🎤 Artistes populaires et suivis")

st.write(
    "Quels artistes combinent une forte popularité "
    "et un grand nombre de followers ?"
)


# ============================================================
# INDICATEURS
# ============================================================

meilleur_artiste = top_artistes.index[0]
meilleur_score = top_artistes.iloc[0]["score"]

popularite_meilleur = top_artistes.iloc[0]["popularite"]
followers_meilleur = top_artistes.iloc[0]["followers"]


col1, col2, col3 = st.columns(3)


with col1:
    st.metric(
        "🏆 Artiste en tête",
        meilleur_artiste
    )


with col2:
    st.metric(
        "⭐ Popularité",
        f"{popularite_meilleur:.0f}/100"
    )


with col3:
    st.metric(
        "📈 Score combiné",
        f"{meilleur_score:.3f}"
    )


# ============================================================
# GRAPHIQUE
# ============================================================

st.markdown(
    """
    <div class="section-header">
        <div class="section-title">
            🌟 Top 10 des artistes populaires et suivis
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


fig = px.scatter(
    top_artistes,
    x="followers",
    y="popularite",
    size="score",
    color="score",
    text=top_artistes.index,
    hover_name=top_artistes.index,
    hover_data={
        "followers": ":,.0f",
        "popularite": True,
        "nombre_titres": True,
        "score": ":.3f"
    },
    log_x=True,
    color_continuous_scale=[
        "#7B1FA2",
        "#C2185B",
        "#FF4081"
    ],
    labels={
        "followers": "Nombre de followers",
        "popularite": "Popularité",
        "score": "Score combiné",
        "nombre_titres": "Nombre de titres"
    }
)


# Position des noms des artistes

fig.update_traces(
    textposition="top center",
    textfont=dict(
        color="white",
        size=12
    ),
    marker=dict(
        opacity=0.85,
        line=dict(
            width=1
        )
    )
)


# Style du graphique

fig.update_layout(
    plot_bgcolor="#181818",
    paper_bgcolor="#121212",
    font=dict(
        color="white"
    ),
    xaxis=dict(
        gridcolor="#333333",
        color="white",
        tickfont=dict(
            color="white"
        ),
        title_font=dict(
            color="white"
        )
    ),
    yaxis=dict(
        gridcolor="#333333",
        color="white",
        tickfont=dict(
            color="white"
        ),
        title_font=dict(
            color="white"
        )
    ),
    coloraxis_colorbar=dict(
        title="Score",
        tickfont=dict(
            color="white"
        ),
        title_font=dict(
            color="white"
        )
    )
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# EXPLICATION
# ============================================================

st.info(
    "💡 Le score combiné prend en compte à parts égales "
    "la popularité de l'artiste et son nombre de followers. "
    "Les artistes présents sur moins de 3 titres sont exclus."
)


# ============================================================
# CLASSEMENT
# ============================================================

st.markdown(
    """
    <div class="section-header">
        <div class="section-title">
            🏆 Classement
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


classement = top_artistes[
    [
        "nombre_titres",
        "popularite",
        "followers",
        "score"
    ]
].copy()


classement["score"] = classement["score"].round(3)


st.dataframe(
    classement,
    use_container_width=True
)


# ============================================================
# CONCLUSION
# ============================================================

st.subheader("💡 Conclusion")

st.write(
    f"Selon notre score combiné, **{meilleur_artiste}** arrive "
    f"en première position avec un score de **{meilleur_score:.3f}**."
)

st.write(
    "Ce classement permet d'identifier les artistes qui présentent "
    "le meilleur équilibre entre popularité et audience."
)