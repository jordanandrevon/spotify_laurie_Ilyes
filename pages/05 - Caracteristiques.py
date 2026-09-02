import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# Chargement des données
df_spotify = pd.read_excel("data/Spotify.xlsx")


# Titre de la page
st.title("⏱️ Caractéristiques des titres populaires")

st.write(
    "Cette analyse cherche à identifier certaines caractéristiques "
    "communes aux titres les plus populaires."
)


# Sélection des 10 titres les plus populaires
top_titres = (
    df_spotify
    .sort_values("track_popularity", ascending=False)
    .head(10)
)


# Calcul des durées moyennes
duree_moyenne_dataset = df_spotify["track_duration_min"].mean()
duree_moyenne_top10 = top_titres["track_duration_min"].mean()


# Création d'une catégorie de durée avec NumPy
df_spotify["categorie_duree"] = np.select(
    [
        df_spotify["track_duration_min"] < 3,
        df_spotify["track_duration_min"] < 4
    ],
    [
        "Court",
        "Moyen"
    ],
    default="Long"
)


# Affichage des durées moyennes
col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Durée moyenne du dataset",
        f"{duree_moyenne_dataset:.2f} min"
    )

with col2:
    st.metric(
        "Durée moyenne du Top 10",
        f"{duree_moyenne_top10:.2f} min"
    )


# Graphique des durées du Top 10
fig = px.bar(
    top_titres.sort_values("track_duration_min"),
    x="track_duration_min",
    y="track_name",
    orientation="h",
    labels={
        "track_duration_min": "Durée (minutes)",
        "track_name": "Titre"
    },
    title="Durée des 10 titres les plus populaires"
)

st.plotly_chart(fig, use_container_width=True)


# Analyse des genres du Top 10
genres_top10 = (
    top_titres["artist_genres"]
    .dropna()
    .str.split(",")
    .explode()
    .str.strip()
    .value_counts()
)


st.subheader("🎸 Genres associés au Top 10")


fig_genres = px.bar(
    genres_top10,
    labels={
        "value": "Nombre d'occurrences",
        "index": "Genre"
    },
    title="Genres associés aux titres du Top 10"
)

st.plotly_chart(fig_genres, use_container_width=True)


# Répartition des catégories de durée dans le Top 10
categories_top10 = top_titres.copy()

categories_top10["categorie_duree"] = np.select(
    [
        categories_top10["track_duration_min"] < 3,
        categories_top10["track_duration_min"] < 4
    ],
    [
        "Court",
        "Moyen"
    ],
    default="Long"
)


st.subheader("⏱️ Catégories de durée du Top 10")


repartition_duree = categories_top10["categorie_duree"].value_counts()


fig_duree = px.pie(
    repartition_duree,
    values=repartition_duree.values,
    names=repartition_duree.index,
    title="Répartition des durées des titres du Top 10"
)

st.plotly_chart(fig_duree, use_container_width=True)


# Conclusion
st.subheader("💡 Conclusion")

difference = duree_moyenne_top10 - duree_moyenne_dataset

st.write(
    f"La durée moyenne des titres du Top 10 est de "
    f"**{duree_moyenne_top10:.2f} minutes**, contre "
    f"**{duree_moyenne_dataset:.2f} minutes** pour l'ensemble du dataset."
)

st.write(
    f"L'écart est de **{abs(difference):.2f} minute(s)**. "
    "Cette différence ne permet toutefois pas d'établir une règle générale, "
    "notamment car le Top 10 ne contient que dix titres."
)