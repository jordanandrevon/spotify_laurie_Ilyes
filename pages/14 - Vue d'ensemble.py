import os, glob, re, numpy as np, pandas as pd, streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Vue d'ensemble", page_icon="📊", layout="wide")

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
# CORRECTION ICI : ajout de 'neutral'
PALETTE = {'primary': '#0072B2', 'secondary': '#D55E00', 'tertiary': '#009E73', 'quaternary':'#CC79A7', 'neutral': '#555555'}
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

# --- CALCULS NUMPY Q1 à Q4 ---
def compute_q1(df, snapshot=SNAPSHOT_DATE):
    days = df['album_release_date'].dt.dayofweek.to_numpy()
    pop  = df['track_popularity'].to_numpy().astype(float)
    dates = df['album_release_date'].to_numpy()
    age_days = (np.datetime64(snapshot) - dates).astype('timedelta64[D]').astype(np.int64)
    age_days = np.clip(age_days, 0, None).astype(float)
    m = (pop > 0) & (age_days >= 0)
    days_m, pop_m = days[m], pop[m]
    mean_pop = np.array([pop_m[days_m == i].mean() if (days_m == i).any() else 0 for i in range(7)])
    return {'mean_pop': mean_pop}

def compute_q2(df, pop_threshold=75, snapshot=SNAPSHOT_DATE):
    pop   = df['track_popularity'].to_numpy().astype(float)
    dates = df['album_release_date'].to_numpy()
    age_days = (np.datetime64(snapshot) - dates).astype('timedelta64[D]').astype(np.int64)
    age_days = np.clip(age_days, 0, None).astype(float)
    top_mask = pop >= pop_threshold
    return {'age_top_weeks': age_days[top_mask] / 7.0, 'median_weeks_top': float(np.median(age_days[top_mask] / 7.0)) if top_mask.sum() > 0 else 0, 'n_top': int(top_mask.sum())}

def compute_q3(df, pop_threshold=75):
    years = df['album_release_date'].dt.year.to_numpy().astype(np.int64)
    pop   = df['track_popularity'].to_numpy().astype(float)
    feat_re = re.compile(r'\b(?:ft\.|feat\.|featuring)', re.IGNORECASE)
    has_feat = df['track_name'].str.contains(feat_re, regex=True, na=False).to_numpy()
    def ps(y1, y2):
        m = (years >= y1) & (years <= y2) & (pop >= pop_threshold)
        n = int(m.sum())
        return {'n_top': n, 'pct_feat': float(has_feat[m].mean() * 100) if n > 0 else 0.0}
    return {'p_old': ps(2019, 2020), 'p_new': ps(2024, 2025)}

def compute_q4(df, top_n=100, min_year=2013):
    years   = df['album_release_date'].dt.year.to_numpy().astype(np.int64)
    pop     = df['track_popularity'].to_numpy().astype(np.float64)
    artists = df['artist_name'].to_numpy().astype(object)
    m_y = years >= min_year
    years_y, pop_y, artists_y = years[m_y], pop[m_y], artists[m_y]
    unique_years = np.unique(years_y)
    n_unique = np.empty(unique_years.size, dtype=np.int64)
    for i, y in enumerate(unique_years):
        m = years_y == y
        pop_yy, artists_yy = pop_y[m], artists_y[m]
        k = min(top_n, pop_yy.size)
        n_unique[i] = np.unique(artists_yy[np.argpartition(pop_yy, -k)[-k:]]).size if k > 0 else 0
    slope, intercept = np.polyfit(unique_years, n_unique, 1)
    return unique_years, n_unique, slope, slope * unique_years + intercept

stats_q1 = compute_q1(df)
stats_q2 = compute_q2(df)
stats_q3 = compute_q3(df)
years_q4, n_unique_q4, slope_q4, trend_q4 = compute_q4(df)

# --- UI ---
st.title("📊 Vue d'ensemble — 4 axes en synthèse")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Q1 — Pop. moyenne (max)", f"{stats_q1['mean_pop'].max():.1f}/100", WEEKDAY_FR[int(np.argmax(stats_q1['mean_pop']))])
c2.metric("Q2 — Âge médian top", f"{stats_q2['median_weeks_top']:.0f} sem", f"n = {stats_q2['n_top']}")
c3.metric("Q3 — Évolution featurings", f"{stats_q3['p_new']['pct_feat'] - stats_q3['p_old']['pct_feat']:+.1f} pts")
c4.metric("Q4 — Pente diversité", f"{slope_q4:+.2f} artistes/an", "↓" if slope_q4 < 0 else "↑")
st.divider()

col_l, col_r = st.columns(2)

with col_l:
    st.markdown("#### Q1 — Jour de sortie")
    fig_q1 = go.Figure(go.Bar(x=WEEKDAY_FR, y=stats_q1['mean_pop'], marker_color=PALETTE['primary']))
    fig_q1.update_layout(template=DARK_TEMPLATE, height=350, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_q1, use_container_width=True)

with col_r:
    st.markdown("#### Q2 — Temps vers le sommet")
    fig_q2 = go.Figure(go.Histogram(x=stats_q2['age_top_weeks'], nbinsx=30, marker_color=PALETTE['secondary']))
    fig_q2.update_layout(template=DARK_TEMPLATE, height=350, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_q2, use_container_width=True)

with col_l:
    st.markdown("#### Q3 — Featurings")
    fig_q3 = go.Figure(go.Bar(x=['2019-2020', '2024-2025'], y=[stats_q3['p_old']['pct_feat'], stats_q3['p_new']['pct_feat']], marker_color=[PALETTE['neutral'], PALETTE['tertiary']]))
    fig_q3.update_layout(template=DARK_TEMPLATE, height=350, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_q3, use_container_width=True)

with col_r:
    st.markdown("#### Q4 — Diversité Top 100")
    fig_q4 = go.Figure()
    fig_q4.add_trace(go.Scatter(x=years_q4, y=n_unique_q4, mode='lines+markers', line=dict(color=PALETTE['quaternary'], width=3), marker=dict(size=10)))
    fig_q4.add_trace(go.Scatter(x=years_q4, y=trend_q4, mode='lines', line=dict(color=PALETTE['secondary'], width=2, dash='dash')))
    fig_q4.update_layout(template=DARK_TEMPLATE, height=350, margin=dict(l=20, r=20, t=30, b=20), showlegend=False)
    st.plotly_chart(fig_q4, use_container_width=True)

st.caption(SOURCE_NOTE)