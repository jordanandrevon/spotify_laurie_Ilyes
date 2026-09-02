import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Followers & popularité",
    page_icon="👥",
    layout="wide"
)


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

df_spotify = pd.read_excel("data/Spotify.xlsx")


# ============================================================
# PRÉPARATION DES DONNÉES
# ============================================================

popularite_followers = df_spotify[
    [
        "artist_name",
        "artist_followers",
        "artist_popularity",
        "track_popularity"
    ]
].copy()


# ============================================================
# CALCUL DE LA CORRÉLATION
# ============================================================

correlation = popularite_followers[
    ["artist_followers", "track_popularity"]
].corr().iloc[0, 1]


# Classification de la corrélation avec NumPy
niveau_correlation = np.select(
    [
        abs(correlation) < 0.3,
        abs(correlation) < 0.7,
        abs(correlation) >= 0.7
    ],
    [
        "Faible",
        "Modérée",
        "Forte"
    ],
    default="Non définie"
).item()


# ============================================================
# PRÉPARATION DU GRAPHIQUE
# ============================================================

# Regroupement des données par artiste
artistes_graphique = (
    popularite_followers
    .groupby("artist_name")
    .agg(
        followers=("artist_followers", "max"),
        popularite_moyenne=("track_popularity", "mean"),
        nombre_titres=("track_popularity", "count")
    )
    .reset_index()
)


# On conserve uniquement les artistes présents sur au moins 3 titres
artistes_graphique = artistes_graphique[
    artistes_graphique["nombre_titres"] >= 3
]


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

    /* Bloc de section */
    .section-header {
        background: linear-gradient(
            135deg,
            #1565C0,
            #512DA8
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

st.title("👥 Followers & popularité")

st.write(
    "Cette analyse cherche à déterminer si le nombre de followers "
    "d'un artiste est lié à la popularité de ses titres."
)


# ============================================================
# INDICATEURS
# ============================================================

col1, col2 = st.columns(2)


with col1:

    st.metric(
        "📈 Corrélation followers / popularité",
        f"{correlation:.3f}"
    )


with col2:

    st.metric(
        "🎯 Niveau de corrélation",
        niveau_correlation
    )


# ============================================================
# EXPLICATION DE LA CORRÉLATION
# ============================================================

if niveau_correlation == "Faible":

    st.info(
        "💡 Une corrélation de 0,232 indique une relation positive "
        "mais faible entre le nombre de followers et la popularité "
        "des titres."
    )

elif niveau_correlation == "Modérée":

    st.info(
        "💡 La corrélation indique une relation modérée entre "
        "le nombre de followers et la popularité des titres."
    )

else:

    st.info(
        "💡 La corrélation indique une relation forte entre "
        "le nombre de followers et la popularité des titres."
    )


# ============================================================
# GRAPHIQUE
# ============================================================

st.markdown(
    """
    <div class="section-header">
        <div class="section-title">
            📊 Followers et popularité moyenne des artistes
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


fig = px.scatter(
    artistes_graphique,
    x="followers",
    y="popularite_moyenne",
    size="nombre_titres",
    hover_name="artist_name",
    hover_data={
        "followers": ":,.0f",
        "popularite_moyenne": ":.1f",
        "nombre_titres": True
    },
    log_x=True,
    labels={
        "followers": "Nombre de followers",
        "popularite_moyenne": "Popularité moyenne des titres",
        "nombre_titres": "Nombre de titres"
    }
)


# Style des points
fig.update_traces(
    marker=dict(
        size=8,
        opacity=0.6
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
    )
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# EXPLICATION DU GRAPHIQUE
# ============================================================

st.info(
    "💡 Chaque point représente un artiste présent sur au moins "
    "3 titres dans notre dataset. La taille du point correspond "
    "au nombre de titres associés à l'artiste."
)


# ============================================================
# CONCLUSION
# ============================================================

st.subheader("💡 Conclusion")


st.write(
    f"La corrélation est positive ({correlation:.3f}), "
    f"mais elle reste {niveau_correlation.lower()}. "
    "Le nombre de followers semble donc avoir une influence "
    "limitée sur la popularité des titres."
)