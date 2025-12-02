# app.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# ============================================================
# 1. Paramètres généraux
# ============================================================

CSV_PATH = "Flex4IoT.csv"   # nom du fichier de mesures
TOLERANCE = 0.5             # tolérance ± °C autour de la consigne

# ------------------------------------------------------------
# 2. Définition des zones et des pièces (sans "Eteindre")
# ------------------------------------------------------------

ZONE_ROOMS = {
    "Classes": [
        "Salle 31",
        "Salle 32",
        "Salle étude 2",
        "Classe 1",
        "Classe 2",
        "Classe 3",
        "Classe 5",
        "Classe 6",
        "Classe 7",
        "Classe 8",
        "Classe 9",
        "Classe 10",
        "Classe 11",
        "Classe 12",
        "Classe 13",
        "Classe 14",
        "Salle de dessin 13",
        "Classe 16",
        "Classe 17",
        "Classe 18",
        "Classe 19",
        "Classe 21",
        "Classe 22",
        "Classe 23",
        "Classe 4",
        "Salle 30",
        "Salle 34",
        "Salle 33",
    ],
    "Circulations": [
        "Couloir 1e Bat 6",
        "Degagement 3 bat 3",
        "Degagement - 15",
        "Couloir RDC - 5",
        "Couloir bureaux",
        "Couloir RDC Bat 6",
        "Degagement 4 - 2",
    ],
    "Locaux annexe": [
        "Sanitaire - 9",
        "Orientation",
        "Gardien - 29",
        "Sanitaire 1E - 5",
        "Vestiaire 6",
        "Dépot 5",
        "Dépot 4 - 6",
        "Dépot 2 - 7",
        "Labo - 6",
        "Labo - 8",
        "Labo - 10",
        "WC - 12",
        "WC - 11",
        "Sanitaire 22",
        "Sanitaire 23",
        "WC Personnel -- 20",
        "Sanitaire RDC - 5",
        "Depot 9",
        "Dépot 2 - 6",
        "Sanitaires Hommes 1E - 6",
        "Sanitaires Dames 1E - 6",
    ],
    "Administratif": [
        "Infirmerie",
        "Lingerie",
        "Soins",
        "CDI",
        "S T P",
        "Salle des machines - 20",
        "Conseiller - 18",
        "Principal adjoint - 24",
        "Secretariat - 25",
        "Direction - 26",
        "Salle des profs",
        "Salle de réunion",
    ],
    "Refectoire": [
        "Cantine",
        "SAM Prof 1",
        "SAM Prof 2",
    ],
    "Salle polyvalente": [
        "Préau",
    ],
    "Cuisine": [
        "Plonge",
        "Reserve - 11",
        "Entrée - 18",
        "Cuisine",
    ],
    "Radiateur electrique": [
        "Salle étude 1",
        "Salle de réunion - 32",
        "Atelier - 7",
        "Vie scolaire - 3",
        "Gestion - 30",
        "Bureau CPE - 1",
        "Salle de travail - 2",
    ],
}


def normalize_name(name: str) -> str:
    """
    Normalise un nom de pièce :
    - enlève le mot 'Eteindre' s'il est présent
    - strip espaces
    """
    if not isinstance(name, str):
        return ""
    return name.replace("Eteindre", "").strip()


# mapping inverse pièce -> zone
ROOM_TO_ZONE = {
    normalize_name(room): zone
    for zone, rooms in ZONE_ROOMS.items()
    for room in rooms
}

# ------------------------------------------------------------
# 3. Scénarios par zone (fonction de consigne)
# ------------------------------------------------------------

def get_setpoint(zone: str, dt) -> float:
    """
    Retourne la consigne (°C) pour une zone donnée et un datetime.
    Scénarios définis pour chaque zone.
    """

    if zone is None or zone == "" or zone == "Inconnue" or pd.isna(zone):
        return np.nan

    weekday = dt.weekday()  # 0 = lundi ... 6 = dimanche
    h = dt.hour
    m = dt.minute
    minutes = h * 60 + m

    is_weekend = weekday >= 5  # samedi/dimanche

    if zone == "Classes":
        if is_weekend:
            return 16.0
        # 19° de 5:30 à 17:00, 17° sinon
        day_start = 5 * 60 + 30
        day_end = 17 * 60
        return 19.0 if (day_start <= minutes < day_end) else 17.0

    elif zone == "Circulations":
        if is_weekend:
            return 15.0
        # 17° de 6:00 à 17:00, 16° sinon
        day_start = 6 * 60
        day_end = 17 * 60
        return 17.0 if (day_start <= minutes < day_end) else 16.0

    elif zone == "Locaux annexe":
        if is_weekend:
            return 15.0
        # 17° de 8:00 à 17:00, 16° sinon
        day_start = 8 * 60
        day_end = 17 * 60
        return 17.0 if (day_start <= minutes < day_end) else 16.0

    elif zone == "Administratif":
        if is_weekend:
            return 16.0
        # 19° de 5:30 à 17:00, 17° sinon
        day_start = 5 * 60 + 30
        day_end = 17 * 60
        return 19.0 if (day_start <= minutes < day_end) else 17.0

    elif zone == "Refectoire":
        if is_weekend:
            return 17.0
        # 21° de 6:00 à 17:00, 18° sinon
        day_start = 6 * 60
        day_end = 17 * 60
        return 21.0 if (day_start <= minutes < day_end) else 18.0

    elif zone == "Salle polyvalente":
        if is_weekend:
            return 15.0
        # 19° de 6:00 à 17:00, 17° sinon
        day_start = 6 * 60
        day_end = 17 * 60
        return 19.0 if (day_start <= minutes < day_end) else 17.0

    elif zone in ("Cuisine", "Radiateur electrique"):
        if is_weekend:
            return 15.0
        # 19° de 6:00 à 17:00, 17° sinon
        day_start = 6 * 60
        day_end = 17 * 60
        return 19.0 if (day_start <= minutes < day_end) else 17.0

    return np.nan


# ------------------------------------------------------------
# 4. Chargement et pré-traitement des données
# ------------------------------------------------------------

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # noms normalisés pour match avec les listes
    df["Name_clean"] = df["Name"].apply(normalize_name)

    # zone à partir du mapping
    df["Zone"] = df["Name_clean"].map(ROOM_TO_ZONE)
    df["Zone"] = df["Zone"].fillna("Inconnue")

    # datetime
    df["datetime_utc"] = pd.to_datetime(df["time"], utc=True)
    try:
        df["datetime"] = df["datetime_utc"].dt.tz_convert("Europe/Paris")
    except Exception:
        df["datetime"] = df["datetime_utc"].dt.tz_localize(None)

    df["weekday"] = df["datetime"].dt.weekday
    df["date"] = df["datetime"].dt.date

    # consigne
    df["consigne"] = df.apply(
        lambda r: get_setpoint(r["Zone"], r["datetime"]), axis=1
    )

    # écart et booléen OK
    df["ecart"] = df["temperature"] - df["consigne"]
    df["OK"] = df["ecart"].abs() <= TOLERANCE

    return df


def compute_stats(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}
    stats = {
        "Température moyenne": df["temperature"].mean(),
        "Consigne moyenne": df["consigne"].mean(),
        "Écart moyen (mesure - consigne)": df["ecart"].mean(),
        "Écart max absolu": df["ecart"].abs().max(),
        "Température min": df["temperature"].min(),
        "Température max": df["temperature"].max(),
        "Pourcentage de temps dans la tolérance": 100.0 * df["OK"].mean(),
    }
    return stats


# ------------------------------------------------------------
# 5. Tracé des graphiques
# ------------------------------------------------------------

def plot_piece_series(df_piece: pd.DataFrame, piece_name: str, zone_name: str):
    """
    Trace température et consigne pour UNE pièce.
    """
    if df_piece.empty:
        st.warning(f"Pas de données pour la pièce {piece_name}.")
        return

    g = df_piece.groupby("datetime").agg(
        temperature=("temperature", "mean"),
        consigne=("consigne", "mean"),
    ).reset_index()

    plt.figure(figsize=(6, 3))
    plt.plot(g["datetime"], g["temperature"], label="Température")
    plt.plot(g["datetime"], g["consigne"], linestyle="--", label="Consigne")
    plt.xlabel("Temps")
    plt.ylabel("Température (°C)")
    plt.title(f"{piece_name} – {zone_name}")
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.close()


# ------------------------------------------------------------
# 6. Application Streamlit
# ------------------------------------------------------------

def main():
    st.title("Analyse des températures par zone et par pièce")

    st.caption(f"Fichier de données : **{CSV_PATH}**")
    df = load_data(CSV_PATH)

    mode = st.radio(
        "Mode d'affichage",
        ["Vue globale par zone", "Vue détaillée par pièce"],
    )

    zones = list(ZONE_ROOMS.keys())

    if mode == "Vue globale par zone":
        zone_sel = st.selectbox("Zone à analyser :", zones)

        df_zone = df[df["Zone"] == zone_sel].copy()
        st.write(
            f"Nombre de mesures pour la zone **{zone_sel}** : {len(df_zone)}"
        )

        stats = compute_stats(df_zone)
        if not stats:
            st.warning("Aucune donnée pour cette zone.")
            return

        st.subheader("Statistiques de la zone")
        for k, v in stats.items():
            if "Pourcentage" in k:
                st.write(f"- {k} : {v:.1f} %")
            else:
                st.write(f"- {k} : {v:.2f}")

        st.subheader("Graphiques par pièce dans la zone")

        pieces_zone = sorted(df_zone["Name_clean"].unique())
        cols = st.columns(2)

        for i, piece in enumerate(pieces_zone):
            df_piece = df_zone[df_zone["Name_clean"] == piece].copy()
            col = cols[i % 2]
            with col:
                st.markdown(f"**{piece}**")
                plot_piece_series(df_piece, piece, zone_sel)

    else:  # Vue détaillée par pièce
        zone_sel = st.selectbox("Choisir une zone :", zones)

        df_zone = df[df["Zone"] == zone_sel].copy()
        pieces_dispo = sorted(df_zone["Name_clean"].unique())

        if not pieces_dispo:
            st.warning("Aucune pièce trouvée pour cette zone.")
            return

        piece_sel = st.selectbox("Choisir une pièce :", pieces_dispo)

        df_piece = df_zone[df_zone["Name_clean"] == piece_sel].copy()
        st.write(
            f"Nombre de mesures pour **{piece_sel}** (zone {zone_sel}) : {len(df_piece)}"
        )

        stats = compute_stats(df_piece)
        if not stats:
            st.warning("Pas assez de données pour cette pièce.")
            return

        st.subheader("Statistiques de la pièce")
        for k, v in stats.items():
            if "Pourcentage" in k:
                st.write(f"- {k} : {v:.1f} %")
            else:
                st.write(f"- {k} : {v:.2f}")

        st.subheader("Température vs consigne pour la pièce")
        plot_piece_series(df_piece, piece_sel, zone_sel)


if __name__ == "__main__":
    main()
