import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Analyse des titres explicites",
    page_icon="🔞",
    layout="wide"
)


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

df_spotify = pd.read_excel("data/Spotify.xlsx")


# ============================================================
# CALCULS DES PROPORTIONS
# ============================================================

# 1. Proportion globale de titres explicit (cellule 96)
proportion_globale = df_spotify["explicit"].mean() * 100

# 2. Proportion par type d'album (cellule 145)
proportion_album = df_spotify.groupby("album_type")["explicit"].mean() * 100

# 3. Popularité moyenne explicit vs non-explicit (cellule 136)
popularite_explicit = df_spotify.groupby("explicit")["track_popularity"].mean()

# 4. Répartition des genres avec explicit (cellules 16-17)
proportion_genre = (
    df_spotify.groupby("artist_genres")["explicit"]
    .mean()
    .mul(100)
)

genres_avec_explicit = np.sum(proportion_genre > 0)
genres_sans_explicit = np.sum(proportion_genre == 0)
total_genres = len(proportion_genre)

pourcentage_avec = (genres_avec_explicit / total_genres) * 100
pourcentage_sans = (genres_sans_explicit / total_genres) * 100

# 5. Top 10 des genres avec explicit (cellules 25-31)
nombre_titres = df_spotify.groupby("artist_genres")["track_name"].count()
proportion_genre_filtre = proportion_genre[nombre_titres >= 50]
top_10_genres = proportion_genre_filtre[proportion_genre_filtre > 0].sort_values(ascending=False).head(10)


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

    .red-card {
        background: linear-gradient(135deg, #E53935, #B71C1C);
    }

    .blue-card {
        background: linear-gradient(135deg, #2196F3, #1565C0);
    }

    .green-card {
        background: linear-gradient(135deg, #1DB954, #148A3B);
    }

    .purple-card {
        background: linear-gradient(135deg, #9C27B0, #6A1B9A);
    }

    .orange-card {
        background: linear-gradient(135deg, #FF9800, #E65100);
    }

    .section-header {
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

    .header-red {
        background: linear-gradient(135deg, #E53935, #B71C1C);
    }

    .header-blue {
        background: linear-gradient(135deg, #1565C0, #512DA8);
    }

    .header-green {
        background: linear-gradient(135deg, #1DB954, #148A3B);
    }

    .header-purple {
        background: linear-gradient(135deg, #7B1FA2, #C2185B);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITRE
# ============================================================

st.title("🔞 Analyse des titres explicites")

st.write(
    "Cette analyse explore la proportion de titres explicites, "
    "leur répartition par type d'album et leur popularité."
)


# ============================================================
# INDICATEURS CLÉS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="stat-card red-card">
            <div class="stat-title">
                🔞 Proportion de titres explicites
            </div>
            <div class="stat-value">
                {proportion_globale:.1f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="stat-card green-card">
            <div class="stat-title">
                ⭐ Popularité des titres explicites
            </div>
            <div class="stat-value">
                {popularite_explicit[True]:.1f}/100
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="stat-card blue-card">
            <div class="stat-title">
                ⭐ Popularité des titres non-explicites
            </div>
            <div class="stat-value">
                {popularite_explicit[False]:.1f}/100
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# GRAPHIQUE 1 : PROPORTION PAR TYPE D'ALBUM (cellule 145)
# ============================================================

st.markdown(
    """
    <div class="section-header header-blue">
        <div class="section-title">
            📊 Proportion de titres explicites selon le type d'album
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

fig_album = px.bar(
    x=proportion_album.index,
    y=proportion_album.values,
    labels={
        "x": "Type d'album",
        "y": "Proportion de titres explicites (%)"
    },
    text=proportion_album.values.round(2),
    color=proportion_album.index,
    color_discrete_sequence=["#1DB954", "#2196F3", "#9C27B0"]
)

fig_album.update_traces(
    textposition="outside",
    textfont=dict(color="white"),
    hovertemplate="<b>%{x}</b><br>" +
                  "Proportion explicit : %{y:.2f}%<br>" +
                  "<extra></extra>",
    marker=dict(line=dict(width=2, color='white'))
)

fig_album.update_layout(
    plot_bgcolor="#181818",
    paper_bgcolor="#121212",
    font=dict(color="white"),
    xaxis=dict(
        gridcolor="#333333",
        color="white",
        tickfont=dict(color="white"),
        title_font=dict(color="white")
    ),
    yaxis=dict(
        gridcolor="#333333",
        color="white",
        tickfont=dict(color="white"),
        title_font=dict(color="white"),
        ticksuffix="%"
    ),
    showlegend=False,
    hoverlabel=dict(
        bgcolor="#333333",
        font_size=14,
        font_color="white"
    )
)

st.plotly_chart(fig_album, use_container_width=True)


# ============================================================
# GRAPHIQUE 2 : COMPARAISON DE POPULARITÉ (cellule 136)
# ============================================================

st.markdown(
    """
    <div class="section-header header-blue">
        <div class="section-title">
            📈 Comparaison de popularité : Explicit vs Non-Explicit
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

fig_popularite = px.box(
    df_spotify,
    x="explicit",
    y="track_popularity",
    color="explicit",
    color_discrete_map={True: "#FF8A65", False: "#4FC3F7"},
    labels={
        "explicit": "Titre explicite",
        "track_popularity": "Popularité"
    }
)

fig_popularite.update_traces(
    hovertemplate="<b>Explicit : %{x}</b><br>" +
                  "Popularité : %{y}<br>" +
                  "<extra></extra>"
)

fig_popularite.update_layout(
    plot_bgcolor="#181818",
    paper_bgcolor="#121212",
    font=dict(color="white"),
    xaxis=dict(
        gridcolor="#333333",
        color="white",
        tickfont=dict(color="white"),
        title_font=dict(color="white")
    ),
    yaxis=dict(
        gridcolor="#333333",
        color="white",
        tickfont=dict(color="white"),
        title_font=dict(color="white")
    ),
    showlegend=False,
    hoverlabel=dict(
        bgcolor="#333333",
        font_size=14,
        font_color="white"
    )
)

st.plotly_chart(fig_popularite, use_container_width=True)


# ============================================================
# GRAPHIQUE 3 : RÉPARTITION DES GENRES (cellules 16-17)
# ============================================================

st.markdown(
    """
    <div class="section-header header-green">
        <div class="section-title">
            🎵 Répartition des genres selon la présence de titres explicites
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

genres_repartition = pd.DataFrame({
    "Catégorie": ["Sans explicit", "Avec explicit"],
    "Pourcentage": [pourcentage_sans, pourcentage_avec],
    "Nombre": [genres_sans_explicit, genres_avec_explicit]
})

fig_genres_repartition = px.bar(
    genres_repartition,
    x="Catégorie",
    y="Pourcentage",
    text=genres_repartition["Pourcentage"].round(1),
    color="Catégorie",
    color_discrete_map={
        "Sans explicit": "#4FC3F7",
        "Avec explicit": "#FF8A65"
    },
    hover_data={
        "Nombre": True,
        "Pourcentage": True
    },
    labels={
        "Catégorie": "Catégorie de genre",
        "Pourcentage": "Pourcentage de genres (%)"
    }
)

fig_genres_repartition.update_traces(
    textposition="outside",
    textfont=dict(color="white", size=18),
    hovertemplate="<b>%{x}</b><br>" +
                  "Nombre de genres : %{customdata[0]}<br>" +
                  "Pourcentage : %{y:.1f}%<br>" +
                  "<extra></extra>",
    marker=dict(line=dict(width=2, color='white'))
)

fig_genres_repartition.update_layout(
    height=450,
    plot_bgcolor="#181818",
    paper_bgcolor="#121212",
    font=dict(color="white"),
    xaxis=dict(
        gridcolor="#333333",
        color="white",
        tickfont=dict(color="white", size=14),
        title_font=dict(color="white", size=16)
    ),
    yaxis=dict(
        gridcolor="#333333",
        color="white",
        tickfont=dict(color="white", size=14),
        title_font=dict(color="white", size=16),
        ticksuffix="%"
    ),
    showlegend=False,
    hoverlabel=dict(
        bgcolor="#333333",
        font_size=14,
        font_color="white"
    ),
    margin=dict(l=10, r=30, t=20, b=20)
)

st.plotly_chart(fig_genres_repartition, use_container_width=True)


# ============================================================
# GRAPHIQUE 4 : TOP 10 DES GENRES EXPLICITES (cellules 25-31)
# ============================================================

st.markdown(
    """
    <div class="section-header header-red">
        <div class="section-title">
            🎤 Top 10 des genres avec le plus de titres explicites
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

fig_genres = px.bar(
    x=top_10_genres.values,
    y=top_10_genres.index,
    orientation="h",
    labels={
        "x": "Proportion de titres explicites (%)",
        "y": "Genre"
    },
    text=top_10_genres.values.round(2),
    color=top_10_genres.values,
    color_continuous_scale=["#FF8A65", "#E53935", "#B71C1C"]
)

fig_genres.update_traces(
    textposition="outside",
    textfont=dict(color="white"),
    hovertemplate="<b>%{y}</b><br>" +
                  "Proportion explicit : %{x:.2f}%<br>" +
                  "<extra></extra>"
)

fig_genres.update_layout(
    plot_bgcolor="#181818",
    paper_bgcolor="#121212",
    font=dict(color="white"),
    xaxis=dict(
        gridcolor="#333333",
        color="white",
        tickfont=dict(color="white"),
        title_font=dict(color="white")
    ),
    yaxis=dict(
        color="white",
        tickfont=dict(color="white"),
        title_font=dict(color="white"),
        categoryorder="total ascending"
    ),
    coloraxis_showscale=False,
    hoverlabel=dict(
        bgcolor="#333333",
        font_size=14,
        font_color="white"
    )
)

st.plotly_chart(fig_genres, use_container_width=True)


# ============================================================
# CONCLUSION
# ============================================================

st.subheader("💡 Conclusion")

st.write(
    f"Les titres explicites représentent **{proportion_globale:.1f}%** "
    "du dataset et sont en moyenne **plus populaires** "
    f"({popularite_explicit[True]:.1f}/100) que les titres "
    f"non-explicites ({popularite_explicit[False]:.1f}/100)."
)

st.write(
    f"Sur **{total_genres}** genres identifiés, "
    f"**{genres_avec_explicit}** ({pourcentage_avec:.1f}%) contiennent "
    f"au moins un titre explicite, tandis que **{genres_sans_explicit}** "
    f"({pourcentage_sans:.1f}%) n'en contiennent aucun."
)

st.write(
    "Les **albums** contiennent la plus forte proportion de titres "
    "explicites, tandis que les **compilations** en contiennent le moins."
)

st.write(
    "Les genres **rap, hip-hop et emo rap** présentent les plus "
    "fortes proportions de titres explicites."
)