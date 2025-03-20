import pandas as pd
from sqlalchemy import create_engine
import os

# Configuration de la base de données
NOM_BDD = "donnees_nbpower.db"
CHEMIN_BDD = f"sqlite:///{NOM_BDD}"  # Utilisation de SQLite pour simplifier
engine = create_engine(CHEMIN_BDD)

def exporter_vers_excel(donnees, nom_fichier):
    """
    Exporte les données vers un fichier Excel.
    
    Args:
        donnees (pd.DataFrame): Les données à exporter.
        nom_fichier (str): Le nom du fichier Excel (sans extension).
    """
    if donnees is not None and not donnees.empty:
        chemin_fichier = f"{nom_fichier}.xlsx"
        donnees.to_excel(chemin_fichier, index=False)
        print(f"Données exportées vers {chemin_fichier}")
    else:
        print("Aucune donnée à exporter.")

def exporter_vers_bdd(donnees, nom_table):
    """
    Exporte les données vers la base de données.
    
    Args:
        donnees (pd.DataFrame): Les données à exporter.
        nom_table (str): Le nom de la table dans la base de données.
    """
    if donnees is not None and not donnees.empty:
        donnees.to_sql(nom_table, con=engine, if_exists="append", index=False)
        print(f"Données exportées vers la table '{nom_table}' dans la base de données.")
    else:
        print("Aucune donnée à exporter.")

def supprimer_bdd_et_fichiers():
    """
    Supprime la base de données et les fichiers Excel créés.
    """
    try:
        # Supprimer la base de données
        if os.path.exists(NOM_BDD):
            os.remove(NOM_BDD)
            print(f"Base de données '{NOM_BDD}' supprimée.")
        
        # Supprimer les fichiers Excel
        fichiers_excel = [f for f in os.listdir() if f.endswith(".xlsx")]
        for fichier in fichiers_excel:
            os.remove(fichier)
            print(f"Fichier '{fichier}' supprimé.")
    except Exception as e:
        print(f"Erreur lors de la suppression : {e}")

