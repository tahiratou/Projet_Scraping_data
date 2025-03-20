from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import time
import energyDataHarvest




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

class donnees_archivées(Base):
    __tablename__ = 'donnees_archivées'
    id = Column(Integer, primary_key=True)
    HEURE = Column(String)
    CHARGE_AU_NB = Column(String)
    DEMANDE_AU_NB = Column(String)
    ISO_NE = Column(String)
    NMISA = Column(String)
    QUEBEC = Column(String)
    NOUVELLE_ECOSSE = Column(String)
    IPE = Column(String)

class Interruption(Base):
    __tablename__ = 'interruptions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(Integer)
    category = Column(String)
    forced_outage = Column(String)
    status = Column(String)
    planned_start = Column(String)
    planned_stop = Column(String)
    queued_time = Column(String)
    affected_interfaces = Column(String)
    purpose = Column(String)
    status_comments = Column(String)
    interaction_impacts = Column(String)
    additional_information = Column(String)
    mailto = Column(String)

class prevision_charges(Base):
    __tablename__ = 'previsions_charges'
    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(String)
    charge = Column(Integer)


# Configuration de la base de données
engine = create_engine('sqlite:///energieNB.db', echo=True)

# Création des tables dans la base de données
Base.metadata.create_all(engine)

#Appel de la fonction Interruption
energyDataHarvest.interruption(engine, Interruption) 

#Appel de la fonction donnée_archivées
energyDataHarvest.donnée_archivées(donnees_archivées, engine)


# Appel de la fonction prévisions des charges
energyDataHarvest.previsions_de_charges(prevision_charges, engine)

# Boucle principale pour exécuter le scraper de la page "données du réseau" toutes les 5 minutes
while True:
    energyDataHarvest.scraper(engine, DonneeDuRéseau_5min)
    # Attendre 5 minutes (300 secondes) avant la prochaine exécution
    time.sleep(300)


