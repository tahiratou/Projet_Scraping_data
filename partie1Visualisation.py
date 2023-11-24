from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt



Base = declarative_base()

class DonneeDuRéseau_5min(Base):
    __tablename__ = 'donneesduRéseau_5min'
    date = Column(DateTime, primary_key=True, default=datetime.utcnow) 
    charge_nb = Column(Integer)
    demande_nb = Column(Integer)
    iso_ne = Column(Integer)
    emec = Column(Integer)
    mps = Column(Integer)
    quebec = Column(Integer)
    nova_scotia = Column(Integer)
    pei = Column(Integer)
    marge_reserve_10min_non_synchrone = Column(Integer)
    marge_reserve_10min_synchrone = Column(Integer)
    marge_reserve_30min = Column(Integer)

# Configuration de la base de données
engine = create_engine('sqlite:///donneesduRéseau_5min.db', echo=True)

# Création des tables dans la base de données
Base.metadata.create_all(engine)

# Fonction qui permet de récupérer les données exactes dont j'ai besoin sur la page donnée du réseau
def scraper(url):
    r = requests.get(url)
    bs = BeautifulSoup(r.content, "html.parser")
    table = bs.find_all('table')
    font = bs.find_all('font')

    # Vérifier s'il y a au moins deux balises <table> et récupérer le contenu de la deuxième balise <table>
    if len(table) >= 2:
        deuxieme_table = table[1]
        # Vérifier s'il y a au moins 6 balises <font>
    if len(font) >= 6:
        font6 = font[4]
    # Vérifier s'il y a au moins trois balises <tr> et récupérer le contenu de la deuxième et troisième balises <tr>
    tr = deuxieme_table.find_all('tr')
    if len(tr) >= 3:
        tr2_data = [(td.text.strip()) for td in tr[1].find_all('td')]
        tr3_data = [(td.text.strip()) for td in tr[2].find_all('td')]
        font6_data = [(i.text.strip()) for i in font6.find_all('i')]
    # Créer un DataFrame pandas à partir des données
    df = pd.DataFrame([tr2_data, tr3_data, font6_data])

    # Vérifier si le fichier Excel existe
    if os.path.exists('donnees.xlsx'):
        # Charger le DataFrame existant depuis le fichier Excel
        df_existing = pd.read_excel('donnees.xlsx')

        # Concaténer le DataFrame existant avec le nouveau DataFrame
        df_combined = pd.concat([df_existing, df])
    else:
        # Si le fichier Excel n'existe pas, utiliser le nouveau DataFrame
        df_combined = df
    df_combined.to_excel('donnees.xlsx', index=False)

    # Créer une session SQLAlchemy
    Session = sessionmaker(bind=engine)
    session = Session()

    # Créer un objet Donnee avec les données extraites
    Donnee_5min = DonneeDuRéseau_5min(
        charge_nb=tr3_data[0],
        demande_nb=tr3_data[1],
        iso_ne=tr3_data[2],
        emec=tr3_data[3],
        mps=tr3_data[4],
        quebec=tr3_data[5],
        nova_scotia=tr3_data[6],
        pei=tr3_data[7],
        marge_reserve_10min_non_synchrone=tr3_data[8],
        marge_reserve_10min_synchrone=tr3_data[9],
        marge_reserve_30min=tr3_data[10]
    )

    # Ajouter l'objet à la session et commit pour le stocker dans la base de données
    session.add(Donnee_5min)
    session.commit()


    # Récupérer toutes les données de la table 'donnees'
    donnees = session.query(DonneeDuRéseau_5min).all()
    colonnes_a_extraire = ['date', 'charge_nb', 'demande_nb', 'iso_ne', 'emec', 'mps', 'quebec', 'nova_scotia', 'pei', 'marge_reserve_10min_non_synchrone', 'marge_reserve_10min_synchrone', 'marge_reserve_30min']

    # Initialiser un dictionnaire pour stocker les listes de données pour chaque colonne
    donnees_par_colonne = {colonne: [] for colonne in colonnes_a_extraire}
    # Extraire les données pour chaque colonne
    for donnee in donnees:
        for colonne in colonnes_a_extraire:
            donnees_par_colonne[colonne].append(getattr(donnee, colonne))

    # Tracer les données
    for colonne, valeurs in donnees_par_colonne.items():
        if colonne != 'date':  # Exclure la colonne 'date' du tracé
            plt.plot(donnees_par_colonne['date'], valeurs, marker='o', linestyle='-', label=colonne.capitalize())

    plt.xlabel('Timestamp')
    plt.ylabel('Valeur')
    plt.title('Évolution des valeurs au fil du temps')
    plt.legend()
    plt.xticks(rotation=45)
    plt.show()
    # Fermer la session
    session.close()



# Boucle principale pour exécuter le scraper toutes les 5 minutes
while True:
    scraper("https://tso.nbpower.com/Public/fr/SystemInformation_realtime.asp")
    # Attendre 5 minutes (300 secondes) avant la prochaine exécution
    time.sleep(300)
