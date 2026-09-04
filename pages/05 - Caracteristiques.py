import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Caractéristiques des titres",
    page_icon="⏱️",
    layout="wide"
)


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

df_spotify = pd.read_excel("data/Spotify.xlsx")


# ============================================================
# PRÉPARATION DES DONNÉES
# ============================================================

# Top 10 des titres les plus populaires
top_titres = (
    df_spotify
    .sort_values("track_popularity", ascending=False)
    .head(10)
    .copy()
)

# Durées moyennes
duree_moyenne_dataset = np.mean(
    df_spotify["track_duration_min"]
)

duree_moyenne_top10 = np.mean(
    top_titres["track_duration_min"]
)

difference = duree_moyenne_top10 - duree_moyenne_dataset


# Catégorisation des durées avec NumPy
top_titres["categorie_duree"] = np.select(
    [
        top_titres["track_duration_min"] < 3,
        top_titres["track_duration_min"] < 4
    ],
    [
        "Court",
        "Moyen"
    ],
    default="Long"
)


# Genres présents dans le Top 10
genres_top10 = (
    top_titres["artist_genres"]
    .dropna()
    .str.split(",")
    .explode()
    .str.strip()
    .value_counts()
)


# ============================================================
# STYLE GLOBAL
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0F1117;
        color: white;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* TITRE PRINCIPAL */

    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #AEB6C7;
        margin-bottom: 30px;
    }

    /* TITRES DE SECTIONS */

    .section-title {
        font-size: 25px;
        font-weight: 700;
        color: #FFFFFF;
        margin-top: 30px;
        margin-bottom: 15px;
        padding-left: 12px;
        border-left: 5px solid #00B8D9;
    }

    /* CARTES KPI */

    [data-testid="stMetric"] {
        background: linear-gradient(
            135deg,
            #151B29,
            #1B2030
        );

        border: 1px solid #293247;
        border-radius: 14px;
        padding: 18px;
    }

    [data-testid="stMetricLabel"] {
        color: #AEB6C7 !important;
    }

    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }

    /* BLOC INFORMATION */

    .info-box {
        background: linear-gradient(
            135deg,
            #151B29,
            #1B2030
        );

        border: 1px solid #293247;
        border-radius: 14px;
        padding: 20px 22px;
        margin-top: 20px;
        color: #DDE3F0;
        line-height: 1.6;
    }

    /* CONCLUSION */

    .conclusion-box {
        background: linear-gradient(
            135deg,
            #111B24,
            #18202D
        );

        border: 1px solid #00B8D9;
        border-radius: 14px;
        padding: 22px;
        margin-top: 20px;
        color: #FFFFFF;
        line-height: 1.6;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITRE
# ============================================================

st.markdown(
    '<div class="main-title">⏱️ Caractéristiques des titres</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    "Analyse de la durée et des genres des titres les plus populaires"
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# INDICATEURS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Durée moyenne du dataset",
        f"{duree_moyenne_dataset:.2f} min"
    )

with col2:
    st.metric(
        "Durée moyenne du Top 10",
        f"{duree_moyenne_top10:.2f} min"
    )

with col3:
    st.metric(
        "Écart",
        f"{abs(difference):.2f} min"
    )


# ============================================================
# GRAPHIQUE 1 : DURÉE DES TITRES
# ============================================================

st.markdown(
    '<div class="section-title">'
    "🎵 Durée des 10 titres les plus populaires"
    "</div>",
    unsafe_allow_html=True
)

duree_graphique = (
    top_titres[
        [
            "track_name",
            "track_duration_min",
            "track_popularity"
        ]
    ]
    .sort_values("track_duration_min")
)

fig_duree = px.bar(
    duree_graphique,
    x="track_duration_min",
    y="track_name",
    orientation="h",
    text="track_duration_min",
    color="track_duration_min",

    color_continuous_scale=[
        "#00B8D9",
        "#00C9A7",
        "#7C4DFF"
    ],

    labels={
        "track_duration_min": "Durée (minutes)",
        "track_name": "Titre"
    },

    hover_data={
        "track_duration_min": ":.2f",
        "track_popularity": True
    }
)

fig_duree.update_traces(
    texttemplate="%{text:.2f} min",
    textposition="outside",
    textfont=dict(color="white"),
    marker_line_width=0
)

fig_duree.update_layout(
    height=520,

    paper_bgcolor="#0F1117",
    plot_bgcolor="#151922",

    font=dict(color="white"),

    coloraxis_showscale=False,

    margin=dict(
        l=10,
        r=80,
        t=20,
        b=20
    ),

    xaxis=dict(
        gridcolor="#293247",
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
    fig_duree,
    use_container_width=True
)


# ============================================================
# GRAPHIQUE 2 : GENRES
# ============================================================

st.markdown(
    '<div class="section-title">'
    "🎸 Genres présents dans le Top 10"
    "</div>",
    unsafe_allow_html=True
)

genres_graphique = (
    genres_top10
    .head(10)
    .sort_values()
    .reset_index()
)

genres_graphique.columns = [
    "Genre",
    "Occurrences"
]

fig_genres = px.bar(
    genres_graphique,
    x="Occurrences",
    y="Genre",
    orientation="h",
    text="Occurrences",
    color="Occurrences",

    color_continuous_scale=[
        "#7C4DFF",
        "#6C63FF",
        "#00B8D9",
        "#00C9A7"
    ],

    labels={
        "Occurrences": "Nombre d'occurrences",
        "Genre": "Genre"
    }
)

fig_genres.update_traces(
    textposition="outside",
    textfont=dict(color="white"),
    marker_line_width=0
)

fig_genres.update_layout(
    height=480,

    paper_bgcolor="#0F1117",
    plot_bgcolor="#151922",

    font=dict(color="white"),

    coloraxis_showscale=False,

    margin=dict(
        l=10,
        r=60,
        t=20,
        b=20
    ),

    xaxis=dict(
        gridcolor="#293247",
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
    fig_genres,
    use_container_width=True
)


# ============================================================
# GRAPHIQUE 3 : CATÉGORIES DE DURÉE
# ============================================================

st.markdown(
    '<div class="section-title">'
    "📊 Répartition des durées"
    "</div>",
    unsafe_allow_html=True
)

repartition_duree = (
    top_titres["categorie_duree"]
    .value_counts()
    .reset_index()
)

repartition_duree.columns = [
    "Catégorie",
    "Nombre"
]

fig_categories = px.pie(
    repartition_duree,

    names="Catégorie",
    values="Nombre",

    hole=0.50,

    color="Catégorie",

    color_discrete_map={
        "Court": "#00C9A7",
        "Moyen": "#00B8D9",
        "Long": "#7C4DFF"
    }
)

fig_categories.update_traces(
    textinfo="label+percent",

    textfont=dict(
        color="white",
        size=15
    ),

    hovertemplate=(
        "<b>%{label}</b>"
        "<br>%{value} titre(s)"
        "<extra></extra>"
    )
)

fig_categories.update_layout(
    height=420,

    paper_bgcolor="#0F1117",
    plot_bgcolor="#0F1117",

    font=dict(color="white"),

    legend=dict(
        font=dict(color="white")
    ),

    margin=dict(
        l=20,
        r=20,
        t=20,
        b=20
    )
)

st.plotly_chart(
    fig_categories,
    use_container_width=True
)


# ============================================================
# INTERPRÉTATION
# ============================================================

st.markdown(
    '<div class="section-title">💡 Interprétation</div>',
    unsafe_allow_html=True
)

texte_interpretation = f"""
<div class="info-box">

<b>Durée :</b> les 10 titres les plus populaires ont une durée moyenne
de <b>{duree_moyenne_top10:.2f} minutes</b>, contre
<b>{duree_moyenne_dataset:.2f} minutes</b> pour l'ensemble du dataset.

L'écart est donc d'environ
<b>{abs(difference):.2f} minute</b>.

<br><br>

<b>Genres :</b> plusieurs genres apparaissent dans les titres du Top 10.
Les associations les plus représentées sont notamment
<b>Country, Pop, Indie et Folk</b>.

</div>
"""

st.markdown(
    texte_interpretation,
    unsafe_allow_html=True
)


# ============================================================
# CONCLUSION
# ============================================================

st.markdown(
    """
    <div class="conclusion-box">

    <b>⚠️ À retenir :</b> la différence de durée reste faible.
    On ne peut donc pas conclure qu'une durée précise rend un titre
    plus populaire à partir de seulement 10 titres.

    </div>
    """,
    unsafe_allow_html=True
)