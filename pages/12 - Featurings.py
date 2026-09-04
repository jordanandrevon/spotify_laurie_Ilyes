import os, glob, re, numpy as np, pandas as pd, streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Q3 — Featurings", page_icon="🎤", layout="wide")

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
PALETTE = {'primary': '#0072B2', 'secondary': '#D55E00', 'neutral': '#555555'}
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

# --- Q3 CALCUL NUMPY ---
def compute_q3(df, pop_threshold=75):
    years = df['album_release_date'].dt.year.to_numpy().astype(np.int64)
    pop   = df['track_popularity'].to_numpy().astype(float)
    feat_re = re.compile(r'\b(?:ft\.|feat\.|featuring)', re.IGNORECASE)
    has_feat = df['track_name'].str.contains(feat_re, regex=True, na=False).to_numpy()

    def period_stats(y_start, y_end, label):
        m = (years >= y_start) & (years <= y_end) & (pop >= pop_threshold)
        n = int(m.sum())
        pct = float(has_feat[m].mean() * 100) if n > 0 else 0.0
        return {'period': label, 'n_top': n, 'pct_feat': pct}

    p_old = period_stats(2019, 2020, '2019-2020')
    p_new = period_stats(2024, 2025, "2024-2025")

    unique_years = np.unique(years)
    yearly_y, yearly_pct, yearly_n = [], [], []
    for y in unique_years:
        m = (years == y) & (pop >= pop_threshold)
        n = int(m.sum())
        if n >= 10:
            yearly_y.append(int(y))
            yearly_pct.append(float(has_feat[m].mean() * 100))
            yearly_n.append(n)
    yearly = (np.array(yearly_y), np.array(yearly_pct), np.array(yearly_n))
    slope, _ = (np.polyfit(yearly[0], yearly[1], 1) if len(yearly_y) >= 3 else (None, None))
    return {'p_old': p_old, 'p_new': p_new, 'yearly': yearly, 'slope': slope}

pop_threshold = st.sidebar.slider("Seuil de popularité « haut du classement »", 0, 100, 75, step=5)
stats = compute_q3(df, pop_threshold=pop_threshold)

# --- UI ---
st.title("🎤 Featurings : aujourd'hui vs il y a 5 ans")
st.markdown("**Question** : Les featurings s'imposent-ils davantage dans le haut du classement aujourd'hui qu'il y a 5 ans ?")

delta = stats['p_new']['pct_feat'] - stats['p_old']['pct_feat']
c1, c2, c3 = st.columns(3)
c1.metric("2019-2020", f"{stats['p_old']['pct_feat']:.1f} %", f"n = {stats['p_old']['n_top']}")
c2.metric("2024-2025", f"{stats['p_new']['pct_feat']:.1f} %", f"n = {stats['p_new']['n_top']}")
c3.metric("Évolution", f"{delta:+.1f} pts")
st.divider()

# Graphique 1 : Barres groupées
st.subheader("Part des featurings dans le haut du classement")
periods = [stats['p_old']['period'], stats['p_new']['period']]
pcts    = [stats['p_old']['pct_feat'], stats['p_new']['pct_feat']]
ns      = [stats['p_old']['n_top'], stats['p_new']['n_top']]

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(x=periods, y=pcts, marker_color=[PALETTE['neutral'], PALETTE['primary']], text=[f'{v:.1f} %<br>n={n}' for v, n in zip(pcts, ns)], textposition='outside'))
fig_bar.update_layout(template=DARK_TEMPLATE, title='Part des featurings', yaxis_title=f'% featurings (pop. ≥ {pop_threshold})', height=500)
fig_bar.update_yaxes(range=[0, max(pcts) * 1.35 + 2])
st.plotly_chart(fig_bar, use_container_width=True)

# Graphique 2 : Évolution annuelle
st.subheader("Évolution annuelle de la part des featurings")
yrs, pct_y, n_y = stats['yearly']
fig_ev = go.Figure()
fig_ev.add_trace(go.Scatter(x=yrs, y=pct_y, mode='lines+markers', line=dict(color=PALETTE['primary'], width=3), marker=dict(size=12), name='% featurings'))
if stats['slope'] is not None:
    trend = stats['slope'] * yrs + np.polyfit(yrs, pct_y, 1)[1]
    fig_ev.add_trace(go.Scatter(x=yrs, y=trend, mode='lines', line=dict(color=PALETTE['secondary'], width=2, dash='dash'), name=f"Tendance ({stats['slope']:+.2f} pts/an)"))
fig_ev.update_layout(template=DARK_TEMPLATE, title='Évolution annuelle', xaxis_title='Année', yaxis_title='% featurings', height=500, legend=dict(orientation='h', yanchor='bottom', y=1.02))
st.plotly_chart(fig_ev, use_container_width=True)

st.caption(SOURCE_NOTE + " Featurings détectés via ft./feat./featuring.")