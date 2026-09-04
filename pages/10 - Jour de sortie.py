import os, glob, numpy as np, pandas as pd, streamlit as st
import plotly.graph_objects as go, plotly.express as px

st.set_page_config(page_title="Test Sorties par jour", page_icon="📅", layout="wide")

# --- CSS FOND NOIR (SANS LA SIDEBAR) ---
st.markdown("""<style>
.stApp { background-color: #0a0a0a; }
section[data-testid="stMain"] { color: #FFFFFF; }
section[data-testid="stMain"] p, section[data-testid="stMain"] li { color: #E6E6E6; }
section[data-testid="stMain"] h1, section[data-testid="stMain"] h2, section[data-testid="stMain"] h3 { color: #FFFFFF; }
</style>""", unsafe_allow_html=True)

DARK_TEMPLATE = go.layout.Template(layout=go.Layout(
    paper_bgcolor='#0a0a0a', plot_bgcolor='#121212', font=dict(color='#FFFFFF'),
    xaxis=dict(gridcolor='#333333', tickfont=dict(color='#CCCCCC')),
    yaxis=dict(gridcolor='#333333', tickfont=dict(color='#CCCCCC'))
))

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data(show_spinner="Chargement...")
def load_data(path):
    df = pd.read_excel(path)
    df['album_release_date'] = pd.to_datetime(df['album_release_date'], errors='coerce')
    df = df.dropna(subset=['album_release_date', 'track_popularity', 'track_name', 'artist_name']).copy()
    df['track_popularity'] = df['track_popularity'].astype(float)
    # Création de la colonne jour_sortie (ex: "Monday", "Friday"...)
    df['jour_sortie'] = df['album_release_date'].dt.day_name()
    return df

def get_data():
    candidates = ['Spotify.xlsx', './Spotify.xlsx', './data/Spotify.xlsx', './upload/Spotify.xlsx', '../Spotify.xlsx', '../data/Spotify.xlsx']
    found = next((p for p in candidates if os.path.isfile(p)), None)
    if found is None:
        for root in ['.', '..']:
            found = next((m for m in glob.glob(os.path.join(root, '**', 'Spotify.xlsx'), recursive=True)), None)
            if found: break
    if found: return load_data(found)
    uploaded = st.sidebar.file_uploader("Spotify.xlsx", type=['xlsx', 'xls'])
    return load_data(uploaded) if uploaded else None

df_clean = get_data()
if df_clean is None:
    st.warning("Veuillez fournir Spotify.xlsx")
    st.stop()

# ==========================================
# TON CODE NUMPY ADAPTÉ
# ==========================================
# --- UI ---
st.title("📅 Analyse des jours de sortie vs position / durée")
st.markdown("**Question** : Les morceaux sortis un jour particulier atteignent-ils de meilleures positions ou restent-ils plus longtemps dans le classement ?")

# 1. Préparation des données avec NumPy
jours_np = df_clean['jour_sortie'].to_numpy()
popularite_np = df_clean['track_popularity'].to_numpy()
ordre_jours = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
ordre_jours_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

# 2. Calculer le nombre total de sorties par jour avec NumPy
tailles_par_jour = np.array([np.sum(jours_np == jour) for jour in ordre_jours])

# 3. Préparer les données pour le Boxplot (répartition de la popularité par jour)
donnees_boxplot = [popularite_np[jours_np == jour] for jour in ordre_jours]

# Astuce pour Plotly Express : on aplatit la liste d'arrays Numpy en un DataFrame "long"
df_boxplot = pd.DataFrame({
    'Jour': np.repeat(ordre_jours_fr, [len(p) for p in donnees_boxplot]),
    'Popularité': np.concatenate([p if len(p) > 0 else np.array([0.0]) for p in donnees_boxplot])
})

# 4. Création de 2 colonnes côte à côte
st.subheader("Analyse des sorties par jour")
col1, col2 = st.columns(2)

# --- Graphique 1 : Nombre de sorties par jour (Plotly) ---
with col1:
    st.markdown("**Nombre total de morceaux sortis par jour**")
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=ordre_jours_fr, 
        y=tailles_par_jour, 
        marker_color='mediumseagreen',
        marker_line_color='black',
        marker_line_width=1,
        text=tailles_par_jour, # Affiche les valeurs au-dessus des barres
        textposition='outside'
    ))
    fig1.update_layout(
        template=DARK_TEMPLATE,
        xaxis_title='Jour de la semaine',
        yaxis_title='Nombre de morceaux',
        height=450,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig1, use_container_width=True)

# ==========================================
# GRAPHIQUE 3 : ÂGE DES TITRES PAR JOUR
# ==========================================

# 1. Calculs Numpy pour l'âge (adapté à df_clean et ordre_jours)
import pandas as pd
SNAPSHOT_DATE = pd.Timestamp('2025-10-31')
dates = df_clean['album_release_date'].to_numpy()
snapshot_np = np.datetime64(SNAPSHOT_DATE)

# Âge en jours
age_days = (snapshot_np - dates).astype('timedelta64[D]').astype(np.int64)
age_days = np.clip(age_days, 0, None).astype(float)

# Calcul vectorisé par jour avec Numpy
mean_age = np.array([age_days[jours_np == jour].mean() if (jours_np == jour).any() else 0 for jour in ordre_jours])
median_age = np.array([np.median(age_days[jours_np == jour]) if (jours_np == jour).any() else 0 for jour in ordre_jours])
counts = np.array([np.sum(jours_np == jour) for jour in ordre_jours])

# Constantes de couleur (si elles ne sont pas déjà définies plus haut dans ton fichier)
PALETTE = {'secondary': '#D55E00'}
OKABE_ITO = ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#56B4E9', '#E69F00', '#F0E442']

# 2. Création du graphique Plotly
st.divider()
st.subheader("Âge des titres encore écoutés")

fig_bar = go.Figure()

# Barres : Âge moyen
fig_bar.add_trace(go.Bar(
    x=ordre_jours_fr, 
    y=mean_age, 
    marker_color=OKABE_ITO[:7], 
    name='Âge moyen (jours)', 
    text=[f'{v:.0f} j<br>n={n}' for v, n in zip(mean_age, counts)], 
    textposition='outside'
))

# Courbe : Âge médian
fig_bar.add_trace(go.Scatter(
    x=ordre_jours_fr, 
    y=median_age, 
    mode='lines+markers', 
    line=dict(color=PALETTE['secondary'], width=3), 
    marker=dict(size=12), 
    name='Âge médian (jours)'
))

fig_bar.update_layout(
    template=DARK_TEMPLATE,
    title='Âge des titres par jour de sortie',
    xaxis_title='Jour de la semaine',
    yaxis_title='Âge (jours)',
    barmode='group', 
    height=500, 
    legend=dict(orientation='h', yanchor='bottom', y=1.02)
)

st.plotly_chart(fig_bar, use_container_width=True)

st.caption("Source : Spotify.xlsx (instantané 2025-10-31).")