import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
import time

# Configuration de Selenium
CHEMIN_PILOTE_CHROME = "C:/Users/tahir/OneDrive/Documents/Logiciels/chromedriver-win64/chromedriver-win64/chromedriver.exe"

class RecupDonneesTempsReel:
    """
    Classe pour récupérer les données en temps réel depuis la page "Données du réseau (mise à jour 5 min)".
    """
    def __init__(self):
        self.url = "https://tso.nbpower.com/Public/fr/SystemInformation_realtime.asp"

    def recuperer_donnees(self):
        """
        Récupère les données en temps réel et les retourne sous forme de dictionnaire.
        """
        reponse = requests.get(self.url)
        if reponse.status_code == 200:
            soup = BeautifulSoup(reponse.content, 'html.parser')
            lignes = soup.find_all('tr')
            titres = [b.get_text().strip() for b in lignes[4].find_all('b')]
            valeurs = [td.get_text().strip() for td in lignes[5].find_all('td')]
            return dict(zip(titres, valeurs))
        else:
            print(f"Échec de la récupération des données. Code d'état : {reponse.status_code}")
            return {}


class RecupDonneesArchivees:
    """
    Classe pour récupérer les données archivées depuis la page "Données archivées".
    """
    def __init__(self):
        self.url = "https://tso.nbpower.com/Public/fr/system_information_archive.aspx"
        self.pilote = webdriver.Chrome(service=Service(CHEMIN_PILOTE_CHROME))

    def recuperer_donnees(self, mois, annee):
        """
        Récupère les données archivées pour un mois et une année donnés.
        """
        self.pilote.get(self.url)
        Select(self.pilote.find_element(By.NAME, 'ctl00$cphMainContent$ddlMonth')).select_by_value(str(mois))
        Select(self.pilote.find_element(By.NAME, 'ctl00$cphMainContent$ddlYear')).select_by_value(str(annee))
        self.pilote.find_element(By.ID, 'ctl00_cphMainContent_lbGetData').click()
        time.sleep(2)  # Attendre le chargement des données

        donnees_csv = self.pilote.find_element(By.TAG_NAME, 'body').text
        if "Erreur" in donnees_csv:
            print(f"Aucune donnée disponible pour {mois}/{annee}.")
            return None
        return donnees_csv

    def fermer_pilote(self):
        """
        Ferme le navigateur Selenium.
        """
        self.pilote.quit()


class RecupInterruptions:
    """
    Classe pour récupérer les données des interruptions depuis la page "Interruptions".
    """
    def __init__(self):
        self.url = "https://tso.nbpower.com/Public/fr/outages.aspx"
        self.pilote = webdriver.Chrome(service=Service(CHEMIN_PILOTE_CHROME))

    def recuperer_donnees(self):
        """
        Récupère les données des interruptions.
        """
        self.pilote.get(self.url)
        time.sleep(2)  # Attendre le chargement de la page

        # Récupérer les éléments <a> avec la classe "popup"
        elements_a = self.pilote.find_elements(By.CSS_SELECTOR, 'a.popup')
        numeros_interruptions = [a.text.strip() for a in elements_a]

        donnees_interruptions = []
        for numero in numeros_interruptions:
            # Simuler un clic sur chaque interruption pour récupérer les détails
            self.pilote.execute_script(f"$('.popup').click();")
            time.sleep(1)
            details = self.pilote.execute_script("""
                return {
                    categorie: $('#mdlDetails .category').text(),
                    statut: $('#mdlDetails .status').text(),
                    debut_prevue: $('#mdlDetails .planned-start').text(),
                    fin_prevue: $('#mdlDetails .planned-stop').text()
                };
            """)
            donnees_interruptions.append({"numero": numero, **details})
            time.sleep(1)

        return donnees_interruptions

    def fermer_pilote(self):
        """
        Ferme le navigateur Selenium.
        """
        self.pilote.quit()


class RecupPrevisions:
    """
    Classe pour récupérer les données de prévision des charges.
    """
    def __init__(self):
        self.url = "https://tso.nbpower.com/Public/fr/op/market/report_list.aspx?path=/load%20forecast"
        self.pilote = webdriver.Chrome(service=Service(CHEMIN_PILOTE_CHROME))

    def recuperer_donnees(self):
        """
        Récupère les données de prévision des charges en parcourant les dossiers, sous-dossiers et fichiers CSV.
        """
        self.pilote.get(self.url)
        time.sleep(10)  # Attendre le chargement de la page

        # Liste pour stocker les données CSV
        donnees_csv = []

        # Fonction récursive pour parcourir les dossiers et sous-dossiers
        def parcourir_dossier():
            # Récupérer tous les éléments de la page (dossiers et fichiers)
            elements = self.pilote.find_elements(By.CSS_SELECTOR, 'a[href]')

            # Parcourir les éléments
            for element in elements:
                if "lv_" in element.get_attribute("id"):  # Les dossiers ont un ID commençant par "lv_"
                    dossier_nom = element.text
                    print(f"Ouverture du dossier : {dossier_nom}")
                    element.click()  # Ouvrir le dossier
                    time.sleep(5)  # Attendre le chargement du dossier

                    # Récupérer les fichiers CSV dans le dossier actuel
                    fichiers_csv = self.pilote.find_elements(By.CSS_SELECTOR, 'a[href$=".csv"]')
                    for fichier in fichiers_csv:
                        url_fichier = fichier.get_attribute('href')
                        reponse = requests.get(url_fichier)
                        if reponse.status_code == 200:
                            donnees_csv.append(reponse.text)
                            print(f"Fichier CSV récupéré : {url_fichier}")
                        else:
                            print(f"Échec de la récupération du fichier {url_fichier}. Code d'état : {reponse.status_code}")

                    # Parcourir les sous-dossiers récursivement
                    parcourir_dossier()

                    # Revenir au dossier parent
                    self.pilote.back()
                    time.sleep(5)

        # Commencer le parcours à partir de la page principale
        parcourir_dossier()

        return donnees_csv

    def fermer_pilote(self):
        """
        Ferme le navigateur Selenium.
        """
        self.pilote.quit()