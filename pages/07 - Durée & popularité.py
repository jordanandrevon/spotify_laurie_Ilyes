import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Durée & popularité",
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

# Extraction de l'année
df_spotify['release_year'] = df_spotify['album_release_date'].dt.year

# Groupe de popularité
df_spotify['popularity_group'] = pd.cut(
    df_spotify['track_popularity'],
    bins=[0, 20, 40, 60, 80, 100],
    labels=['Très faible', 'Faible', 'Moyenne', 'Élevée', 'Très élevée']
)

# Durée moyenne par année
duree_par_annee = df_spotify.groupby('release_year')['track_duration_min'].mean().reset_index()

# Durée moyenne par groupe de popularité
duree_par_popularite = df_spotify.groupby('popularity_group', observed=True)['track_duration_min'].mean().reset_index()


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

st.title("⏱️ Durée & popularité")

st.write(
    "Cette analyse explore l'**évolution de la durée moyenne des morceaux** "
    "au fil des années et son **influence sur leur popularité**."
)


# ============================================================
# STATISTIQUES CLÉS
# ============================================================

st.subheader("📊 Statistiques clés")

col1, col2, col3 = st.columns(3)

# Durée moyenne globale
duree_moyenne = np.mean(df_spotify['track_duration_min'])

# Année avec la durée moyenne la plus élevée
annee_max = duree_par_annee.loc[duree_par_annee['track_duration_min'].idxmax()]

# Année avec la durée moyenne la plus faible
annee_min = duree_par_annee.loc[duree_par_annee['track_duration_min'].idxmin()]

with col1:
    st.markdown(
        f"""
        <div class="stat-card green-card">
            <div class="stat-title">
                ⏱️ Durée moyenne globale
            </div>
            <div class="stat-value">
                {duree_moyenne:.2f} min
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="stat-card orange-card">
            <div class="stat-title">
                📈 Année avec la durée la + élevée
            </div>
            <div class="stat-value">
                {int(annee_max['release_year'])}
                <span style="font-size:16px;">({annee_max['track_duration_min']:.2f} min)</span>
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
                📉 Année avec la durée la + faible
            </div>
            <div class="stat-value">
                {int(annee_min['release_year'])}
                <span style="font-size:16px;">({annee_min['track_duration_min']:.2f} min)</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# GRAPHIQUE 1 : ÉVOLUTION DE LA DURÉE MOYENNE PAR ANNÉE
# ============================================================

st.markdown(
    """
    <div class="section-header">
        <div class="section-title">
            📈 Évolution de la durée moyenne des morceaux (1952 - 2025)
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

fig_evolution = px.line(
    duree_par_annee,
    x='release_year',
    y='track_duration_min',
    markers=True,
    labels={
        'release_year': 'Année de sortie',
        'track_duration_min': 'Durée moyenne (minutes)'
    }
)

fig_evolution.add_hline(
    y=duree_moyenne,
    line_dash="dash",
    line_color="#1DB954",
    annotation_text=f"Moyenne globale : {duree_moyenne:.2f} min",
    annotation_position="bottom right"
)

fig_evolution.update_traces(
    line=dict(color="#1DB954", width=3),
    marker=dict(size=8, color="#1DB954"),
    hovertemplate="<b>Année : %{x}</b><br>" +
                  "Durée moyenne : %{y:.2f} min<br>" +
                  "<extra></extra>"
)

fig_evolution.update_layout(
    plot_bgcolor="#181818",
    paper_bgcolor="#121212",
    font=dict(color="white"),
    xaxis=dict(
        gridcolor="#333333",
        color="white",
        tickfont=dict(color="white"),
        title_font=dict(color="white"),
        range=[1950, 2026]
    ),
    yaxis=dict(
        gridcolor="#333333",
        color="white",
        tickfont=dict(color="white"),
        title_font=dict(color="white")
    ),
    hoverlabel=dict(
        bgcolor="#333333",
        font_size=14,
        font_color="white"
    )
)

st.plotly_chart(fig_evolution, use_container_width=True)


# ============================================================
# GRAPHIQUE 2 : DURÉE MOYENNE PAR POPULARITÉ (BARRES BLEU/VIOLET)
# ============================================================

st.markdown(
    """
    <div class="section-header">
        <div class="section-title">
            📊 Durée moyenne selon le niveau de popularité
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Réordonner les catégories
ordre_categories = ['Très faible', 'Faible', 'Moyenne', 'Élevée', 'Très élevée']
duree_par_popularite['popularity_group'] = pd.Categorical(
    duree_par_popularite['popularity_group'],
    categories=ordre_categories,
    ordered=True
)
duree_par_popularite = duree_par_popularite.sort_values('popularity_group')

fig_popularite = px.bar(
    duree_par_popularite,
    x='popularity_group',
    y='track_duration_min',
    labels={
        'popularity_group': 'Niveau de popularité',
        'track_duration_min': 'Durée moyenne (minutes)'
    },
    text=duree_par_popularite['track_duration_min'].round(2),
    color='popularity_group',
    color_discrete_sequence=['#4FC3F7', '#29B6F6', '#0288D1', '#01579B', '#4A148C']
)

fig_popularite.update_traces(
    textposition="outside",
    textfont=dict(color="white", size=14),
    hovertemplate="<b>%{x}</b><br>" +
                  "Durée moyenne : %{y:.2f} min<br>" +
                  "<extra></extra>",
    marker=dict(line=dict(width=1, color='white'))
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
# GRAPHIQUE 3 : BOXPLOT PAR DÉCENNIE
# ============================================================

st.markdown(
    """
    <div class="section-header">
        <div class="section-title">
            📦 Distribution des durées par décennie
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Création des décennies
df_spotify['decade'] = (df_spotify['release_year'] // 10) * 10
df_spotify['decade'] = df_spotify['decade'].astype(str) + 's'

# Filtrer les décennies avec au moins 10 titres
decades_counts = df_spotify['decade'].value_counts()
decades_filtered = decades_counts[decades_counts >= 10].index
df_decades = df_spotify[df_spotify['decade'].isin(decades_filtered)]

fig_box = px.box(
    df_decades,
    x='decade',
    y='track_duration_min',
    color='decade',
    labels={
        'decade': 'Décennie',
        'track_duration_min': 'Durée (minutes)'
    },
    color_discrete_sequence=px.colors.sequential.Greens_r
)

fig_box.update_traces(
    hovertemplate="<b>Décennie : %{x}</b><br>" +
                  "Durée : %{y:.2f} min<br>" +
                  "<extra></extra>"
)

fig_box.update_layout(
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

st.plotly_chart(fig_box, use_container_width=True)


# ============================================================
# CONCLUSION
# ============================================================

st.subheader("💡 Conclusion")

st.write(
    f"La durée moyenne des morceaux dans le dataset est de "
    f"**{duree_moyenne:.2f} minutes**."
)

st.markdown(
    f"""
    **Évolution temporelle :**
    - 📈 La durée moyenne a atteint son **maximum en {int(annee_max['release_year'])}** avec **{annee_max['track_duration_min']:.2f} min**
    - 📉 La durée moyenne a atteint son **minimum en {int(annee_min['release_year'])}** avec **{annee_min['track_duration_min']:.2f} min**
    - On observe une **tendance générale à la baisse** depuis les années 1970
    """
)

st.markdown(
    f"""
    **Influence sur la popularité :**
    - Les titres **"Très populaires"** ont une durée moyenne de **{duree_par_popularite[duree_par_popularite['popularity_group'] == 'Très élevée']['track_duration_min'].values[0]:.2f} min**
    - Les titres **"Peu populaires"** ont une durée moyenne de **{duree_par_popularite[duree_par_popularite['popularity_group'] == 'Très faible']['track_duration_min'].values[0]:.2f} min**
    """
)

st.info(
    "Les morceaux plus courts (3 à 3.5 min) tendent à être légèrement plus populaires, "
    "ce qui peut s'expliquer par les habitudes d'écoute modernes (streaming, playlists). "
    "Les années 1960-1970 étaient marquées par des morceaux plus longs (rock progressif, psychédélique), "
    "tandis que les années récentes privilégient des formats plus courts adaptés aux plateformes numériques."
)