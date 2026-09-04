import os, glob, numpy as np, pandas as pd, streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Q4 — Diversité Top 100", page_icon="🏆", layout="wide")

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

# --- Q4 CALCUL NUMPY ---
def compute_q4(df, top_n=100, min_year=2013):
    years   = df['album_release_date'].dt.year.to_numpy().astype(np.int64)
    pop     = df['track_popularity'].to_numpy().astype(np.float64)
    artists = df['artist_name'].to_numpy().astype(object)
    mask_y = years >= min_year
    years_y, pop_y, artists_y = years[mask_y], pop[mask_y], artists[mask_y]
    unique_years = np.unique(years_y)
    n = unique_years.size
    n_unique = np.empty(n, dtype=np.int64)
    n_total  = np.empty(n, dtype=np.int64)
    for i, y in enumerate(unique_years):
        m = years_y == y
        pop_yy     = pop_y[m]
        artists_yy = artists_y[m]
        n_total[i] = m.sum()
        k = min(top_n, pop_yy.size)
        if k > 0:
            top_idx    = np.argpartition(pop_yy, -k)[-k:]
            n_unique[i] = np.unique(artists_yy[top_idx]).size
        else:
            n_unique[i] = 0
    slope, intercept = np.polyfit(unique_years, n_unique, 1)
    trend = slope * unique_years + intercept
    return unique_years, n_unique, n_total, slope, intercept, trend

min_y = int(df['album_release_date'].dt.year.min())
max_y = int(df['album_release_date'].dt.year.max())
top_n = st.sidebar.slider("Taille du Top N", 50, 200, 100, step=10)
min_year = st.sidebar.slider("Année minimale", min_y, max_y, max(2013, min_y))

years, n_unique, n_total, slope, intercept, trend = compute_q4(df, top_n=top_n, min_year=min_year)

# --- UI ---
st.title("🏆 Diversité des artistes dans le Top N par année")
st.markdown("**Question** : Le nombre d'artistes différents représentés dans le Top N augmente-t-il ou diminue-t-il avec le temps ?")

delta_label = "↓ décroissante" if slope < 0 else "↑ croissante"
st.metric("Tendance linéaire (pente)", f"{slope:+.2f} artistes/an", delta=delta_label)
st.divider()

# Graphique Principal
st.subheader(f"Diversité des artistes dans le Top {top_n} par année")
fig = go.Figure()
fig.add_trace(go.Bar(x=years, y=n_total, name='Nb total de sorties', marker_color=PALETTE['neutral'], opacity=0.3, yaxis='y2'))
fig.add_trace(go.Scatter(x=years, y=n_unique, mode='lines+markers', line=dict(color=PALETTE['primary'], width=3), marker=dict(size=12), name=f'Artistes uniques Top {top_n}', text=[f'{int(v)}' for v in n_unique], textposition='top center'))
fig.add_trace(go.Scatter(x=years, y=trend, mode='lines', line=dict(color=PALETTE['secondary'], width=2, dash='dash'), name=f'Tendance ({slope:+.2f}/an)'))

# CORRECTION ICI : titlefont est devenu title=dict(font=...)
fig.update_layout(template=DARK_TEMPLATE, title='Diversité vs Volume total', xaxis_title='Année',
                  yaxis=dict(title=dict(text='Artistes uniques', font=dict(color=PALETTE['primary'])), tickfont=dict(color=PALETTE['primary']), gridcolor='#333333'),
                  yaxis2=dict(title=dict(text='Nb total de sorties', font=dict(color=PALETTE['neutral'])), tickfont=dict(color=PALETTE['neutral']), overlaying='y', side='right', showgrid=False),
                  height=600, legend=dict(orientation='h', yanchor='bottom', y=1.02))
st.plotly_chart(fig, use_container_width=True)

st.caption(SOURCE_NOTE + f" Top {top_n} par popularité pour chaque année ≥ {min_year}.")