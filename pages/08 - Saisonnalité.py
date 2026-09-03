import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Saisons & Top",
    page_icon="🌡️",
    layout="wide"
)


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

df_spotify = pd.read_excel("data/Spotify.xlsx")


# ============================================================
# PRÉPARATION DES DONNÉES
# ============================================================

# Extraction du mois
df_spotify['release_month'] = df_spotify['album_release_date'].dt.month

# Association des mois avec les saisons
def assigner_saison(mois):
    if mois in [12, 1, 2]:
        return 'Hiver'
    elif mois in [3, 4, 5]:
        return 'Printemps'
    elif mois in [6, 7, 8]:
        return 'Été'
    elif mois in [9, 10, 11]:
        return 'Automne'

df_spotify['saison'] = df_spotify['release_month'].apply(assigner_saison)

# Filtrer les titres populaires (popularité >= 70)
top_titres = df_spotify[df_spotify['track_popularity'] >= 70]

# Nombre de titres par saison
saisons_top = top_titres['saison'].value_counts().reindex(
    ['Hiver', 'Printemps', 'Été', 'Automne']
).fillna(0)


# ============================================================
# STATISTIQUES AVEC NUMPY
# ============================================================

total_top = np.sum(saisons_top.values)
saison_max = saisons_top.idxmax()
valeur_max = np.max(saisons_top.values)
saison_min = saisons_top.idxmin()
valeur_min = np.min(saisons_top.values)

# Pourcentages
pourcentages = (saisons_top.values / total_top) * 100

# DataFrame d'analyse
saisons_analyse = pd.DataFrame({
    "Saison": saisons_top.index,
    "Titres dans le Top": saisons_top.values.astype(int),
    "Pourcentage": np.round(pourcentages, 2)
})


# ============================================================
# STYLE VISUEL
# ============================================================

st.markdown(
    """
    <style>

    /* Fond général */
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

    /* CARTES STATISTIQUES */
    .stat-card {
        padding: 20px;
        border-radius: 14px;
        text-align: center;
        min-height: 120px;
        margin-bottom: 15px;
        border: 1px solid #293247;
    }

    .stat-title {
        font-size: 15px;
        margin-bottom: 8px;
        color: #AEB6C7;
    }

    .stat-value {
        font-size: 32px;
        font-weight: bold;
        color: #FFFFFF;
    }

    /* CARTES PAR SAISON */
    .hiver {
        background: linear-gradient(135deg, #0D47A1, #1565C0);
    }

    .printemps {
        background: linear-gradient(135deg, #1B5E20, #2E7D32);
    }

    .ete {
        background: linear-gradient(135deg, #BF360C, #E64A19);
    }

    .automne {
        background: linear-gradient(135deg, #E65100, #F57C00);
    }

    /* BLOC CONCLUSION */
    .conclusion-box {
        background: linear-gradient(135deg, #111B24, #18202D);
        border: 1px solid #00B8D9;
        border-radius: 14px;
        padding: 22px;
        margin-top: 20px;
        color: #FFFFFF;
        line-height: 1.6;
    }

    .info-box {
        background: linear-gradient(135deg, #151B29, #1B2030);
        border: 1px solid #293247;
        border-radius: 14px;
        padding: 20px 22px;
        margin-top: 20px;
        color: #DDE3F0;
        line-height: 1.6;
    }

    /* MÉTRIQUES STREAMLIT */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #151B29, #1B2030);
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

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITRE
# ============================================================

st.markdown(
    '<div class="main-title">🌡️ Saisonnalité</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    "Les titres sortis en hiver ou en été sont-ils les plus présents dans le Top ?"
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# STATISTIQUES CLÉS
# ============================================================

st.markdown(
    '<div class="section-title">📊 Résultats par saison</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="stat-card hiver">
            <div class="stat-title">❄️ Hiver</div>
            <div class="stat-value">{int(saisons_top['Hiver'])}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="stat-card printemps">
            <div class="stat-title">🌸 Printemps</div>
            <div class="stat-value">{int(saisons_top['Printemps'])}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="stat-card ete">
            <div class="stat-title">☀️ Été</div>
            <div class="stat-value">{int(saisons_top['Été'])}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="stat-card automne">
            <div class="stat-title">🍂 Automne</div>
            <div class="stat-value">{int(saisons_top['Automne'])}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# MÉTRIQUES COMPLÉMENTAIRES
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "📈 Total de titres dans le Top",
        total_top
    )

with col2:
    st.metric(
        "🏆 Saison gagnante",
        saison_max
    )

with col3:
    st.metric(
        "📉 Saison perdante",
        saison_min
    )


# ============================================================
# GRAPHIQUE : BARRES INTERACTIF
# ============================================================

st.markdown(
    '<div class="section-title">📊 Nombre de titres du Top par saison</div>',
    unsafe_allow_html=True
)

fig = px.bar(
    saisons_analyse,
    x="Saison",
    y="Titres dans le Top",
    text="Titres dans le Top",
    color="Saison",
    color_discrete_map={
        "Hiver": "#4FC3F7",
        "Printemps": "#81C784",
        "Été": "#FF8A65",
        "Automne": "#FFD54F"
    },
    hover_data={
        "Pourcentage": True
    }
)

fig.update_traces(
    textposition="outside",
    textfont=dict(color="white", size=18),
    hovertemplate="<b>Saison : %{x}</b><br>" +
                  "Titres dans le Top : %{y}<br>" +
                  "Pourcentage du Top : %{customdata[0]:.1f}%<br>" +
                  "<extra></extra>",
    marker=dict(line=dict(width=2, color='white'))
)

fig.update_layout(
    height=500,
    paper_bgcolor="#0F1117",
    plot_bgcolor="#151922",
    font=dict(color="white"),
    xaxis=dict(
        gridcolor="#293247",
        color="white",
        tickfont=dict(color="white", size=14),
        title_font=dict(color="white", size=16)
    ),
    yaxis=dict(
        gridcolor="#293247",
        color="white",
        tickfont=dict(color="white", size=14),
        title_font=dict(color="white", size=16)
    ),
    showlegend=False,
    hoverlabel=dict(
        bgcolor="#333333",
        font_size=14,
        font_color="white"
    ),
    margin=dict(l=10, r=30, t=20, b=20)
)

st.plotly_chart(fig, use_container_width=True)


# ============================================================
# TABLEAU DÉTAILLÉ
# ============================================================

st.markdown(
    '<div class="section-title">📋 Détails par saison</div>',
    unsafe_allow_html=True
)

st.dataframe(
    saisons_analyse.sort_values("Titres dans le Top", ascending=False),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Saison": st.column_config.TextColumn("Saison"),
        "Titres dans le Top": st.column_config.NumberColumn("Titres dans le Top"),
        "Pourcentage": st.column_config.NumberColumn("% du Top", format="%.1f%%")
    }
)


# ============================================================
# CONCLUSION
# ============================================================

st.markdown(
    '<div class="section-title">💡 Conclusion</div>',
    unsafe_allow_html=True
)

# Interprétation personnalisée selon la saison gagnante
if saison_max == 'Été':
    interpretation = (
        "L'**Été** est la saison qui place le plus de titres dans le Top ! "
        "Cela peut s'expliquer par les sorties estivales, les festivals, "
        "et les playlists d'été qui boostent la popularité des morceaux."
    )
elif saison_max == 'Hiver':
    interpretation = (
        "L'**Hiver** est la saison qui place le plus de titres dans le Top ! "
        "Cela peut s'expliquer par les sorties de fin d'année, les fêtes de Noël, "
        "et les playlists hivernales qui augmentent l'écoute."
    )
elif saison_max == 'Printemps':
    interpretation = (
        "Le **Printemps** est la saison qui place le plus de titres dans le Top ! "
        "Cela peut s'expliquer par les reprises d'activité musicale après l'hiver."
    )
else:
    interpretation = (
        "L'automne est la saison qui place le plus de titres dans le Top ! "
        "Cela peut s'expliquer par les sorties post-été et la préparation des fins d'année."
    )

st.markdown(
    f"""
    <div class="conclusion-box">
        <b></b> {interpretation}
        <br><br>
        <b>⚠️ À noter :</b> les différences entre les saisons restent modérées,
        avec un écart maximal de {valeur_max - valeur_min} titres.
    </div>
    """,
    unsafe_allow_html=True
)