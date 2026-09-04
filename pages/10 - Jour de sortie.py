import os, glob, numpy as np, pandas as pd, streamlit as st
import plotly.graph_objects as go, plotly.express as px

st.set_page_config(page_title="Analyse des Jours de sortie", page_icon="📅", layout="wide")

# --- CSS FOND NOIR (SANS LA SIDEBAR) ---
st.markdown("""<style>
.stApp { background-color: #0a0a0a; }
section[data-testid="stMain"] { color: #FFFFFF; }
section[data-testid="stMain"] p, section[data-testid="stMain"] li { color: #E6E6E6; }
section[data-testid="stMain"] h1, section[data-testid="stMain"] h2, section[data-testid="stMain"] h3 { color: #FFFFFF; }
div[data-testid="stMetric"] { background-color: #1E1E1E; padding: 15px; border-radius: 10px; border: 1px solid #333333; }
div[data-testid="stMetric"] label { color: #B3B3B3; }
div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #1DB954; }
</style>""", unsafe_allow_html=True)

# --- CONSTANTES & CONFIG ---
SNAPSHOT_DATE = pd.Timestamp('2025-10-31')
WEEKDAY_FR = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
PALETTE = {'primary': '#0072B2', 'secondary': '#D55E00', 'tertiary': '#009E73', 'quaternary':'#CC79A7', 'neutral': '#555555'}
OKABE_ITO = ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#56B4E9', '#E69F00', '#F0E442', '#000000']
SOURCE_NOTE = "Source : Spotify.xlsx (instantané 2025-10-31)."

DARK_TEMPLATE = go.layout.Template(layout=go.Layout(
    paper_bgcolor='#0a0a0a', plot_bgcolor='#121212', font=dict(color='#FFFFFF'),
    xaxis=dict(gridcolor='#333333', tickfont=dict(color='#CCCCCC')),
    yaxis=dict(gridcolor='#333333', tickfont=dict(color='#CCCCCC')),
    legend=dict(bgcolor='rgba(30,30,30,0.8)', font=dict(color='#FFFFFF')), colorway=OKABE_ITO))

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data(show_spinner="Chargement...")
def load_data(path):
    df = pd.read_excel(path)
    df['album_release_date'] = pd.to_datetime(df['album_release_date'], errors='coerce')
    df = df.dropna(subset=['album_release_date', 'track_popularity', 'track_name', 'artist_name']).copy()
    df['track_popularity'] = df['track_popularity'].astype(float)
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

df = get_data()
if df is None:
    st.warning("Veuillez fournir Spotify.xlsx")
    st.stop()

# --- Q1 CALCUL NUMPY ---
def compute_q1(df, snapshot=SNAPSHOT_DATE):
    days = df['album_release_date'].dt.dayofweek.to_numpy()
    pop  = df['track_popularity'].to_numpy().astype(float)
    dates = df['album_release_date'].to_numpy()
    snapshot_np = np.datetime64(snapshot)
    age_days = (snapshot_np - dates).astype('timedelta64[D]').astype(np.int64)
    age_days = np.clip(age_days, 0, None).astype(float)
    m = (pop > 0) & (age_days >= 0)
    days_m, pop_m, age_m = days[m], pop[m], age_days[m]
    mean_pop   = np.array([pop_m[days_m == i].mean() if (days_m == i).any() else 0 for i in range(7)])
    median_pop = np.array([np.median(pop_m[days_m == i]) if (days_m == i).any() else 0 for i in range(7)])
    mean_age   = np.array([age_m[days_m == i].mean() if (days_m == i).any() else 0 for i in range(7)])
    median_age = np.array([np.median(age_m[days_m == i]) if (days_m == i).any() else 0 for i in range(7)])
    counts     = np.array([(days_m == i).sum() for i in range(7)])
    pop_by_day = [pop_m[days_m == i] for i in range(7)]
    return {'mean_pop': mean_pop, 'median_pop': median_pop, 'mean_age': mean_age, 'median_age': median_age, 'counts': counts, 'pop_by_day': pop_by_day, 'n': m.sum()}

stats = compute_q1(df)

# --- UI ---
st.title("📅 Analyse des jours de sortie vs position / durée")
st.markdown("**Question** : Les morceaux sortis un jour particulier atteignent-ils de meilleures positions ou restent-ils plus longtemps dans le classement ?")

best_idx = int(np.argmax(stats['mean_pop']))
c1, c2, c3, c4 = st.columns(4)
c1.metric("Titres analysés", f"{stats['n']:,}".replace(",", " "))
c2.metric("Meilleur jour (pop. moy.)", WEEKDAY_FR[best_idx], f"{stats['mean_pop'][best_idx]:.1f}/100")
c3.metric("Âge moyen global", f"{stats['mean_age'].mean():.0f} jours")
c4.metric("Total sorties", f"{stats['counts'].sum():,}".replace(",", " "))
st.divider()

# Graphique 1 : Boxplot dynamique
st.subheader("Distribution de la popularité par jour")
pop_long = pd.DataFrame({
    'Jour': np.repeat(WEEKDAY_FR, [len(p) for p in stats['pop_by_day']]),
    'Popularité': np.concatenate([p if len(p) > 0 else np.array([0.0]) for p in stats['pop_by_day']])
})
fig_box = px.box(pop_long, x='Jour', y='Popularité', color='Jour', category_orders={'Jour': WEEKDAY_FR}, color_discrete_sequence=OKABE_ITO, template=DARK_TEMPLATE)
fig_box.add_scatter(x=WEEKDAY_FR, y=stats['mean_pop'], mode='markers+lines', marker=dict(color='#FFFFFF', size=14, line=dict(color='#000000', width=2)), name='Moyenne')
fig_box.update_layout(title='Popularité Spotify selon le jour de sortie', yaxis_title='Popularité (0-100)', showlegend=False, height=500)
fig_box.update_yaxes(range=[0, 100])
st.plotly_chart(fig_box, use_container_width=True)

# Graphique 2 : Barres âge moyen + courbe médian
st.subheader("Âge des titres encore écoutés (proxy durée)")
fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(x=WEEKDAY_FR, y=stats['mean_age'], marker_color=OKABE_ITO[:7], name='Âge moyen (jours)', text=[f'{v:.0f} j<br>n={n}' for v, n in zip(stats['mean_age'], stats['counts'])], textposition='outside'))
fig_bar.add_trace(go.Scatter(x=WEEKDAY_FR, y=stats['median_age'], mode='lines+markers', line=dict(color=PALETTE['secondary'], width=3), marker=dict(size=12), name='Âge médian (jours)'))
fig_bar.update_layout(template=DARK_TEMPLATE, title='Âge des titres par jour de sortie', yaxis_title='Âge (jours)', barmode='group', height=500, legend=dict(orientation='h', yanchor='bottom', y=1.02))
st.plotly_chart(fig_bar, use_container_width=True)

st.caption(SOURCE_NOTE)