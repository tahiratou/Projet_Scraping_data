import pandas as pd
from io import StringIO  # Utiliser StringIO depuis la bibliothèque standard

def traite_donnees_temps_reel(donnees_brutes):
    """
    Traite les données en temps réel.
    """
    if not donnees_brutes:
        return None

    # Convertir les données en DataFrame pour un traitement facile
    donnees_traitees = pd.DataFrame([donnees_brutes])
    return donnees_traitees

def traite_donnees_archivees(donnees_brutes):
    """
    Traite les données archivées.
    """
    if not donnees_brutes:
        return None

    # Convertir les données en DataFrame
    donnees_traitees = pd.read_csv(StringIO(donnees_brutes))  # Utiliser StringIO directement
    return donnees_traitees

def traite_interruptions(donnees_brutes):
    """
    Traite les données des interruptions.
    """
    if not donnees_brutes:
        return None

    # Convertir les données en DataFrame
    donnees_traitees = pd.DataFrame(donnees_brutes)
    return donnees_traitees

def traite_previsions(donnees_brutes):
    """
    Traite les données de prévision des charges.
    """
    if not donnees_brutes:
        return None

    # Convertir les données en DataFrame
    dfs = []
    for csv_data in donnees_brutes:
        df = pd.read_csv(pd.compat.StringIO(csv_data))
        dfs.append(df)
    donnees_traitees = pd.concat(dfs, ignore_index=True)
    return donnees_traitees