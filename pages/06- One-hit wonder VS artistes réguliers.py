import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Artistes : One Hit vs Réguliers",
    page_icon="🎤",
    layout="wide"
)


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

df_spotify = pd.read_excel("data/Spotify.xlsx")


# ============================================================
# CALCULS (basés sur les cellules 16 à 32 du notebook)
# ============================================================

# Nombre de titres uniques par artiste
artist_counts = df_spotify.groupby('artist_name')['track_name'].nunique()

# Artistes avec un seul titre
one_hit_wonders = (artist_counts == 1).sum()

# Artistes avec plusieurs titres (réguliers/album)
regular_artists = (artist_counts > 1).sum()

# Total d'artistes
total_artists = one_hit_wonders + regular_artists

# Pourcentages
pct_one_hit = (one_hit_wonders / total_artists) * 100
pct_multi_hit = (regular_artists / total_artists) * 100

# Ratio
ratio = one_hit_wonders / regular_artists if regular_artists > 0 else 0

# Top 10 des artistes avec le plus de titres
top_artists = (
    df_spotify.groupby("artist_name")["track_name"]
    .count()
    .sort_values(ascending=False)
    .head(10)
)


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
        background: linear-gradient(135deg, #1DB954, #148A3B);
    }

    .blue-card {
        background: linear-gradient(135deg, #2196F3, #1565C0);
    }

    .section-header {
        padding: 12px 20px;
        border-radius: 10px;
        margin-top: 25px;
        margin-bottom: 15px;
        background: linear-gradient(135deg, #1DB954, #148A3B);
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

st.title("🎤 Artistes : One Hit Wonder vs Réguliers")

st.write(
    "Cette analyse répond à la question : "
    "**Combien d'artistes n'ont placé qu'un seul titre au sommet "
    "par rapport à ceux qui y placent régulièrement tout un album ?**"
)


# ============================================================
# STATISTIQUES CLÉS
# ============================================================

st.subheader("📊 Résultats")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div class="stat-card green-card">
            <div class="stat-title">
                🎵 Artistes avec 1 seul titre
            </div>
            <div class="stat-value">
                {one_hit_wonders}
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
                📀 Artistes avec plusieurs titres
            </div>
            <div class="stat-value">
                {regular_artists}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# GRAPHIQUE 1 : CAMEMBERT INTERACTIF (AGRANDI)
# ============================================================

st.markdown(
    """
    <div class="section-header">
        <div class="section-title">
            🥧 Répartition des artistes
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

labels = ["Un seul titre au sommet", "Plusieurs titres / Album"]
sizes = [one_hit_wonders, regular_artists]
colors = ["#1DB954", "#2196F3"]

fig_pie = px.pie(
    names=labels,
    values=sizes,
    color=labels,
    color_discrete_sequence=colors,
    hole=0.4,
    height=600
)

fig_pie.update_traces(
    textposition="inside",
    textinfo="percent",
    textfont=dict(color="white", size=22),
    insidetextorientation="horizontal",
    hovertemplate="<b>%{label}</b><br>" +
                  "Nombre d'artistes : %{value}<br>" +
                  "Pourcentage : %{percent}<br>" +
                  "<extra></extra>",
    pull=[0.08, 0],
    marker=dict(line=dict(color="#121212", width=3))
)

fig_pie.update_layout(
    plot_bgcolor="#181818",
    paper_bgcolor="#121212",
    font=dict(color="white", size=14),
    showlegend=True,
    legend=dict(
        font=dict(color="white", size=16),
        orientation="h",
        yanchor="bottom",
        y=-0.15,
        xanchor="center",
        x=0.5
    ),
    hoverlabel=dict(
        bgcolor="#333333",
        font_size=14,
        font_color="white"
    ),
    margin=dict(l=20, r=20, t=20, b=80)
)

st.plotly_chart(fig_pie, use_container_width=True)


# ============================================================
# GRAPHIQUE 2 : BARRES INTERACTIF
# ============================================================

st.markdown(
    """
    <div class="section-header">
        <div class="section-title">
            📊 Comparaison en nombre d'artistes
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

fig_bar = px.bar(
    x=["Un seul titre", "Plusieurs titres"],
    y=[one_hit_wonders, regular_artists],
    labels={
        "x": "Catégorie d'artiste",
        "y": "Nombre d'artistes"
    },
    text=[one_hit_wonders, regular_artists],
    color=["Un seul titre", "Plusieurs titres"],
    color_discrete_sequence=["#1DB954", "#2196F3"]
)

fig_bar.update_traces(
    textposition="outside",
    textfont=dict(color="white", size=16),
    hovertemplate="<b>%{x}</b><br>" +
                  "Nombre d'artistes : %{y}<br>" +
                  "<extra></extra>"
)

fig_bar.update_layout(
    height=450,
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

st.plotly_chart(fig_bar, use_container_width=True)


# ============================================================
# TABLEAU TOP 10 DES ARTISTES
# ============================================================

st.subheader("🏆 Top 10 des artistes avec le plus de titres dans le dataset")

st.dataframe(
    top_artists.reset_index().rename(
        columns={"artist_name": "Artiste", "track_name": "Nombre de titres"}
    ),
    use_container_width=True
)


# ============================================================
# CONCLUSION
# ============================================================

st.subheader("💡 Conclusion")

st.write(
    f"Sur **{total_artists}** artistes présents dans le dataset :"
)

st.markdown(
    f"""
    - 🎵 **{one_hit_wonders}** artistes ({pct_one_hit:.1f}%) n'ont placé **qu'un seul titre** au sommet
    - 📀 **{regular_artists}** artistes ({pct_multi_hit:.1f}%) ont placé **plusieurs titres** (album régulier)
    - 📊 Le ratio est de **1:{ratio:.2f}** : pour 1 artiste régulier, on trouve environ {ratio:.1f} one-hit wonders
    """
)

st.info(
    "La majorité des artistes (63,9%) ne parviennent à placer qu'un seul titre "
    "au sommet, ce qui suggère que le succès durable est rare dans l'industrie musicale. "
    "Seuls 36,1% des artistes parviennent à s'imposer régulièrement avec plusieurs titres."
)