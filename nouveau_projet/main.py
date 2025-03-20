from recup_données import (
    RecupDonneesTempsReel,
    RecupDonneesArchivees,
    RecupInterruptions,
    RecupPrevisions
)
from traitement_données import (
    traite_donnees_temps_reel,
    traite_donnees_archivees,
    traite_interruptions,
    traite_previsions
)
from export_données import (
    exporter_vers_excel,
    exporter_vers_bdd
)

def main():
    """
    Fonction principale pour exécuter la récupération, le traitement et le stockage des données.
    """
    # 1. Récupération des données en temps réel
    donnees_temps_reel_brutes = RecupDonneesTempsReel().recuperer_donnees()
    
    # 2. Traitement des données en temps réel
    donnees_temps_reel_traitees = traite_donnees_temps_reel(donnees_temps_reel_brutes)
    
    # 3. Stockage des données en temps réel
    if donnees_temps_reel_traitees is not None:
        exporter_vers_excel(donnees_temps_reel_traitees, "donnees_temps_reel")
        exporter_vers_bdd(donnees_temps_reel_traitees, "donnees_temps_reel")

    # 1. Récupération des données archivées (exemple pour janvier 2023)
    donnees_archivees_brutes = RecupDonneesArchivees().recuperer_donnees(mois=1, annee=2023)
    
    # 2. Traitement des données archivées
    donnees_archivees_traitees = traite_donnees_archivees(donnees_archivees_brutes)
    
    # 3. Stockage des données archivées
    if donnees_archivees_traitees is not None:
        exporter_vers_excel(donnees_archivees_traitees, "donnees_archivees")
        exporter_vers_bdd(donnees_archivees_traitees, "donnees_archivees")
    RecupDonneesArchivees().fermer_pilote()

    # 1. Récupération des données des interruptions
    donnees_interruptions_brutes = RecupInterruptions().recuperer_donnees()
    
    # 2. Traitement des données des interruptions
    donnees_interruptions_traitees = traite_interruptions(donnees_interruptions_brutes)
    
    # 3. Stockage des données des interruptions
    if donnees_interruptions_traitees is not None:
        exporter_vers_excel(donnees_interruptions_traitees, "donnees_interruptions")
        exporter_vers_bdd(donnees_interruptions_traitees, "donnees_interruptions")
    RecupInterruptions().fermer_pilote()

    # 1. Récupération des données de prévision des charges
    donnees_previsions_brutes = RecupPrevisions().recuperer_donnees()
    
    # 2. Traitement des données de prévision des charges
    donnees_previsions_traitees = traite_previsions(donnees_previsions_brutes)
    
    # 3. Stockage des données de prévision des charges
    if donnees_previsions_traitees is not None:
        exporter_vers_excel(donnees_previsions_traitees, "donnees_previsions")
        exporter_vers_bdd(donnees_previsions_traitees, "donnees_previsions")
    RecupPrevisions().fermer_pilote()

if __name__ == "__main__":
    main()