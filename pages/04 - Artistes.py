import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# Chargement des données
df_spotify = pd.read_excel("data/Spotify.xlsx")


# Titre de la page
st.title("👨‍🎤 Artistes populaires et suivis")

st.write(
    "Quels artistes combinent une forte popularité "
    "et un grand nombre de followers ?"
)


# Regroupement des données par artiste
# On conserve uniquement les artistes présents sur au moins 3 titres
artistes_analyse = (
    df_spotify
    .groupby("artist_name")
    .agg(
        nombre_titres=("track_name", "count"),
        popularite=("artist_popularity", "max"),
        followers=("artist_followers", "max")
    )
    .query("nombre_titres >= 3")
    .copy()
)


# Normalisation des données avec NumPy
# Les deux indicateurs sont ramenés sur une échelle de 0 à 1

popularite_min = artistes_analyse["popularite"].min()
popularite_max = artistes_analyse["popularite"].max()

followers_min = artistes_analyse["followers"].min()
followers_max = artistes_analyse["followers"].max()


artistes_analyse["popularite_normalisee"] = (
    (artistes_analyse["popularite"] - popularite_min)
    / (popularite_max - popularite_min)
)

artistes_analyse["followers_normalises"] = (
    (artistes_analyse["followers"] - followers_min)
    / (followers_max - followers_min)
)


# Calcul du score combiné avec NumPy
# Les deux critères ont ici le même poids
artistes_analyse["score"] = np.mean(
    [
        artistes_analyse["popularite_normalisee"],
        artistes_analyse["followers_normalises"]
    ],
    axis=0
)


# Classement selon le score
top_artistes_forts = (
    artistes_analyse
    .sort_values("score", ascending=False)
    .head(10)
)


# Graphique
fig = px.scatter(
    top_artistes_forts,
    x="followers",
    y="popularite",
    text=top_artistes_forts.index,
    size="score",
    hover_data=[
        "nombre_titres",
        "followers",
        "popularite",
        "score"
    ],
    log_x=True,
    labels={
        "followers": "Nombre de followers",
        "popularite": "Popularité",
        "score": "Score combiné"
    },
    title="Top 10 des artistes populaires et suivis"
)

fig.update_traces(
    textposition="top center"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# Classement
st.subheader("🏆 Classement")

st.dataframe(
    top_artistes_forts[
        [
            "nombre_titres",
            "popularite",
            "followers",
            "score"
        ]
    ].round(
        {
            "score": 3
        }
    ),
    use_container_width=True
)


# Conclusion
st.subheader("💡 Conclusion")

meilleur_artiste = top_artistes_forts.index[0]
meilleur_score = top_artistes_forts.iloc[0]["score"]

st.write(
    f"Selon notre score combiné, **{meilleur_artiste}** arrive en première "
    f"position avec un score de **{meilleur_score:.3f}**."
)

st.write(
    "Ce score permet de prendre en compte simultanément la popularité "
    "de l'artiste et son nombre de followers."
)