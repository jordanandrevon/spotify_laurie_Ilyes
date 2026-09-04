import os, glob, numpy as np, pandas as pd, streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Q2 — Temps vers le sommet", page_icon="⏱️", layout="wide")

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
PALETTE = {'primary': '#0072B2', 'secondary': '#D55E00', 'tertiary': '#009E73', 'quaternary':'#CC79A7'}
SOURCE_NOTE = "Source : Spotify.xlsx."
DARK_TEMPLATE = go.layout.Template(layout=go.Layout(paper_bgcolor='#0a0a0a', plot_bgcolor='#121212', font=dict(color='#FFFFFF'), xaxis=dict(gridcolor='#333333', tickfont=dict(color='#CCCCCC')), yaxis=dict(gridcolor='#333333', tickfont=dict(color='#CCCCCC'))))

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

# --- Q2 CALCUL NUMPY ---
def compute_q2(df, pop_threshold=75, snapshot=SNAPSHOT_DATE):
    pop   = df['track_popularity'].to_numpy().astype(float)
    dates = df['album_release_date'].to_numpy()
    snapshot_np = np.datetime64(snapshot)
    age_days = (snapshot_np - dates).astype('timedelta64[D]').astype(np.int64)
    age_days = np.clip(age_days, 0, None).astype(float)
    top_mask = pop >= pop_threshold
    age_top_weeks = age_days[top_mask] / 7.0
    bins = np.array([0, 20, 40, 60, pop_threshold, 90, 100], dtype=float)
    bin_idx = np.digitize(pop, bins) - 1
    bin_idx = np.clip(bin_idx, 0, len(bins) - 2)
    n_bins = len(bins) - 1
    median_w = np.empty(n_bins); mean_w = np.empty(n_bins); counts = np.empty(n_bins, dtype=int)
    for i in range(n_bins):
        m = bin_idx == i
        if m.any():
            median_w[i] = np.median(age_days[m]) / 7.0
            mean_w[i]   = age_days[m].mean() / 7.0
            counts[i]   = m.sum()
        else:
            median_w[i] = mean_w[i] = 0.0; counts[i] = 0
    return {'age_top_weeks': age_top_weeks, 'median_weeks_top': float(np.median(age_top_weeks)) if age_top_weeks.size > 0 else 0, 'mean_weeks_top': float(np.mean(age_top_weeks)) if age_top_weeks.size > 0 else 0, 'n_top': int(top_mask.sum()), 'bins': bins, 'median_w': median_w, 'mean_w': mean_w, 'counts': counts}

pop_threshold = st.sidebar.slider("Seuil de popularité « haut du classement »", 0, 100, 75, step=5)
stats = compute_q2(df, pop_threshold=pop_threshold)

# --- UI ---
st.title("⏱️ Temps pour atteindre le sommet")
st.markdown("**Question** : Combien de semaines faut-il en moyenne à un titre pour atteindre sa position maximale ?")

c1, c2, c3 = st.columns(3)
c1.metric("Titres « top »", f"{stats['n_top']:,}".replace(",", " "))
c2.metric("Âge médian", f"{stats['median_weeks_top']:.1f} sem")
c3.metric("Âge moyen", f"{stats['mean_weeks_top']:.1f} sem")
st.divider()

# Graphique 1 : Histogramme
st.subheader(f"Distribution de l'âge des titres top (pop. ≥ {pop_threshold})")
fig_hist = go.Figure()
fig_hist.add_trace(go.Histogram(x=stats['age_top_weeks'], nbinsx=40, marker_color=PALETTE['primary'], marker_line_color='#FFFFFF', marker_line_width=1, opacity=0.85))
fig_hist.add_vline(x=stats['median_weeks_top'], line_dash='dash', line_color=PALETTE['tertiary'], line_width=3, annotation_text=f"Médiane = {stats['median_weeks_top']:.1f} sem")
fig_hist.add_vline(x=stats['mean_weeks_top'], line_dash='dot', line_color=PALETTE['quaternary'], line_width=3, annotation_text=f"Moyenne = {stats['mean_weeks_top']:.1f} sem")
fig_hist.update_layout(template=DARK_TEMPLATE, title='Âge des titres au sommet', xaxis_title='Âge (semaines)', yaxis_title='Nombre de titres', height=500)
st.plotly_chart(fig_hist, use_container_width=True)

# Graphique 2 : Tranches de popularité
st.subheader("Âge du titre selon sa tranche de popularité")
labels = ['0-20', '21-40', '41-60', f'61-{pop_threshold}', f'{pop_threshold+1}-90', '91-100']
fig_tr = go.Figure()
fig_tr.add_trace(go.Scatter(x=labels, y=stats['median_w'], mode='lines+markers', line=dict(color=PALETTE['primary'], width=3), marker=dict(size=14), name='Âge médian', text=[f'{v:.0f} sem<br>n={n}' for v, n in zip(stats['median_w'], stats['counts'])], textposition='top center'))
fig_tr.add_trace(go.Scatter(x=labels, y=stats['mean_w'], mode='lines+markers', line=dict(color=PALETTE['secondary'], width=2, dash='dash'), marker=dict(size=12), name='Âge moyen'))
fig_tr.update_layout(template=DARK_TEMPLATE, title='Âge par tranche de popularité', yaxis_title='Âge (semaines)', height=500, legend=dict(orientation='h', yanchor='bottom', y=1.02))
st.plotly_chart(fig_tr, use_container_width=True)

st.caption(SOURCE_NOTE)