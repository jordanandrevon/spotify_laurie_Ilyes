import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Genres musicaux",
    page_icon="🎸",
    layout="wide"
)


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

df_spotify = pd.read_excel("data/Spotify.xlsx")


# ============================================================
# PRÉPARATION DES GENRES
# ============================================================

# Un artiste peut être associé à plusieurs genres.
# On sépare donc les différents genres présents dans chaque ligne.

genres = (
    df_spotify["artist_genres"]
    .dropna()
    .str.split(",")
    .explode()
    .str.strip()
)


# Comptage des occurrences
top_genres = genres.value_counts().head(10)


# ============================================================
# CALCULS AVEC NUMPY
# ============================================================

# Nombre total d'occurrences des 10 genres principaux
total_top_genres = np.sum(top_genres.values)


# Calcul du pourcentage de chaque genre
pourcentages = (
    top_genres.values / total_top_genres
) * 100


# Création du tableau d'analyse
genres_analyse = pd.DataFrame({
    "Genre": top_genres.index,
    "Occurrences": top_genres.values,
    "Pourcentage": np.round(pourcentages, 2)
})


# ============================================================
# INFORMATIONS PRINCIPALES
# ============================================================

genre_principal = genres_analyse.iloc[0]["Genre"]
nombre_principal = genres_analyse.iloc[0]["Occurrences"]
pourcentage_principal = genres_analyse.iloc[0]["Pourcentage"]


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

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITRE
# ============================================================

st.title("🎸 Genres musicaux")

st.write(
    "Cette analyse permet d'identifier les genres musicaux "
    "les plus représentés dans notre dataset."
)


# ============================================================
# INDICATEURS
# ============================================================

st.subheader("📊 En quelques chiffres")


col1, col2 = st.columns(2)


with col1:
    st.metric(
        "🎵 Genre le plus représenté",
        genre_principal
    )


with col2:
    st.metric(
        "📈 Nombre d'occurrences",
        nombre_principal
    )


# ============================================================
# TREEMAP
# ============================================================

st.subheader("🌈 Top 10 des genres les plus représentés")


fig = px.treemap(
    genres_analyse,
    path=["Genre"],
    values="Occurrences",
    color="Occurrences",
    color_continuous_scale=[
        "#00C853",
        "#00BFA5",
        "#2979FF",
        "#651FFF",
        "#AA00FF",
        "#F50057"
    ],
    hover_data={
        "Occurrences": True,
        "Pourcentage": True
    }
)


# Texte du treemap
fig.update_traces(
    textinfo="label+value+percent entry",
    textfont=dict(
        color="white",
        size=16
    ),
    hovertemplate=(
        "<b>%{label}</b><br>"
        "Occurrences : %{value}<br>"
        "<extra></extra>"
    )
)


# Style du graphique
fig.update_layout(
    height=600,
    paper_bgcolor="#121212",
    plot_bgcolor="#121212",
    font=dict(
        color="white"
    ),
    margin=dict(
        t=20,
        l=10,
        r=10,
        b=10
    ),
    coloraxis_colorbar=dict(
        title="Occurrences",
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
# TABLEAU DÉTAILLÉ
# ============================================================

st.subheader("📋 Détail des genres")


st.dataframe(
    genres_analyse,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# INFORMATIONS
# ============================================================

st.info(
    f"💡 **{genre_principal}** est le genre le plus représenté "
    f"avec **{nombre_principal} occurrences**, soit "
    f"**{pourcentage_principal:.2f} %** des occurrences "
    "du Top 10."
)


# ============================================================
# CONCLUSION
# ============================================================

st.subheader("💡 Conclusion")


st.write(
    f"Le genre le plus représenté dans notre dataset est "
    f"**{genre_principal}**, avec **{nombre_principal} occurrences**."
)

st.write(
    "Les résultats montrent une diversité importante de genres "
    "musicaux dans les données analysées."
)